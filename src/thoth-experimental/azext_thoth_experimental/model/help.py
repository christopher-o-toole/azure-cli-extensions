import json
import os
from pathlib import Path
from typing import Any, Dict, Union

from azext_thoth_experimental.model.file_util import assert_file_exists
from azext_thoth_experimental.model.link import Link

HelpTableType = Dict[str, Any]
TableOfContentsType = Dict[str, Any]

SCRIPT_PATH: Path = Path(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_HELP_TABLE_PATH: Path = SCRIPT_PATH / 'help_table_2.11.1.json'
DEFAULT_TOC_TABLE_PATH: Path = SCRIPT_PATH / 'toc.json'


class HelpTable():
    def __init__(self, help_table: HelpTableType, table_of_contents: TableOfContentsType):
        super().__init__()
        self.help_table = help_table
        self.table_of_contents = table_of_contents
        self.docs: Dict[str, str] = self._get_cli_doc_page_lookup_tbl(table_of_contents)

    def _get_cli_doc_page_lookup_tbl(self, root, tbl=None):
        tbl = tbl or {}
        children = root.get('items') or root.get('children') or []

        for node in children:
            if (display_name := node.get('displayName')) and display_name.startswith('az ') and (href := node.get('href')):
                if display_name not in tbl or '/ext/' in tbl[display_name]:
                    tbl[display_name] = href
            if hasattr(node, 'items') or hasattr(node, 'children'):
                tbl.update(self._get_cli_doc_page_lookup_tbl(node, tbl))

        return tbl

    def __getitem__(self, command: str):
        return self.help_table[command]

    def __contains__(self, command: str) -> bool:
        return command in self.help_table

    def get_description(self, entity: str) -> Union[str, None]:
        description: Union[str, None] = None

        if entity in self:
            return self[entity].get('short-summary')

        return description

    def generate_link(self, keyword: str) -> Union[Link, None]:
        locale = 'en-us'
        link = None

        if keyword not in self.docs:
            keyword = f'az {keyword}'
        if keyword in self.docs:
            href = self.docs[keyword]
            link = Link(url=f'https://docs.microsoft.com/{locale}/cli/azure{href[2:]}', context=keyword)

        return link

    @classmethod
    def load(cls, help_table_path: Path = DEFAULT_HELP_TABLE_PATH,
             table_of_contents_path: Union[None, Path] = DEFAULT_TOC_TABLE_PATH) -> HelpTableType:

        assert_file_exists(help_table_path)

        help_table: HelpTableType = None
        table_of_contents: TableOfContentsType = None

        with open(help_table_path) as help_table_file:
            help_table = json.load(help_table_file)

        if table_of_contents_path:
            assert_file_exists(table_of_contents_path)

            with open(table_of_contents_path) as table_of_contents_file:
                table_of_contents = json.load(table_of_contents_file)

        return cls(help_table, table_of_contents)
