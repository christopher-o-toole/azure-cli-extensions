# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging

from knack.log import get_logger as get_knack_logger


class ExtensionLoggerAdapter(logging.LoggerAdapter):
    EXTENSION_LOG_PREFIX_ATTR = 'extension_log_prefix'

    def process(self, msg, kwargs):
        buffer = [msg]

        if self.EXTENSION_LOG_PREFIX_ATTR in self.extra:
            buffer.insert(0, self.extra[self.EXTENSION_LOG_PREFIX_ATTR])

        return ' '.join(buffer), kwargs


def get_logger(module_name: str) -> logging.LoggerAdapter:
    logger = get_knack_logger(module_name)
    adapter = ExtensionLoggerAdapter(logger, {ExtensionLoggerAdapter.EXTENSION_LOG_PREFIX_ATTR: '[thoth-experimental]:'})
    return adapter
