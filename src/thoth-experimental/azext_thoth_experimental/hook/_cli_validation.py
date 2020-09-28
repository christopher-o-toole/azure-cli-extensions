# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from msrest.serialization import Serializer, ValidationError

_validate = Serializer.validate


def validate_hook(*args, **kwargs):
    if isinstance(args[0], Serializer):
        args = args[1:]

    try:
        return _validate(*args, **kwargs)
    except ValidationError as ex:
        setattr(ex, '_invalid_value', args[0])
        raise


def apply_cli_validation_hook():
    Serializer.validate = validate_hook
