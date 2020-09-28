# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-few-public-methods

import re
import sys
from enum import Enum
from typing import Callable, Dict, Pattern, Tuple, Union

from azure.cli.core.azclierror import AzCLIError

from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._util import assert_value_is_of_correct_type
import azext_thoth_experimental.hook._custom_error_handlers as error_handlers
from azext_thoth_experimental.hook._suggested_error_correction import SuggestedErrorCorrection

logger = get_logger(__name__)


class ErrorTypeInfo():
    def __init__(self, error_type: str, pattern: str):
        super().__init__()
        assert_value_is_of_correct_type('error_type', error_type, str)
        assert_value_is_of_correct_type('pattern', pattern, str)
        self.error_type = error_type
        self.pattern = pattern

    @property
    def value(self) -> str:
        return self.error_type


class AzCliErrorHandlerType(Enum):
    ArgumentRequired = ErrorTypeInfo(
        error_type='Argument required',
        pattern=(
            r'the following arguments are required'
        )
    )
    CharacterNotAllowed = ErrorTypeInfo(
        error_type='Character not allowed',
        pattern=(
            r'[Pp]arameter\s+\'(?P<parameter>.*)\'\s+.*pattern[:\s]+\'(?P<regex>.*)\''
        )
    )
    CommandNotFound = ErrorTypeInfo(
        error_type='Command not found',
        pattern=(
            r'([\'\"])(?P<subcommand>.*)\1 is misspelled or not recognized by the system.'
        )
    )
    ResourceNotFound = ErrorTypeInfo(
        error_type='Resource not found',
        pattern=(
            r'(?P<azure_resource>[A-Za-z\s]+)\s+\'(?P<invalid_resource_name>.*)\'\s+(?:not found|could not be found)'
        )
    )
    ValueRequired = ErrorTypeInfo(
        error_type='Value Required',
        pattern=(
            r'expected (at least)?\s?one argument'
        )
    )

    def __init__(self, error_info: ErrorTypeInfo):
        super().__init__()
        self._error_type: str = error_info.error_type
        self._pattern: Pattern[str] = re.compile(error_info.pattern)

    @property
    def error_type(self) -> str:
        return self._error_type

    @property
    def pattern(self) -> Pattern[str]:
        return self._pattern

    def __eq__(self, value: Union['AzCliErrorHandler', str]):
        if hasattr(value, 'value'):
            value = value.value
        # pylint: disable=comparison-with-callable
        return self.value == value

    def __hash__(self):
        return hash(self.value)


ErrorHandlerMapType = Dict[AzCliErrorHandlerType, Callable[[re.Match], Union[str, Tuple[str, SuggestedErrorCorrection], None]]]


class AzCliErrorHandler():
    def __init__(self):
        super().__init__()
        self.error_handlers: ErrorHandlerMapType = {
            AzCliErrorHandlerType.ResourceNotFound: error_handlers.handle_resource_not_found_error,
            AzCliErrorHandlerType.CharacterNotAllowed: error_handlers.handle_character_not_allowed_error,
            AzCliErrorHandlerType.CommandNotFound: error_handlers.handle_command_not_found_error,
            AzCliErrorHandlerType.ArgumentRequired: error_handlers.handle_argument_required_error,
            AzCliErrorHandlerType.ValueRequired: error_handlers.handle_value_required_error
        }

        self.suggested_fix: Union[SuggestedErrorCorrection, None] = None
        self.error_msg: Union[str, None] = None
        self.exception: Union[Exception, None] = None

    def _get_error_metadata(self, error_handler_type: AzCliErrorHandlerType) -> Union[Exception, str]:
        is_character_not_allowed_error = error_handler_type == AzCliErrorHandlerType.CharacterNotAllowed
        return self.exception if is_character_not_allowed_error else self.error_msg

    def _get_error_msg(self, result: Union[str, Tuple[str, SuggestedErrorCorrection], None]):
        error_msg = result

        if isinstance(result, tuple):
            if len(result) == 2:
                error_msg, self.suggested_fix = result
            else:
                if len(result) > 2:
                    raise ValueError(f'too many values to unpack (expected 2, got {len(result)})')

                raise ValueError('too few values to unpack (expected 2, got 1)')

        return error_msg

    def handle_cli_error(self, cli_error: AzCLIError):
        classname = type(self).__name__
        logger.debug('%(classname)s : called on error: %(error)s', {'classname': classname, 'error': cli_error})

        match: Union[re.Match, None] = None

        self.error_msg = cli_error.error_msg
        _exc_type, exc_value, _traceback = sys.exc_info()
        self.exception = cli_error.raw_exception or exc_value
        cli_error_handler_type: Union[AzCliErrorHandlerType, None] = None
        override = True

        for cli_error_handler_type, error_handler in self.error_handlers.items():
            if match := cli_error_handler_type.pattern.search(self.error_msg):
                error_metadata = self._get_error_metadata(cli_error_handler_type)
                kwargs = {}
                if cli_error_handler_type == AzCliErrorHandlerType.CommandNotFound and hasattr(cli_error, 'command_group'):
                    kwargs.update({'command_group': getattr(cli_error, 'command_group', None)})
                if result := error_handler(match, error_metadata, **kwargs):
                    error_msg = self._get_error_msg(result)
                    break
        else:
            logger.debug('%(classname)s : the error message was not overridden.', {'classname': classname})
            override = False

        if override and cli_error_handler_type:
            if error_msg:
                cli_error.error_msg = error_msg
            cli_error.error_type = cli_error_handler_type.value

            if hasattr(cli_error, 'suggested_fix') and self.suggested_fix:
                setattr(cli_error, 'suggested_fix', self.suggested_fix)
