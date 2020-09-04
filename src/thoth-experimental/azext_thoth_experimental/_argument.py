from typing import Union

from colorama import Fore

from azext_thoth_experimental._text import Text
from azext_thoth_experimental._util import safe_repr

ArgumentType = Union[str, None]


class Argument():
    parameter = Text(color=Fore.BLUE)
    argument = Text()

    def __init__(self, parameter: str, argument: ArgumentType = None):
        super().__init__()
        self.parameter = parameter
        self.argument = argument

    def __repr__(self) -> str:
        attrs = {
            'parameter': self.parameter,
            'argument': self.argument
        }
        return safe_repr(self, attrs)

    def __str__(self) -> str:
        separator = ' ' if self.argument else ''
        return f'{self.parameter}{separator}{self.argument}'
