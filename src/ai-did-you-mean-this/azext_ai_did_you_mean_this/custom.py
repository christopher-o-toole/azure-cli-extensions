# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
from http import HTTPStatus

import azure.cli.core.telemetry as telemetry
import requests
from requests import RequestException

from azext_ai_did_you_mean_this._cmd_table import CommandTable
from azext_ai_did_you_mean_this._command import Command
from azext_ai_did_you_mean_this._const import (
    RECOMMEND_RECOVERY_OPTIONS_LOG_FMT_STR,
    RECOMMENDATION_HEADER_FMT_STR,
    RECOMMENDATION_PROCESSING_TIME_FMT_STR,
    SERVICE_CONNECTION_TIMEOUT,
    TELEMETRY_IS_DISABLED_STR,
    TELEMETRY_IS_ENABLED_STR,
    TELEMETRY_MISSING_CORRELATION_ID_STR,
    TELEMETRY_MISSING_SUBSCRIPTION_ID_STR,
    UNABLE_TO_HELP_FMT_STR)
from azext_ai_did_you_mean_this._logging import get_logger
from azext_ai_did_you_mean_this._style import style_message
from azext_ai_did_you_mean_this._suggestion import Suggestion, SuggestionParseError, InvalidSuggestionError
from azext_ai_did_you_mean_this._suggestion_encoder import SuggestionEncoder
from azext_ai_did_you_mean_this._telemetry import (
    FaultType,
    NoRecommendationReason,
    TelemetryProperty,
    ExtensionTelemterySession,
    get_correlation_id,
    get_subscription_id,
    set_exception,
    set_properties,
    set_property
)
from azext_ai_did_you_mean_this._timer import Timer
from azext_ai_did_you_mean_this._util import safe_repr
from azext_ai_did_you_mean_this.version import VERSION
from colorama import Style, Fore, Back

logger = get_logger(__name__)


# Commands
# note: at least one command is required in order for the CLI to load the extension.
def show_extension_version():
    print(f'Current version: {VERSION}')


def normalize_and_sort_parameters(command_table, command, parameters):
    logger.debug('normalize_and_sort_parameters: command: "%s", parameters: "%s"', command, parameters)

    _command, parsed_command = Command.parse(command_table, command)
    normalized_parameters, unrecognized_parameters = Command.normalize(_command, *parameters)
    normalized_parameters = ','.join(normalized_parameters)
    unrecognized_parameters = ','.join(unrecognized_parameters)

    set_properties({
        TelemetryProperty.RawCommand: command,
        TelemetryProperty.Command: parsed_command,
        TelemetryProperty.RawParams: ','.join(parameters),
        TelemetryProperty.Params: normalized_parameters,
        TelemetryProperty.UnrecognizedParams: unrecognized_parameters
    })

    return parsed_command, normalized_parameters


def recommend_recovery_options(version, command, parameters, extension):
    result = []
    execution_time = Timer()

    with ExtensionTelemterySession():
        with execution_time:
            cmd_tbl = CommandTable.CMD_TBL
            logger.debug(RECOMMEND_RECOVERY_OPTIONS_LOG_FMT_STR,
                         version, command, parameters, extension)

            set_properties({
                TelemetryProperty.CoreVersion: version,
                TelemetryProperty.ExtensionVersion: VERSION,
            })

            # if the command is empty...
            if not command:
                # try to get the raw command field from telemetry.
                session = telemetry._session  # pylint: disable=protected-access
                # get the raw command parsed by the CommandInvoker object.
                command = session.raw_command
                if command:
                    logger.debug(f'Setting command to [{command}] from telemtry.')

            def append(line):
                result.append(line)

            def unable_to_help(command):
                msg = UNABLE_TO_HELP_FMT_STR.format(command=command)
                append(msg)

            def show_recommendation_header():
                append(f'\n{Style.BRIGHT}{Fore.WHITE}TRY{Style.RESET_ALL}')

            if extension:
                reason = NoRecommendationReason.CommandFromExtension.value
                set_properties({
                    TelemetryProperty.ResultSummary: reason,
                    TelemetryProperty.InferredExtension: extension
                })
                logger.debug('Detected extension. No action to perform.')
            if not command:
                reason = NoRecommendationReason.EmptyCommand.value
                set_property(
                    TelemetryProperty.ResultSummary, reason
                )
                logger.debug('Command is empty. No action to perform.')

            # if an extension is in-use or the command is empty...
            if extension or not command:
                return result

            # perform some rudimentary parsing to extract the parameters and command in a standard form
            command, parameters = normalize_and_sort_parameters(cmd_tbl, command, parameters)
            response = call_aladdin_service(command, parameters, version)

            # only show recommendations when we can contact the service.
            if response and response.status_code == HTTPStatus.OK:
                #recommendations = get_recommendations_from_http_response(response)

                error_message = telemetry._session.result_summary.lower()
                user_fault_type = 'Unknown'
                if 'unrecognized' in error_message:
                    user_fault_type = 'UnrecognizedArguments'
                elif 'expected one argument' in error_message or 'expected at least one argument' in error_message:
                    user_fault_type = 'ExpectedArgument'
                elif 'command group' in error_message:
                    user_fault_type = 'UnknownSubcommand'
                elif 'arguments are required' in error_message:
                    user_fault_type = 'MissingRequiredParameters'
                    if '_subcommand' in error_message:
                        user_fault_type = 'MissingRequiredSubcommand'
                    elif '_command_package' in error_message:
                        user_fault_type = 'UnableToParseCommandInput'
                elif 'not found' in error_message or 'could not be found' in error_message:
                    user_fault_type = 'AzureResourceNotFound'
                    if 'storage_account' in error_message:
                        user_fault_type = 'StorageAccountNotFound'
                    elif 'resource_group' in error_message:
                        user_fault_type = 'ResourceGroupNotFound'
                elif 'pattern' in error_message or 'is not a valid value' in error_message or 'invalid' in error_message:
                    user_fault_type = 'InvalidParameterValue'
                    if 'jmespath_type' in error_message:
                        user_fault_type = 'InvalidJMESPathQuery'
                    elif 'datetime_type' in error_message:
                        user_fault_type = 'InvalidDateTimeArgumentValue'
                    elif '--output' in error_message:
                        user_fault_type = 'InvalidOutputType'
                elif "validation error" in error_message:
                    user_fault_type = 'ValidationError'


                with open(r'C:\Users\chotool.REDMOND\Documents\Azure\azure-cli-extensions\src\ai-did-you-mean-this\azext_ai_did_you_mean_this\model.json') as model_file:
                    model = json.load(model_file)

                suggestions = model.get(user_fault_type, {}).get(command.lower().strip(), [])
                print(suggestions)
                recommendations = [Suggestion.parse(suggestion) for suggestion in suggestions]

                if recommendations:
                    show_recommendation_header()

                    for recommendation in recommendations:
                        append(f"{recommendation}")

                    with open(r'C:\Users\chotool.REDMOND\Documents\Azure\azure-cli-extensions\src\ai-did-you-mean-this\azext_ai_did_you_mean_this\toc.json') as toc_file:
                        toc = json.load(toc_file)

                    def get_doc_href_lookup_tbl(root, tbl=None):
                        tbl = tbl or {}
                        children = root.get('items') or root.get('children') or []

                        for node in children:
                            if (display_name := node.get('displayName')) and display_name.startswith('az ') and (href := node.get('href')):
                                if display_name not in tbl or '/ext/' in tbl[display_name]:
                                    tbl[display_name] = href
                            if hasattr(node, 'items') or hasattr(node, 'children'):
                                tbl.update(get_doc_href_lookup_tbl(node, tbl))

                        return tbl

                    doc_href_lookup_tbl = get_doc_href_lookup_tbl(toc)
                    if (href := doc_href_lookup_tbl.get(f'az {command}')):
                        append(f'\033[4m{Style.BRIGHT}{Fore.CYAN}https://docs.microsoft.com/en-us/cli/azure{href[2:]}{Style.RESET_ALL}')
                        append(f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}Read more about az {command}{Style.RESET_ALL}\n")

                # only prompt user to use "az find" for valid CLI commands
                # note: pylint has trouble resolving statically initialized variables, which is why
                # we need to disable the unsupported membership test rule
                elif any(cmd.startswith(command) for cmd in cmd_tbl.keys()):  # pylint: disable=unsupported-membership-test
                    set_property(TelemetryProperty.SuggestedAzFind, True)
                    unable_to_help(command)
            else:
                set_property(
                    TelemetryProperty.ResultSummary,
                    NoRecommendationReason.ServiceRequestFailure.value
                )

        logger.debug(RECOMMENDATION_PROCESSING_TIME_FMT_STR, execution_time.elapsed_ms)
        set_property(TelemetryProperty.ExecutionTimeMs, execution_time.elapsed_ms)

    return result


def get_recommendations_from_http_response(response):
    suggestions = []
    _suggestions = response.json()
    suggestion_count = len(_suggestions)

    for suggestion in _suggestions:
        try:
            suggestion = Suggestion.parse(suggestion)
            suggestions.append(suggestion)
        except SuggestionParseError as ex:
            logger.debug('Failed to parse suggestion field: %s', ex)
            set_exception(exception=ex,
                          fault_type=FaultType.SuggestionParseError.value,
                          summary='Unexpected error while parsing suggestions from HTTP response body.')
        except InvalidSuggestionError as ex:
            msg = f'Failed to parse suggestion: {safe_repr(Suggestion, suggestion)}'
            logger.debug(msg)
            set_exception(exception=ex,
                          fault_type=FaultType.InvalidSuggestionError.value,
                          summary=msg)

    valid_suggestion_count = len(suggestions)

    set_properties({
        TelemetryProperty.NumberOfValidSuggestions: valid_suggestion_count,
        TelemetryProperty.NumberOfSuggestions: suggestion_count
    })

    set_property(TelemetryProperty.Suggestions, json.dumps(suggestions, cls=SuggestionEncoder))

    return suggestions


def call_aladdin_service(command, parameters, version):
    logger.debug('call_aladdin_service: version: "%s", command: "%s", parameters: "%s"',
                 version, command, parameters)

    response = None

    time_to_get_user_info = Timer()

    with time_to_get_user_info:
        correlation_id = get_correlation_id()
        subscription_id = get_subscription_id()

    set_property(TelemetryProperty.TimeToRetrieveUserInfoMs, time_to_get_user_info.elapsed_ms)

    is_telemetry_enabled = telemetry.is_telemetry_enabled()

    telemetry_context = {
        'correlationId': correlation_id,
        'subscriptionId': subscription_id
    }

    telemetry_context = {k: v for k, v in telemetry_context.items() if v is not None and is_telemetry_enabled}

    if not is_telemetry_enabled:
        logger.debug(TELEMETRY_IS_DISABLED_STR)
    else:
        logger.debug(TELEMETRY_IS_ENABLED_STR)

        if subscription_id is None:
            set_property(TelemetryProperty.NoSubscriptionId, True)
            logger.debug(TELEMETRY_MISSING_SUBSCRIPTION_ID_STR)
        if correlation_id is None:
            set_property(TelemetryProperty.NoCorrelationId, True)
            logger.debug(TELEMETRY_MISSING_CORRELATION_ID_STR)

    context = {
        **telemetry_context,
        "versionNumber": version
    }

    query = {
        "command": command,
        "parameters": parameters
    }

    api_url = 'https://app.aladdin.microsoft.com/api/v1.0/suggestions'
    headers = {'Content-Type': 'application/json'}

    try:
        round_trip_request_time = Timer()

        with round_trip_request_time:
            response = requests.get(
                api_url,
                params={
                    'query': json.dumps(query),
                    'clientType': 'AzureCli',
                    'context': json.dumps(context),
                    'extensionVersion': VERSION
                },
                headers=headers,
                timeout=(SERVICE_CONNECTION_TIMEOUT, None))

        set_property(TelemetryProperty.RoundTripRequestTimeMs, round_trip_request_time.elapsed_ms)
    except RequestException as ex:
        if isinstance(ex, requests.Timeout):
            set_property(TelemetryProperty.RequestTimedOut, True)

        logger.debug('requests.get() exception: %s', ex)
        set_exception(exception=ex,
                      fault_type=FaultType.RequestError.value,
                      summary='HTTP Get Request to Aladdin suggestions endpoint failed.')

    return response
