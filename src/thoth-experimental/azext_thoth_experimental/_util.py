# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pprint
from enum import Enum
from typing import Any, Dict, Tuple, Union


def safe_repr(obj: Union[type, object], attrs: Dict[str, Any]):
    classname = type(obj).__name__
    buffer = []

    if hasattr(obj, '__name__'):
        classname = obj.__name__

    for name, value in attrs.items():
        is_enum_value = isinstance(value, Enum)
        buffer.append(f'{name}={str(value) if is_enum_value else pprint.pformat(value)}')

    return '{classname}({args})'.format(
        classname=classname,
        args=', '.join(buffer)
    )


def assert_value_is_of_correct_type(name: str, obj: Any, class_or_tuple: Union[type, Tuple[type]]):
    if not isinstance(obj, class_or_tuple):
        of_type_msg = f'of type {class_or_tuple.__name__}' if isinstance(class_or_tuple, type) else \
                      f'{" or ".join([_type.__name__ for _type in class_or_tuple])}'
        raise TypeError(f'expected {name} to be {of_type_msg}, got {type(obj).__name__}')
