# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_thoth_experimental._color import Color


class Theme():
    pass


class DarkTheme(Theme):
    ERROR = Color(241, 76, 76)
    PRIMARY_TEXT = Color(255, 255, 255)
    SECONDARY_TEXT = Color(125, 125, 125)

    TRY = PRIMARY_TEXT
    DESCRIPTION = PRIMARY_TEXT
    COMMAND = Color(86, 156, 214)
    COMMAND_HIGHLIGHT = COMMAND.brightness(1.2)
    PARAMETER = Color(1, 207, 255)
    ARGUMENT = PRIMARY_TEXT


def get_theme():
    return DarkTheme
