# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Union

import azure.cli.core.telemetry as cli_core_telemetry

from azext_thoth_experimental._logging import get_logger

from azext_thoth_experimental.model.file_util import assert_file_exists

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


class FailureRecoveryModel():
    def __init__(self, model: ModelType):
        super().__init__()
        self.model = model

    def _get_user_fault_type(self) -> UserFaultType:
        # pylint: disable=protected-access
        error_message = cli_core_telemetry._session.result_summary
        user_fault_type: UserFaultType = UserFaultType.Unknown

        if error_message is not None:
            error_message = error_message.lower()
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
                if 'storage_account' in error_message:
                    user_fault_type = UserFaultType.StorageAccountNotFound
                elif 'resource_group' in error_message:
                    user_fault_type = UserFaultType.ResourceGroupNotFound
            elif 'pattern' in error_message or 'is not a valid value' in error_message or 'invalid' in error_message:
                user_fault_type = 'InvalidParameterValue'
                if 'jmespath_type' in error_message:
                    user_fault_type = UserFaultType.InvalidJMESPathQuery
                elif 'datetime_type' in error_message:
                    user_fault_type = UserFaultType.InvalidDateTimeArgumentValue
                elif '--output' in error_message:
                    user_fault_type = UserFaultType.InvalidOutputType
            elif "validation error" in error_message or 'character not allowed':
                user_fault_type = UserFaultType.ValidationError
        else:
            logger.debug('Result summary was None. Unable to classify error.')

        if user_fault_type != UserFaultType.Unknown:
            logger.debug(f"Classified error as {user_fault_type}")
        else:
            logger.debug('Unknown error type. This may impact model performance.')

        return user_fault_type

    def get_suggestions(self, command: str, user_fault_type: Union[UserFaultType, None] = None) -> List['Suggestion']:
        from azext_thoth_experimental._suggestion import Suggestion
        user_fault_type = user_fault_type or self._get_user_fault_type()
        suggestions = self.model.get(user_fault_type, {}).get(command, [])
        return [Suggestion.parse(suggestion) for suggestion in suggestions]

    @classmethod
    def load(cls, path: Path = DEFAULT_MODEL_PATH):
        assert_file_exists(path)
        model: dict = None

        with open(path) as model_file:
            model = json.load(model_file)

        return cls(model)
