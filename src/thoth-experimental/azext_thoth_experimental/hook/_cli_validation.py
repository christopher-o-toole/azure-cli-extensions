# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from msrest.serialization import Serializer, ValidationError

_validate = Serializer.validate


def validate_hook(_, data, name, **kwargs):
    try:
        return _validate(data, name, **kwargs)
    except ValidationError as ex:
        setattr(ex, '_invalid_value', data)
        raise


def apply_cli_validation_hook():
    Serializer.validate = validate_hook
