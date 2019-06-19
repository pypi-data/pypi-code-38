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
import contextlib
import os
import re
import json
import datetime
import traceback
import threading
import inspect
import itertools

import six
import numpy as np
import pandas
import ast
import sys
import networkx as nx
import collections

from sympathy.api import qt
from sympathy.platform import exceptions
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

res_col_regex = re.compile(r"res\.col\('([^']*)'\).data")
res_get_regex = re.compile(r"res\['([^']*)'\]")

fs_encoding = sys.getfilesystemencoding()


class ResCol(object):
    def __init__(self, table, name):
        self._table = table
        self._name = name

    @property
    def data(self):
        return self._table[self._name]


class ResTable(object):
    def __init__(self):
        self._cols = {}

    def __getitem__(self, col):
        return self._cols[col]

    def __setitem__(self, col, value):
        self._cols[col] = value

    def __delitem__(self, col):
        del self._cols[col]

    def __contains__(self, col):
        return col in self._cols

    def col(self, name):
        return ResCol(self, name)

    def __iter__(self):
        return iter(self._cols)


@six.python_2_unicode_compatible
class Calc(object):

    def __init__(self, name, expr=None, enabled=False, type='calc'):
        self._name = name
        self._expr = expr
        self._enabled = enabled
        self._type = type
        self._valid = None
        self._deps = None
        self._ex = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def expr(self):
        return self._expr

    @expr.setter
    def expr(self, value):
        self._expr = value
        self._valid = None
        self._deps = None

    @property
    def empty_expr(self):
        sexpr = self._expr.lstrip()
        return not sexpr or sexpr.startswith('#')

    @property
    def enabled(self):
        return int(self._enabled)

    @enabled.setter
    def enabled(self, value):
        self._enabled = int(value)

    @property
    def type(self):
        return self._type

    @property
    def deps(self):
        if self._deps is None:
            cols = []
            cols.extend(res_col_regex.findall(self._expr))
            cols.extend(res_get_regex.findall(self._expr))
            self._deps = list(collections.OrderedDict.fromkeys(cols).keys())
        return self._deps

    @property
    def valid(self):
        # TODO(erik): consider setting in valid if expression forms self cycle.
        # Currently, cycle handling is all external.
        # Consider fine grained, printable exceptions.
        def check_ast(calc, ctx=None):

            def check_var(load, store, top_store, ctx):
                for l in load:
                    if (l not in store and
                            l not in [item[0] for item in inspect.getmembers(
                                six.moves.builtins)] and
                            l not in ctx and
                            l not in top_store):
                        raise NameError(
                            'NameError: {} can\'t be found'.format(l))

            def find_name_errors(_ast, store, asts, ctx):
                ls = []
                ss = []

                if isinstance(_ast, ast.Name):
                    if isinstance(_ast.ctx, ast.Load):
                        ls.append(_ast.id)
                    elif isinstance(_ast.ctx, ast.Store) or isinstance(
                            _ast.ctx, ast.Param):
                        ss.append(_ast.id)
                elif hasattr(ast, 'arg') and isinstance(_ast, ast.arg):
                    ss.append(_ast.arg)

                children = ast.iter_child_nodes(_ast)
                for child in children:
                    a, b = find_name_errors(child, ss, asts, ctx)
                    ls += a
                    ss += b

                if (isinstance(_ast, ast.comprehension) or
                        isinstance(_ast, ast.Expression)):
                    check_var(ls, ss, store, ctx)

                asts.remove(_ast)
                return ls, ss

            if ctx is None:
                ctx = dict(context)

            xa = compile(calc, '<string>', 'eval', ast.PyCF_ONLY_AST)
            asts = list(ast.walk(xa))
            find_name_errors(xa, [], asts, ctx)

            if len(asts):
                raise Exception(
                    'Something went wrong while traversing asts', len(asts))

        if self._valid is None:
            exc = None
            variables = {'arg': None, 'res': table.File()}
            try:
                ctx = updated_context(variables)
                check_ast(self.expr, ctx)
            except Exception as e:
                exc = e
            except SyntaxError as e:
                exc = e

            self._exc = exc
            self._valid = exc is None

        return self._valid

    @property
    def exc(self):
        """
        Return raw exception.
        """
        # Force ast check.
        self.valid
        return self._exc

    @property
    def exception(self):
        """
        Return (human?) readable exception string.
        """
        exc = self.exc
        res = ''
        if isinstance(exc, NameError):
            res = 'Analyzing {}: {}'.format(self.name, exc)
        elif isinstance(exc, SyntaxError):
            res = 'Analyzing {}: SyntaxError'.format(self.name)
        elif isinstance(exc, Exception):
            res = 'Analyzing {}: {}'.format(self.name, exc)
        return res

    def __str__(self):
        return "res['{}'] = {}".format(self._name, self._expr)

    @classmethod
    def from_calc(cls, calc):
        """
        Return a copy.
        """
        res = cls(name=calc._name, expr=calc._expr, enabled=calc._enabled,
                  type=calc._type)
        res._valid = calc._valid
        res._deps = calc._deps
        res._ex = calc._ex
        return res


def parse_nodes(calc_lines):
    return [Calc(*parse_calc(calc)) for calc in calc_lines]


class CalculationGraph(object):
    def __init__(self, calc_objs):
        self._graph = nx.DiGraph()
        self._calc_map = {}

        for calc_obj in calc_objs:
            self._graph.add_node(calc_obj)
            self._calc_map[calc_obj.name] = calc_obj

        for calc_obj in calc_objs:
            self._add_calc_edges(calc_obj)

    def _add_node(self, calc_obj):
        self._graph.add_node(calc_obj)
        self._calc_map[calc_obj.name] = calc_obj

    def _remove_node(self, calc_obj):
        self._graph.remove_node(calc_obj)
        del self._calc_map[calc_obj.name]

    def add_calc(self, calc_obj):
        curr = self._calc_map.get(calc_obj.name)
        if curr is not None:
            # In case there are already dependencies on nodes not
            # existing there will be placeholder elements of missing
            # type.
            assert curr.type == 'miss', (
                'Should not be possible to create calculation with same name.')
            self._replace_node(curr, calc_obj)
        else:
            self._add_node(calc_obj)
            self._add_calc_edges(calc_obj)

    def _add_calc_edges(self, calc_obj):
        for col in calc_obj.deps:
            dep_obj = self._calc_map.get(col)
            if dep_obj is None:
                dep_obj = Calc(col, '[]', enabled=False, type='miss')
                self._add_node(dep_obj)
            self._graph.add_edge(calc_obj, dep_obj)

    def _replace_node(self, old_calc, new_calc):
        predecessors = list(self._graph.predecessors(old_calc))
        successors = list(self._graph.successors(old_calc))
        self._remove_node(old_calc)
        self._add_node(new_calc)

        for node in predecessors:
            self._graph.add_edge(node, new_calc)

        for node in successors:
            self._graph.add_edge(new_calc, node)

        self._add_calc_edges(new_calc)

        self._remove_unused_missing()

    def remove_calc(self, calc_obj):
        predecessors = [node for node in self._graph.predecessors(calc_obj)
                        if node is not calc_obj]
        self._remove_node(calc_obj)

        if predecessors:
            dep_obj = Calc(calc_obj.name, '[]', enabled=False, type='miss')
            self._add_node(dep_obj)
            for node in predecessors:
                self._graph.add_edge(node, dep_obj)

        self._remove_unused_missing()

    def rename_calc(self, calc_obj, new_name, add_if_missing=True):
        if not add_if_missing and calc_obj not in self:
            calc_obj.name = new_name
        else:
            self.remove_calc(calc_obj)
            calc_obj.name = new_name
            self.add_calc(calc_obj)

    def change_calc_expr(self, calc_obj, new_expr):
        self.remove_calc(calc_obj)
        calc_obj.expr = new_expr
        self.add_calc(calc_obj)

    def _remove_unused_missing(self):
        for node in list(self._graph.nodes()):
            if node.type == 'miss' and len(
                    list(self._graph.predecessors(node))) == 0:
                self._graph.remove_node(node)
                del self._calc_map[node.name]

    def _calc_cycles(self):
        """
        May return duplicates when there are self cycles.
        """
        return itertools.chain([set(self.nodes_in_self_cycles())],
                               self.nodes_in_cycles())

    def nodes_in_calc_cycles(self):
        return set([node for comp in self._calc_cycles() for node in comp])

    def nodes_in_cycles(self):
        return (comp for comp in nx.strongly_connected_components(self._graph)
                if len(comp) > 1)

    def nodes_in_self_cycles(self):
        return iter({edge[0] for edge in
                     self._graph.selfloop_edges()})

    def node_valid(self, node):
        cycle_nodes = self.nodes_in_calc_cycles()
        valid_nodes = {}

        def inner(node):
            valid = False
            if node in valid_nodes:
                valid = valid_nodes[node]
            else:
                valid = node.valid
                valid_nodes[node] = valid

            if not valid:
                return False

            if node in cycle_nodes:
                return False

            return all((inner(n) for n in self._graph.successors(node)))

        return inner(node)

    def node_enabled_ancestors(self, node):
        res = True
        if not node.enabled:
            res = any(ans.enabled for ans in nx.ancestors(self._graph, node))
        return res

    def nodes_missing_ancestors(self):
        nodes = set()
        for node in self._graph.nodes():
            if node.type == 'miss':
                # Depends on missing cols.
                nodes.update(nx.ancestors(self._graph, node))
        return nodes

    def ancestor_calcs(self, calc_obj):
        return nx.ancestors(self._graph, calc_obj)

    def descendant_calcs(self, calc_obj):
        return nx.descendants(self._graph, calc_obj)

    def successor_calcs(self, calc_obj):
        try:
            return self._graph.successors(calc_obj)
        except Exception:
            return {}

    def topological_sort(self, nodes=None, nodes_in_cycles=None):
        graph = self._graph
        if nodes_in_cycles is None:
            nodes_in_cycles = self.nodes_in_calc_cycles()
        if nodes_in_cycles:
            graph = nx.DiGraph(incoming_graph_data=graph)
            graph.remove_nodes_from(nodes_in_cycles)

        if nodes is not None:
            res = list(reversed([node for node in nx.topological_sort(graph)
                                 if node.type == 'calc' and node in nodes]))
        else:
            res = list(reversed([node for node in nx.topological_sort(graph)
                                 if node.type == 'calc']))
        return res

    def nodes(self):
        return self._graph.nodes()

    def __contains__(self, node):
        return node in self._graph

    @classmethod
    def from_graph(cls, graph):
        """
        Return a copy.
        """
        def copy_graph(old_graph):
            # TODO: custom graph copy, remove when possible.
            # Workaround for graph.copy() performing deepcopy on Python 2
            # creating new Calc instances.
            # new_graph = old_graph.copy()
            new_graph = type(old_graph)()
            for node in old_graph.nodes():
                new_graph.add_node(node)
            for src, dst in old_graph.edges():
                new_graph.add_edge(src, dst)
            return new_graph

        res = cls([])
        old_graph = graph._graph
        res._graph = copy_graph(old_graph)
        res._calc_map = dict(graph._calc_map)
        return res


def execute_calcs(graph, ordered_calcs, arg, res, skip):
    def _gen_execute_calcs(graph, ordered_calcs, arg, res, skip):
        invalid = set(graph.nodes_missing_ancestors())

        for calc in ordered_calcs:

            if calc not in invalid and graph.node_enabled_ancestors(calc):
                try:
                    output = python_calculator(
                        calc.expr, {'res': res, 'arg': arg})
                    res[calc.name] = output
                    yield calc, output
                except Exception as e:
                    invalid.update(
                        graph.ancestor_calcs(calc))
                    if not skip:
                        raise
                    else:
                        yield calc, e
                except:  # NOQA
                    # For example if user code is a SyntaxError.
                    e = sys.exc_info()[1]
                    if not skip:
                        raise
                    else:
                        yield calc, e
    list(_gen_execute_calcs(graph, ordered_calcs, arg, res, skip))


def parse_calc(calc_line):
    var, calc = calc_line.split(FUNCTION_SPLIT, 1)
    try:
        calc, enabled = calc.split(ENABLED_SPLIT, 1)
        enabled = 1 if enabled.strip() == '1' else 0
    except ValueError:
        # Compatibility with calculations that does not have the enabled flag
        enabled = 1
    return var.strip(), calc.strip(), enabled


def python_calculator(calc_text, extra_globals=None):
    output = advanced_eval(calc_text, extra_globals)
    if not isinstance(output, np.ndarray):
        if isinstance(output, list):
            output = np.array(output)
        else:
            # Assume scalar value.
            output = np.array([output])
    return output


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
    try:
        return eval(compile(calc, "<string>", "eval", compiler_flags), ctx, {})
    except Exception:
        msg = 'Error executing calculation: {}.'.format(calc)
        raise exceptions.SyUserCodeError(sys.exc_info(), msg)


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
        self._is_computing = state
        self.emitDataChanged()

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.BackgroundRole:
            if not self._valid:
                return colors.DANGER_BG_COLOR
            elif self.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
            return None
        elif role == QtCore.Qt.ToolTipRole:
            return self.text()
        else:
            return super(CalculatorCalculationItem, self).data(role)


class CalculatorModelItem(QtGui.QStandardItem):
    """A model item for calculated columns"""

    def __init__(self, name, calculation='', calc_item=None, parent=None):
        super(CalculatorModelItem, self).__init__(parent=parent)
        self._errors = {}
        self._is_warned = False
        self.node = Calc(name, calculation, None)
        self._old_name = self.name
        self.message = ''
        self._attributes = []
        self._duplicate = False
        self._column_data = np.array([])
        self._calc_item = calc_item
        self._dangerous_name = re.search('\s$', self.name) is not None

    def text(self):
        return self.node.name

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return self.node.name
        elif role == QtCore.Qt.BackgroundRole:
            if not self.valid or self._duplicate:
                return colors.DANGER_BG_COLOR
            elif self.is_computing or self._dangerous_name or self._is_warned:
                return colors.WARNING_BG_COLOR
            else:
                return None
        elif role == QtCore.Qt.ToolTipRole:
            text = six.text_type(self.node)
            deps = self.node.deps
            if deps:
                text += '\n\nUsed columns:\n'
                text += '\n'.join(
                    ['- {}'.format(i) for i in deps])

            # TODO(erik):
            # Ask model for this information.
            # if len(self._child_columns):
            #     text += '\n\nDependent columns:\n'
            #     text += '\n'.join(['- {}'.format(i.name)
            #                        for i in self._child_columns])

            if self._dangerous_name:
                text += ('\n\nWarning: \n This columns name contains '
                         'whitespace at the end')
            return text
        else:
            return None

    def flags(self):
        return QtCore.Qt.ItemIsEnabled

    @property
    def enabled(self):
        return self.node.enabled

    @enabled.setter
    def enabled(self, value):
        self.node.enabled = value
        if self.model():
            self.model().data_ready.emit()

    @property
    def valid(self):
        return self.node.valid

    @property
    def warned(self):
        return self._is_warned

    @warned.setter
    def warned(self, state):
        self._is_warned = bool(state)
        self.emitDataChanged()

    @property
    def name(self):
        return self.node.name

    @name.setter
    def name(self, name):
        self._old_name = self.node.name
        if name != self._old_name:
            self.model().rename_item(self, name)
            self._dangerous_name = re.search('\s$', self.name) is not None

    def rename(self, new_name):
        # WARNING: only called to ensure update, actual renames must
        # go through the graph.
        self.model().data_ready.emit()

    @property
    def expr(self):
        return self.node.expr

    @expr.setter
    def expr(self, value):
        if isinstance(self._calc_item, QtGui.QStandardItem):
            self._calc_item.setText(value)
        old_expr = self.node.expr
        if value != old_expr and self.model() is not None:
            self.model().change_item_expr(self, value)
            self.model().data_ready.emit()

    @property
    def duplicate(self):
        return self._duplicate

    @duplicate.setter
    def duplicate(self, value):
        self._duplicate = value

    def update(self):
        self.model()._recompute_item(self)
        self.model().data_ready.emit()

    @property
    def column_data(self):
        return self._column_data

    @column_data.setter
    def column_data(self, data):
        self._column_data = data
        self.emitDataChanged()

    @property
    def is_computing(self):
        return self._calc_item._is_computing

    @is_computing.setter
    def is_computing(self, state):
        self._calc_item.is_computing = state
        self.emitDataChanged()

    @property
    def attributes(self):
        return self._attributes

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.index() == other.index()

    def __ne__(self, other):
        return self.index() != other.index()


def display_calculation(calc):
    if isinstance(calc, six.binary_type):
        calc = six.text_type(calc.decode('utf8'))
    return calc


class DragItem(QtGui.QStandardItem):

    def __init__(self, parent=None):
        super(DragItem, self).__init__(parent=parent)

    def data(self, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            return '\u205e'
        elif role == QtCore.Qt.ToolTipRole:
            return 'Grab with the first mouse button to drag!'
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        return super(DragItem, self).data(role)


class CalculatorEnableItem(QtGui.QStandardItem):
    def __init__(self, main_item):
        self._main_item = main_item
        super(CalculatorEnableItem, self).__init__()

    def setData(self, value, role=QtCore.Qt.UserRole):
        if role == QtCore.Qt.CheckStateRole:
            self._main_item.enabled = value == QtCore.Qt.Checked
        super(CalculatorEnableItem, self).setData(value, role=role)


class CalculatorItemModel(QtGui.QStandardItemModel):
    data_ready = QtCore.Signal()
    item_dropped = QtCore.Signal(QtCore.QModelIndex)

    """
    Calculator Model.
    """
    def __init__(self, in_tables, parameters,
                 preview_calculator=None, parent=None,
                 empty_input=False):
        """
        Initialize :class:CalculatorModel

        Parameters
        ----------
        in_tables : table.FileList
        parameters : dict
        preview_calculator : function or None
        parent : None or QtGui.QObject
        """

        def trim_name(name):
            if name.startswith('res.col(') and name.endswith(')'):
                name = name[8:-1]
            if name.startswith('${') and name.endswith('}'):
                name = name[2:-1]
            return name

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

            return sorted(
                input_column_names_and_types, key=lambda s: s[0].lower())

        super(CalculatorItemModel, self).__init__(parent=parent)
        self._in_tables = in_tables
        self._parameter_root = parameters
        self._graph = CalculationGraph([])

        self.empty_input = empty_input
        self._input_column_names_and_types = []
        self._preview_queue = []

        if not self._in_tables:
            self._in_tables = table.FileList()

        if len(self._in_tables) > 0:
            table_file = self._in_tables[0]
        else:
            table_file = table.File()
        self._preview_worker = CalculatorModelPreviewWorker(table_file)

        self.calc_timer = QtCore.QTimer()
        self.calc_timer.setInterval(1000)  # 1s timeout before calc runs
        self.calc_timer.setSingleShot(True)

        self.calc_timer.timeout.connect(self._compute_items)

        input_column_names_and_types = set()
        input_column_names = set()
        parent_name = 'arg'

        for in_data in self._in_tables:
            if isinstance(in_data, sygeneric):
                self.empty_input = True
                break
            self._input_column_names_and_types = flatten_input(
                in_data,
                input_column_names_and_types,
                input_column_names,
                parent_name)

        calc_attrs_dict = dict(json.loads(
            self._parameter_root['calc_attrs_dict'].value or '[]'))

        self._preview_worker.preview_ready.connect(self._update_item)
        for i, item in enumerate(self._parameter_root['calc_list'].list):
            name, calculation, enabled = parse_calc(item)
            name = trim_name(name)
            model_item = self.add_item(name, calculation, bool(enabled))
            item_attrs = calc_attrs_dict.get(i, [])
            if item_attrs:
                model_item.attributes[:] = item_attrs

        self._start_preview()

    def cleanup_preview_worker(self):
        try:
            self._preview_worker.preview_ready.disconnect(self._update_item)
        except RuntimeError:
            pass

    def flags(self, index):
        if index.isValid():
            flags = QtCore.Qt.NoItemFlags
            if index.column() != 3:
                flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
                if index.column() == 2:
                    flags |= QtCore.Qt.ItemIsUserCheckable
            return flags
        else:
            return super(CalculatorItemModel, self).flags(index)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ['text/plain']

    def dropMimeData(self, mime_data, action, row, column, parent):
        return False

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

    def items(self):
        return (self.item(row) for row in range(self.rowCount()))

    def get_item_by_name(self, name):
        items = self.findItems(name, flags=QtCore.Qt.MatchExactly, columns=0)
        if items:
            return items[0]

    def build_item(self, name='', calculation='', enabled=True):
        calculation_item = CalculatorCalculationItem(calculation, parent=self)
        name_item = CalculatorModelItem(name, calculation, calculation_item,
                                        parent=self)
        enabled_item = CalculatorEnableItem(name_item)
        enabled_item.setCheckable(True)
        enabled_item.setToolTip(
            "Uncheck this to create a temporary variable usable in the "
            "following calculations but excluded from the output.")
        if enabled:
            enabled_item.setCheckState(QtCore.Qt.Checked)
        drag_item = DragItem()
        name_item.enabled = enabled
        return name_item, calculation_item, enabled_item, drag_item

    def add_item(self, name=None, calculation=None, enabled=True):
        """Add a column to the model and the preview table."""
        if name is None:
            name = 'New Column {}'.format(self.rowCount())
        if calculation is None:
            calculation = ''
        item_row = self.build_item(name, calculation, enabled)
        item = item_row[0]
        node = item.node
        self._before_add_item_set_duplicate(item)
        self.appendRow(item_row)
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.add_calc(node)

        if self.rowCount() < 2:
            self.setHeaderData(0, QtCore.Qt.Horizontal, 'Column name')
            self.setHeaderData(1, QtCore.Qt.Horizontal, 'Calculation')
            self.setHeaderData(2, QtCore.Qt.Horizontal, 'On')
            self.setHeaderData(3, QtCore.Qt.Horizontal, '')

        return item_row[0]

    def insert_item(self, name='', calculation='', row=0):
        item_row = self.build_item(name, calculation)
        item = item_row[0]
        node = item.node
        self._before_add_item_set_duplicate(item)
        self.insertRow(row, item_row)
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.add_calc(node)
        return item_row[0]

    def copy_item(self, row):
        item = self.item(row, 0)
        new_item = self.insert_item(
            '{} Copy'.format(item.name),
            item.expr, row + 1)
        new_item.attributes[:] = item.attributes
        self._recompute_item(new_item)

    def remove_item(self, row):
        """Remove a column from the model."""

        item = self.item(row, 0)
        if item is None:
            # List is empty
            return

        self.removeRow(row)
        node = item.node
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.remove_calc(node)
            self._preview_worker.remove_column(node.name)
        else:
            self._after_remove_item_set_duplicate(item)

        self.data_ready.emit()
        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def rename_item(self, item, new_name):
        node = item.node
        old_name = node.name

        items_with_old_name = [
            i for i in self.items() if i.name == old_name]
        items_with_new_name = [
            i for i in self.items() if i.name == new_name]

        items_with_old_name.remove(item)
        n_old_name = len(items_with_old_name)
        n_new_name = len(items_with_new_name)

        if n_new_name >= 1:
            self._set_item_duplicate(item, True)
            self._graph.rename_calc(
                node, new_name, add_if_missing=False)

            for i in items_with_new_name:
                self._set_item_duplicate(i, True)
                # Force update.
                i.rename(new_name)
        else:
            if item.duplicate:
                item.duplicate = False

            if node not in self._graph:
                self._graph.rename_calc(
                    node, new_name, add_if_missing=False)
                with self._invalidate_affected(node):
                    self._graph.add_calc(node)
            else:
                with self._invalidate_affected(node):
                    try:
                        self._graph.rename_calc(node, new_name)
                    except Exception:
                        pass
            self._preview_worker.remove_column(old_name)

        # Force update.
        item.rename(new_name)
        if n_old_name == 1:
            self._set_item_duplicate(items_with_old_name[0], False)

        self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())

    def change_item_expr(self, item, new_expr):
        node = item.node
        if not item.duplicate:
            with self._invalidate_affected(node):
                self._graph.change_calc_expr(node, new_expr)
        else:
            node.expr = new_expr

    def _set_item_duplicate(self, item, value):
        item.duplicate = value
        node = item.node

        if node in self._graph:
            if value:
                with self._invalidate_affected(node):
                    self._graph.remove_calc(node)
        else:
            if not value:
                with self._invalidate_affected(node):
                    self._graph.add_calc(node)

    def _before_add_item_set_duplicate(self, item):
        name = item.name
        items_with_same_name = [i for i in self.items() if name == i.name]
        if items_with_same_name:
            for i in items_with_same_name:
                self._set_item_duplicate(i, True)
            item.duplicate = True

    def _after_remove_item_set_duplicate(self, item):
        name = item.name
        items_with_same_name = [i for i in self.items() if name == i.name]
        if len(items_with_same_name) == 1:
            for i in items_with_same_name:
                self._set_item_duplicate(i, False)
            item.duplicate = False

    @contextlib.contextmanager
    def _invalidate_affected(self, node):
        try:
            nodes = set(self._graph.ancestor_calcs(node))
        except Exception:
            nodes = set()
        yield
        nodes.add(node)
        try:
            nodes.update(self._graph.ancestor_calcs(node))
        except Exception:
            pass

        nodes = {n for n in nodes if n in self._graph}
        self._queue_nodes(nodes)

    def _queue_nodes(self, nodes):
        self._preview_graph = CalculationGraph.from_graph(self._graph)
        self._preview_queue.insert(0, {node: Calc.from_calc(node)
                                       for node in nodes})
        self.calc_timer.start()

    def _start_preview(self):
        self._preview_queue[:] = []
        self._queue_nodes(set(n.node for n in self.items()))

    def _recompute_item(self, item):
        if item.valid:
            self._queue_nodes([item.node])

    def _compute_items(self):
        item_map = {}
        for item in self.items():
            item_map[item.node] = item

        old_to_new_node_map = {}

        preview_graph = CalculationGraph.from_graph(self._preview_graph)

        for group in self._preview_queue:
            for old_calc, new_calc in group.items():
                if old_calc not in old_to_new_node_map:
                    try:
                        preview_graph.remove_calc(old_calc)
                        preview_graph.add_calc(new_calc)
                    except Exception:
                        pass
                    else:
                        old_to_new_node_map[old_calc] = new_calc

        new_to_old_node_map = dict(zip(old_to_new_node_map.values(),
                                       old_to_new_node_map.keys()))
        node_set = set(new_to_old_node_map.keys())
        for node in list(node_set):
            node_set.update(preview_graph.descendant_calcs(node))
        cycles = preview_graph.nodes_in_calc_cycles()
        normal_nodes = node_set.difference(cycles)

        if normal_nodes:
            exec_order = preview_graph.topological_sort(
                normal_nodes, nodes_in_cycles=cycles)
            for new_node in exec_order:
                old_node = node
                if new_node in new_to_old_node_map:
                    old_node = new_to_old_node_map[new_node]
                self._preview_worker.calculate((old_node, new_node))
                item = item_map.get(old_node)
                if item:
                    item.is_computing = True

        self._preview_queue[:] = []

    def _update_item(self, items):

        calc, data, error_lines = items
        item = None
        for i in self.items():
            if i.node is calc:
                item = i
                break

        if item is None:
            return

        is_warned = False
        message = ''
        item.is_computing = False
        # check if the data can be stored in a sytable

        if error_lines:
            if calc.expr:
                is_warned = True
        try:
            dummy_output_table = table.File()
            dummy_output_table.set_column_from_array(item.name, data)
            item.column_data = data

            if error_lines:
                message = 'Calculating {}: {}'.format(
                    item.name, error_lines[0])
            elif is_warned:
                message = data[0]
            else:
                message = ''
        except Exception as e:
            if len(data) > 0:
                message = '{}'.format(e)
                is_warned = True

        item.message = message
        item.warned = is_warned
        item.emitDataChanged()
        self.data_ready.emit()

    def validate(self):

        def check_item_messages():
            """Return first message of items."""
            for item in items:
                if item.message:
                    return item.message
            return ''

        def check_column_length():
            """Return True if all selected columns have the same length."""
            enabled = [item for item in items
                       if item.enabled and not item.is_computing]
            # for i in enabled:
            #     print('i', item, item.expr, item.is_computing)
            col_lens = np.array([len(i.column_data) for i in enabled])
            if len(col_lens):
                return np.all((col_lens - col_lens[0]) == 0)
            return True

        def check_valid_names():
            """Return True if all column names are valid."""
            col_names_valid = [i.valid for i in items if i.node.empty_expr]
            return np.all(col_names_valid)

        def check_calculation():
            """Return True if all column names are valid."""
            return [i for i in items if not i.node.empty_expr and not i.valid]

        def check_empty_calculations():
            return [i for i in items if i.node.empty_expr]

        def check_preview_warnings():
            """Return True if all calculations have finished."""
            calculations_warned = [i.warned
                                   for i in items]
            return np.all(calculations_warned)

        def check_duplicate():
            return [i for i in items if i.duplicate]

        def check_cycles():
            return self._graph.nodes_in_calc_cycles()

        items = list(self.items())
        item_message = check_item_messages()
        valid = all([i.valid and not i.duplicate for i in items])
        cycles = check_cycles()

        if cycles:
            self_cycles = list(self._graph.nodes_in_self_cycles())
            if self_cycles:
                return False, 'Cyclic dependencies to itself in: {}'.format(
                    ', '.join(sorted(
                        n.name for n in self._graph.nodes_in_self_cycles())))
            else:
                return (
                    False,
                    'Cyclic dependencies in the following groups: {}'.format(
                        ', '.join('{{{}}}'.format(
                            ', '.join(sorted(n.name for n in g)))
                                  for g in self._graph.nodes_in_cycles())))

        if valid:
            if check_preview_warnings():
                item_map = {}
                for item in self.items():
                    item_map[item.node] = item
                    # Ensure the first message.
                    for node in self._graph.topological_sort(
                            item_map.keys()):
                        if item_message:
                            item_message = item_map[node].message
                            break
                return True, item_message
            elif self.empty_input:
                return True, 'No input data available'
            elif item_message:
                return True, item_message
            elif not check_column_length():
                return (False, 'The calculated columns do not have the same '
                        'length')
            return True, ''
        else:
            if check_calculation():
                return False, check_calculation()[0].node.exception
            elif check_duplicate():
                duplicate_s = ', '.join(sorted(set(
                    i.node.name for i in check_duplicate())))
                return False, 'Duplicate calculation names: {}'.format(
                    duplicate_s)
            elif check_empty_calculations():
                return True, 'Empty calculation'
            return False, 'Unknown Error'

    def save_parameters(self):
        var = '{}'
        self._parameter_root['calc_list'].list = [
            (var + ' {} {} {}{}').format(
                item.name, FUNCTION_SPLIT, item.expr, ENABLED_SPLIT,
                item.enabled) for item in self.items()]

        self._parameter_root['calc_attrs_dict'].value = json.dumps(
            [(i, item.attributes)
             for i, item in enumerate(self.items())
             if item.attributes])


class CalculatorModelPreviewWorker(QtCore.QObject):
    preview_ready = QtCore.Signal(list)

    def __init__(self, arg):
        super(CalculatorModelPreviewWorker, self).__init__()
        self._queue = six.moves.queue.Queue()
        self._arg = arg
        self._res = ResTable()
        self._err = set()
        self._thread = threading.Thread(target=self._run, args=(self._queue,))
        self._thread.daemon = True
        self._thread.start()

    def _run(self, queue):
        while True:
            args = queue.get()
            self._run_cmd(args)

    def calculate(self, calc):
        self._queue.put(calc)

    def remove_column(self, col):
        try:
            del self._res[col]
        except KeyError:
            pass

    def _run_cmd(self, calc_tuple):
        org_calc, pre_calc = calc_tuple
        name = pre_calc.name
        deps = pre_calc.deps
        expr = pre_calc.expr
        empty = pre_calc.empty_expr
        valid = pre_calc.valid

        self._res[name] = None
        error = set(deps).intersection(self._err)
        missing = set(deps).difference(self._res)
        error.update(missing)
        output = np.array([])
        error_lines = []
        if not valid:
            self._err.add(name)
            if empty:
                error_lines = ['Empty']
            else:
                error_lines = ['Invalid']
            output = np.array(error_lines)
        elif error:
            self._err.add(name)
            missing_s = ', '.join(sorted(error))
            output = np.array(['Missing deps: {}'.format(missing_s)])
            error_lines = ['Missing dependencies of {}: {}'.format(
                name, missing_s)]
        else:
            output = None
            try:
                output = python_calculator(
                    expr, {'res': self._res, 'arg': self._arg})
                self._res[name] = output
                try:
                    self._err.remove(name)
                except Exception:
                    pass
            except exceptions.SyUserCodeError as e:
                error_lines = e.brief_help_text.splitlines()
                output = np.array([error_lines[-1]])
                self._err.add(name)
            except:  # NOQA
                # For example if user code is a SyntaxError.
                e = sys.exc_info()[1]
                error_lines = traceback.format_exception_only(type(e), e)
                output = np.array([error_lines[-1]])
                self._err.add(name)

        self.preview_ready.emit([org_calc, output, error_lines])
