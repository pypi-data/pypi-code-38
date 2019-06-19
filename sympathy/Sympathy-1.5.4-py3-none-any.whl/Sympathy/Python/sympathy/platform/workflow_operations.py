# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import sys
import re
import argparse
import json
import traceback
import codecs
import logging

# from collect_files_and_change_xml import get_param_dict, set_param_dict
from sympathy.platform.workflow_converter import XMLToJson, JsonToXml
from sympathy.platform import version_support as vs
from sympathy.utils import error

core_logger = logging.getLogger('core')

# The first '=' sign is used to split the string.
# The '.' is used to split the parameter identifiers
CONFIG_STRINGS = [
    '{4c90d8e7-5eae-442e-8e59-ece2822d5781}.parameters.db_password.value=test',
    '{4c90d8e7-5eae-442e-8e59-ece2822d5781}.parameters.db_user.value = test3',
    '{509eb9ed-4d75-4cf2-bb16-7a7cfb6fb8ee}.parameters.db_databasename.value=m'
]


def error_message(x):
    error.error_message(x, 'CONFIG FILE')


def warning_message(x):
    error.warning_message(x, 'CONFIG FILE')


exit_code = 0

# The base handle this part $(*). Used by config file parser as well.
ENV_REGEX_BASE = u'\\$\\({}\\)'


def preprocess_config_items(config_items):
    # Avoid new lines and comments.
    no_newline_or_comments = [
        (line_no, line) for line_no, line in config_items
        if line and not line.startswith('#')]
    alias_dict = {}
    # An alias must be declared before it is used.
    decl_alias_regex = re.compile(u'alias +(\w+) *= *({[a-f0-9-]+})')
    using_alias_regex = re.compile(u'^(\w+).')

    prepared_items = []
    for line_no, line in no_newline_or_comments:
        match_alias_decl = decl_alias_regex.match(line)
        if match_alias_decl is not None:
            alias_name, alias_uuid = match_alias_decl.groups()
            alias_dict[alias_name] = alias_uuid
        else:
            match_alias_use = using_alias_regex.match(line)
            if match_alias_use is not None:
                alias_name, = match_alias_use.groups()
                new_line = line.replace(alias_name, alias_dict[alias_name])
                prepared_items.append((line_no, new_line))
            else:
                prepared_items.append((line_no, line))

    return prepared_items


def get_config_files(config_filenames_with_comma):
    config_filenames = config_filenames_with_comma.split(',')
    if config_filenames is None:
        return []
    existing_config_files = []
    for config_filename in config_filenames:
        if not os.path.exists(config_filename):
            print('The file {} does not exist. '
                  'This config file is not used.'.format(config_filename))
            continue

        existing_config_files.append(config_filename)
    return existing_config_files


def parse_config_arg(configfile_arg):
    if configfile_arg:
        core_logger.warn(
            'Config file argument is deprecated and will be removed '
            'in version 1.6.0 and later.')
    if configfile_arg is None:
        return [], None
    elif len(configfile_arg) == 1:
        return get_config_files(configfile_arg[0]), None
    elif len(configfile_arg) == 2:
        return get_config_files(configfile_arg[0]), configfile_arg[1]
    raise NotImplementedError('Not a valid config file state.')


def read_config_files(fq_config_filenames):
    lines = []
    for fq_config_filename in fq_config_filenames:
        with codecs.open(fq_config_filename, 'r', 'utf-8') as config_file:
            lines.extend([(line_no, line) for line_no, line in enumerate(
                config_file.read().splitlines(), 1)])
    return preprocess_config_items(lines)


def match_configurations(node_uuid, config_items, env_var_instance):
    global exit_code
    matching_configurations = []
    ENV_REGEX_STRING = ENV_REGEX_BASE.format('(\w+)')
    ENV_REGEX = re.compile(u'^{} *= *"(.*)"'.format(
        ENV_REGEX_STRING))

    for line_number, config_item in config_items:
        try:
            match_env_var = ENV_REGEX.match(config_item)
            if match_env_var is not None:
                name, value = match_env_var.groups()
                if re.match(ENV_REGEX_STRING, value) is not None:
                    warning_message(
                        u'Line {}: environment variables as values is not '
                        u'supported. "{}"'.format(line_number, config_item))

                if env_var_instance:
                    env_var_instance().set_shell_variable(name, value)
            else:
                node_uuids_and_param_keys, value = re.split(
                    ' *= *', config_item, 1)
                node_uuids, param_keys = node_uuids_and_param_keys.split(
                    '.parameters.')
                if re.match(node_uuids, node_uuid) is not None:
                    matching_configurations.append(
                        (line_number, param_keys.split('.'), value))
        except:
            exit_code = 1
            error_message(
                u'Line {} error: cannot parse line "{}"'.format(
                    line_number, config_item))

    return matching_configurations


def update_node_parameters(match, parameter_dict):
    _, param_keys, value = match
    change_param_dict = parameter_dict
    param_keys_except_last = param_keys[:-1]
    last_param_key = param_keys[-1]
    for param_key in param_keys_except_last:
        change_param_dict = change_param_dict[param_key]

    change_param_dict[last_param_key] = json.loads(value)


def update_workflow_config(fq_xml_filename, config_lines, out_filename,
                           env_var_instance=None):
    """Update the workflow's parameters from the config_lines."""
    global exit_code
    xml_flow_dict = None
    with open(fq_xml_filename, 'r') as xml_file:
        xml_flow = XMLToJson(xml_file)
    xml_flow_dict = xml_flow.dict()
    nodes = xml_flow_dict['nodes']

    for node in nodes:
        matches = match_configurations(node['uuid'], config_lines,
                                       env_var_instance)
        for match in matches:
            parameter_dict = node['parameters']['data']
            try:
                update_node_parameters(match, parameter_dict)
                node['parameters']['data'] = parameter_dict
            except ValueError as e:
                line_number, parameter_keys, value = match
                error_message('Line {0} error: {1}'.format(
                    line_number, traceback.format_exc()))
                exit_code = 1
            except KeyError as e:
                line_number, parameter_keys, value = match
                error_message(
                    'Line {} error: {} is not a valid parameter item.'.format(
                        line_number, e))
                exit_code = 1
    with open(out_filename, 'wb') as f:
        f.write(vs.encode(JsonToXml().from_dict(xml_flow_dict).xml(), 'utf-8'))


def main():
    parser = argparse.ArgumentParser(
        'Collect all files used in a flow, copy these to the directory of '
        'the flow and change paths in the xml-file to refer to the copied '
        'files.')
    parser.add_argument(
        '-i', '--infile', action='store', default=None,
        help='Path to the input workflow.')
    parser.add_argument(
        '-c', '--config_file', action='store', default=None,
        help='Path to the config file.')
    parser.add_argument(
        '-o', '--outfile', action='store', default=None,
        help=('Path to the output workflow.'))

    args = parser.parse_args()

    update_workflow_config(
        args.infile,
        read_config_files(args.config_file),
        args.outfile)


if __name__ == '__main__':
    main()
    sys.exit(exit_code)
