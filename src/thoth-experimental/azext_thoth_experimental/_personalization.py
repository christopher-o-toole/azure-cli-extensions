import math
import re
from collections import defaultdict
from typing import DefaultDict, Dict, List, Pattern

from azext_thoth_experimental._logging import get_logger
from azext_thoth_experimental._parameter import GLOBAL_PARAM_LOOKUP_TBL
from azext_thoth_experimental._suggestion import Suggestion
from azext_thoth_experimental.model.help import HelpTable
from azext_thoth_experimental.parser import CommandParser

logger = get_logger(__name__)

ANSI_COLOR_CODE_PATTERN: Pattern[str] = re.compile(r'\x1b\[[^m]+m')


def remove_ansi_color_codes(text: str) -> str:
    return re.sub(ANSI_COLOR_CODE_PATTERN, '', text)


def mentioned_in_error_message(parameter: str) -> bool:
    from azure.cli.core.error import AzCliErrorHandler
    error_handler = AzCliErrorHandler()
    last_error = error_handler.get_last_error()
    messages = [last_error.message, last_error.overridden_message] if last_error else []
    mentioned = True

    possible_values = [parameter, re.sub('-', '_', parameter), re.sub('-', ' ', parameter)]
    mentioned = any(value in message for value in possible_values for message in messages)
    return mentioned

def reduce_param_description(desc: str):
    return re.sub(r'You can configure[^$]+$|the|new', '', desc)

def get_personalized_suggestions(suggestions: List[Suggestion], parser: CommandParser, help_table: HelpTable) -> List[Suggestion]:
    cmd_parse_tbl = parser.cmd_parse_tbl
    parameter_rank: DefaultDict[str, float] = defaultdict(
        lambda: math.inf,
        {parameter: rank for rank, parameter in enumerate(parser.normalized_parameters)}
    )

    for i, suggestion in enumerate(suggestions):
        suggested_command: str = remove_ansi_color_codes(suggestion.command)[3:]
        suggested_parameters: str = [remove_ansi_color_codes(param) for param in suggestion.parameters]
        suggested_placeholders: str = [remove_ansi_color_codes(arg) for arg in suggestion.arguments]
        is_parameter_suggested: DefaultDict[str, bool] = defaultdict(
            lambda: False,
            {p: True for p in suggested_parameters}
        )
        user_specified_parameter: DefaultDict[str, bool] = defaultdict(
            lambda: False
        )
        ranks = []
        update_suggestion: bool = False

        if help_table and (param_tbl := help_table.get_parameter_table(suggested_command)) and (fail_cmd_param_tbl := help_table.get_parameter_table(parser.command)):
            valid_parameter_set = set([*list(param_tbl.keys()), *[alias for info in param_tbl.values() for alias in info.setdefault('name', [])]])
            fail_cmd_param_tbl = {alias: info for name, info in fail_cmd_param_tbl.items() for alias in info.setdefault('name', [])}
            param_tbl = {alias: info for name, info in param_tbl.items() for alias in info.setdefault('name', [])}

            for parameter, argument in zip(parser.normalized_parameters, parser.arguments):
                user_specified_parameter[parameter] = True
                if parameter not in valid_parameter_set:
                    continue

                fail_param_summary = fail_cmd_param_tbl.get(parameter, {}).get('short-summary')
                param_summary = param_tbl.get(parameter, {}).get('short-summary')
                are_logically_equivalent = fail_param_summary == param_summary
                if fail_param_summary and param_summary and not are_logically_equivalent:
                    fail_param_summary, param_summary = reduce_param_description(fail_param_summary), reduce_param_description(param_summary)
                    from difflib import SequenceMatcher
                    comp = SequenceMatcher(None, fail_param_summary, param_summary)
                    ratio = comp.ratio()
                    are_logically_equivalent = ratio >= .9

                if not is_parameter_suggested[parameter] and not mentioned_in_error_message(parameter) and parameter not in GLOBAL_PARAM_LOOKUP_TBL and are_logically_equivalent:
                    if not any(is_parameter_suggested[alias] for alias in param_tbl.get(parameter, {}).get('name', [])):
                        suggested_parameters.append(parameter)
                        suggested_placeholders.append(argument)
                        update_suggestion = True

            # marked_for_deletion = set()
            # for elem_idx, suggested_parameter in enumerate(suggested_parameters):
            #     if not user_specified_parameter[suggested_parameter] and not mentioned_in_error_message(suggested_parameter) \
            #        and not param_tbl.get(suggested_parameter, {}).setdefault('required', False):
            #         marked_for_deletion.add(elem_idx)

            # suggested_parameters = [p for idx, p in enumerate(suggested_parameters) if idx not in marked_for_deletion]
            # suggested_placeholders = [p for idx, p in enumerate(suggested_placeholders) if idx not in marked_for_deletion]
            # update_suggestion = True
        else:
            logger.debug('No help table loaded. Personalization of suggestions based on user input could be impacted.')

        preferred = {'group': {'--resource-group': '--name'}}
        preferred_tbl = preferred.get(parser.command_group, {})

        for j, parameter in enumerate(suggested_parameters):
            is_parameter_suggested[parameter] = True

            if (entry := cmd_parse_tbl.get(parameter)) and (argument := entry.autocorrected_argument or entry.argument):
                suggested_placeholders[j] = argument
                suggested_parameters[j] = entry.parameter
                update_suggestion = True
            elif parameter in preferred_tbl:
                suggested_parameters[j] = preferred_tbl[parameter]
                update_suggestion = True
            ranks.append(parameter_rank[parameter])

        if update_suggestion:
            suggestions[i] = Suggestion.parse({
                'command': suggested_command,
                'parameters': [p for _, p in sorted(zip(ranks, suggested_parameters), key=lambda pair: pair[0])],
                'placeholders': [p for _, p in sorted(zip(ranks, suggested_placeholders), key=lambda pair: pair[0])]
            }, help_table)

    return suggestions
