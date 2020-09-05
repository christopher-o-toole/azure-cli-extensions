# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import sys
import json
import azure.cli.core.telemetry as cli_core_telemetry
from colorama import Back, Fore, Style

from azext_thoth_experimental._event_handlers import (
    CommandTableEventHandler, ParseArgsEventHandler)
from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._scenarios import scenarios
from azext_thoth_experimental.parser import (
    Argument,
    CliCommand,
    Command,
    CommandParser
)
from azext_thoth_experimental.version import VERSION

logger = get_logger(__name__)


def show_extension_version():
    print(f'Current version: {VERSION}')


def display_help():
    print(
        f'{Style.BRIGHT}Help{Style.NORMAL}: Run {Fore.LIGHTBLUE_EX}{Style.BRIGHT}az{Style.NORMAL} {Fore.BLUE}--help{Style.RESET_ALL}'
        f' or go to {Fore.CYAN}aka.ms/CLI_ref{Style.RESET_ALL}\n'
    )


def display_suggestions(scenario: dict):
    sys.stdout.write('\n')

    if suggestion := scenario.get('try'):
        print(f'{Style.BRIGHT}Try{Style.NORMAL}: {suggestion}{Style.RESET_ALL}')

    display_help()


def main(*_, **__):
    # prevent the extension from triggering twice in one command session.
    if not hasattr(main, 'debounce'):
        main.debounce = True
    else:
        return

    command_parser = CommandParser(ParseArgsEventHandler.PRE_PARSE_ARGS)
    input_command = command_parser.command
    scenario = scenarios.get(input_command)

    if scenario:
        display_suggestions(scenario)

    if 'storage create' in input_command:
        print(f'\n{Style.BRIGHT}{Fore.WHITE}TRY{Style.RESET_ALL}')
        print(str(CliCommand('storage account create', [Argument('--name', 'samplestorage2'), Argument('--location', 'westus2')])))
        print(f'{Style.BRIGHT}{Fore.LIGHTBLACK_EX}Create a storage account.{Style.RESET_ALL}')
        print(f'\n\033[4m{Style.BRIGHT}{Fore.CYAN}https://docs.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-create{Style.RESET_ALL}')
        print(f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}Read more about az storage account{Style.RESET_ALL}\n")
