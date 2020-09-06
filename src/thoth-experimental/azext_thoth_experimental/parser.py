import re
from typing import List, Pattern


from azext_thoth_experimental._cli_command import CliCommand
from azext_thoth_experimental._event_handlers import CommandTableEventHandler


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
        self.parameters: List[str] = []
        self.arguments: List[str] = []

        for parameter, argument, _start_quote, _end_quote in self.ARGUMENT_PATTERN.findall(_input):
            self.parameters.append(parameter)
            self.arguments.append(argument)

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
    def cli_command(self):
        return CliCommand(self.command, self.parameters, self.arguments)
