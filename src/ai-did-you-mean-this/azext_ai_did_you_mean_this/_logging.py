# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging

from knack.log import get_logger as get_knack_logger

EXTENSION_NICKNAME = 'Thoth'
LOG_PREFIX = f'[{EXTENSION_NICKNAME}]'
LOG_PREFIX_KEY = 'extension_log_prefix'


class ExtensionLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        buffer = [msg]

        if LOG_PREFIX_KEY in self.extra:
            buffer.insert(0, f'{self.extra[LOG_PREFIX_KEY]}:')

        return ' '.join(buffer), kwargs


def get_logger(module_name: str) -> logging.LoggerAdapter:
    logger = get_knack_logger(module_name)
    adapter = ExtensionLoggerAdapter(logger, {LOG_PREFIX_KEY: LOG_PREFIX})
    return adapter
