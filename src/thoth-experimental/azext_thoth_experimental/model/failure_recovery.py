# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import re
from pathlib import Path
from typing import Callable, Dict, List, Match, Pattern, Union

import azure.cli.core.telemetry as cli_core_telemetry
from azure.cli.core.command_recommender import AladdinUserFaultType

from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental.hook._cli_error_handling import command_recommender_hook
from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental.parser import CommandParseTable

from azext_thoth_experimental.model._file_util import assert_file_exists
from azext_thoth_experimental.model.help import HelpTable

logger = get_logger(__name__)

ModelType = Dict[str, Dict[str, Dict[str, str]]]

SCRIPT_PATH: Path = Path(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_MODEL_PATH: Path = SCRIPT_PATH / 'model.json'


def _handle_invalid_help_call(match: Match, help_table: Union[HelpTable, None] = None) -> List[Suggestion]:
    command_or_command_group: str = match.group('command_or_command_group')
    if help_table and command_or_command_group in help_table:
        return [
            {
                'command': command_or_command_group,
                'description': f'Show help for az {command_or_command_group}',
                'parameters': '--help',
                'placeholders': ''
            }
        ]


class RuleBasedFailureRecoveryModel():
    def __init__(self):
        super().__init__()

        self.rules: Dict[Pattern[str], Callable[[str], List[Suggestion]]] = {
            re.compile(r'(?P<command_or_command_group>[a-z-\s]+)\s+(help)$'): _handle_invalid_help_call
        }

    def get_suggestions(self, parser: CommandParseTable, help_table: Union[HelpTable, None] = None) -> List[Suggestion]:
        suggestions: List[Suggestion] = []

        for rule, handler in self.rules.items():
            match = rule.match(parser.command)
            if match:
                suggestions = handler(match, help_table)

        return suggestions


def get_error_message():
    from azext_thoth_experimental.hook._cli_error_handling import last_cli_error
    # pylint: disable=protected-access
    error_message = last_cli_error.original_error_message or cli_core_telemetry._session.result_summary
    return error_message.lower().strip()


class FailureRecoveryModel():
    def __init__(self, model: ModelType):
        super().__init__()
        self.model = model
        self.rule_based_model = RuleBasedFailureRecoveryModel()

    def _get_user_fault_type(self) -> AladdinUserFaultType:
        # cli may not call aladdin service for every type of error. this statement
        # rectifies that.
        if not command_recommender_hook.classified_error_type:
            command_recommender_hook.error_msg = get_error_message()
            # pylint: disable=protected-access
            command_recommender_hook._set_aladdin_recommendations()

        user_fault_type = command_recommender_hook.aladdin_user_fault_type

        if user_fault_type != AladdinUserFaultType.Unknown:
            logger.debug(f"Classified error as {user_fault_type}")
        else:
            logger.debug('Unknown error type. This may impact model performance.')

        return user_fault_type

    def _reduce(self, entity: str, keys: List[str], delim: str = ' ', recurse: bool = True):
        key: Union[str, None] = entity

        if entity and entity not in keys and recurse:
            last_delim_idx = entity.rfind(delim)
            if last_delim_idx != -1:
                key = self._reduce(key[:last_delim_idx], keys)
                logger.debug('FailureRecoveryModel._reduce : Reduce operation yielded key %r', key)

        return key

    def get_suggestions(self, parser: CommandParseTable, user_fault_type: Union[AladdinUserFaultType, None] = None,
                        help_table: Union[HelpTable, None] = None) -> List[Suggestion]:
        resource_not_found_user_fault_type_set = {
            AladdinUserFaultType.InvalidResourceGroupName,
            AladdinUserFaultType.InvalidAccountName,
            AladdinUserFaultType.AzureResourceNotFound,
            AladdinUserFaultType.StorageAccountNotFound,
            AladdinUserFaultType.ResourceGroupNotFound
        }
        user_fault_type = user_fault_type or self._get_user_fault_type()
        # get suggestions based on rule-based logic.
        suggestions = self.rule_based_model.get_suggestions(parser, help_table)
        # get suggestions from a more complex model if rule-based logic fails.
        key = '' if user_fault_type in resource_not_found_user_fault_type_set else parser.command
        user_fault_type_model = self.model.get(user_fault_type, {})
        key = self._reduce(key, user_fault_type_model.keys())
        suggestions = suggestions or user_fault_type_model.get(key, [])
        return [Suggestion.parse(suggestion, help_table) for suggestion in suggestions]

    @classmethod
    def load(cls, path: Path = DEFAULT_MODEL_PATH):
        assert_file_exists(path)
        model: dict = None

        with open(path) as model_file:
            model = json.load(model_file)

        return cls(model)
