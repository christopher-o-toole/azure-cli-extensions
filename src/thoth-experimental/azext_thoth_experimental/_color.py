import colorsys
from functools import lru_cache
from typing import Union

ColorComponentType = Union[float, int]


class ColorComponent():
    def __init__(self, name: str, default: int = 0):
        super().__init__()
        self._default = default
        self.name = name

        self.data = {}

    def __get__(self, instance: type, owner: object):
        return self.data.get(id(instance), self._default)

    def __set__(self, instance: type, value: ColorComponentType):
        if isinstance(value, float):
            if value < 0 or value > 1:
                raise ValueError(f'{self.name} must be in range [0, 1]')
            value = round(value * 255)
        elif isinstance(value, int):
            if value < 0 or value > 255:
                raise ValueError(f'{self.name} must be in range [0, 255]')
        else:
            raise TypeError(f'{self.name} must be float or int')

        self.data[id(instance)] = max(min(value, 255), 0)


class Color():
    r = ColorComponent('r')
    g = ColorComponent('g')
    b = ColorComponent('b')

    def __init__(self, r: ColorComponentType, g: ColorComponentType, b: ColorComponentType):
        super().__init__()
        self._set_color(r, g, b)

    def _set_color(self, r: ColorComponentType, g: ColorComponentType, b: ColorComponentType):
        self.r, self.g, self.b = (r, g, b)

    @lru_cache(maxsize=None)
    def brightness(self, scalar: float):
        h, l, s = colorsys.rgb_to_hls(self.r / 255, self.g / 255, self.b / 255)
        return Color(*colorsys.hls_to_rgb(h, max(0, min(1, scalar * l)), s))

    def __repr__(self):
        return f'\x1b[38;2;{self.r};{self.g};{self.b}m'

    def __str__(self):
        return repr(self)


def colored_text(text: str, color: Color) -> str:
    return f'{color}{text}\x1b[0m'
