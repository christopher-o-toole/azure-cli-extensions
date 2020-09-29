# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import Union

import azure.cli.core.telemetry as cli_core_telemetry

from azext_thoth_experimental._display import show_suggestions
from azext_thoth_experimental._event_handlers import ParseArgsEventHandler
from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._personalization import get_personalized_suggestions
from azext_thoth_experimental._style import disable_colorama_and_enable_virtual_terminal_support_if_available
from azext_thoth_experimental.hook._cli_error_handling import last_cli_error
from azext_thoth_experimental.parser import CommandParser
from azext_thoth_experimental.version import VERSION
from azext_thoth_experimental.model.failure_recovery import FailureRecoveryModel
from azext_thoth_experimental.model.help import HelpTable

UNABLE_TO_LOAD_HELP_DUMP_MSG = (
    'Unable to load help dump. Links to CLI documentation and command descriptions may not be available.'
)

logger = get_logger(__name__)


def show_extension_version():
    print(f'Current version: {VERSION}')


def main(*_, **__):
    # prevent the extension from triggering twice in one command session.
    if not hasattr(main, 'debounce'):
        main.debounce = True
    else:
        return

    # pylint: disable=protected-access
    status = cli_core_telemetry._session.result
    logger.debug('Called after command terminated with status %s.', status)

    if status and (str(status).lower() in ('userfault', 'failure') or last_cli_error.error_type):
        with disable_colorama_and_enable_virtual_terminal_support_if_available():
            help_table: Union[HelpTable, None] = None

            try:
                help_table = HelpTable.load()
            except FileNotFoundError as ex:
                logger.debug(ex)
                logger.debug(UNABLE_TO_LOAD_HELP_DUMP_MSG)

            model = FailureRecoveryModel.load()
            command_parser = CommandParser(ParseArgsEventHandler.PRE_PARSE_ARGS)

            command: str = command_parser.command
            is_valid_command: bool = command_parser.is_valid_command
            command_group: str = command_parser.command_group

            suggestions = model.get_suggestions(parser=command_parser, help_table=help_table)
            suggestions = get_personalized_suggestions(suggestions, parser=command_parser, help_table=help_table)

            cli_docs_link = None

            if help_table:
                cli_docs_link = help_table.generate_link(command if is_valid_command else command_group)

            show_suggestions(suggestions, link=cli_docs_link)
