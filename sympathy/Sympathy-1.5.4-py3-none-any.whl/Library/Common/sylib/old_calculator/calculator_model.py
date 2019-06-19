# Copyright (c) 2015, Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import __future__
import functools
import os
import re
import json
import datetime
import traceback
import threading
import inspect
from io import BytesIO

import six
import numpy as np
import pandas
import ast
import tokenize
import sys

from sympathy.api import qt
from sympathy.platform.exceptions import sywarn
from sympathy.typeutils import table
from sympathy.utils import dtypes
from sympathy.types.sydict import sydict
from sympathy.types.sygeneric import sygeneric
from sympathy.types.sylist import sylist, sylistReadThrough
from sympathy.types.syrecord import syrecord
from sympathy.types.sytuple import sytuple

from sylib.calculator import plugins
from sympathy.platform import colors

QtCore = qt.QtCore
QtGui = qt.QtGui

FUNCTION_SPLIT = '='
ENABLED_SPLIT = '#ENABLED:'

context = {'datetime': datetime,
           'np': np,
           'os': os,
           'json': json,
           'pandas': pandas,
           'six': six,
           're': re}

table_display_regex = r"\.col\('([^']*)'\).data"  # Change later
table_display_regex2 = r"\['([^']*)'\]"  # Change later
table_display_regex_old = r'\${([^{}]+)}'

table_format_regex = r"\.col\('([^']*)'\).data"
table_format_regex2 = r"\['([^']*)'\]"
adaf_format_regex = r"\.sys(\['.*'\]*)"

var_string = r"(?:\b)(?:arg|res|table)(?:\b)(?:\[\d+\])*"

fs_encoding = sys.getfilesystemencoding()


def cell_format(data):
    # TODO: Share with other previews in library.
    try:
        data = data.tolist()
    except AttributeError:
        pass

    if isinstance(data, datetime.datetime):
        data = data.isoformat()
    elif isinstance(data, six.binary_type):
        # repr will show printable ascii characters as usual but will
        # replace any non-ascii or non-printable characters with an escape
        # sequence. The slice removes the quotes added by repr.
        if six.PY2:
            data = repr(data)[1:-1]
        else:
            data = repr(data)[2:-1]
    else:
        data = six.text_type(data)
    return data


formatted_table = cell_format('{}.col(\'{}\').data')
formatted_table_new = cell_format('{}[\'{}\']')
displayed_table = cell_format(formatted_table)   # Change later to ex {}.c(
# \'{}\')
displayed_table_old = '${{{}}}'
displayed = {displayed_table_old: formatted_table,
             displayed_table: formatted_table}
formatted = {formatted_table: displayed_table,
             formatted_table_new: displayed_table_old}


def line_parser(varname, calc, all_columns):
    """Make valid python code from the calculation string by replacing e.g.
    ${a} with col_0.

    Expands wilcards into multiple calculations. We support three cases:
      0: Only ever one match for all columns
      1: One with many matches, the rest with one
      2: All with the same number of matches

    Returns
    -------
    tuple
        A tuple with three elements:
            0. A dictionary mapping old column names to the new col_0 names.
            1. A list of calculations with replaced column names.
            2. A list of outgoing column names.

    Raises
    ------
    KeyError
        if a calculation uses a column name that isn't in all_columns.
    """
    col_ctr = [0]
    column_names = {}
    outputs = []
    calcs = []

    if calc is None or not calc.strip():
        return column_names, calcs, outputs

    columns = {}
    var_names = []
    item_names = []
    order = go_deep(calc)

    for _text in order:
        var_names += re.findall(var_string, _text)
        item_names += re.findall(table_format_regex, _text)
        item_names += re.findall(table_format_regex2, _text)
        item_names += re.findall(adaf_format_regex, _text)

        for s in set(var_names):
            for i in range(0, len(item_names)):
                if ("{}['{}']".format(s, item_names[i]) in _text or
                        "{}.sys{}".format(s, item_names[i]) in _text or
                        "{}.col('{}').data".format(s, item_names[i]) in _text):
                    if s not in columns:
                        columns[s] = []
                    columns[s].append(item_names[i])

    def replacer(match_):
        if isinstance(match_, six.string_types):
            match = match_
        else:
            match = match_.groups()[0]
        if match in column_names:
            name = column_names[match]
        else:
            name = 'col_{}'.format(col_ctr[0])
            column_names[match] = name
            col_ctr[0] += 1
        return name

    filtered_columns = []

    for k in columns.keys():
        for column in columns[k]:
            filtered_column = [n for n in all_columns[k]
                               if n == column]

            # Raise KeyError if there is no match
            if not filtered_column:
                # raise KeyError(column)
                break

            filtered_columns.append((column, filtered_column))
    lengths = set([len(match) for c, match in filtered_columns])
    unique_matches = sorted((tuple(x) for c, x in filtered_columns),
                            key=lambda m: len(m), reverse=True)

    match_case = -1
    if len(lengths) == 1:
        if min(lengths) == 1:
            match_case = 0
        else:
            match_case = 2
    elif len(lengths) == 2:
        if min(lengths) == 1:
            match_case = 1
        elif min(lengths) == max(lengths):
            if len(unique_matches) == 1:
                match_case = 2

    # Construct the replaced calculations
    if match_case > 0:
        col_name, match_columns = max(
            filtered_columns, key=lambda m: len(m[1]))
        for column in set(match_columns):
            function_call = re.sub(
                var_string + table_format_regex.format(col_name),
                replacer(column), calc)
            function_call = re.sub(table_format_regex, replacer, function_call)
            calcs.append(function_call)
            outputs.append(varname.replace('*', column))
    else:
        if match_case == 0:

            function_call = re.sub(
                r"(?:res|arg|table)" + table_format_regex,
                replacer, calc)
            function_call = re.sub(r"(?:res)" + table_format_regex2,
                                       replacer, function_call)

            calcs.append(function_call)
            outputs.append(varname)
        elif match_case == -1:
            calcs.append(calc)
            outputs.append(varname)

    return column_names, calcs, outputs


def _tokenize_compat():
    return ((tokenize.generate_tokens, b'"') if six.PY2 else
            (tokenize.tokenize, '"'))


def go_deep(calc):
    i = 0
    inners = [[]]
    done = []
    tok_fun, quote = _tokenize_compat()

    g = tok_fun(BytesIO(calc.encode(fs_encoding)).readline)
    for ttype, ttext, (slineno, scol), (elineno, ecol), ltext in g:
        if ttype == 53 and '(' in ttext:
            inners.append([])
            i += 1
        elif ttype == 53 and ')' in ttext:
            done.append(tokenize.untokenize(inners[i]))
            i -= 1
        if not (ttype == tokenize.STRING and quote in ttext):
            for j in range(1, i + 1):
                inners[j].append((ttype, ttext, (slineno, scol),
                                  (elineno, ecol), ltext))
            inners[0].append((ttype, ttext, (slineno, scol), (elineno, ecol),
                              ltext))

    done.append(tokenize.untokenize(inners[0]).decode(fs_encoding))
    return done


def remove_comments(calc):
    result = []
    tok_fun, quote = _tokenize_compat()
    try:
        g = tok_fun(BytesIO(calc.encode(fs_encoding)).readline)
        for ttype, ttext, (slineno, scol), (elineno, ecol), ltext in g:
            if not (ttype == tokenize.STRING and quote in ttext):
                result.append(
                    (ttype, ttext, (slineno, scol), (elineno, ecol), ltext))
        return tokenize.untokenize(result).decode(fs_encoding)
    except tokenize.TokenError:
        return calc


def sort_calculation_queue(graph_unsorted):
    """
    Sort the calculation queue.

    Returns
    -------
    list
    """
    graph_sorted = []
    while graph_unsorted:
        acyclic = False
        for item in graph_unsorted:
            for edge in item[1]:
                if edge in dict(graph_unsorted):
                    break
            else:
                acyclic = True
                graph_unsorted.remove(item)
                graph_sorted.append(item[0])

        if not acyclic:
            raise RuntimeError('A cyclic dependency occurred')
    return graph_sorted[::-1]


def get_calculation_order(calc_list):
    original_order = [(get_varname_and_calc_and_enabled(calc_line, False))
                      for calc_line in calc_list]

    calc_list = original_order
    original_order = [l[0] for l in original_order]
    graph_unsorted = []
    for item in original_order:
        graph_unsorted.append((item, set()))
    for var, calc in calc_list:
        columns = re.findall(table_format_regex, calc)
        columns += re.findall(table_format_regex2, calc)
        columns += re.findall(table_display_regex_old, calc)
        for col in columns:
            for item in graph_unsorted:
                if col == item[0] and col != var:
                    item[1].add(var)
    try:
        graph_sorted = sort_calculation_queue(graph_unsorted)
    except RuntimeError:
        sywarn('There are cyclic dependencies in your columns!')
        return [], []

    reverse_sorting = [graph_sorted.index(node) for node in original_order]
    calc_sorting = [original_order.index(node) for node in graph_sorted]
    return calc_sorting, reverse_sorting


def parse_calc(calc_line):
    var, calc = calc_line.split(FUNCTION_SPLIT, 1)
    try:
        calc, enabled = calc.split(ENABLED_SPLIT, 1)
        enabled = 1 if enabled.strip() == '1' else 0
    except ValueError:
        # Compatibility with calculations that does not have the enabled flag
        enabled = 1
    return var.strip(), calc.strip(), enabled


def get_varname_and_calc_and_enabled(calc_line, get_enabled=True):
    varname, calc, enabled = parse_calc(calc_line)
    if get_enabled:
        return varname, calc, enabled
    return varname, calc


def get_column_names(in_data, calc):
    col_names = {}
    variables = re.findall(var_string, calc)
    for var in set(variables):
        if var != 'res':
            if var not in col_names:
                col_names[var] = []
            brackets = re.findall(r'\[([^{}])]', var)
            try:
                if brackets:
                    col_names[var] += recursive_column_names(in_data, brackets)
                else:
                    col_names[var] = in_data.column_names()
            except:
                pass
    return col_names


def recursive_column_names(in_data, brackets):
    if len(brackets) <= 1:
        return (in_data[int(brackets[0])]).column_names()
    else:
        return recursive_column_names(in_data[0], brackets[1:])


def python_calculator(in_data, calc_text, extra_globals=None, generic=False):
    varname, calc, enabled = get_varname_and_calc_and_enabled(
        format_calculation(calc_text, generic))
    calcs, outputs, variables = prepare_calculation(calc, extra_globals,
                                                    generic, in_data, varname)
    output_data = []
    for calc, col_name in zip(calcs, outputs):
        # Add col_0, col_1, etc to global variables:
        output = advanced_eval(calc, variables)
        if not isinstance(output, np.ndarray):
            if isinstance(output, list):
                output = np.array(output)
            else:
                output = np.array([output])
        output_data.append((col_name, output))
    return output_data, enabled


def prepare_calculation(calc, extra_globals, generic, in_data, varname):
    col_names = {'arg': []}
    variables = {'res': table.File()}

    col_names.update(get_column_names(in_data, calc))

    if generic:
        variables.update({'arg': in_data})
    else:
        variables.update({'table': in_data})
        if 'table' not in col_names:
            col_names['table'] = in_data.column_names()

        item_names = re.findall(table_format_regex, calc)
   #     item_names += re.findall(table_format_regex2, calc)
        for idx in range(0, len(item_names)):
            name = item_names[idx]
            if name in extra_globals.keys():
                calc = calc.replace("table.col('{}').data".format(name),
                                    "res.col('{}').data".format(name))

    if 'res' not in col_names:
        col_names['res'] = []
    col_names['res'].extend(list(extra_globals.keys()))
    old_names, calcs, outputs = line_parser(varname, calc, col_names)

    for old_name in old_names:
        if old_name in extra_globals:
            variables[old_names[old_name]] = extra_globals[old_name]
        else:
            variables[old_names[old_name]] = in_data.get_column_to_array(
                old_name)
    variables.update(extra_globals or {})
    return calcs, outputs, variables


def advanced_eval(calc, globals_dict=None):
    """
    Evaluate expression in a standardized python environment with a few
    imports:
     - datetime
     - numpy as np
     - os
     - json
     - pandas
     - re

    globals_dict argument can be used to extend the environment.
    """
    ctx = updated_context(globals_dict)
    compiler_flags = (__future__.division.compiler_flag |
                      __future__.unicode_literals.compiler_flag)
    return eval(compile(calc, "<string>", "eval", compiler_flags), ctx, {})


def updated_context(globals_dict):
    ctx = dict(context)

    if globals_dict:
        ctx.update(globals_dict)
    for plugin in plugins.available_plugins():
        ctx.update(plugin.globals_dict())
        ctx.update(plugin.imports())

    return ctx


class CalculatorCalculationItem(QtGui.QStandardItem):
    """
    A helper model item for showing the items in the calculation column.
    """

    def __init__(self, calculation, parent=None):
        super(CalculatorCalculationItem, self).__init__(calculation,
                                                        parnet=parent)
        self._valid = True
        self._is_computing = False

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, state):
        self._valid = bool(state)
        self.emitDataChanged()

    @property
    def is_computing(self):
        return self._is_computing

    @is_computing.setter
    def is_computing(self, state):
        self._is_computing = bool(state)
        self.emitDataChanged()

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundRole:
            if not self._valid:
                return colors.DANGER_BG_COLOR
            elif self.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
        elif role == QtCore.Qt.ToolTipRole:
            return self.text()
        else:
            return super(CalculatorCalculationItem, self).data(role)


class CalculatorModelItem(QtGui.QStandardItem):
    """A model item for calculated columns"""

    def __init__(self, name, calculation='', calc_item=None, parent=None,
                 generic=False):
        super(CalculatorModelItem, self).__init__(parent=parent)
        self._is_valid = True
        self._is_warned = False
        self._is_computing = False
        self._calc_is_valid = True
        self.generic = generic

        self._name = ''
        self._old_name = ''
        self._calculation = ''
        self._func = ''
        self.message = ''
        self._child_columns = set()
        self.used_columns = []
        self._attributes = {}
        self._column_data = np.array([])
        self._calc_item = calc_item
        self._dangerous_name = False

        self.name = name
        self.calculation = calculation
        self.is_computing = False
        self._enabled = None

    def text(self):
        return self._name

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.name
        elif role == QtCore.Qt.BackgroundRole:
            if not self.valid:
                return colors.DANGER_BG_COLOR
            elif self.is_computing or self._dangerous_name:
                return colors.WARNING_BG_COLOR
            else:
                return None
        elif role == QtCore.Qt.ToolTipRole:
            text = '{} {} {}'.format(
                self.name, FUNCTION_SPLIT, self.calculation)

            if len(self.used_columns):
                text += '\n\nUsed columns:\n'
                text += '\n'.join(
                    ['- {}'.format(i) for i in self.used_columns])

            if len(self._child_columns):
                text += '\n\nDependent columns:\n'
                text += '\n'.join(['- {}'.format(i.name)
                                   for i in self._child_columns])

            if self._dangerous_name:
                text += ('\n\nWarning: \n This columns name contains '
                         'whitespace at the end')
            return text
        else:
            return None

    def flags(self):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled

    def set_enabled_checkbox(self, checkbox):
        self._enabled = checkbox

    def enabled(self):
        return int(self._enabled.checkState() == QtCore.Qt.Checked)

    @property
    def valid(self):
        return self._is_valid

    @valid.setter
    def valid(self, state):
        self._is_valid = bool(state)
        self.emitDataChanged()

    @property
    def warned(self):
        return self._is_warned

    @warned.setter
    def warned(self, state):
        self._is_warned = bool(state)
        self.emitDataChanged()

    @property
    def calculation_valid(self):
        return self._calc_is_valid

    @calculation_valid.setter
    def calculation_valid(self, state):
        self._calc_is_valid = bool(state)
        self._calc_item.valid = self._calc_is_valid
        self.emitDataChanged()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._old_name = self._name
        self._name = name
        self.validate_name()

    @property
    def func(self):
        return self._func

    @property
    def calculation(self):
        return self._calculation

    @calculation.setter
    def calculation(self, func):
        if isinstance(self._calc_item, QtGui.QStandardItem):
            self._calc_item.setText(func)

        old_func = self._calculation
        calc = format_calculation(func, self.generic)
        self._calculation = calc
        self._func = func
        self.validate_calculation()

        if self._calculation != old_func and self.model() is not None:
            self.model().data_ready.emit()

    def update(self):
        self.model().recompute_item(self)
        self.model().data_ready.emit()

    @property
    def dependent_columns(self):
        return self._child_columns

    @property
    def column_data(self):
        return self._column_data

    @column_data.setter
    def column_data(self, data):
        self._column_data = data
        self.emitDataChanged()

    @property
    def is_computing(self):
        return self._is_computing

    @is_computing.setter
    def is_computing(self, state):
        self._is_computing = bool(state)
        self._calc_item.is_computing = self._is_computing
        self.emitDataChanged()

    @property
    def attributes(self):
        return self._attributes

    def set_attribute(self, name, value):
        self._attributes[name] = value
        self.emitDataChanged()

    def remove_attribute(self, name):
        self._attributes.pop(name)
        self.emitDataChanged()

    def validate(self):
        self.validate_name()
        self.validate_calculation()

    def validate_name(self):
        self._child_columns = set()
        if self.name == '':
            self.valid = False
        elif self.model() is not None:
            model = self.model()
            if self.name in model.get_other_column_names(self):
                self.valid = False
            model.reevaluate_items_after_name_change(self._old_name)
            items = model.reevaluate_items_after_name_change(self._name)
            for item in items:
                self.add_child(item)
            else:
                self.valid = True
        self._dangerous_name = re.search('\s$', self.name) is not None

    def compile(self):
        try:
            calc = self.calculation
            variables = {'arg': None, 'res': table.File()}

            if not self.generic:
                variables.update({'table': None})

            ctx = updated_context(variables)
            check_ast(calc, ctx)
        except SyntaxError as e:
            if not e.text:
                e.text = ""
            self.message = ("SyntaxError: " + e.msg + " " +
                            display_calculation(e.text, self.generic))
            self.calculation_valid = False
            return False
        except NameError as e:
            self.message = e.args[0]
            self.calculation_valid = False
            return False
        except Exception as e:
            self.message = e
            self.calculation_valid = False
            return False
        self.message = ''
        self.calculation_valid = True
        return True

    def validate_calculation(self):
        if self.model() is None:
            return
        if self.calculation == '':
            self.message = 'Empty calculation'
            self.calculation_valid = True
            return

        compiled = self.compile()
        if not compiled:
            return

        # parse calculation function
        columns = re.findall(table_format_regex, self.calculation)
        columns += re.findall(table_format_regex2, self.calculation)
        # check if used columns are a subset of available ones
        available_columns = []
        for col in self.model().available_columns:
            found = re.findall(table_display_regex, col)
            #found += re.findall(table_display_regex2, col)
            if len(found):
                available_columns.append(found[0])
            else:
                available_columns.append(col)

        is_subset = set(columns).issubset(sorted(available_columns))
        if not is_subset and compiled:
            self.message = 'Missing column names in input data!'

        # add `self` to used_column items
        self.register_at_parent_items(columns)
        # check if used columns are all valid
        for used_col in self.used_columns:
            item = self.model().get_item_by_name(used_col)
            if item is not None:
                if not item.calculation_valid:
                    self.calculation_valid = False
                    self.message = item.message
                    break
        # propagate validation to dependent columns
        for dep_item in self.dependent_columns:
            if self.calculation_valid:
                dep_item.validate_calculation()
            else:
                dep_item.calculation_valid = False
                dep_item.message = self.message

    def register_at_parent_items(self, used_columns):
        # remove `self` from previously used columns
        for old_used_col in self.used_columns:
            item = self.model().get_item_by_name(old_used_col)
            if isinstance(item, CalculatorModelItem):
                item.remove_child(self)
        self.used_columns = used_columns
        # add `self` to used columns
        all_column_names = self.model().column_names
        for used_col in self.used_columns:
            if used_col in all_column_names:
                item = self.model().get_item_by_name(used_col)
                if isinstance(item, CalculatorModelItem) and item is not self:
                    item.add_child(self)

        is_cycle, dependent_items = self.model().get_dependencies(self)
        if is_cycle:
            self.message = "There are cyclic dependencies in your columns"
            self.calculation_valid = False

    def add_child(self, child):
        self._child_columns.add(child)

    def remove_child(self, child):
        if child in self._child_columns:
            self._child_columns.remove(child)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.index() == other.index()

    def __ne__(self, other):
        return self.index() != other.index()


def format_calculation(calc, generic):
    if isinstance(calc, six.binary_type):
        calc = six.text_type(calc.decode('utf8'))
    clean_calc = remove_comments(calc)
    var_names = re.findall(var_string, clean_calc)
    item_names = re.findall(var_string + table_display_regex, clean_calc)
    #item_names += re.findall(var_string + table_display_regex2, clean_calc)
    if not generic:
        # Special handling for table.
        item_names += re.findall(table_display_regex_old, clean_calc)

        for i in range(0, len(item_names)):
            calc = calc.replace(
                displayed_table_old.format(item_names[i]),
                displayed[displayed_table_old].format('table', item_names[i]))

    # Future handling for all.
    for i in range(0, min(len(item_names), len(var_names))):
        calc = calc.replace(
            displayed_table.format(var_names[i], item_names[i]),
            displayed[displayed_table].format(var_names[i], item_names[i]))

    # Translation of variable names that uses functions.
    for form in displayed.keys():
        calc = calc.replace(form, displayed[form])
    return calc


def display_calculation(calc, generic):
    if isinstance(calc, six.binary_type):
        calc = six.text_type(calc.decode('utf8'))
    var_names = re.findall(var_string, calc)
    item_names = re.findall(var_string + table_format_regex, calc)
    item_names += re.findall(var_string + table_format_regex2, calc)

    if not generic:
        # Special handling for table.
        for i in range(0, len(item_names)):
            calc = calc.replace(
                formatted_table.format('table', cell_format(item_names[i])),
                displayed_table_old.format(cell_format(item_names[i])))
            calc = calc.replace(
                formatted_table_new.format(var_names[i], item_names[i]),
                formatted[formatted_table_new].format(item_names[i]))

    # Future handling for all.
    for i in range(0, min(len(item_names), len(var_names))):
        calc = calc.replace(
            formatted_table.format(var_names[i], item_names[i]),
            formatted[formatted_table].format(var_names[i], item_names[i]))

    # Translation of variable names that uses functions.
    for form in formatted.keys():
        calc = calc.replace(form, formatted[form])
    return calc


def check_ast(calc, ctx=None):
    if ctx is None:
        ctx = dict(context)

    xa = compile(calc, '<string>', 'eval', ast.PyCF_ONLY_AST)
    asts = list(ast.walk(xa))
    find_name_errors(xa, [], asts, ctx)

    if len(asts):
        raise Exception(
            'Something went wrong while traversing asts', len(asts))


def check_var(load, store, top_store, ctx):
    for l in load:
        if (l not in store and
                l not in [item[0] for item in inspect.getmembers(
                    six.moves.builtins)] and
                l not in ctx and
                l not in top_store):
            raise NameError('NameError: {} can\'t be found'.format(l))


def find_name_errors(_ast, store, asts, ctx):
    l = []
    s = []

    if isinstance(_ast, ast.Name):
        if isinstance(_ast.ctx, ast.Load):
            l.append(_ast.id)
        elif isinstance(_ast.ctx, ast.Store) or isinstance(
                _ast.ctx, ast.Param):
            s.append(_ast.id)
    elif hasattr(ast, 'arg') and isinstance(_ast, ast.arg):
        s.append(_ast.arg)

    children = ast.iter_child_nodes(_ast)
    for child in children:
        a, b = find_name_errors(child, s, asts, ctx)
        l += a
        s += b

    if (isinstance(_ast, ast.comprehension) or
            isinstance(_ast, ast.Expression)):
        check_var(l, s, store, ctx)

    asts.remove(_ast)
    return l, s


def flatten_input(in_data, input_column_names_and_types,
                  input_column_names, parent_name=''):

    if any(isinstance(in_data, sytype) for sytype in
           (sytuple, sylist, sylistReadThrough)):
        for i, item in enumerate(in_data):
            name = parent_name + '[{}]'.format(str(i))
            flatten_input(item, input_column_names_and_types,
                          input_column_names, name)
    elif isinstance(in_data, syrecord) or isinstance(in_data, sydict):
        # TODO: Implement.
        pass

    else:
        names = in_data.names('calc')
        types = in_data.types('calc')

        for cname, dtype in zip(names, types):
            if cname not in input_column_names:
                dtype = dtypes.typename_from_kind(dtype.kind)
                name = parent_name + cname
                input_column_names_and_types.add((name, dtype))
                input_column_names.add(name)

    return sorted(input_column_names_and_types, key=lambda s: s[0].lower())


class CalculatorItemModel(QtGui.QStandardItemModel):
    get_preview = QtCore.Signal(list)
    data_ready = QtCore.Signal()
    item_dropped = QtCore.Signal(QtCore.QModelIndex)

    """
    Calculator Model.
    """
    def __init__(self, in_tables, parameters, backend='python',
                 preview_calculator=None, parent=None, generic=False,
                 empty_input=False):
        """
        Initialize :class:CalculatorModel

        Parameters
        ----------
        in_tables : table.FileList
        parameters : dict
        backend : unicode or str
        preview_calculator : function or None
        parent : None or QtGui.QObject
        """
        super(CalculatorItemModel, self).__init__(parent=parent)
        self.generic = generic
        self._in_tables = in_tables
        self._parameter_root = parameters
        self._backend = backend
        self._preview_calculator = preview_calculator

        self.empty_input = empty_input
        self._calculation_queue = set()
        self._input_column_names_and_types = []

        if not self._in_tables:
            self._in_tables = table.FileList()

        if self._backend == 'python':
            if len(self._in_tables) > 0:
                table_file = self._in_tables[0]
            else:
                table_file = table.File()
            # create partial function
            self._worker_preview_calc = functools.partial(
                self._preview_calculator,
                table_file)
            self._preview_worker = CalculatorModelPreviewWorker(
                self._worker_preview_calc, self.generic)
            self.init_preview_worker()

        self.calc_timer = QtCore.QTimer()
        self.calc_timer.setInterval(1000)  # 1s timeout before calc runs
        self.calc_timer.setSingleShot(True)

        # connect signals
        self.calc_timer.timeout.connect(self.compute_items)

        # populate model with data from in_tables
        self.init_from_parameters()

    def init_from_parameters(self):
        input_column_names_and_types = set()
        input_column_names = set()

        if self.generic:
            parent_name = 'arg'
        else:
            parent_name = 'table'

        for in_data in self._in_tables:
            if isinstance(in_data, sygeneric):
                self.empty_input = True
                break
            self._input_column_names_and_types = flatten_input(
                in_data,
                input_column_names_and_types,
                input_column_names,
                parent_name)

        for item in self._parameter_root['calc_list'].list:
            name, calculation, enabled = parse_calc(item)
            name = trim_name(name)
            self.add_item(name, calculation, bool(enabled))

        # TODO: Fix this in a better way
        for item in self.get_items_gen():
            self.recompute_item(item)

    def init_preview_worker(self):
        self.get_preview.connect(self._preview_worker.add_preview_args)
        self._preview_worker.preview_ready.connect(self._update_item)

    def cleanup_preview_worker(self):
        try:
            self.get_preview.disconnect(self._preview_worker.add_preview_args)
        except RuntimeError:
            pass

    def flags(self, index):
        if index.isValid():
            if index.column() == 2:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            return super(CalculatorItemModel, self).flags(index)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ['text/plain']

    def dropMimeData(self, mime_data, action, row, column, parent):
        if action == QtCore.Qt.IgnoreAction:
            return True
        if not mime_data.hasFormat('text/plain'):
            return False

        if row != -1:
            begin_row = row
        elif parent.isValid():
            begin_row = parent.row()
        else:
            begin_row = self.rowCount()

        encoded_data = mime_data.data('text/plain').data()
        item_names = re.findall(table_display_regex, encoded_data)
        #item_names += re.findall(table_display_regex2, encoded_data)
        item = None
        for r, item_name in enumerate(item_names):
            if self.generic:
                item = self.insert_item(item_name, item_name, begin_row + r)
            else:
                item = self.insert_item(item_name, '${{{}}}'.format(item_name),
                                        begin_row + r)
        if item is not None:
            self.item_dropped.emit(item.index())
        return True

    @property
    def input_tables(self):
        return self._in_tables

    @property
    def first_input_table(self):
        return self._in_tables[0]

    @property
    def column_names(self):
        return [self.item(r).name for r in range(self.rowCount())]

    @property
    def available_columns(self):
        input_column_names = [i[0] for i in self._input_column_names_and_types]
        all_columns = sorted(input_column_names + self.column_names,
                             key=lambda s: s.lower())
        return all_columns

    @property
    def input_columns_and_types(self):
        return self._input_column_names_and_types

    @property
    def input_column_names(self):
        return [i[0] for i in self.input_columns_and_types]

    @property
    def backend(self):
        return self._backend

    def get_other_column_names(self, reference_item, only_valid=True):
        if only_valid:
            item_names = [item.name for item in self.get_items_gen() if
                          item is not reference_item and item.valid]
        else:
            item_names = [item.name for item in self.get_items_gen() if
                          item is not reference_item]
        return item_names

    def get_items_gen(self):
        return (self.item(row) for row in range(self.rowCount()))

    def get_item_by_name(self, name):
        items = self.findItems(name, flags=QtCore.Qt.MatchExactly, columns=0)
        if items:
            return items[0]

    def build_item(self, name='', calculation='', enabled=True):
        calculation_item = CalculatorCalculationItem(calculation, parent=self)
        name_item = CalculatorModelItem(name, calculation, calculation_item,
                                        parent=self, generic=self.generic)
        enabled_item = QtGui.QStandardItem()
        enabled_item.setCheckable(True)
        enabled_item.setToolTip(
            "Uncheck this to create a temporary variable usable in the "
            "following calculations but excluded from the output.")
        if enabled:
            enabled_item.setCheckState(QtCore.Qt.Checked)
        name_item.set_enabled_checkbox(enabled_item)
        return name_item, calculation_item, enabled_item

    def add_item(self, name=None, calculation=None, enabled=True):
        """Add a column to the model and the preview table."""
        if name is None:
            name = 'New Column {}'.format(self.rowCount())
        if calculation is None:
            calculation = ''
        item_row = self.build_item(name, calculation, enabled)
        self.appendRow(item_row)
        item_row[0].validate()
        self.reevaluate_items_after_name_change(item_row[0].name)
        if self.rowCount() < 2:
            self.setHeaderData(0, QtCore.Qt.Horizontal, 'Column name')
            self.setHeaderData(1, QtCore.Qt.Horizontal, 'Calculation')
            self.setHeaderData(2, QtCore.Qt.Horizontal, 'On')
        return item_row[0]

    def insert_item(self, name='', calculation='', row=0):
        item_row = self.build_item(name, calculation)
        self.insertRow(row, item_row)
        item_row[0].validate()
        self.reevaluate_items_after_name_change(item_row[0].name)
        return item_row[0]

    def copy_item(self, row):
        item = self.item(row, 0)
        new_item = self.insert_item(
            '{} Copy'.format(item.name),
            display_calculation(item.calculation, self.generic),
            row + 1)
        self.recompute_item(new_item)

    def remove_item(self, row):
        """Remove a column from the model."""
        item = self.item(row, 0)
        if item is None:
            # List is empty
            return
        for i in self.get_items_gen():
            i.remove_child(item)
        self.removeRow(row)
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
        self.reevaluate_items_after_name_change(item.name)

    def reevaluate_items_after_name_change(self, name):
        items_using_name = set()
        for item in self.get_items_gen():
            for col in item.used_columns:
                if name == col:
                    item.validate_calculation()
                    self.recompute_item(item)
                    items_using_name.add(item)
        return items_using_name

    def recompute_item(self, item):
        if isinstance(item, CalculatorModelItem) and item.calculation_valid:
            is_cycle, all_dependencies = self.get_dependencies(item)
            if not is_cycle:
                self.add_item_to_calculation_queue(item)
                for dep_item in all_dependencies:
                    dep_item.validate_calculation()
                    if dep_item.calculation_valid:
                        self.add_item_to_calculation_queue(dep_item)
                self.calc_timer.start()
            else:
                self.calc_timer.stop()
                self._calculation_queue = set()

    def add_item_to_calculation_queue(self, item):
        item.is_computing = True
        self._calculation_queue.add(item)

    def get_dependencies(self, item):
        """
        Find cycles in the item dependencies.

        Returns if a cycle is found (True) and all dependent items.

        Parameters
        ----------
        item : CalculatorModelItem
            The root item where to start searching.

        Returns
        -------
        bool
            True if a cycle was found.
        set
            Child items.

        """
        # build graph
        g = {i: tuple(i.dependent_columns) for i in self.get_items_gen()}

        path = set()
        visited = set()

        def visit(item):
            if item in visited:
                return False
            visited.add(item)
            path.add(item)
            for child in g.get(item, ()):
                if child in path or visit(child):
                    return True
            path.remove(item)
            return False

        return visit(item), visited

    def compute_items(self):
        input_column_names = [i[0] for i in self.input_columns_and_types
                              if i[0] not in self.column_names]
        try:
            graph_unsorted = {i: tuple(i.dependent_columns) for
                              i in self._calculation_queue}
            g = []
            for key in graph_unsorted.keys():
                g.append((key, graph_unsorted[key]))
            queue = sort_calculation_queue(g)
        except RuntimeError:
            sywarn('There are cyclic dependencies in your columns!')
            for item in self._calculation_queue:
                item.is_computing = False
                item.calculation_valid = False
                item.message = "There are cyclic dependencies in your columns"
            self._calculation_queue = set()
            return

        calculation_list = []
        for item in queue:
            # filter out input_column_names
            used_columns = [name for name in item.used_columns if name not
                            in input_column_names]
            used_items = [self.get_item_by_name(name) for name in used_columns]
            used_item_data = {i.name: i.column_data.copy() for i in
                              used_items if i is not None}
            used_item_data.pop(item.name, None)  # remove reference to itself
            calculation_list.append((item.name, item.calculation, item.row(),
                                     used_item_data))
        self._calculation_queue = set()
        self.validate()
        self.get_preview.emit(calculation_list)

    @QtCore.Slot(int, six.text_type, np.ndarray, bool)
    def _update_item(self, column_idx, column_name, data, is_warning):
        item = self.item(column_idx)
        item.is_computing = False
        # check if the data can be stored in a sytable

        try:
            dummy_output_table = table.File()
            dummy_output_table.set_column_from_array(item.name, data)
            item.column_data = data
            if is_warning:
                item.message = data[0]
            else:
                item.message = ''
        except Exception as e:
            if len(data) > 0:
                item.message = e
                is_warning = True

        item.warned = is_warning
        item.emitDataChanged()
        self.data_ready.emit()

    def check_item_messages(self):
        """Return first message of items."""
        for item in self.get_items_gen():
            if item.message:
                return item.message
        return ''

    def check_column_length(self):
        """Return True if all selected columns have the same length."""
        items = [item for item in self.get_items_gen() if item.enabled()]
        col_lens = np.array([len(i.column_data) for i in items])
        if len(col_lens):
            return np.all((col_lens - col_lens[0]) == 0)
        return True

    def check_valid_names(self):
        """Return True if all column names are valid."""
        col_names_valid = [i.valid for i in self.get_items_gen()]
        return np.all(col_names_valid)

    def check_calculation(self):
        """Return True if all column names are valid."""
        valid = True
        checked_calculations = [(i.calculation_valid, i.message)
                                for i in self.get_items_gen()]
        status = True
        for valid, msg in checked_calculations:
            if not valid and msg:
                return valid, msg
            status &= valid
        return valid, ""

    def check_warnings(self):
        """Return True if all calculations have finished."""
        calculations_warned = [i.warned
                               for i in self.get_items_gen()]
        return np.all(calculations_warned)

    def validate(self):
        item_message = self.check_item_messages()
        valid, msg = self.check_calculation()
        if valid:
            self.save_parameters()
            empty_calc = item_message == 'Empty calculation'
            if self.check_warnings():
                return True, item_message
            elif empty_calc:
                return True, item_message
            elif self.empty_input:
                return True, 'No input data available'
            elif item_message:
                return True, item_message
            return True, ''
        else:
            if not self.check_valid_names():
                return False, 'Some column names are invalid'
            elif msg != "":
                return False, msg
            elif (not self.check_column_length() and
                  self._parameter_root['same_length_res'].value):
                return (False, 'The calculated columns do not have the same '
                        'length')
            elif not self.check_calculation():
                return False, 'One or more calculations are invalid'
            return False, 'Unknown Error'

    def save_parameters(self):
        var = '{}'
        if not self.generic:
            var = '${{{}}}'
        self._parameter_root['calc_list'].list = [
            (var + ' {} {} {}{}').format(
                item.name, FUNCTION_SPLIT, item.func, ENABLED_SPLIT,
                item.enabled()) for item in self.get_items_gen()]


def trim_name(name):
    if name.startswith('res.col(') and name.endswith(')'):
        name = name[8:-1]
    if name.startswith('${') and name.endswith('}'):
        name = name[2:-1]
    return name


class CalculatorModelPreviewWorker(QtCore.QObject):
    preview_ready = QtCore.Signal(int, six.text_type, np.ndarray, bool)

    def __init__(self, calc_function, generic=False):
        super(CalculatorModelPreviewWorker, self).__init__()
        self._calc_function = calc_function
        self.generic = generic
        self._queue = six.moves.queue.Queue()
        self._thread = threading.Thread(target=self._run, args=(self._queue,))
        self._thread.daemon = True
        self._thread.start()

    def _run(self, queue):
        while True:
            args = queue.get()
            self._create_preview_table(args)

    def add_preview_args(self, args):
        try:
            # Clear queue.
            while True:
                self._queue.get_nowait()
        except six.moves.queue.Empty:
            pass

        self._queue.put(args)

    def _create_preview_table(self, *args):
        calc = ""
        outputs = {}
        calc_list = args[0]
        for name, func, col_idx, extra_columns in calc_list:
            is_warning_column = False
            result = []
            # update extra data with previously computed column data
            extra_columns.update(outputs)
            try:
                calc = '{} {} {}'.format(name, FUNCTION_SPLIT, func)
                calc = format_calculation(calc, self.generic)
                calc_res, _ = self._calc_function(calc, extra_columns,
                                                  self.generic)
                col_name = calc_res[0][0]
                result = calc_res[0][1]
                outputs[col_name] = result
            except Exception as e:
                # Show the exception in the preview
                error_lines = traceback.format_exception_only(type(e), e)
                try:
                    col_name = calc.split(FUNCTION_SPLIT)[0].strip()
                    col_name = trim_name(col_name)
                    if (col_name.startswith("${") and
                            col_name.endswith("}") and len(col_name) >= 4):
                        col_name = col_name[2:-1]
                except Exception:
                    col_name = 'Calc {}'.format(col_idx)
                if func or func != "":
                    result = np.array(error_lines[-1:])
                    is_warning_column = True
                    outputs[col_name] = result
            self.preview_ready.emit(col_idx, col_name, result,
                                    is_warning_column)
