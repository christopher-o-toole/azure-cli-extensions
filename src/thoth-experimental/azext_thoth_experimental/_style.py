# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import platform
import sys
from contextlib import contextmanager

from azext_thoth_experimental._config import GlobalConfig
from azext_thoth_experimental._logging import get_logger

logger = get_logger(__name__)


def should_enable_styling():
    try:
        if GlobalConfig.ENABLE_STYLING and sys.stdout.isatty():
            return True
    except AttributeError:
        pass
    return False


@contextmanager
def disable_colorama_and_enable_virtual_terminal_support_if_available():
    from colorama import deinit, init

    if should_enable_styling():
        deinit()

        if platform.system() == 'Windows':
            from azext_thoth_experimental._win_vt import enable_vt_mode
            logger.debug('attempting to enable virtual terminal support...')
            enable_vt_mode()
        else:
            logger.debug('not enabling virtual terminal support, platform is not windows')

        yield None

        logger.debug('renabling colorama')
        init()
    else:
        logger.debug('virtual terminal support was not enabled due to styling being disabled')
