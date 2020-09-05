import re
from typing import Union

from colorama import Fore, Style

from azext_thoth_experimental._text import Text

CommandType = Union[None, str, re.Match]


class Command(Text):
    TEXT_COLOR = Fore.BLUE
    TEXT_STYLE = Style.BRIGHT

    def format(self, value: CommandType) -> str:
        if value is None:
            return ''
        if hasattr(value, 'group') and callable(value.group):
            value = value.group()

        value = value.strip()

        if not value.startswith('az'):
            value = f'az {value}'

        return value
