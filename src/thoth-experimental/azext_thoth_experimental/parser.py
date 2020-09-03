import re
from typing import List, Pattern, Union

from colorama import Style, Fore, Back

from azext_thoth_experimental._event_handlers import CommandTableEventHandler
from azext_thoth_experimental._util import safe_repr

COMMAND_PATTERN: Pattern[str] = re.compile(r'^az\s+(?P<command>(?:[a-z][a-z-]+ ?)+)')


class Command():
    TEXT_COLOR = Fore.BLUE
    TEXT_STYLE = Style.BRIGHT

    def __init__(self, command: Union[None, str, re.Match]):
        super().__init__()
        self._command = None

        self.command = command

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command: Union[str, re.Match]):
        if command is None:
            return
        if hasattr(command, 'group') and callable(command.group):
            command = command.group()

        self._command = command.strip()

    def __repr__(self):
        attrs = {'command', self.command}
        return safe_repr(self, attrs)

    def __str__(self):
        return f'{self.TEXT_STYLE}{self.TEXT_COLOR}az {self.command}{Style.RESET_ALL}'


class Argument():
    PARAMETER_TEXT_COLOR = Fore.BLUE
    PARAMETER_TEXT_STYLE = None

    def __init__(self, parameter: str, argument: Union[str, None] = None):
        super().__init__()
        self.parameter = parameter
        self.argument = argument

    def __repr__(self):
        attrs = {
            'parameter': self.parameter,
            'argument': self.argument
        }
        return safe_repr(self, attrs)

    def __str__(self):
        buffer = [self.PARAMETER_TEXT_COLOR]
        if self.PARAMETER_TEXT_STYLE:
            buffer.append(self.PARAMETER_TEXT_STYLE)
        buffer.extend([self.parameter, Style.RESET_ALL])
        if self.argument:
            buffer.extend([' ', self.argument])
        return ''.join(buffer)


class CliCommand():
    def __init__(self, command: Command, arguments: Union[None, List[Argument]] = None):
        super().__init__()
        self.command = command
        self.arguments = arguments

    def __repr__(self):
        attrs = {
            'command': self.command,
            'arguments': self.arguments
        }
        return safe_repr(self, attrs)

    def __str__(self):
        arguments = [str(argument) for argument in self.arguments] if self.arguments else []
        buffer = [str(self.command), *arguments]
        return ' '.join(buffer)


class CommandParser():
    """Breaks down a CLI command into its command, parameters, and argument components.
    """
    COMMAND_PATTERN: Pattern[str] = re.compile(r'^(?P<command>(?:[a-z][a-z-]+ ?)+)')
    ARGUMENT_PATTERN: Pattern[str] = re.compile(r'''(?P<parameter>-{1,2}[a-z][A-Za-z-]*)(?:[ \t](?!-)(?P<argument>(["'])(?:(?=(\\?))\4.)*?\3|[^\s]+))?''')

    def __init__(self, args: List[str]):
        super().__init__()
        raw_input: str = ' '.join(args)
        self.command: Command = Command(self.COMMAND_PATTERN.match(raw_input))
        self.arguments: List[Argument] = []

        raw_arguments = self.ARGUMENT_PATTERN.findall(raw_input)
        for parameter, argument, _start_quote, _end_quote in raw_arguments:
            self.arguments.append(Argument(parameter.strip(), argument.strip()))
