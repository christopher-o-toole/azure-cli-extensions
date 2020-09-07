# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import errno
import os
from pathlib import Path


def _raise_file_not_found_error(path: Path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def assert_file_exists(path: Path):
    if not path.is_file():
        _raise_file_not_found_error(path)


def assert_dir_exists(path: Path):
    if not path.is_dir():
        _raise_file_not_found_error(path)
