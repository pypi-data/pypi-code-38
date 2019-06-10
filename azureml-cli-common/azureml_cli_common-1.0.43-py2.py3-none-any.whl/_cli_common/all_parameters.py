# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import argparse
import sys
from .commands_utility import introspect
from knack.arguments import ignore_type
from .constants import SUPPORTED_RUNTIMES


def register_command_arguments(az_command_loader, command_name, command_json_file):
    """ Takes the name of a command (ex: "ml execute start") and cycles through all
        arguments for it, registering all of them.
    """

    details = introspect(command_json_file)
    # Checking if this is an o16n command.
    if command_name not in details:
        return

    command = details[command_name].copy()

    with az_command_loader.argument_context(command_name) as argument_context:
        for argument_name in command["arguments"].keys():
            try:
                argument_dict = command["arguments"][argument_name]

                if "positional_argument" in argument_dict:
                    arguments_dict = {"options_list": [argument_name], "help": argument_dict["description"],
                                      "nargs": argparse.REMAINDER}
                    argument_context.positional(argument_name, **arguments_dict)
                else:
                    args = get_arguments(argument_dict, argument_name)
                    argument_context.argument(argument_name, **args)
            except KeyError as error:
                sys.exit('The given command is not part of command_details.json: {}, \n'
                         'error: {}'.format(argument_name, error))


def get_arguments(arguments, key):
    """ Takes the dictionary of arguments and modifies it based on args that need
        additional modification. Uses key to check if description needs to be replaced.
    """

    if "long_form" in arguments and "short_form" in arguments:
        arguments["options_list"] = get_options(arguments)
    arguments.pop('long_form', None)
    arguments.pop('short_form', None)

    if "description" in arguments:
        arguments["help"] = process_description(arguments["description"], key)
    arguments.pop('description', None)

    if "default" in arguments:
        arguments["default"] = process_default(arguments["default"])

    if "arg_type" in arguments:
        arguments["arg_type"] = process_arg_type(arguments["arg_type"])

    if "type" in arguments:
        arguments["type"] = process_type(arguments["type"])
    return arguments


def get_options(arguments):
    """ Converts long_form/short_form into the appropriate tuple for argument
        registration.
    """

    if arguments["long_form"] != '' and arguments["short_form"] != '':
        return (arguments["long_form"], arguments["short_form"])
    if arguments["long_form"] == '':
        return (arguments["short_form"], )
    return (arguments["long_form"], )


def process_default(value):
    if value == "None":
        return None
    return value


def process_arg_type(value):
    if value == "ignore_type":
        return ignore_type
    return value


def process_type(value):
    if value == "int":
        return int
    if value == "float":
        return float
    if value == "[]":
        return []
    return value


def process_description(value, key):
    if value == "argparse.SUPPRESS":
        return argparse.SUPPRESS
    if key == "target_runtime" or key == "runtime":
        return value + '{}'.format('|'.join(SUPPORTED_RUNTIMES.keys()))
    return value
