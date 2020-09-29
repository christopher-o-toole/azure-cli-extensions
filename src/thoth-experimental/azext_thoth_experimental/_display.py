# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, Union

from colorama import Style, Fore

from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental._theme import get_theme
from azext_thoth_experimental.model.link import Link

theme = get_theme()


def show_suggestions(suggestions: List[Suggestion], link: Union[Link, None]):
    if suggestions:
        buffer: List[str] = [f'\n{Style.BRIGHT}{theme.TRY}TRY{Style.RESET_ALL}']

        for suggestion in suggestions:
            buffer.append(f'{str(suggestion)}\n')

        if link:
            buffer.append(f'{Style.BRIGHT}{Fore.CYAN}{link.url}{Style.RESET_ALL}')
            buffer.append(f'{Style.BRIGHT}{theme.DESCRIPTION}Read more about {link.context}')

        print('\n'.join(buffer))
