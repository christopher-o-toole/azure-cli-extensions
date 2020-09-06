# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys

from azext_thoth_experimental._config import GlobalConfig


def should_enable_styling():
    try:
        if GlobalConfig.ENABLE_STYLING and sys.stdout.isatty():
            return True
    except AttributeError:
        pass
    return False
