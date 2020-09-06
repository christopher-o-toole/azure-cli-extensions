# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import platform
from contextlib import contextmanager

import azure.cli.core.telemetry as cli_core_telemetry

from azext_thoth_experimental._display import show_suggestions
from azext_thoth_experimental._event_handlers import ParseArgsEventHandler
from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental.parser import CommandParser
from azext_thoth_experimental.version import VERSION
from azext_thoth_experimental.model import FailureRecoveryModel

logger = get_logger(__name__)


def show_extension_version():
    print(f'Current version: {VERSION}')


@contextmanager
def disable_colorama_and_enable_virtual_terminal_support_if_available():
    from azext_thoth_experimental._style import should_enable_styling
    from colorama import deinit, init

    if should_enable_styling():
        deinit()

        if platform.system() == 'Windows':
            from azext_thoth_experimental._win_vt import enable_vt_mode
            enable_vt_mode()

        yield None

        init()


def main(*_, **__):
    # prevent the extension from triggering twice in one command session.
    if not hasattr(main, 'debounce'):
        main.debounce = True
    else:
        return

    # pylint: disable=protected-access
    status = cli_core_telemetry._session.result
    logger.debug('Called after command terminated with status %s.', status)

    if status and str(status).lower() in ('userfault', 'failure', 'none'):
        with disable_colorama_and_enable_virtual_terminal_support_if_available():
            model = FailureRecoveryModel.load()
            command_parser = CommandParser(ParseArgsEventHandler.PRE_PARSE_ARGS)

            command: str = command_parser.command
            is_valid_command: bool = command_parser.is_valid_command
            command_group: str = command_parser.command_group

            suggestions = model.get_suggestions(command=command)
            cli_docs_link = None

            if Suggestion.HELP_TABLE:
                cli_docs_link = Suggestion.HELP_TABLE.generate_link(command if is_valid_command else command_group)

            show_suggestions(suggestions, link=cli_docs_link)
