# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_thoth_experimental.arguments import Arguments
from azext_thoth_experimental._types import ArgumentsType


class CliCommand():
    parameters = Arguments('parameters', delim=',')
    arguments = Arguments('arguments', delim='♠')

    def __init__(self, command: str, parameters: ArgumentsType = '', arguments: ArgumentsType = ''):
        self.command_only = parameters == '' and arguments == ''
        self.command = command
        self.parameters = parameters
        self.arguments = arguments

        arguments_len = len(self.arguments)
        parameters_len = len(self.parameters)
        if arguments_len < parameters_len:
            missing_argument_count = parameters_len - arguments_len
            for _ in range(missing_argument_count):
                self.arguments.append('')
        elif arguments_len > parameters_len:
            raise ValueError(f'Got more arguments ({arguments_len}) than parameters ({parameters_len}).')

    def __str__(self):
        buffer = []

        if not self.command_only:
            for (param, arg) in zip(self.parameters, self.arguments):
                optional = '\a' in arg
                arg = arg.replace('\a', '') 
                from azext_thoth_experimental._personalization import remove_ansi_color_codes
                arg = arg if remove_ansi_color_codes(arg) else ''
                param = param if remove_ansi_color_codes(param) else ''
                if not buffer:
                    buffer.append('')
                if arg:
                    buffer.append(' '.join((param, arg)))
                else:
                    buffer.append(param)
                if optional and buffer[-1]:
                    buffer[-1] = f'[{buffer[-1]}]'

        return f"{self.command}{' '.join(buffer)}"

    def __eq__(self, value):
        return (self.command == value.command and
                self.parameters == value.parameters and
                self.arguments == value.arguments)

    def __hash__(self):
        return hash((self.command, self.parameters, self.arguments))
