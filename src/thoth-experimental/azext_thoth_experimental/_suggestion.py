# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict, Union

from colorama import Fore, Style
#setattr(Fore, '')

from azext_thoth_experimental._cli_command import CliCommand
from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._style import should_enable_styling
from azext_thoth_experimental._types import ArgumentsType
from azext_thoth_experimental._util import safe_repr
from azext_thoth_experimental.model.help import HelpTable

logger = get_logger(__name__)


class SuggestionParseError(KeyError):
    pass


class InvalidSuggestionError(ValueError):
    pass


class Suggestion(CliCommand):
    # pylint: disable=useless-super-delegation
    def __init__(self, command: str, description: str = '', parameters: ArgumentsType = '',
                 placeholders: ArgumentsType = '', help_table: Union[HelpTable, None] = None):
        super().__init__(command, parameters, placeholders)
        self.description = description
        self.help_table = help_table

        if not description and self.help_table:
            self.description = help_table.get_description(command)

        if should_enable_styling():
            self._apply_styles()

    def _apply_styles(self):
        from azure.cli.core.error import AzCliErrorHandler, AzCliErrorType
        from azext_thoth_experimental._personalization import remove_ansi_color_codes
        error_handler = AzCliErrorHandler()
        last_error = error_handler.get_last_error()

        applied_command_highlighting = False

        if last_error and last_error.cli_error_type == AzCliErrorType.CommandNotFound:
            failed_command = remove_ansi_color_codes(last_error.message).replace('Command not found: az ', '').strip()
            failure_tokens = failed_command.split()
            suggested_tokens = self.command.split()
            failure_token_set = set(failure_tokens)
            suggested_token_set = set(suggested_tokens)
            if failure_token_set.issubset(suggested_token_set):
                missing_subcommands = suggested_token_set.difference(failure_token_set)
                command_buffer = [f'{Style.BRIGHT}{Fore.BLUE}az']
                for token in suggested_tokens:
                    if not applied_command_highlighting and token in missing_subcommands:
                        token = f'\x1b[38;2;136;174;255m{token}{Fore.BLUE}'
                        applied_command_highlighting = True
                    command_buffer.append(token)
                self.command = ' '.join(command_buffer) + Style.RESET_ALL
                print(repr(self.command))

        if not applied_command_highlighting:
            self.command = f'{Style.BRIGHT}{Fore.BLUE}az {self.command}{Style.RESET_ALL}'

        self.description = f'{Fore.LIGHTBLACK_EX}{self.description}{Style.RESET_ALL}' if self.description else None
        self.parameters = [f'{Fore.BLUE}{param}{Style.RESET_ALL}' for param in self.parameters]

    def __str__(self):
        buffer = [super().__str__()]

        if self.description:
            buffer.append(self.description)

        return '\n'.join(buffer)

    def __repr__(self):
        attrs = dict(command=self.command, parameters=self.parameters, arguments=self.arguments)
        return safe_repr(self, attrs)

    @classmethod
    def parse(cls, data: Dict[str, str], *args):
        try:
            command = data['command']
            parameters = data['parameters']
            placeholders = data['placeholders']
            description = data.get('description')
        except KeyError as e:
            raise SuggestionParseError(*e.args)

        try:
            return Suggestion(command, description, parameters, placeholders, *args)
        except ValueError as e:
            raise InvalidSuggestionError(*e.args)
