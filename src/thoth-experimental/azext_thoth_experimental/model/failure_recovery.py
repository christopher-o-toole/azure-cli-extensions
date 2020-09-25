# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import re
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Pattern, Union

import azure.cli.core.telemetry as cli_core_telemetry

from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental.parser import CommandParseTable

from azext_thoth_experimental.model._file_util import assert_file_exists
from azext_thoth_experimental.model.help import HelpTable

logger = get_logger(__name__)

ModelType = Dict[str, Dict[str, Dict[str, str]]]

SCRIPT_PATH: Path = Path(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_MODEL_PATH: Path = SCRIPT_PATH / 'model.json'


class UserFaultType(Enum):
    ExpectedArgument = 'ExpectedArgument'
    UnrecognizedArguments = 'UnrecognizedArguments'
    ValidationError = 'ValidationError'
    UnknownSubcommand = 'UnknownSubcommand'
    MissingRequiredParameters = 'MissingRequiredParameters'
    MissingRequiredSubcommand = 'MissingRequiredSubcommand'
    StorageAccountNotFound = 'StorageAccountNotFound'
    Unknown = 'Unknown'
    InvalidJMESPathQuery = 'InvalidJMESPathQuery'
    InvalidOutputType = 'InvalidOutputType'
    InvalidParameterValue = 'InvalidParameterValue'
    UnableToParseCommandInput = 'UnableToParseCommandInput'
    ResourceGroupNotFound = 'ResourceGroupNotFound'
    InvalidDateTimeArgumentValue = 'InvalidDateTimeArgumentValue'
    InvalidResourceGroupName = 'InvalidResourceGroupName'
    AzureResourceNotFound = 'AzureResourceNotFound'
    InvalidAccountName = 'InvalidAccountName'

    def __eq__(self, value: Union['UserFaultType', str]):
        if hasattr(value, 'value'):
            value = value.value
        # pylint: disable=comparison-with-callable
        return self.value == value

    def __hash__(self):
        return hash(self.value)


def _handle_invalid_help_call(match: re.Match, help_table: Union[HelpTable, None] = None) -> List[Suggestion]:
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
            if match := rule.match(parser.command):
                suggestions = handler(match, help_table)

        return suggestions


def get_error_message():
    # pylint: disable=protected-access
    error_message = cli_core_telemetry._session.result_summary

    if not error_message:
        from azure.cli.core.error import AzCliErrorHandler
        error_handler = AzCliErrorHandler()
        last_error = error_handler.get_last_error()

        if last_error:
            error_message = last_error.overridden_message

    return error_message.lower().strip()


class FailureRecoveryModel():
    def __init__(self, model: ModelType):
        super().__init__()
        self.model = model
        self.rule_based_model = RuleBasedFailureRecoveryModel()

    def _get_user_fault_type(self) -> UserFaultType:
        # pylint: disable=protected-access

        error_message = get_error_message()
        user_fault_type: UserFaultType = UserFaultType.Unknown

        if error_message is not None:
            logger.debug(f'Classiying the following error message "{error_message}"')

            if 'unrecognized' in error_message:
                user_fault_type = UserFaultType.UnrecognizedArguments
            elif 'expected one argument' in error_message or 'expected at least one argument' in error_message \
                 or 'value required' in error_message:
                user_fault_type = UserFaultType.ExpectedArgument
            elif 'command not found' in error_message or 'command group' in error_message:
                user_fault_type = UserFaultType.UnknownSubcommand
            elif 'arguments are required' in error_message or 'argument required' in error_message:
                user_fault_type = UserFaultType.MissingRequiredParameters
                if '_subcommand' in error_message:
                    user_fault_type = UserFaultType.MissingRequiredSubcommand
                elif '_command_package' in error_message:
                    user_fault_type = UserFaultType.UnableToParseCommandInput
            elif 'not found' in error_message or 'could not be found' in error_message \
                 or 'resource not found' in error_message:
                user_fault_type = UserFaultType.AzureResourceNotFound
                if 'storage_account' in error_message or 'storage account' in error_message:
                    user_fault_type = UserFaultType.StorageAccountNotFound
                elif 'resource_group' in error_message or 'resource group' in error_message:
                    user_fault_type = UserFaultType.ResourceGroupNotFound
            elif 'pattern' in error_message or 'is not a valid value' in error_message or 'invalid' in error_message:
                user_fault_type = 'InvalidParameterValue'
                if 'jmespath_type' in error_message:
                    user_fault_type = UserFaultType.InvalidJMESPathQuery
                elif 'datetime_type' in error_message:
                    user_fault_type = UserFaultType.InvalidDateTimeArgumentValue
                elif '--output' in error_message:
                    user_fault_type = UserFaultType.InvalidOutputType
                elif 'resource_group' in error_message:
                    user_fault_type = UserFaultType.InvalidResourceGroupName
                elif 'storage_account' in error_message:
                    user_fault_type = UserFaultType.InvalidAccountName
            elif "validation error" in error_message:
                user_fault_type = UserFaultType.ValidationError
        else:
            logger.debug('Result summary was None. Unable to classify error.')

        if user_fault_type != UserFaultType.Unknown:
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

    def get_suggestions(self, parser: CommandParseTable, user_fault_type: Union[UserFaultType, None] = None,
                        help_table: Union[HelpTable, None] = None) -> List[Suggestion]:
        resource_not_found_user_fault_type_set = {
            UserFaultType.InvalidResourceGroupName,
            UserFaultType.InvalidAccountName,
            UserFaultType.AzureResourceNotFound,
            UserFaultType.StorageAccountNotFound,
            UserFaultType.ResourceGroupNotFound
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
