# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" commands_utility.py, A file for simplifying how commands are registered with the cli."""

# pylint: disable=line-too-long
import json
from .ml_cli_error import MlCliError


def load_commands(az_command_loader, commands, command_json_file):
    details = introspect(command_json_file)
    with az_command_loader.command_group('ml') as group:
        for key, value in commands.items():
            command_name = ' '.join(key.split(' ')[1:])
            command_details = details[key]
            operations_tmpl = command_details['command_function'].split('#')[0] + '#{}'
            method_name = command_details['command_function'].split('#')[1]
            _add_to_group(group, command_name, method_name, operations_tmpl=operations_tmpl, **value)


def introspect(command_json_file):
    try:
        with open(command_json_file) as data_file:
            return json.load(data_file)
    except IOError as error:
        raise MlCliError('Error loading commands from json: {}'.format(error))


def _add_to_group(group, command_name, method_name, operations_tmpl, **kwargs):
    group.command(command_name, method_name, operations_tmpl=operations_tmpl, **kwargs)
