# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from typing import Dict

from azext_ai_did_you_mean_this._cli_command import CliCommand
from azext_ai_did_you_mean_this._types import ArgumentsType
from azext_ai_did_you_mean_this._util import safe_repr

from colorama import Style, Fore, Back

with open(r'C:\Users\chotool.REDMOND\Documents\Azure\azure-cli-extensions\src\ai-did-you-mean-this\azext_ai_did_you_mean_this\cli_help_table_dump-2.10.1.json', 'r') as dump_file:
    help_dump = json.load(dump_file)

class SuggestionParseError(KeyError):
    pass


class InvalidSuggestionError(ValueError):
    pass


def get_description(command: str):
    return help_dump.get(command, {'short-summary': ''})['short-summary']


class Suggestion(CliCommand):
    # pylint: disable=useless-super-delegation
    def __init__(self, command: str, parameters: ArgumentsType = '', placeholders: ArgumentsType = ''):
        super().__init__(command, parameters, placeholders)

    def __str__(self):
        return f"{super().__str__()}\n" \
               f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{get_description(self.command)}{Style.RESET_ALL}\n"

    def __repr__(self):
        attrs = dict(command=self.command, parameters=self.parameters, arguments=self.arguments)
        return safe_repr(self, attrs)

    @classmethod
    def parse(cls, data: Dict[str, str]):
        try:
            command = data['command']
            parameters = data['parameters']
            placeholders = data['placeholders']
        except KeyError as e:
            raise SuggestionParseError(*e.args)

        try:
            return Suggestion(command, parameters, placeholders)
        except ValueError as e:
            raise InvalidSuggestionError(*e.args)
