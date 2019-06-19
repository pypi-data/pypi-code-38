# -*- coding: utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import re
import copy
import sys
import logging
from collections import OrderedDict

from sympathy.utils import error
from sympathy.platform import version_support as vs

core_logger = logging.getLogger('core')

# The base handle this part $(*). Used by config file parser as well.
ENV_REGEX_BASE = r'\$\({}\)'

# The template adds extra paranthesis to group the full expression.
ENV_REGEX_TEMPLATE = r'({})'.format(ENV_REGEX_BASE)

# The regex string base handles $(FILENAME) or $(FILENAME=example.h5).
# Special handling [^\(^\)] to avoid parentheses.
ENV_REGEX_STRING = ENV_REGEX_TEMPLATE.format(r'(((\w+)=([^\(^\)]+))|(\w+))')

ENV_REGEX = re.compile(ENV_REGEX_STRING)
_environment_instance = None


def error_message(msg):
    error.error_message(msg, 'ENVIRONMENT VARIABLE')


def warning_message(msg):
    error.warning_message(msg, 'ENVIRONMENT VARIABLE')


def node_dict_copy_with_vars_substituted(old_node_dict,
                                         workflow_vars=None):
    node_dict = copy.deepcopy(old_node_dict)
    if workflow_vars is None:
        instance().apply_variables_to_configuration(node_dict['parameters'])
    else:
        old_workflow_vars = instance().workflow_variables()
        instance().set_workflow_variables(workflow_vars)
        try:
            instance().apply_variables_to_configuration(
                node_dict['parameters'])
        finally:
            instance().set_workflow_variables(old_workflow_vars)
    return node_dict


def find_env_vars(k, d):
    val = d.get('value')
    if val is not None:
        try:
            if d['type'] == 'string' and ENV_REGEX.search(val) is not None:
                yield d
        except TypeError:
            core_logger.error(
                'Parameter: %s is of type string but its value is: %s.', k, val)

    for k in d:
        if isinstance(d[k], dict):
            for i in find_env_vars(k, d[k]):
                yield i


def get_prioritized_env_value(env_var_name, variables):
    for env_dict in variables.values():
        env_value = env_dict.get(env_var_name)
        if env_value is not None:
            return env_value
    return None


class Environment(object):
    def __init__(self):
        self._variables = OrderedDict(
            [('shell', {}), ('workflow', {}), ('global', {})])
        self._variables['shell'].update(vs.OS.environ.items())

    def apply_variables_to_configuration(self, node_dict):
        node_env_vars = find_env_vars('/', node_dict)
        for node_env_var in node_env_vars:
            env_var_names = ENV_REGEX.findall(node_env_var['value'])
            for env_var_name in env_var_names:
                self._replace_env_var(env_var_name, node_env_var)

        return node_dict

    def _replace_env_var(self, env_var_tuple, node_env_var):
        # ['$(FILENAME)', 'FILENAME', '', '', '', 'FILENAME'] or
        # ['$(FILENAME=example.h5)', 'FILENAME=example.h5',
        #  'FILENAME=example.h5', 'FILENAME', 'example.h5', '']
        # en_w_or_wo_d_full -> environment variable with or without default
        # en_w_d_full -> environment variable with default full
        (en_full, en_w_or_wo_d_full, en_w_d_full, en_w_d_name,
            en_d, en_wo_d_name) = env_var_tuple
        env_var_name = en_w_d_name if en_w_d_name else en_wo_d_name
        if sys.platform == 'win32':
            env_value = self.shell_variable(env_var_name.upper(), None)
            if env_value is None:
                env_value = get_prioritized_env_value(
                    env_var_name, self._variables)
        else:
            env_value = get_prioritized_env_value(
                env_var_name, self._variables)

        if env_value is not None:
            # Replace $(FILENAME=example.h5) or $(FILENAME)
            node_env_var['value'] = node_env_var['value'].replace(
                en_full, env_value)

        elif en_d:
            # Use default value $(FILENAME=example.h5) when no
            # FILENAME exist in the environment.
            node_env_var['value'] = node_env_var['value'].replace(
                en_full, en_d)
        else:
            warning_message(
                'Cannot find variable {} in the environment.'.format(
                    env_var_name))

    def variables(self):
        return self._variables

    def prioritized_variables(self, exclude=None):
        prio_dict = {}
        for name, scope_value in reversed(self._variables.items()):
            if exclude is None or name not in exclude:
                prio_dict.update(scope_value)
        return prio_dict

    def variable(self, name, scope):
        return self._variables[scope].get(name)

    def shell_variable(self, name, scope):
        return self.variable(name, 'shell')

    def shell_variables(self):
        return self._variables['shell']

    def global_variable(self, name, scope):
        return self.variable(name, 'global')

    def global_variables(self):
        return self._variables['global']

    def workflow_variables(self):
        return self._variables['workflow']

    def set_variable(self, name, value, scope):
        self._variables[scope][name] = value

    def set_shell_variable(self, name, value):
        # If shell variable already exist, don't add because it's from
        # env and has precedence.
        if name not in vs.OS.environ:
            self.set_variable(name, value, 'shell')

    def set_global_variable(self, name, value):
        self.set_variable(name, value, 'global')

    def set_shell_variables(self, variable_dict):
        self._variables['shell'] = variable_dict

    def set_global_variables(self, variable_dict):
        self._variables['global'] = variable_dict

    def set_workflow_variables(self, variable_dict):
        self._variables['workflow'] = variable_dict


def instance():
    global _environment_instance
    if _environment_instance is None:
        _environment_instance = Environment()
    return _environment_instance
