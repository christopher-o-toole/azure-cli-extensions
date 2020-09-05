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
        self.cmd_tbl = CommandTableEventHandler.PRE_TRUNCATE_CMD_TBL
        self.cmd_grp_tbl = CommandTableEventHandler.CMD_GRP_TBL
        self.command_group: str = self._get_command_group(args)

        _input: str = ' '.join(args)
        command: re.Match = self.COMMAND_PATTERN.match(_input)

        self.command = command.group().strip().lower() if command else None
        self.is_valid_command = self.command in self.cmd_tbl
        self.arguments: List[Argument] = []

        for parameter, argument, _start_quote, _end_quote in self.ARGUMENT_PATTERN.findall(_input):
            self.arguments.append(Argument(parameter, argument))

    def _get_command_group(self, tokens: List[str]):
        command_group: str = ''

        for token in tokens:
            next_command_group = f'{command_group}{" " if command_group else ""}{token}'
            if next_command_group in self.cmd_grp_tbl:
                command_group = next_command_group
            else:
                break

        return command_group

    @property
    def cli_command(self) -> CliCommand:
        return CliCommand(command=self.command, arguments=self.arguments)

