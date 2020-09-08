import re
from typing import Dict, List, Tuple, Pattern, Union

from azure.cli.core.error import AzCliErrorHandler, AzCliError, SuggestedErrorCorrection

from azext_thoth_experimental._cli_command import CliCommand
from azext_thoth_experimental._command import Command
from azext_thoth_experimental._event_handlers import CommandTableEventHandler
from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._util import safe_repr

logger = get_logger(__name__)


class CommandParseTableEntry():
    def __init__(self, parameter: str, normalized_parameter: str, argument: str):
        super().__init__()
        self.parameter = parameter
        self.normalized_parameter = normalized_parameter
        self.argument = argument
        self.autocorrected_argument = argument

        self._last_error: AzCliError = AzCliErrorHandler().get_last_error()
        self._suggested_fix: SuggestedErrorCorrection = self._get_suggested_fix()

        if self._suggested_fix and normalized_parameter == self._suggested_fix.parameter:
            if self._suggested_fix.suggestion:
                self.autocorrected_argument = self._suggested_fix.suggestion

    def _get_suggested_fix(self) -> Union[None, SuggestedErrorCorrection]:
        return self._last_error.suggested_fix if self._last_error else None

    def __repr__(self):
        attrs = {
            'parameter': self.parameter,
            'normalized_parameter': self.normalized_parameter,
            'argument': self.argument,
            'autocorrected_argument': self.autocorrected_argument
        }
        return safe_repr(self, attrs)


class CommandParseTable():
    def __init__(self, table: Dict[str, CommandParseTableEntry]):
        super().__init__()
        self.table = table

    @classmethod
    def parse(cls, parameters: List[str], normalized_parameters: List[str],
              arguments: List[str]) -> Dict[str, CommandParseTableEntry]:

        data = {}

        for parameter, normalized_parameter, argument in zip(parameters, normalized_parameters, arguments):
            data[normalized_parameter] = CommandParseTableEntry(parameter, normalized_parameter, argument)

        return data


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

        logger.debug('Parsed parameters as %s', self.parameters)
        logger.debug('Parsed arugments as %s', self.arguments)

        self.normalized_parameters: List[str] = []
        self.cmd_parse_tbl = self._get_cmd_parse_tbl()

    def _get_cmd_parse_tbl(self):
        cmd_tbl = CommandTableEventHandler.CMD_TBL
        command, _ = Command.parse(cmd_tbl, self.command)
        self.normalized_parameters = Command.normalize(command, *self.parameters)
        logger.debug('Normalized parameters to %s', self.normalized_parameters)

        cmd_parse_tbl = CommandParseTable.parse(self.parameters, self.normalized_parameters, self.arguments)

        logger.debug('Parse table generated from expression %s', cmd_parse_tbl)
        return cmd_parse_tbl

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
