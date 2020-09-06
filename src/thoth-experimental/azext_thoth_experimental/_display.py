# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from typing import List, Union

from colorama import Style, Fore

from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental.model import Link


def show_suggestions(suggestions: List[Suggestion], link: Union[Link, None]):
    if suggestions:
        buffer: List[str] = [f'\n{Style.BRIGHT}{Fore.WHITE}TRY{Style.RESET_ALL}']

        for suggestion in suggestions:
            buffer.append(f'{str(suggestion)}\n')

        if link:
            buffer.append(f'{Style.BRIGHT}{Fore.CYAN}{link.url}{Style.RESET_ALL}')
            buffer.append(f'{Style.DIM}{Fore.LIGHTBLACK_EX}Read more about {link.context}\n')

        print('\n'.join(buffer))
