import re
from typing import List, Pattern, Union

from colorama import Fore, Style

from azext_thoth_experimental._argument import Argument, ArgumentType
from azext_thoth_experimental._command import Command, CommandType
from azext_thoth_experimental._event_handlers import CommandTableEventHandler
from azext_thoth_experimental._util import safe_repr


class CliCommand():
    command = Command()

    def __init__(self, command: str, arguments: Union[None, List[Argument]] = None):
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
        arguments = [str(arg) for arg in self.arguments] or []
        buffer = [self.command, *arguments]
        return ' '.join(buffer)


class CommandParser():
    """Breaks down a CLI command into its command, parameters, and argument components.
    """
    COMMAND_PATTERN: Pattern[str] = re.compile(r'^(?P<command>(?:[a-z][a-z-]+ ?)+)')
    ARGUMENT_PATTERN: Pattern[str] = re.compile(r'''(?P<parameter>-{1,2}[a-z][A-Za-z-]*)(?:[ \t](?!-)(?P<argument>(["'])(?:(?=(\\?))\4.)*?\3|[^\s]+))?''')

    def __init__(self, args: List[str]):
        super().__init__()

        raw_input: str = ' '.join(args)
        command = self.COMMAND_PATTERN.match(raw_input)

        self.command = command.group() if command else None
        self.arguments: List[Argument] = []

        for parameter, argument, _start_quote, _end_quote in self.ARGUMENT_PATTERN.findall(raw_input):
            self.arguments.append(Argument(parameter, argument))

    @property
    def cli_command(self) -> CliCommand:
        return CliCommand(command=self.command, arguments=self.arguments)
