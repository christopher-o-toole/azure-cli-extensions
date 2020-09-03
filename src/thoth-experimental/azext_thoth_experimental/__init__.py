# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_thoth_experimental._help import helps  # pylint: disable=unused-import
from azext_thoth_experimental._event_handlers import (
    ParseArgsEventHandler,
    CommandTableEventHandler
)
from azext_thoth_experimental.custom import main


class ThothExperimentalCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        thoth_experimental_custom = CliCommandType(
            operations_tmpl='azext_thoth_experimental.custom#{}')
        super().__init__(cli_ctx=cli_ctx, custom_command_type=thoth_experimental_custom)

        # excute after a command ran
        from knack.events import (
            EVENT_CLI_POST_EXECUTE,
            EVENT_INVOKER_PRE_PARSE_ARGS,
            EVENT_INVOKER_CMD_TBL_LOADED
        )
        from azure.cli.core.commands.events import (
            EVENT_INVOKER_PRE_CMD_TBL_TRUNCATE
        )
        self.cli_ctx.register_event(EVENT_CLI_POST_EXECUTE, main)
        self.cli_ctx.register_event(EVENT_INVOKER_PRE_PARSE_ARGS, ParseArgsEventHandler.on_pre_parse_args)
        self.cli_ctx.register_event(
            EVENT_INVOKER_PRE_CMD_TBL_TRUNCATE,
            lambda *args, **kwargs: CommandTableEventHandler.on_pre_truncate_command_table(
                cmd_tbl=cli_ctx.invocation.commands_loader.command_table.copy()
            )
        )
        self.cli_ctx.register_event(
            EVENT_INVOKER_CMD_TBL_LOADED,
            lambda *args, **kwargs: CommandTableEventHandler.on_load_command_table(
                cmd_tbl=cli_ctx.invocation.commands_loader.command_table.copy(),
                commands_loader=cli_ctx.invocation.commands_loader
            )
        )

    def load_command_table(self, args):
        from azext_thoth_experimental.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        from azext_thoth_experimental._params import load_arguments
        load_arguments(self, command)


COMMAND_LOADER_CLS = ThothExperimentalCommandsLoader
