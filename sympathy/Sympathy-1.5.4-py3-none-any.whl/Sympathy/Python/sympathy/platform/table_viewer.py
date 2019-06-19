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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import re
import six
import datetime
import operator
import itertools
import collections
import fnmatch

from sympathy.api import qt as qt_compat
from sympathy.utils import prim

QtCore = qt_compat.QtCore
QtGui = qt_compat.QtGui
qt_compat.backend.use_matplotlib_qt()
import numpy as np
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib import offsetbox

from sympathy.platform import widget_library as sywidgets
from sympathy.api import table
from sympathy.utils.mock import mock_wrap
from . viewerbase import ViewerBase
from .. utils import dtypes
from .. utils import search


DTYPE_COLOR = [QtGui.QColor.fromHsvF(i / len(dtypes.typenames()), 0.18, 0.9)
               for i in range(len(dtypes.typenames()))]
COLUMN_COLORS = {kind: color for kind, color in zip(
    dtypes.typenames(), DTYPE_COLOR)}

DATA_FONT = QtGui.QFont('Courier')
VALID_AS_X = ('f', 'i', 'u', 'M')
VALID_AS_Y = ('f', 'i', 'u', 'b', 'm')
VALID_AS_HIST = ('f', 'i', 'u', 'b', 'M', 'S', 'U')


def fuzzy_list_filter(pattern, items):

    if pattern:
        filter_ = search.fuzzy_pattern(pattern)
        display = []
        for row, col_item in enumerate(items):
            if isinstance(col_item, list):
                is_match = any(
                    [search.matches(
                        filter_,
                        TableModel.format_data(item))
                     for item in col_item])
            else:
                is_match = search.matches(filter_,
                                          TableModel.format_data(col_item))
            if is_match:
                display.append(row)
    else:
        display = range(len(items))

    return display


def glob_list_filter(pattern, items):

    def globmatch(item, pattern):
        return fnmatch.fnmatchcase(item.lower(), pattern.lower())

    if pattern:
        display = []

        for row, col_item in enumerate(items):
            if isinstance(col_item, list):
                is_match = any(globmatch(TableModel.format_data(item), pattern)
                               for item in col_item)
            else:
                is_match = globmatch(TableModel.format_data(col_item), pattern)
            if is_match:
                display.append(row)
    else:
        display = range(len(items))
    return display


def meta_filter(pattern, columns):
    identifiers = ['a', 'c', '*']

    if (pattern.startswith(':') and len(pattern) >= 2 and
            pattern[1] in identifiers):
        # prefix search case
        startend = []
        patterns = []
        for m in re.finditer(r':([ac*])\s', pattern):
            startend.extend([m.start(), m.end()])
            patterns.append(m.group(1))
        if len(startend):
            startend.pop(0)
            startend.append(len(pattern))

        startend = [slice(startend[i], startend[i+1])
                    for i in range(len(startend)) if not i % 2]
        patterns = [(p, pattern[se]) for p, se in zip(patterns, startend)]

    else:
        # default to column search
        patterns = [('c', pattern)]

    org_columns = columns[:]  # copy original columns

    for type, pat in patterns:
        pat = pat.strip(' ')
        if type == 'c':
            # handle column search
            names = [col.name for col in columns]
            search_in = [names]
        elif type == 'a':
            # handle attribute search
            keys = [col.attrs.keys() for col in columns]
            values = [col.attrs.values() for col in columns]
            search_in = [keys, values]
        else:
            # handle search in both attributes and column names
            names = [col.name for col in columns]
            keys = [col.attrs.keys() for col in columns]
            values = [col.attrs.values() for col in columns]
            search_in = [names, keys, values]
        # apply search
        result = set()
        for items in search_in:
            result.update(apply_filter(pat, items))
        columns = [columns[idx] for idx in result]

    filtered_item_indexes = [org_columns.index(col) for col in columns]
    return filtered_item_indexes


def apply_filter(pat, items):
    patterns = pat.split(',')
    filtered_item_indexes = set()
    for p in patterns:
        if '*' in p or '?' in p:
            display = glob_list_filter(p, items)
        else:
            display = fuzzy_list_filter(p, items)
        filtered_item_indexes.update(display)
    return filtered_item_indexes


class TransposedModel(QtCore.QAbstractTableModel):
    def __init__(self, base_model, parent=None):
        super(TransposedModel, self).__init__(parent)
        self._base_model = base_model
        self._base_model.layoutChanged.connect(self.layoutChanged)
        self._base_model.modelAboutToBeReset.connect(self.beginResetModel)
        self._base_model.modelReset.connect(self.endResetModel)

    def _transpose_index(self, index):
        return self._base_model.index(
            index.column(), index.row(), index.parent())

    def base_model(self):
        return self._base_model

    def rowCount(self, index):
        return self._base_model.columnCount(self._transpose_index(index))

    def columnCount(self, index):
        return self._base_model.rowCount(self._transpose_index(index))

    def data(self, index, role):
        return self._base_model.data(self._transpose_index(index), role)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Vertical:
            orientation = QtCore.Qt.Horizontal
        else:
            orientation = QtCore.Qt.Vertical
        return self._base_model.headerData(section, orientation, role)

    def column_names(self):
        return self._base_model.column_names()

    def column_name(self, row, column):
        """
        Return name for table column with index row.

        This method can be used to get the column name for a cell without
        checking if the model is transposed or not.
        """
        if 0 <= row < len(self.column_names()):
            return self.column_names()[row]
        else:
            raise IndexError("Column {} does not exist.".format(row))

    def table(self):
        return self._base_model.table()

    def set_decimals(self, round_fn):
        return self._base_model.set_decimals(round_fn)


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self._show_colors = True

        self._table = None
        self._round_fn = lambda x: x
        self._headers = None
        self._row_count = 0
        self._column_count = 0

        # max row number due to qt bug
        self._max_row_limit = 71582788

        self._cache = {}
        # self._cnt = 0

    def table(self):
        return self._table

    def set_table(self, table_):
        if table is None:
            return

        self.beginResetModel()
        self._table = table_
        self._headers = table_.column_names()
        self._row_count = self._table.number_of_rows()
        self._column_count = self._table.number_of_columns()
        self._cache = {}
        self._update_cache(0, 0)
        self.endResetModel()

    def set_decimals(self, round_fn):
        self._round_fn = round_fn

    @staticmethod
    def _format_data(data, float_round_fn=None):

        if isinstance(data, float) and float_round_fn:
            data = float_round_fn(data)
        elif isinstance(data, complex) and float_round_fn:
            real = data.real
            imag = data.imag
            data = six.text_type(float_round_fn(real))
            if imag >= 0:
                data += "+" + six.text_type(float_round_fn(imag))[1:] + "j"
            else:
                data += six.text_type(float_round_fn(imag)) + "j"
        elif isinstance(data, datetime.datetime):
            data = data.isoformat()
        elif isinstance(data, six.binary_type):
            # repr will show printable ascii characters as usual but will
            # replace any non-ascii or non-printable characters with an escape
            # sequence. The slice removes the quotes added by repr.
            if six.PY2:
                data = repr(data)[1:-1]
            else:
                data = repr(data)[2:-1]
        elif data is None:
            data = '--'
        return six.text_type(data)

    @classmethod
    def format_data(cls, data, float_round_fn=None):
        try:
            data = data.tolist()
        except AttributeError:
            pass

        return cls._format_data(data, float_round_fn)

    def column_names(self):
        if self._table is None:
            return []
        else:
            return self._table.column_names()

    def column_name(self, row, column):
        """
        Return name for table column with index column.

        This method can be used to get the column name for a cell without
        checking if the model is transposed or not.
        """
        if 0 <= column < len(self.column_names()):
            return self.column_names()[column]
        else:
            raise IndexError("Column {} does not exist.".format(column))

    def set_show_colors(self, show):
        self._show_colors = show

    def rowCount(self, qmodelindex):
        if self._row_count > self._max_row_limit:
            return self._max_row_limit
        return self._row_count

    def columnCount(self, qmodelindex):
        return self._column_count

    def data(self, qmodelindex, role):
        if not qmodelindex.isValid():
            return None
        row = qmodelindex.row()
        col = qmodelindex.column()
        if role == QtCore.Qt.DisplayRole:
            if row < self._max_row_limit - 1:
                try:
                    data = self._cache[(row, col)]
                except KeyError:
                    self._update_cache(row, col)
                    data = self._cache[(row, col)]
                element = self.format_data(data, self._round_fn)
            else:
                element = 'Data truncated!'
            return element
        elif role == QtCore.Qt.ToolTipRole:
            if row < self._max_row_limit - 1:
                text = self.format_data(self._cache[(row, col)])
            else:
                text = 'Data truncated since maximum view limit reached!'
            # Escape HTML characters in a way that is compatible with QToolTip.
            return QtGui.QTextDocumentFragment.fromPlainText(text).toHtml()
        elif role == QtCore.Qt.BackgroundRole:
            if self._show_colors:
                if row < self._max_row_limit - 1:
                    return self._column_color(col)
                return QtGui.QColor.fromRgb(228, 186, 189)
            else:
                return None
        elif role == QtCore.Qt.FontRole:
            return DATA_FONT
        return None

    def _create_column_tooltip_string(self, column_name):
        column_type = self._table.column_type(column_name)
        tooltip_string = '"{}"\n\nType: {} ({})'.format(
            column_name, dtypes.typename_from_kind(column_type.kind),
            column_type)
        attrs = self._table.get_column_attributes(column_name)
        attrs_string = '\n'.join(
            ['{}: {}'.format(k, v) for k, v in six.iteritems(attrs)])
        if attrs_string:
            tooltip_string += '\n\nAttributes:\n{}'.format(attrs_string)
        return tooltip_string

    def _column_color(self, column):
        column_type = self._table.column_type(self._headers[column])
        return COLUMN_COLORS.get(dtypes.typename_from_kind(column_type.kind),
                                 None)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._headers[section]
            elif role == QtCore.Qt.ToolTipRole:
                return self._create_column_tooltip_string(
                    self._headers[section])
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.BackgroundRole:
                return self._column_color(section)
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return six.text_type(section)
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft

        return super(TableModel, self).headerData(section, orientation, role)

    def attributes(self):
        attrs = self._table.get_table_attributes() or {}
        return ['{}: {}'.format(k, v) for k, v in six.iteritems(attrs)]

    def _update_cache(self, row, col, row_cache_size=1000,
                      col_cache_size=100, max_cache_size=1000000):
        def lt(x, y): return x < y

        def gt(x, y): return x > y

        def bound_fn(rel, val, bound): return val if rel(val, bound) else bound

        def lower_bound(val, bound): return bound_fn(gt, val, bound)

        def upper_bound(val, bound): return bound_fn(lt, val, bound)

        start_row = lower_bound(row - row_cache_size // 2, 0)
        end_row = upper_bound(row + row_cache_size // 2, self._row_count)

        start_col = lower_bound(col - col_cache_size // 2, 0)
        end_col = upper_bound(col + col_cache_size // 2, self._column_count)

        rows_to_cache = range(start_row, end_row)
        cols_to_cache = range(start_col, end_col)

        real_row_col = itertools.product(rows_to_cache, cols_to_cache)
        norm_row_col = itertools.product(
            range(end_row - start_row), range(end_col - start_col))

        table_sliced = self._table[start_row:end_row, start_col:end_col]
        if len(self._cache) > max_cache_size:
            self._cache = {}

        columns = [table_sliced.get_column_to_array(name)
                   for name in table_sliced.column_names()]

        self._cache.update({(row, col): columns[n_col][n_row]
                            for (row, col), (n_row, n_col) in six.moves.zip(
                                    real_row_col, norm_row_col)})


class AttributeModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(AttributeModel, self).__init__(parent)

        self._attributes = None
        self._headers = None
        self._row_count = 0
        self._column_count = 0

    def set_attributes(self, attributes_):
        self.beginResetModel()
        if not isinstance(attributes_, dict):
            return
        self._attributes = [(key, value)
                            for key, value in six.iteritems(attributes_)]

        self._headers = ['Name', 'Value']
        self._column_count = 2
        self._row_count = len(self._attributes)
        self.endResetModel()

    def columnCount(self, qmodelindex):
        return self._column_count

    def rowCount(self, qmodelindex):
        return self._row_count

    def data(self, qmodelindex, role):
        if not qmodelindex.isValid():
            return None
        row = qmodelindex.row()
        col = qmodelindex.column()
        if role == QtCore.Qt.DisplayRole:
            data = self._attributes[row][col]
            return data
        elif role == QtCore.Qt.ToolTipRole:
            # Escape HTML characters in a way that is compatible with QToolTip.
            return QtGui.QTextDocumentFragment.fromPlainText(
                six.text_type(self._attributes[row][col])).toHtml()

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self._headers[section]
            elif role == QtCore.Qt.ToolTipRole:
                return self._headers[section]
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            # elif role == QtCore.Qt.BackgroundRole:
            #     return self._column_color(section)

        return super(AttributeModel, self).headerData(section, orientation,
                                                      role)


class TableViewerPreviewTable(sywidgets.EnhancedPreviewTable):
    def __init__(self, model=None, filter_function=None, parent=None):
        super(TableViewerPreviewTable, self).__init__(model, filter_function,
                                                      parent)
        self._preview_table.setMinimumHeight(300)
        self.row_column_legend = sywidgets.RowColumnLegend()
        self.add_widget_to_legend(self.row_column_legend, on_left=True)

    def table(self):
        return self._model.table()

    def show_decimals(self, decimals):
        if len(decimals) > 0:
            s = '{: 1.%sf}' % decimals
        else:
            s = '{}'

        def inner(value):
            try:
                return s.format(value)
            except (TypeError, ValueError):
                return six.text_type(value)

        try:
            self._model.set_decimals(inner)
        except AttributeError:
            return
        self._model.reset()
        # (Bene) the Qt resize is extremely costly for large tables
        # self._preview_table.resizeColumnsToContents()

    def set_row_column_legend(self, row, column):
        self.row_column_legend.set_row_column(row, column)


@mock_wrap
class TableViewer(ViewerBase):
    def __init__(self, table_=None, console=None, plot=True,
                 show_title=True, parent=None):
        super(TableViewer, self).__init__(parent)
        self._table_model = TableModel(self)
        self._attribute_model = AttributeModel(self)
        self._model = self._table_model

        self.has_plot = plot
        self._show_title = show_title

        self._console = console
        self._data_preview = TableViewerPreviewTable(
            model=self._model, filter_function=meta_filter)

        self._table_name_label = QtGui.QLabel()
        self._title_layout = QtGui.QHBoxLayout()
        self._title_layout.addWidget(QtGui.QLabel("Name: "))
        self._title_layout.addWidget(self._table_name_label)
        self._title_layout.addStretch()

        self._legend = Legend()

        if self._show_title:
            self._data_preview.add_layout_to_layout(self._title_layout,
                                                    on_top=True)
        self._data_preview.add_widget_to_legend(self._legend)

        hsplitter = QtGui.QSplitter()
        hsplitter.addWidget(self._data_preview)
        hsplitter.setCollapsible(0, False)

        # Figure
        if self.has_plot:
            self._plot = ViewerPlot(self._table_model)
            hsplitter.addWidget(self._plot)
            hsplitter.setCollapsible(1, False)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(hsplitter)
        if self._console is not None:
            layout.addWidget(self._console)
        self.setLayout(layout)

        table_toolbar = self._data_preview.toolbar()

        # Jump to row menu
        jump_to_row_go_button = QtGui.QPushButton('Go')
        jump_to_row_go_button.clicked.connect(self._handle_jump_to_row)
        self.jump_to_row_value = QtGui.QSpinBox()
        self.jump_to_row_value.setRange(0, 100000)

        jump_to_row_widget = QtGui.QWidget(self)
        jump_to_row_widget.setContentsMargins(2, 2, 2, 2)
        jump_to_row_layout = QtGui.QHBoxLayout()
        jump_to_row_layout.setContentsMargins(0, 0, 0, 0)
        jump_to_row_layout.addWidget(self.jump_to_row_value)
        jump_to_row_layout.addWidget(jump_to_row_go_button)
        jump_to_row_widget.setLayout(jump_to_row_layout)

        self.jump_to_row_menu = QtGui.QMenu(table_toolbar)
        jump_to_row_action = QtGui.QWidgetAction(self)
        jump_to_row_action.setDefaultWidget(jump_to_row_widget)
        self.jump_to_row_menu.addAction(jump_to_row_action)

        jump_to_row_button = QtGui.QToolButton()
        jump_to_row_button.setMenu(self.jump_to_row_menu)
        jump_to_row_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        jump_to_row_button_action = QtGui.QWidgetAction(self)
        jump_to_row_button_action.setDefaultWidget(jump_to_row_button)
        icon = QtGui.QIcon(
            prim.get_icon_path('actions/view-jump-to-row-symbolic.svg'))
        jump_to_row_button.setIcon(icon)
        table_toolbar.addAction(jump_to_row_button_action)
        jump_to_row_button.setToolTip(
            'Enter a row number to jump to that row.')

        self._toggle_attributes_action = table_toolbar.add_action(
            text='Show &attributes',
            icon_name='actions/edit-select-all-symbolic.svg',
            tooltip_text='Show attributes',
            is_checkable=True,
            receiver=self._handle_toggle_attributes,
            signal_type='toggled')

        self._toggle_transpose_action = table_toolbar.add_action(
            text='&Transpose view',
            icon_name='actions/view-transpose-symbolic.svg',
            tooltip_text='Transpose view',
            is_checkable=True,
            receiver=self._handle_toggle_transpose,
            signal_type='toggled')

        self._toggle_colors_action = table_toolbar.add_action(
            text='Show &colors',
            icon_name='actions/view-color-symbolic.svg',
            tooltip_text='Show colors',
            is_checkable=True,
            is_checked=True,
            receiver=self.show_colors,
            signal_type='toggled')

        self._data_preview.preview_table().add_context_menu_action(
            'Copy',
            'copy_selection',
            'actions/edit-copy-symbolic.svg',
            validate_callback=self.validate_copy,
            key_sequence=QtGui.QKeySequence.Copy)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy with column names',
            'copy_selection_with_column_names',
            'actions/edit-copy-symbolic.svg',
            validate_callback=self.validate_copy_with_column_names)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy column name',
            'copy_column_name',
            'actions/edit-copy-symbolic.svg',
            validate_callback=self.validate_copy_column_names)

        self._data_preview.preview_table().add_context_menu_action(
            'Copy all column names',
            'copy_column_names',
            'actions/edit-copy-symbolic.svg',
            validate_callback=self.validate_copy_column_names)

        if self.has_plot:
            self._toggle_plot_action = table_toolbar.add_action(
                text='Show &plot',
                icon_name='actions/view-plot-line-symbolic.svg',
                tooltip_text='Show plot',
                is_checkable=True,
                is_checked=True,
                receiver=self.show_plot,
                signal_type='toggled')
            self._toggle_plot_action.setChecked(False)  # hide to start with

            # init context menus
            self._data_preview.preview_table().add_context_menu_action(
                'Plot column as x',
                'plot_as_x',
                'actions/view-plot-x-axis-symbolic.svg',
                validate_callback=self.validate_as_x)
            self._data_preview.preview_table().add_context_menu_action(
                'Plot column as y',
                'plot_as_y',
                'actions/view-plot-y-axis-symbolic-add.svg',
                validate_callback=self.validate_as_y)
            self._data_preview.preview_table().add_context_menu_action(
                'Show histogram for column',
                'show_stats',
                'actions/view-plot-hist-symbolic-dark.svg',
                validate_callback=self.validate_as_hist)

        self._data_preview.preview_table().contextMenuClicked.connect(
            self.handle_preview_table_context_menu)

        self.update_data(table_)

    def update_data(self, table_):
        if table_ is not None:
            self._data_preview.clear_filter()
            self._data_preview.show_decimals('4')
            self._table_model.set_table(table_)
            self.set_table_name(table_.get_name())
            self._attribute_model.set_attributes(
                self._table_model.table().get_table_attributes() or {})
            self._data_preview.set_row_column_legend(
                table_.number_of_rows(), table_.number_of_columns())
            self.jump_to_row_value.setRange(0, table_.number_of_rows())
        # Keep any old filter active
        self._data_preview.reapply_filter()
        if self.has_plot:
            self._plot.update_model(self._table_model)

    def set_model(self, model, transposed):
        if transposed:
            if isinstance(model, TransposedModel):
                model = model.base_model()
            else:
                model = TransposedModel(model)
        self._model = model
        self._data_preview.set_model(model, transposed)

    def set_table_name(self, name):
        if name is None:
            name = ''
        self._table_name_label.setText(name)
        self._table_name_label.setToolTip(name)

    def show_colors(self, show):
        self._legend.setVisible(show)
        self._table_model.set_show_colors(show)
        self._table_model.layoutChanged.emit()

    def _handle_jump_to_row(self):
        row = col = None
        if self._toggle_transpose_action.isChecked():
            col = self.jump_to_row_value.value()
        else:
            row = self.jump_to_row_value.value()
        self._data_preview.preview_table().center_on_cell(row, col)

    def show_plot(self, show):
        if self.has_plot:
            self._plot.setVisible(show)

    def _handle_toggle_transpose(self, transposed):
        old_selection = self._data_preview.preview_table().selection()
        attributes = self._toggle_attributes_action.isChecked()
        if attributes:
            model = self._attribute_model
        else:
            model = self._table_model
        self.set_model(model, transposed)

        # Reset selection
        if old_selection:
            selection_model = (
                self._data_preview.preview_table().selectionModel())
            old_minrow, old_maxrow, old_mincol, old_maxcol = old_selection

            start_index = self._model.index(old_mincol, old_minrow)
            end_index = self._model.index(old_maxcol - 1, old_maxrow - 1)
            item_selection = QtGui.QItemSelection(start_index, end_index)
            selection_model.select(
                item_selection, QtGui.QItemSelectionModel.Select)

    def _handle_toggle_attributes(self, attributes):
        if attributes:
            model = self._attribute_model
        else:
            model = self._table_model
        transposed = self._toggle_transpose_action.isChecked()
        self.set_model(model, transposed)

    def clear(self):
        self._table_model.set_table(table.File())
        self._attribute_model.set_attributes({})

    def handle_preview_table_context_menu(self, function_name, row_idx,
                                          column_idx):
        function = getattr(self, function_name, None)
        if function is not None:
            function(row_idx, column_idx)

    def copy_selection(self, row, column, include_headers=False):
        """
        Put selected values in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        selection = self._data_preview.preview_table().selection()
        if selection is None:
            return

        self.copy_values(*selection, include_headers=include_headers)

    def copy_selection_with_column_names(self, row, column):
        """
        Put selected values including column names in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        self.copy_selection(row, column, include_headers=True)

    def copy_column_name(self, row, column):
        """
        Put column name at in the clipboard.
        """
        if self._toggle_transpose_action.isChecked():
            self.copy_values(row, row + 1, 0, 0, include_headers=True)
        else:
            self.copy_values(0, 0, column, column + 1, include_headers=True)

    def copy_column_names(self, row, column):
        """
        Put all column names in the clipboard.
        Arguments row and column are not used. Feel free to refactor.
        """
        column_count = len(self._model.column_names())
        if self._toggle_transpose_action.isChecked():
            self.copy_values(0, column_count, 0, 0, include_headers=True)
        else:
            self.copy_values(0, 0, 0, column_count, include_headers=True)

    def copy_values(self, minrow, maxrow, mincol, maxcol,
                    include_headers=False):
        """
        Copy values from the currently shown model.
        Ranges minrow to maxrow and mincol to maxcol are half open; they
        include minrow/mincol but not maxrow/maxcol.
        If include_headers is True a row with the column names for the selected
        column will be included as the first row.
        """
        def escape_html(text):
            return (text.replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;'))

        transposed = self._toggle_transpose_action.isChecked()
        if maxrow - minrow == 0 and maxcol - mincol == 1 and include_headers:
            # Skip the html table when copying a single column name.
            if transposed:
                column_name = self._model.column_names()[minrow]
            else:
                column_name = self._model.column_names()[mincol]
            html = csv = column_name
        elif (maxrow - minrow)*(maxcol - mincol) == 1 and not include_headers:
            # Skip the html table when copying a single value.
            qindex = self._model.index(minrow, mincol)
            html = csv = six.text_type(self._model.data(
                qindex, role=QtCore.Qt.DisplayRole))
        else:
            csv_lines = []
            html_lines = ['<html><body><table>']

            if include_headers and not transposed:
                column_names = self._model.column_names()[mincol:maxcol]
                csv_lines.append(';'.join(column_names))
                html_lines.append('<tr>')
                html_lines.extend(['<th>{}</th>'.format(escape_html(v))
                                   for v in column_names])
                html_lines.append('</tr>')

            for row in range(minrow, maxrow):
                row_values = []
                html_row_values = []
                if include_headers and transposed:
                    column_name = self._model.column_names()[row]
                    row_values.append(column_name)
                    html_row_values.append('<th>{}</th>'.format(
                        escape_html(six.text_type(column_name))))
                for col in range(mincol, maxcol):
                    qindex = self._model.index(row, col)
                    value = self._model.data(
                        qindex, role=QtCore.Qt.DisplayRole)
                    row_values.append(value)
                    html_row_values.append('<td>{}</td>'.format(
                        escape_html(six.text_type(value))))

                # Attributes can be any scalar type so we need to convert it to
                # text_type.
                csv_lines.append(';'.join(
                    [six.text_type(v) for v in row_values]))
                html_lines.append('<tr>')
                html_lines.extend(html_row_values)
                html_lines.append('</tr>')
            html_lines.append('</table></body></html>')
            csv = '\n'.join(csv_lines)
            html = '\n'.join(html_lines)

        mime_data = QtCore.QMimeData()
        mime_data.setHtml(html)
        mime_data.setText(csv)
        QtGui.QApplication.clipboard().setMimeData(mime_data)

    def plot_as_x(self, row, column):
        self._toggle_plot_action.setChecked(True)
        column_name = self._model.column_name(row, column)
        self._plot.add_column_to_plot(column_name, as_y=False)

    def plot_as_y(self, row, column):
        self._toggle_plot_action.setChecked(True)
        column_name = self._model.column_name(row, column)
        self._plot.add_column_to_plot(column_name)

    def show_stats(self, row, column):
        self._toggle_plot_action.setChecked(True)
        column_name = self._model.column_name(row, column)
        self._plot.show_stats_for(column_name)

    def validate_as_x(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_X:
            return True
        return False

    def validate_as_y(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_Y:
            return True
        return False

    def validate_as_hist(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        try:
            column_name = self._model.column_name(row, column)
        except IndexError:
            return False
        col_dtype = self._model.table().column_type(column_name)
        if col_dtype.kind in VALID_AS_HIST:
            return True
        return False

    def validate_copy(self, row, column):
        if row < 0 or column < 0:
            return False
        return True

    def validate_copy_with_column_names(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        if row < 0 or column < 0:
            return False
        return True

    def validate_copy_column_names(self, row, column):
        if self._toggle_attributes_action.isChecked():
            return False
        if self._toggle_transpose_action.isChecked():
            row, column = column, row
        if row >= 0 or column < 0:
            return False
        return True

    def custom_menu_items(self):
        menu_items = [self._toggle_colors_action]
        if self.has_plot:
            menu_items.append(self._toggle_plot_action)
        return menu_items


class Legend(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Legend, self).__init__(parent)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        groupbox = QtGui.QGroupBox('')

        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        for row, text in enumerate(dtypes.typenames()):
            icon = ColorBoxLegend(COLUMN_COLORS[text], label=text[0])
            icon.setToolTip(text)
            hlayout.addWidget(icon, 0, row)
        groupbox.setLayout(hlayout)
        layout.addStretch()
        layout.addWidget(groupbox)
        self.setLayout(layout)

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        text = self.toolTip()
        QtGui.QToolTip.showText(pos, text)
        super(Legend, self).mouseMoveEvent(event)


class ColorBoxLegend(QtGui.QWidget):
    def __init__(self, color, label=None, parent=None):
        super(ColorBoxLegend, self).__init__(parent)
        self.color = color
        self.setMinimumHeight(16)
        self.setMinimumWidth(16)
        self.setMaximumWidth(16)
        self.setMaximumHeight(16)

        self._label_str = label
        self._label = QtGui.QLabel('')
        self._label.setFont(self._get_font())
        self._label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        layout.addWidget(self._label)
        self.setLayout(layout)

        self.set_label(self._label_str)

    def set_label(self, label):
        if label is None:
            return
        self._label.setText(label)

    def _get_font(self):
        font = self._label.font()
        font.setItalic(True)
        return font

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), self.color)
        p.setPen(QtCore.Qt.black)
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))


class ViewerPlot(QtGui.QWidget):
    def __init__(self, data_model=None, parent=None):
        super(ViewerPlot, self).__init__(parent)

        self._model = data_model
        self._x_model = QtGui.QStandardItemModel()
        self._y_model = QtGui.QStandardItemModel()
        self._hist_model = QtGui.QStandardItemModel()

        # show lines or histogram
        self._line_plot_active = True
        self._line_legend = None
        # _max_data_points defines the maximum number of data points before
        # we resample to data to short plot time
        self._max_data_points = 10000

        # set the binning for the histogram
        self._binning_user_set = False

        self.setContentsMargins(1, 1, 1, 1)

        plot_toolbar = sywidgets.SyToolBar(self)
        self.x_label = QtGui.QLabel('X:')
        self.x_value = QtGui.QComboBox()
        self.x_value.setMaximumWidth(100)
        self.x_value.setModel(self._x_model)
        self.x_value.setToolTip('Select the column used for the x values')
        self.y_label = QtGui.QLabel('Y:')
        self.y_value = sywidgets.CheckableComboBox()
        self.y_value.setMaximumWidth(100)
        self.y_value.setModel(self._y_model)
        self.y_value.setToolTip('Select the columns used for the y values. '
                                'Multiple columns can be selected.')
        self.hist_label = QtGui.QLabel('Histogram:')
        self.hist_label.setVisible(False)
        self.hist_value = QtGui.QComboBox()
        self.hist_value.setModel(self._hist_model)
        self.hist_value.setToolTip('Select the column to show histogram '
                                   'and statistics for.')
        self.hist_value.setVisible(False)

        resample_label = QtGui.QLabel('Resample:')
        self.resample_value = QtGui.QSpinBox()
        self.resample_value.setMinimum(1)
        self.resample_value.setMaximum(100000)
        self.resample_value.setToolTip('The step size used for resampling '
                                       'of large datasets.')
        resample_widget = QtGui.QWidget(self)
        resample_widget.setContentsMargins(2, 2, 2, 2)
        resample_layout = QtGui.QHBoxLayout()
        resample_layout.setContentsMargins(0, 0, 0, 0)
        resample_layout.addWidget(resample_label)
        resample_layout.addWidget(self.resample_value)
        resample_widget.setLayout(resample_layout)


        binning_label = QtGui.QLabel('Binning:')
        self.binning_value = QtGui.QSpinBox()
        self.binning_value.setValue(10)
        self.binning_value.setMinimum(1)
        self.binning_value.setMaximum(100000)
        self.binning_value.setToolTip('The number of bins used '
                                      'for the histogram.')
        binning_widget = QtGui.QWidget(self)
        binning_widget.setContentsMargins(2, 2, 2, 2)
        binning_layout = QtGui.QHBoxLayout()
        binning_layout.setContentsMargins(0, 0, 0, 0)
        binning_layout.addWidget(binning_label)
        binning_layout.addWidget(self.binning_value)
        binning_widget.setLayout(binning_layout)

        self._hist_label_action = plot_toolbar.addWidget(self.hist_label)
        self._hist_value_action = plot_toolbar.addWidget(self.hist_value)
        self._x_label_action = plot_toolbar.addWidget(self.x_label)
        self._x_value_action = plot_toolbar.addWidget(self.x_value)
        self._y_label_action = plot_toolbar.addWidget(self.y_label)
        self._y_value_action = plot_toolbar.addWidget(self.y_value)
        plot_toolbar.addSeparator()
        self.resample_action = plot_toolbar.addWidget(resample_widget)
        self.binning_action = plot_toolbar.addWidget(binning_widget)
        self.binning_action.setVisible(False)

        plot_toolbar.addSeparator()

        self.show_line_action = plot_toolbar.add_action(
            text='Show line plot',
            icon_name='actions/view-plot-line-symbolic.svg',
            tooltip_text='Show line plot',
            is_checkable=True,
            is_checked=True,
            is_exclusive=True,
            receiver=self._on_show_line,
            signal_type='toggled')

        self.show_hist_action = plot_toolbar.add_action(
            text='Show histogram',
            icon_name='actions/view-plot-hist-symbolic.svg',
            tooltip_text='Show histogram',
            is_checkable=True,
            is_exclusive=True,
            receiver=self._on_show_hist,
            signal_type='toggled')

        plot_toolbar.addStretch()

        # figure
        self.figure = Figure()
        self._set_figure_background_color()
        self.canvas = FigureCanvas(self.figure)
        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.StyledPanel)
        frame_layout = QtGui.QVBoxLayout()
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frame_layout)
        frame_layout.addWidget(self.canvas)
        policy = QtGui.QSizePolicy()
        policy.setHorizontalStretch(1)
        policy.setVerticalStretch(1)
        policy.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
        self.canvas.setSizePolicy(policy)
        self.canvas.setMinimumWidth(300)
        self.axes = self.figure.add_subplot(111)

        # Figure Layout
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(plot_toolbar)
        layout.addWidget(frame)

        # Default navigation toolbar for matplotlib
        self.mpl_toolbar = sywidgets.SyNavigationToolbar(self.canvas, self)
        layout.addWidget(self.mpl_toolbar)

        self.setLayout(layout)

        self._update_signal_comboboxes()

        self._timeout_after = 500
        self._update_plot_timer = QtCore.QTimer(self)
        self._update_plot_timer.setInterval(self._timeout_after)
        self._update_plot_timer.setSingleShot(True)

        self.hist_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.x_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.y_value.currentIndexChanged[int].connect(
            self._plot_selection_changed)
        self.y_value.selectedItemsChanged.connect(
            self._update_plot_timer.start)
        self.resample_value.valueChanged[int].connect(
            self._resample_value_changed)
        self.binning_value.valueChanged.connect(self._binning_value_changed)
        self._update_plot_timer.timeout.connect(self._update_plot)

        self.setMinimumWidth(500)

    def resizeEvent(self, event):
        super(ViewerPlot, self).resizeEvent(event)
        self._draw_canvas()

    def _set_figure_background_color(self):
        # FIXME: setting the correct facecolor for matplotlib figures embedded
        # in QTabWidgets doesn't work
        color = self.palette().color(self.backgroundRole())
        self.figure.set_facecolor(color.name())

    def _draw_canvas(self):
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _update_plot(self, redraw=True):
        table = self._model.table()
        if table is None:
            return
        if self._line_legend is not None:
            old_legend_loc = self._line_legend._loc
        else:
            old_legend_loc = 1
        self.axes.cla()  # clear plot

        # show line plots
        if self._line_plot_active:
            self._hist_label_action.setVisible(False)
            self._hist_value_action.setVisible(False)
            self._x_label_action.setVisible(True)
            self._x_value_action.setVisible(True)
            self._y_label_action.setVisible(True)
            self._y_value_action.setVisible(True)
            x_column_name = self.x_value.currentText()
            y_column_names = self.y_value.checkedItemNames()
            for y_column_name in y_column_names:
                self._plot_line(x_column_name, y_column_name)
            if len(y_column_names) == 1:
                y_attr = table.get_column_attributes(y_column_names[0])
                unit = y_attr.get('unit', None)
                y_label = six.text_type(y_column_names[0])
                if unit is not None:
                    y_label += ' [{}]'.format(unit)
                self.axes.set_ylabel(y_label)
            if len(self.axes.lines):
                self._line_legend = self.axes.legend(loc='upper left')
            else:
                self._line_legend = None
            if self._line_legend is not None:
                try:
                    self._line_legend.set_draggable(True, use_blit=True)
                except AttributeError:
                    # Assume use of older version.
                    self._line_legend.draggable(True, use_blit=True)

                # (Bene) not a good way to use private variables
                self._line_legend._loc = old_legend_loc
        else:
            # show histogram
            self._hist_label_action.setVisible(True)
            self._hist_value_action.setVisible(True)
            self._x_label_action.setVisible(False)
            self._x_value_action.setVisible(False)
            self._y_label_action.setVisible(False)
            self._y_value_action.setVisible(False)
            hist_column = self.hist_value.currentText()
            if hist_column:
                self._plot_hist(hist_column)
        if redraw:
            self._draw_canvas()

    def _plot_hist(self, y_column_name):
        table = self._model.table()
        row_slice = slice(0,
                          table.number_of_rows(),
                          int(self.resample_value.value()))
        y_data = table.get_column_to_array(y_column_name)[row_slice]
        y_dtype = table.column_type(y_column_name)
        text_params = collections.OrderedDict()

        if isinstance(y_data, np.ma.MaskedArray):
            # Count masked values, but never plot them.
            masked = np.count_nonzero(y_data.mask)
            y_data = y_data.compressed()
        else:
            masked = 0

        if y_dtype.kind in ['S', 'U', 'b']:
            # These data type can not be placed on a continuous axis.
            all_bin_labels, full_hist = np.unique(y_data, return_counts=True)
            if not self._binning_user_set:
                # 10 is the maximum number of bins for automatic binning
                bin_count = min(10, len(full_hist))
            else:
                bin_count = self.binning_value.value()

            # Sort and slice histogram
            hist = full_hist
            bin_labels = all_bin_labels
            if y_dtype.kind == 'b':
                # Always sort True before False
                if all_bin_labels[0] == False:
                    hist = full_hist[::-1]
                    bin_labels = all_bin_labels[::-1]
            else:
                # Sort other types by number of occurances
                sorted_ = sorted(zip(full_hist, all_bin_labels),
                                 key=operator.itemgetter(0), reverse=True)
                hist, bin_labels = zip(*sorted_[:bin_count])
                other = sum(h[0] for h in sorted_[bin_count:])
                if other > 0:
                    hist = list(hist) + [other]
                    bin_labels = list(bin_labels) + ["<other>"]

            x_data = np.arange(len(bin_labels))
            bin_width, rwidth = 1, 0.8
            padding = bin_width*(1 - rwidth)/2.0
            left = x_data - bin_width/2.0 + padding
            self.axes.bar(left, hist, width=rwidth)
            self.axes.set_xticks(x_data)
            self.axes.set_xticklabels(bin_labels)
            self.axes.set_xlim(x_data[0] - 0.5, x_data[-1] + 0.5)

            text_params['unique values'] = len(full_hist)
        elif y_dtype.kind in ['f', 'i', 'u', 'M']:
            # These data type can be placed on a continuous axis.
            if not self._binning_user_set:
                # 10 is the maximum number of bins for automatic binning
                bin_count = min(10, int(np.sqrt(len(y_data))))
            else:
                bin_count = self.binning_value.value()

            nan_count = None
            if y_dtype.kind == 'M':
                y_data = mdates.date2num(y_data.tolist())
            elif y_dtype.kind == 'f':
                nans = np.isnan(y_data)
                nan_count = np.count_nonzero(nans)
                y_data = y_data[np.logical_not(nans)]
            hist, bins = np.histogram(y_data, bin_count)
            width = bins[1] - bins[0]
            self.axes.bar(bins[:-1], hist, width=width)
            if y_dtype.kind == 'M':
                locator = mdates.AutoDateLocator()
                self.axes.xaxis.set_major_locator(locator)
                self.axes.xaxis.set_major_formatter(
                    mdates.AutoDateFormatter(locator))

            if y_dtype.kind == 'M':
                text_params['mean'] = six.text_type(
                    mdates.num2date(np.mean(y_data)))
                text_params['std'] = six.text_type(
                    datetime.timedelta(days=np.std(y_data)))
            else:
                text_params['mean'] = '{:.2e}'.format(np.nanmean(y_data))
                text_params['std'] = '{:.2e}'.format(np.nanstd(y_data))
            if y_dtype.kind == 'f':
                text_params['nan'] = nan_count

        text_params['masked'] = masked
        text = "\n".join(["{}: {}".format(k, v)
                          for k, v in text_params.items()])
        # TODO: make the textbox draggable like the legend in line plot
        text_box = offsetbox.TextArea(text)
        anchored_offset_box = offsetbox.AnchoredOffsetbox(loc=1,
                                                          child=text_box)
        self.axes.add_artist(anchored_offset_box)

    def _plot_line(self, x_column_name, y_column_name):
        table = self._model.table()
        column_names = table.column_names()
        resample_value = int(self.resample_value.value())
        row_slice = slice(0,
                          table.number_of_rows(),
                          resample_value)
        y_data = table.get_column_to_array(y_column_name)[row_slice]
        y_dtype = table.column_type(y_column_name)
        if x_column_name in column_names:
            x_data = table.get_column_to_array(x_column_name)[row_slice]
            x_dtype = table.column_type(x_column_name)
            x_attr = table.get_column_attributes(x_column_name)
        else:
            x_data = np.arange(0, table.number_of_rows(), resample_value)
            x_dtype = x_data.dtype
            x_attr = {}
        if len(x_data) == len(y_data):
            xdate = x_dtype.kind == 'M'
            ydate = y_dtype.kind == 'M'
            if xdate or ydate:
                if xdate:
                    x_data = x_data.astype(datetime.datetime)
                if ydate:
                    y_data = y_data.astype(datetime.datetime)
                self.axes.plot_date(x_data, y_data,
                                    'o', label=y_column_name,
                                    xdate=xdate, ydate=ydate)
                if xdate:
                    self.axes.get_figure().autofmt_xdate()
            else:
                self.axes.plot(x_data, y_data, 'o', label=y_column_name)
            unit = x_attr.get('unit', None)
            x_label = six.text_type(x_column_name)
            if unit is not None:
                x_label += ' [{}]'.format(unit)
            self.axes.set_xlabel(x_label)

    def _plot_selection_changed(self, idx):
        self._update_plot_timer.start()

    def _resample_value_changed(self, idx):
        self._update_plot_timer.start()

    def _binning_value_changed(self, idx):
        self._binning_user_set = True
        self._update_plot_timer.start()

    def _update_hist_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_HIST]
        current_selection = self.hist_value.currentText()
        self.hist_value.clear()
        self.hist_value.addItems(column_names)
        idx = 0
        if current_selection in column_names:
            idx = column_names.index(current_selection)
        self.hist_value.setCurrentIndex(idx)

    def _update_x_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_X]
        column_names = ['(index)'] + column_names
        current_selection = self.x_value.currentText()
        self.x_value.clear()
        self.x_value.addItems(column_names)
        idx = 0
        if current_selection in column_names:
            idx = column_names.index(current_selection)
        self.x_value.setCurrentIndex(idx)

    def _update_y_combobox(self):
        column_names = self._model.column_names()
        table = self._model.table()
        column_names = [name for name in column_names
                        if table.column_type(name).kind in VALID_AS_Y]
        current_selection = self.y_value.checkedItemNames()
        current_text = self.y_value.currentText()
        self.y_value.clear()
        for name in column_names:
            checked = name in current_selection
            self.y_value.add_item(name, checked)
        idx = 0
        if current_text in column_names:
            idx = column_names.index(current_text)
        self.y_value.setCurrentIndex(idx)

    def _update_signal_comboboxes(self):
        self._update_hist_combobox()
        self._update_x_combobox()
        self._update_y_combobox()

    def _on_show_line(self):
        self.show_line_action.setChecked(True)
        self.binning_action.setVisible(False)
        self.resample_action.setVisible(True)
        self._line_plot_active = True
        self._update_plot()

    def _on_show_hist(self):
        self.show_hist_action.setChecked(True)
        self.binning_action.setVisible(True)
        self.resample_action.setVisible(False)
        self._line_plot_active = False
        self._update_plot()

    def add_column_to_plot(self, column_name, as_y=True):
        if as_y:
            items = self._y_model.findItems(column_name)
            if len(items):
                idx = items[0].row()
                self.y_value.set_checked_state(idx, True)
            else:
                idx = -1
            self.y_value.setCurrentIndex(idx)
        else:
            items = self._x_model.findItems(column_name)
            if len(items):
                idx = items[0].row()
            else:
                idx = -1
            self.x_value.setCurrentIndex(idx)
        self._on_show_line()

    def show_stats_for(self, column_name):
        items = self._hist_model.findItems(column_name)
        if len(items):
            column_idx = items[0].row()
        else:
            column_idx = -1
        self.hist_value.setCurrentIndex(column_idx)
        self._on_show_hist()

    def set_max_data_points(self, value):
        self._max_data_points = int(value)

    def update_model(self, model):
        self._model = model
        table = self._model.table()
        # compute a staring value for re-sampling so the
        # number of points per line is not above self._max_data_points
        rows = self._model.rowCount(None)
        if rows > self._max_data_points:
            start_resample_value = int(round(rows / self._max_data_points))
            self.resample_value.setValue(start_resample_value)
        else:
            self.resample_value.setValue(1)
        self._update_signal_comboboxes()
        self._update_plot()
