from typing import Any
from weakref import WeakKeyDictionary

from colorama import Style


class Text():
    """Descriptor for generating styled text with colorama. Styling text is optional and
    can be toggled on and off with the enable_style parameter.
    """
    def __init__(self, default_text='', color=None, style=None, enable_style=True):
        super().__init__()

        if not color:
            color = getattr(self, 'TEXT_COLOR', color)
        if not style:
            style = getattr(self, 'TEXT_STYLE', style)

        self.default = default_text
        self.enable_style = enable_style
        self.color = color
        self.style = style
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance, self.default)

    def __set__(self, instance, value):
        value = self.format(value)

        if self.enable_style:
            buffer = []

            if self.color:
                buffer.append(self.color)
            if self.style:
                buffer.append(self.style)

            buffer.append(value)

            if self.color or self.style:
                buffer.append(Style.RESET_ALL)

            value = ''.join(buffer)

        self.data[instance] = value

    def format(self, value: Any) -> str:
        """Formats the text before styling is applied, behaves like the identity function by default. Override to
        apply custom formats.

        Args:
            value (Any): The object to format.

        Returns:
            str: Text in the new format.
        """
        return value
