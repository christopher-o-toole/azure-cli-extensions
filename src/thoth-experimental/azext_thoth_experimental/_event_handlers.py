
class ParseArgsEventHandler():
    PRE_PARSE_ARGS = []

    @classmethod
    def on_pre_parse_args(cls, _, args):
        cls.PRE_PARSE_ARGS = args


class DefaultCommandLoader():
    def __init__(self):
        super().__init__()
        self.command_table = {}


class CommandTableEventHandler():
    COMMANDS_LOADER = DefaultCommandLoader()
    CMD_TBL = {}
    CMD_GRP_TBL = {}
    PRE_TRUNCATE_CMD_TBL = {}

    @classmethod
    def on_pre_truncate_command_table(cls, cmd_tbl):
        cls.PRE_TRUNCATE_CMD_TBL = cmd_tbl

    @classmethod
    def on_load_command_table(cls, cmd_tbl, commands_loader):
        cls.CMD_TBL = cmd_tbl
        cls.COMMANDS_LOADER.command_table = commands_loader.command_table
        cls.CMD_GRP_TBL = commands_loader.command_group_table
