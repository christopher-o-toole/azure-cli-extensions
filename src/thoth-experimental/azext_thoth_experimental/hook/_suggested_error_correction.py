# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum, auto
from typing import Union

from azext_thoth_experimental._util import safe_repr


class CorrectionType(Enum):
    InvalidArgument = auto()

    def __eq__(self, value: Union['CorrectionType', str]):
        if hasattr(value, 'value'):
            value = value.value
        # pylint: disable=comparison-with-callable
        return self.value == value

    def __hash__(self):
        return hash(self.value)


# pylint: disable=too-few-public-methods
class SuggestedErrorCorrection():
    VALUE_TYPE_TO_PARAMETER_NAME = {
        'resource_group_name': '--resource-group'
    }

    def __init__(self, suggestion: str, correction_type: CorrectionType, parameter: Union[str, None] = None):
        super().__init__()
        self.suggestion = suggestion
        self.parameter = self.VALUE_TYPE_TO_PARAMETER_NAME.get(parameter) or parameter
        self.correction_type = correction_type

    def __repr__(self):
        attrs = {
            'suggestion': self.suggestion,
            'correction_type': self.correction_type,
            'parameter': self.parameter
        }
        return safe_repr(self, attrs)
