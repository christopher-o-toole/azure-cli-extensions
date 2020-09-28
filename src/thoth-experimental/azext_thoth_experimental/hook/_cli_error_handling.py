# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import sys
from typing import Pattern, Union

import azure.cli.core.azclierror as azclierror
import azure.cli.core.command_recommender as command_recommender
import azure.cli.core.parser as _parser
import azure.cli.core.telemetry as _telemetry
import azure.cli.core.util as _util
import azure.cli.core.commands.arm as _arm
import azure.cli.core.commands as _commands
from azure.cli.core.command_recommender import AladdinUserFaultType
from colorama import Style
from knack.log import get_logger

from azext_thoth_experimental._personalization import remove_ansi_color_codes
from azext_thoth_experimental._style import disable_colorama_and_enable_virtual_terminal_support_if_available
from azext_thoth_experimental._theme import get_theme
from azext_thoth_experimental.hook._custom_cli_error_handling import AzCliErrorHandler, ErrorTypeInfo
from azext_thoth_experimental.hook._suggested_error_correction import SuggestedErrorCorrection

UNKNOWN_SUBCOMMAND_PATTERN: Pattern[str] = re.compile(r"'(?P<subcommand>[^']+)'.*misspelled.*$")

logger = get_logger(__name__)
theme = get_theme()

# List of all modules containing a reference to the AzCLiError object
_modules = [
    azclierror,
    _parser,
    _telemetry,
    _util,
    _arm,
    _commands
]


# pylint: disable=too-few-public-methods
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)

        return cls._instances[cls]


class AzCliErrorHook(azclierror.AzCLIError, metaclass=Singleton):
    ERROR_MSG_FMT_STR = f'{Style.BRIGHT}{theme.ERROR}{{error_type}}:{Style.NORMAL} {{msg}}{Style.RESET_ALL}'

    def __init__(self, error_type=None, error_msg=None, raw_exception=None, command=None):
        self.suggested_fix: Union[SuggestedErrorCorrection, None] = None
        self.original_error_message: str = error_msg
        self.cli_error_type = error_type
        super().__init__(error_type, error_msg, raw_exception, command)

        if error_type is not None and error_msg is not None:
            az_cli_error_handler = AzCliErrorHandler()
            az_cli_error_handler.handle_cli_error(self)

    @property
    def command_group(self) -> Union[str, None]:
        # not actually the command group in all cases, should probably either rename or adopt logic from reduce in the model.
        command_group = last_cli_error.command
        if command_group:
            command_group = command_group.strip().lower()
        return command_group

    @property
    def unknown_subcommand(self) -> Union[str, None]:
        if self.cli_error_type != azclierror.AzCLIErrorType.CommandNotFoundError:
            return None
        unknown_subcommand = None
        error_msg = last_cli_error.original_error_message
        if '\x1b' in error_msg:
            error_msg = remove_ansi_color_codes(error_msg)
        if match := re.match(UNKNOWN_SUBCOMMAND_PATTERN, error_msg):
            unknown_subcommand = match.group('subcommand').strip().lower()
        return unknown_subcommand

    def print_error(self):
        with disable_colorama_and_enable_virtual_terminal_support_if_available():
            from azure.cli.core.azlogging import CommandLoggerContext
            with CommandLoggerContext(logger):
                message = self.ERROR_MSG_FMT_STR.format(error_type=self.error_type.value, msg=self.error_msg)
                print(message, file=sys.stderr)
                # logger.error appears to strip color information from the text. could investigate further later
                # logger.error(message)
                if self.raw_exception:
                    logger.exception(self.raw_exception)


class CommandRecommenderHook(command_recommender.CommandRecommender, metaclass=Singleton):
    def __init__(self, command='', parameters='', extension='', error_msg='', cli_ctx=None):
        super().__init__(command, parameters, extension, error_msg, cli_ctx)
        self.aladdin_user_fault_type: AladdinUserFaultType = AladdinUserFaultType.Unknown
        self.classified_error_type: bool = False

    def _set_aladdin_recommendations(self):
        self._get_error_type()
        self.classified_error_type = True

    def _get_error_type(self):
        self.aladdin_user_fault_type = super()._get_error_type()
        return self.aladdin_user_fault_type


def apply_cli_error_handling_hooks(*_args, az_cli_error_cls: type = AzCliErrorHook,
                                   command_recommender_cls: type = CommandRecommenderHook, **_kwargs):
    """Overrides CLI Error Handling with custom behavior specified
    by the user

    Args:
        az_cli_error_cls (type, optional): Replaces the `azure.cli.core.azclierror.AzCliError` class. Defaults to
            AzCliErrorHook.
        command_recommender_cls (type, optional): Replaces the `azure.cli.core.command_recommender.CommandRecommender`
            class. Defaults to CommandRecommenderHook.
    """
    classes = [('az_cli_error_cls', az_cli_error_cls), ('command_recommender_cls', command_recommender_cls)]
    for cls_name, cls in classes:
        # pylint: disable=unidiomatic-typecheck
        if type(cls) is not Singleton:
            raise TypeError(f"Expected '{cls_name}' to be of type `Singleton`, got `{type(cls)}`.")

    for module in _modules:
        if hasattr(module, 'AzCLIError'):
            module.AzCLIError = az_cli_error_cls
        if hasattr(module, 'CommandRecommender'):
            module.CommandRecommender = command_recommender_cls


# the last CLI error captured by our Singleton object.
last_cli_error = AzCliErrorHook()
# the last command recommendation information captured by our Singleton object.
command_recommender_hook = CommandRecommenderHook()
