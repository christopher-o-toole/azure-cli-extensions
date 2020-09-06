# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Dict, Union

from colorama import Fore, Style

from azext_thoth_experimental._cli_command import CliCommand
from azext_thoth_experimental._style import should_enable_styling
from azext_thoth_experimental._types import ArgumentsType
from azext_thoth_experimental._util import safe_repr
from azext_thoth_experimental.model import HelpTable
from azext_thoth_experimental._logging import get_logger

logger = get_logger(__name__)

UNABLE_TO_LOAD_HELP_DUMP_MSG = 'Unable to load help dump. Descriptions of suggested commands may not be available.'


class SuggestionParseError(KeyError):
    pass


class InvalidSuggestionError(ValueError):
    pass


class Suggestion(CliCommand):
    HELP_TABLE: Union[HelpTable, None] = None
    UNABLE_TO_LOAD_HELP_TABLE = False

    # pylint: disable=useless-super-delegation
    def __init__(self, command: str, description: str = '', parameters: ArgumentsType = '',
                 placeholders: ArgumentsType = ''):
        super().__init__(command, parameters, placeholders)
        self.description = description

        if should_enable_styling():
            self._apply_styles()

    def _apply_styles(self):
        self.command = f'{Style.BRIGHT}{Fore.BLUE}az {self.command}{Style.RESET_ALL}'
        self.description = f'{Style.DIM}{Fore.LIGHTBLACK_EX}{self.description}{Style.RESET_ALL}'
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
    def parse(cls, data: Dict[str, str]):
        try:
            command = data['command']
            parameters = data['parameters']
            placeholders = data['placeholders']
            description = data.get('description')

            if description is None:
                if help_table := cls.load_help_table():
                    description = help_table.get_description(command)

        except KeyError as e:
            raise SuggestionParseError(*e.args)

        try:
            return Suggestion(command, description, parameters, placeholders)
        except ValueError as e:
            raise InvalidSuggestionError(*e.args)

    @classmethod
    def load_help_table(cls):
        if not cls.UNABLE_TO_LOAD_HELP_TABLE and cls.HELP_TABLE is None:
            try:
                cls.HELP_TABLE = HelpTable.load()
            except FileNotFoundError as ex:
                logger.error(ex)
                logger.warn(UNABLE_TO_LOAD_HELP_DUMP_MSG)
                cls.UNABLE_TO_LOAD_HELP_TABLE = True

        return cls.HELP_TABLE
