# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest.mock as mock
from typing import Union

from azext_thoth_experimental.hook._cli_error_handling import (
    apply_cli_error_handling_hooks,
    last_cli_error
)
from azure.cli.core.azclierror import AzCLIErrorType
from azure.cli.core.util import handle_exception
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.patches import CliExecutionError
from knack.events import EVENT_CLI_PRE_EXECUTE


class TestCliErrorHandlingHook(ScenarioTest):

    @property
    def error_msg(self) -> Union[str, None]:
        return last_cli_error.error_msg

    @property
    def error_type(self) -> AzCLIErrorType:
        return last_cli_error.error_type

    def test_cli_pre_execute_event(self):
        func = mock.MagicMock(return_value=None)

        self.cli_ctx.register_event(
            EVENT_CLI_PRE_EXECUTE,
            func
        )

        self.cmd('az version')
        self.assertTrue(func.called)

    def test_cli_hook_captures_error_type_and_message(self):
        self.cli_ctx.register_event(
            EVENT_CLI_PRE_EXECUTE,
            apply_cli_error_handling_hooks
        )

        self.cmd('az grup list', expect_failure=True)
        self.assertRegex(self.error_msg, r'\'grup\' is misspelled or not recognized by the system')
        self.assertEqual(self.error_type, AzCLIErrorType.CommandNotFoundError)

        with self.assertRaises(SystemExit):
            self.cmd('az storage create --name samplestorage22 --location westus2 --resource-group sampleUXGroup', expect_failure=True)
        self.assertRegex(self.error_msg, r'\'create\' is misspelled or not recognized by the system')
        self.assertEqual(self.error_type, AzCLIErrorType.CommandNotFoundError)

        with self.assertRaises(SystemExit):
            self.cmd('az storage account help', expect_failure=True)
        self.assertRegex(self.error_msg, r'\'help\' is misspelled or not recognized by the system')
        self.assertEqual(self.error_type, AzCLIErrorType.CommandNotFoundError)

        with self.assertRaises(SystemExit):
            self.cmd('az vm nic show', expect_failure=True)
        self.assertRegex(self.error_msg, r'the following arguments are required: --resource-group/-g, --vm-name, --nic')
        self.assertEqual(self.error_type, AzCLIErrorType.ArgumentParseError)

        with self.assertRaises(SystemExit):
            self.cmd('az group delete', expect_failure=True)
        self.assertRegex(self.error_msg, r'the following arguments are required: --name/-n/--resource-group/-g')
        self.assertEqual(self.error_type, AzCLIErrorType.ArgumentParseError)

        from msrest.exceptions import ValidationError
        ex = ValidationError('pattern', 'resource_group_name', r'^[-\w\._\(\)]+$')
        handle_exception(ex)
        self.assertRegex(self.error_msg, r'Parameter \'resource_group_name\' must conform to the following pattern.*$')
        self.assertEqual(self.error_type, AzCLIErrorType.ValidationError)
