from colorama import Style, Fore

""" storage_create_text = f'{Fore.LIGHTBLUE_EX}az storage {Style.BRIGHT}account{Style.NORMAL} create{Style.RESET_ALL}'
storage_account_create_text = (f'{Fore.LIGHTBLUE_EX}az storage account create '
                               f'{Fore.BLUE}--name{Style.RESET_ALL} {{0}} '
                               f'{Fore.BLUE}--resource-group{Style.RESET_ALL} {{1}} '
                               f'{Fore.BLUE}--location{Style.RESET_ALL} {{2}} '
                               f'{Fore.BLUE}--encryption-services{Style.RESET_ALL} {{3}}')
storage_account_help_text = f'{Fore.LIGHTBLUE_EX}az storage account {Fore.BLUE}--help{Style.RESET_ALL}'
storage_container_create_text = (f'{Fore.LIGHTBLUE_EX}az storage container create '
                                 f'{Fore.BLUE}--name{Style.RESET_ALL} {{0}} '
                                 f'{Fore.BLUE}--account-name{Style.RESET_ALL} {{1}} '
                                 f'{Fore.BLUE}--connection-string{Style.RESET_ALL} {{2}} '
                                 f'{Fore.BLUE}--auth-mode{Style.RESET_ALL} {{3}}')
group_create_text = f'{Fore.BLUE}--name{Style.RESET_ALL} {{0}}'
group_delete_text = f'{Fore.LIGHTBLUE_EX}az group delete {Fore.BLUE}--name{Style.RESET_ALL} {{0}}'
 """
scenarios = {
    "group create": {
        "try": f"{Fore.LIGHTBLUE_EX}az group create {Fore.BLUE}--name{Style.RESET_ALL} {{0}} {Fore.BLUE}--location{Style.RESET_ALL} {{1}}",
        "placeholders": "MyResourceGroup"
    },
    "storage create": {
        "try": f'{Fore.BLUE}az storage {Style.BRIGHT}account{Style.NORMAL} create{Style.RESET_ALL}'
    },
    "storage account create": {
        "try": "\x1b[94maz storage account create \x1b[34m--name\x1b[0m {0} \x1b[34m--resource-group\x1b[0m {1} \x1b[34m--location\x1b[0m {2} \x1b[34m--encryption-services\x1b[0m {3}",
        "placeholders": "mystorageaccount♠MyResourceGroup♠eastus2euap♠blob"
    },
    "storage account help": {
        "try": "\x1b[94maz storage account \x1b[34m--help\x1b[0m"
    },
    "storage container create": {
        "try": "'\x1b[94maz storage container create \x1b[34m--name\x1b[0m {0} \x1b[34m--account-name\x1b[0m {1} \x1b[34m--connection-string\x1b[0m {2} \x1b[34m--auth-mode\x1b[0m {3}",
        "placeholders": "MyStorageContainer♠myaccount♠{connection-string}♠login"
    },
    "group delete": {
        "try": "\x1b[94maz group delete \x1b[34m--name\x1b[0m {0}",
        "placeholders": "MyResourceGroup"
    }
}