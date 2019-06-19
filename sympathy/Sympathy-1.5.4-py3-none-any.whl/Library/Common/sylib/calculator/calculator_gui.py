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
import operator
import re
import six
import cgi
import ast
import datetime

from sympathy.api import qt, ParameterView
from sympathy.platform import widget_library as sywidgets
from sympathy.utils import search
from sylib.calculator import calculator_model as models
from sylib.calculator import plugins
from sympathy.platform import colors

from sympathy.platform.widget_library import BasePreviewTable

QtGui = qt.QtGui
QtCore = qt.QtCore


def init_tree(function_tree, input_columns_and_types=None):
    """Initialises the function tree widget with common functions with
    tooltips.

    Parameters
    ---------
    function_tree : OldTreeDragWidget
        Function tree widget.
    """
    function_tree.setDragEnabled(True)
    function_tree.setDropIndicatorShown(True)
    function_tree.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
    function_tree.setColumnCount(1)
    function_tree.headerItem().setHidden(True)

    def trailing_whitespace(expr):
        res = False
        for item in ast.walk(
                compile(expr, '<string>', 'eval', ast.PyCF_ONLY_AST)):
            if isinstance(item, ast.Str):
                s = item.s
                if re.search('\\s$', s):
                    res = True
                    break
        return res

    def _add_tree_item(parent, text, func_name, tool_tip,
                       warn_whitespace=False,
                       column=0):
        """Creates a new QtGui.QTreeWidgetItem and adds it as child to parent.

        Parameters:
        -----------
        parent : QtGui.QTreeWidgetItem
            The parent QtGui.QTreeWidgetItem node.
        column : int
            The column the text should be placed in.
        text : string
            The node text
        func_name : string
            The method syntax
        tool_tip : string
            The text at the tooltip

        Returns
        --------
        QtGui.QTreeWidgetItem
            The new QtGui.QTreeWidgetItem node.
        """
        item = QtGui.QTreeWidgetItem(parent)
        item.setText(column, text)
        item.setData(0, QtCore.Qt.UserRole, func_name)
        if warn_whitespace:
            item.setBackground(column, QtGui.QBrush(colors.WARNING_BG_COLOR))
            item.setToolTip(
                column,
                '{}\n'
                'Warning, this input contains whitespace at the end.'
                .format(tool_tip))
        else:
            item.setToolTip(column, tool_tip)

        parent.addChild(item)
        return item

    def build_tree(root, content):
        if isinstance(content, list):
            for item in content:
                _add_tree_item(root, *item)
        elif isinstance(content, dict):
            for tree_text, subcontent in six.iteritems(content):
                subroot = QtGui.QTreeWidgetItem(root)
                subroot.setText(0, tree_text)
                build_tree(subroot, subcontent)
        else:
            raise TypeError("Plugin gui dict contained unsupported object "
                            "type: {}".format(type(gui_dict)))

    def purge_hidden_items(gui_dict, hidden_items):
        """
        Create a new gui_dict without the items in hidden_items.

        hidden_items should be a list of tuples with the "paths" in the
        gui_dict that should be hidden.
        """
        if not hidden_items:
            return gui_dict

        # The items that should be hidden on this level in the tree
        current_hidden = [item[0] for item in hidden_items if len(item) == 1]

        if isinstance(gui_dict, list):
            # Hide some items
            new_gui_dict = [item for item in gui_dict
                            if item[0] not in current_hidden]
        elif isinstance(gui_dict, dict):
            new_gui_dict = {}
            for subtree_label, subtree in six.iteritems(gui_dict):
                if subtree_label in current_hidden:
                    # Hide this subtree
                    continue

                new_hidden = [item[1:] for item in hidden_items
                              if item[0] == subtree_label]
                new_gui_dict[subtree_label] = purge_hidden_items(
                    subtree, new_hidden)
        else:
            raise TypeError("Plugin gui dict contained unsupported object "
                            "type: {}".format(type(gui_dict)))
        return new_gui_dict

    if input_columns_and_types:
        available_signals = {
            'Signals': [[name, name, 'Signal: {}\nType: {}'.format(
                name, dtype), trailing_whitespace(name)]
                        for name, dtype in input_columns_and_types]}

        build_tree(function_tree, available_signals)

    available_plugins = sorted(plugins.available_plugins('python'),
                               key=operator.attrgetter("WEIGHT"))

    hidden_items = []
    for plugin in available_plugins:
        hidden_items.extend(plugin.hidden_items())
    for plugin in available_plugins:
        gui_dict = purge_hidden_items(plugin.gui_dict(), hidden_items)
        build_tree(function_tree, gui_dict)


class PreviewTable(BasePreviewTable):
    def __init__(self, parent=None):
        super(PreviewTable, self).__init__(parent)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def scroll_to_column(self, column):
        self.scrollTo(self.model().index(0, column))


class ToolbarMixin(object):
    def __init__(self, *args, **kwargs):
        super(ToolbarMixin, self).__init__(*args, **kwargs)
        toolbar = sywidgets.SyToolBar(self)
        toolbar.setIconSize(QtCore.QSize(18, 18))
        toolbar.add_action('Add',
                           'actions/list-add-symbolic.svg',
                           'Add column',
                           receiver=self.add_item)
        toolbar.add_action('Remove',
                           'actions/list-remove-symbolic.svg',
                           'Remove column',
                           receiver=self.remove_item)
        toolbar.add_action('Copy',
                           'actions/edit-copy-symbolic.svg',
                           'Copy column',
                           receiver=self.copy_item)

        toolbar.addStretch()
        toolbar.add_action('Move up',
                           'actions/go-up-symbolic.svg',
                           'Move row up',
                           receiver=self.move_item_up)
        toolbar.add_action('Move down',
                           'actions/go-down-symbolic.svg',
                           'Move row down',
                           receiver=self.move_item_down)
        self._toolbar = toolbar


class AttributeTableWidget(ToolbarMixin, QtGui.QWidget):
    def __init__(self):
        super(AttributeTableWidget, self).__init__()
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self._table = QtGui.QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Name', 'Value'])
        self._table_model = self._table.model()
        # self.setStyleSheet("QTableWidget {border: 0px;}")
        layout.addWidget(self._table)
        layout.addWidget(self._toolbar)
        self.setLayout(layout)

    def add_item(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        for col in [0, 1]:
            new_item = QtGui.QTableWidgetItem()
            self._table.setItem(row, col, new_item)

        self._table.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(row + 1)])

    def remove_item(self):
        rows = {item.row() for item in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            self._table.removeRow(row)

    def copy_item(self):
        index = self._table.currentIndex()
        row = index.row()
        if index.row() < 0:
            return
        items = [self._table.itemFromIndex(
            self._table_model.index(row, col)) for col in [0, 1]]

        self._table.insertRow(row + 1)
        self._table.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._table.rowCount())])

        for old_item, col in zip(items, [0, 1]):
            new_item = QtGui.QTableWidgetItem()
            new_item.setText(old_item.text())
            self._table.setItem(row + 1, col, new_item)

    def move_item_up(self):
        self._move_item(-1)

    def move_item_down(self):
        self._move_item(1)

    def _move_item(self, direction):
        index = self._table.currentIndex()
        row = index.row()
        if direction > 0 and row == self._table_model.rowCount() - 1:
            return
        elif direction < 0 and row == 0:
            return

        old_row_data = [(col, self._table.takeItem(row + direction, col))
                        for col in [0, 1]]

        new_row_data = [(col, self._table.takeItem(row, col))
                        for col in [0, 1]]

        for col, item in new_row_data:
            self._table.setItem(row + direction, col, item)

        for col, item in old_row_data:
            self._table.setItem(row, col, item)

        selection_model = self._table.selectionModel()
        selected_indices = self._table.selectedIndexes()
        index = self._table.currentIndex()
        selection_model.setCurrentIndex(
            self._table_model.index(index.row() + direction, index.column()),
            QtGui.QItemSelectionModel.Clear |
            QtGui.QItemSelectionModel.Current)
        for index in selected_indices:
            selection_model.setCurrentIndex(
                self._table_model.index(
                    index.row() + direction, index.column()),
                QtGui.QItemSelectionModel.Select)

    @property
    def attributes(self):
        return [
            (self._table.item(row, 0).text(), self._table.item(row, 1).text())
            for row in range(self._table_model.rowCount())]

    @attributes.setter
    def attributes(self, items):
        for _ in range(self._table_model.rowCount()):
            self._table.removeRow(0)
        for row, (key, value) in enumerate(items):
            self._table.insertRow(row)
            for col, text in zip([0, 1], [key, value]):
                new_item = QtGui.QTableWidgetItem()
                new_item.setText(text)
                self._table.setItem(row, col, new_item)
        self._table.setVerticalHeaderLabels(
            [six.text_type(i) for i in range(self._table_model.rowCount())])


class SignalTableWidget(QtGui.QTableWidget):
    def __init__(self, parent=None):
        super(SignalTableWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self._format = '{}'
        self._mime_data = None

        self.setColumnCount(2)
        # self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setHorizontalHeaderLabels(['Name', 'Type'])
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Interactive)
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def sizeHintForColumn(self, column):
        """Override this method to only check width of first 20 rows."""
        max_width = 0
        for row in range(min(self.rowCount(), 20)):
            size = self.item(row, column).sizeHint()
            if size.isValid():
                max_width = max(size.width(), max_width)
            else:
                size = self.itemDelegate().sizeHint(
                    self.viewOptions(),
                    self.indexFromItem(self.item(row, column)))
                if size.isValid():
                    max_width = max(size.width(), max_width)
        return max_width or 80

    def current_items(self):
        selection_model = self.selectionModel()
        indexes = selection_model.selectedIndexes()
        return [self.itemFromIndex(i) for i in indexes if i.column() == 0]

    def get_items(self):
        return (self.item(r, 0) for r in range(self.rowCount()))

    def set_format(self, format_):
        self._format = format_

    def mimeTypes(self):
        return ['text/plain']

    def mimeData(self, items):
        data = ''.join([self._format.format(item.text()) for item in items
                        if item.column() == 0])
        self._mime_data = QtCore.QMimeData()
        self._mime_data.setData('text/plain', data.encode('utf8'))
        return self._mime_data


class TreeDragWidget(QtGui.QTreeWidget):
    """Extends QtGui.QTreeWidget and lets it use drag and drop."""

    def __init__(self, parent=None):
        super(TreeDragWidget, self).__init__(parent)
        self._mime_data = None
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)

    def mimeTypes(self):
        return ['function/plain']

    def mimeData(self, items):
        tree_item = items[0]
        if tree_item.childCount() == 0:
            data = tree_item.data(0, QtCore.Qt.UserRole)
            # TODO: Perhaps a good idea, but I don't like the implementation
            # if '(' not in data:
            #     data = tree_item.text(0)
            self._mime_data = QtCore.QMimeData()
            self._mime_data.setData('function/plain', data.encode('utf8'))
            return self._mime_data


class CalcFieldWidget(QtGui.QPlainTextEdit):
    insert_function = QtCore.Signal(six.text_type)
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
        super(CalcFieldWidget, self).__init__(parent=parent)
        # This should select the systems default monospace font
        f = QtGui.QFont('')
        f.setFixedPitch(True)
        self.setFont(f)

        self.setTabChangesFocus(True)
        self.setUndoRedoEnabled(True)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)

    def canInsertFromMimeData(self, source):
        if source.hasFormat('function/plain'):
            return True
        else:
            res = super(CalcFieldWidget, self).canInsertFromMimeData(source)
            return res

    def insertFromMimeData(self, source):
        if source.hasFormat('function/plain'):
            data = source.data('function/plain').data()
            text = data.decode('utf8')
            self.insert_function.emit(text)
        else:
            super(CalcFieldWidget, self).insertFromMimeData(source)
        self.editingFinished.emit()


class TableDragMixin(object):
    def __init__(self, *args, **kwargs):
        """
        Generic mixin class for enabling dragging in a QTableView
        subclass.

        Parameters
        ----------
        drag_cols : iterable of int
            Column indices where drag should be enabled.

        drag_mode : PySide.QtCore.Qt.DropAction
            Drag mode to use.
        """
        drag_cols = kwargs.pop('drag_cols', [])
        drag_mode = kwargs.pop('drag_mode', None)

        if drag_mode is None:
            drag_mode = QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

        self._drag_index = None
        self._dragging = False
        self._drag_mode = drag_mode
        self._drag_cols = set(drag_cols)
        super(TableDragMixin, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            drag_index = None
            if index.isValid() and index.column() in self._drag_cols:
                drag_index = index
            self._drag_index = drag_index
        return super(TableDragMixin, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_index = None
        return super(TableDragMixin, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if not self._dragging and self._drag_index:
            self._dragging = True
            try:
                # Create new drag and render items on row to use as image
                # (pixmap) while dragging.
                drag = QtGui.QDrag(self)
                row = self._drag_index.row()
                visual_rect = self.visualRect(self._drag_index)
                for i in range(self.model().rowCount()):
                    row_index = self._drag_index.sibling(row, i)
                    if row_index.isValid():
                        visual_rect = visual_rect.united(
                            self.visualRect(row_index))

                pixmap = QtGui.QPixmap(visual_rect.size())
                self.render(pixmap, QtCore.QPoint(0, 0),
                            visual_rect.translated(
                                self.verticalHeader().width(),
                                self.horizontalHeader().height()))
                mime_data = self._row_mime_data(row)
                drag.setMimeData(mime_data)
                drag.setPixmap(pixmap)
                drag.exec_(self._drag_mode)
                event.accept()
            finally:
                self._dragging = False
        else:
            return super(TableDragMixin, self).mouseMoveEvent(event)

    def _row_mime_data(self, row):
        """
        Mime data for dragged row.

        Parameters
        ----------
        row : int
            Row index.

        Returns
        -------
        QtCore.QMimeData
            Mime data for row.
        """
        raise NotImplementedError(
            'Inheriting class needs to implement _row_mime_data.')


class ModelTableView(TableDragMixin, QtGui.QTableView):
    current_row_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(ModelTableView, self).__init__(drag_cols=[3], parent=parent)
        self.verticalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def setModel(self, model):
        super(ModelTableView, self).setModel(model)
        selection_model = self.selectionModel()
        selection_model.currentRowChanged.connect(self.current_row_changed)

    def item_added(self, index):
        if index.isValid():
            self.setCurrentIndex(index)

    def current_item(self):
        index = self.currentIndex()
        if not index.isValid():
            return None
        if index.column() == 0:
            item = self.model().itemFromIndex(index)
        else:
            item = self.model().item(index.row(), 0)
        return item

    def _row_mime_data(self, row):
        mime_data = QtCore.QMimeData()
        data = "res['{}']".format(self.model().itemFromIndex(
            self._drag_index.sibling(row, 0)).name)
        mime_data.setData('text/plain', data.encode('utf8'))
        return mime_data


class CalculatorModelView(ToolbarMixin, QtGui.QWidget):
    new_item_added = QtCore.Signal()

    def __init__(self, model, parent=None):
        super(CalculatorModelView, self).__init__(parent=parent)

        assert(isinstance(model, models.CalculatorItemModel))
        self._model = model

        self.view = ModelTableView(parent=self)

        self.view.setModel(self._model)

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        layout.addWidget(self._toolbar)
        self.setLayout(layout)

        # Workaround to get correct header looks when loading parameters
        # and when creating a new calculator node.
        self.add_item()
        self.remove_item()

        self.view.setColumnWidth(2, 30)
        self.view.setColumnWidth(3, 15)
        self.view.horizontalHeader().moveSection(2, 0)
        self.view.horizontalHeader().moveSection(3, 0)
        self.view.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.view.setWordWrap(False)

    def add_item(self):
        item = self._model.add_item()
        self.view.setCurrentIndex(item.index())
        self.new_item_added.emit()

    def remove_item(self):
        current_selected_index = self.view.currentIndex()
        self._model.remove_item(current_selected_index.row())

    def copy_item(self):
        current_selected_index = self.view.currentIndex()
        self._model.copy_item(current_selected_index.row())

    def move_item_up(self):
        self._move_item(-1)

    def move_item_down(self):
        self._move_item(1)

    def _move_item(self, direction):
        index = self.view.currentIndex()
        row = index.row()
        if direction > 0 and row == self._model.rowCount() - 1:
            return
        elif direction < 0 and row == 0:
            return
        items_row = self._model.takeRow(row)
        self._model.insertRow(row + direction, items_row)
        selection_model = self.view.selectionModel()
        selection_model.setCurrentIndex(
            items_row[0].index(),
            QtGui.QItemSelectionModel.ClearAndSelect |
            QtGui.QItemSelectionModel.Rows)
        items_row[0].emitDataChanged()


class ItemEditBox(QtGui.QGroupBox):

    def __init__(self, *args, **kwargs):
        super(ItemEditBox, self).__init__(*args, **kwargs)
        self._item = None
        self.highlighter = None
        self._init_gui()
        self.highlighter = sywidgets.PygmentsHighlighter(
            self.calc_field, 'python')
        self.calc_field.textChanged.connect(self.highlighter.rehighlight)

        self.calc_timer = QtCore.QTimer()
        self.calc_timer.setInterval(1500)  # 1s timeout before calc runs
        self.calc_timer.setSingleShot(True)

    def _setup_name_colouring(self):
        normal_palette = QtGui.QPalette()
        normal_palette.setColor(QtGui.QPalette.Base, colors.DEFAULT_BG_COLOR)
        normal_palette.setColor(QtGui.QPalette.Text, colors.DEFAULT_TEXT_COLOR)

        warning_palette = QtGui.QPalette()
        warning_palette.setColor(QtGui.QPalette.Base, colors.WARNING_BG_COLOR)
        warning_palette.setColor(
            QtGui.QPalette.Text, colors.WARNING_TEXT_COLOR)

        def update_column_name_color(new_name, editor=self.column_name):
            if re.search("\s$", new_name):
                self.column_name.setPalette(warning_palette)
                self.column_name.setToolTip(
                    'Warning, this column name contains whitespace at the end')
            else:
                self.column_name.setPalette(normal_palette)
                self.column_name.setToolTip('')
        self.column_name.setPalette(normal_palette)
        self.column_name.textChanged.connect(update_column_name_color)

    def _init_gui(self):
        self.column_name = QtGui.QLineEdit('')
        self.column_name.setPlaceholderText('Column name')
        self._setup_name_colouring()

        tabs = QtGui.QTabWidget(parent=self)
        self.calc_field = CalcFieldWidget()
        self.attr_table = AttributeTableWidget()
        tabs.addTab(self.calc_field, 'Calculation')
        tabs.addTab(self.attr_table, 'Attributes')

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.column_name)
        layout.addWidget(tabs)
        self.setLayout(layout)

        self.setTabOrder(self.column_name, self.calc_field)

    def set_item(self, item):

        if self._item is not None:
            self.save_parameters()
            self.column_name.textChanged.disconnect(self.column_name_changed)
            self.calc_field.textChanged.disconnect(self.calc_line_changed)
        self._item = item

        if item is not None:
            self.attr_table.attributes = item.attributes[:]
            self.column_name.setText(self._item.name)
            self.calc_field.setPlainText(self._item.expr)
            self.column_name.textChanged.connect(self.column_name_changed)
            self.calc_field.textChanged.connect(self.calc_line_changed)
        else:
            self.attr_table.attributes = []
            self.column_name.setText('')
            self.calc_field.setPlainText('')

    def column_name_changed(self):
        if self._item is not None:
            self._item.name = self.column_name.text()

    def calc_line_changed(self):
        if self._item is not None:
            self._item.expr = self.calc_field.toPlainText()

        if not self.calc_timer.isActive():
            self.calc_timer.start()
        else:
            self.calc_timer.stop()
            self.calc_timer.start()

    def save_parameters(self):
        if self._item is not None:
            self._item.attributes[:] = self.attr_table.attributes


class CalculatorWidget(ParameterView):
    def __init__(self, in_data, parameters,
                 preview_calculator=None, parent=None,
                 multiple_input=False, empty_input=False,
                 show_copy_input=False):
        super(CalculatorWidget, self).__init__(parent=parent)
        self._status_message = ''
        self._multiple_input = multiple_input
        if multiple_input:
            self._in_tables = in_data
        else:
            self._in_tables = []
            self._in_tables.append(in_data)

        self._parameter_root = parameters
        self.model = models.CalculatorItemModel(
            self._in_tables, parameters,
            preview_calculator=preview_calculator,
            empty_input=empty_input)
        self.preview_model = (
            PreviewModel(self.model) if preview_calculator else None)
        self.view_model = CalculatorModelView(self.model)
        self.model_view = self.view_model.view
        self.preview_view = PreviewTable()

        # edit signal widgets
        self.current_column = ItemEditBox('Edit Signal')
        self.function_tree = TreeDragWidget()
        self.search_field = sywidgets.ClearButtonLineEdit(
            placeholder='Search for signal or function')
        self.tree_head = None

        self.preview_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.preview_view.setModel(self.preview_model)
        hsplitter = QtGui.QSplitter()
        hsplitter.setOpaqueResize(QtCore.Qt.Horizontal)
        hsplitter.setContentsMargins(0, 0, 0, 0)
        hsplitter.addWidget(self.view_model)
        preview_view = PreviewTable()
        preview_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        preview_view.setModel(self.preview_model)

        # function widget
        function_label = QtGui.QLabel("Signals and Common functions")
        self.function_tree.setMaximumWidth(2000)
        function_tree_layout = QtGui.QVBoxLayout()
        function_tree_layout.setContentsMargins(0, 0, 0, 0)
        function_tree_layout.setSpacing(5)
        function_tree_layout.addWidget(function_label)
        function_tree_layout.addWidget(self.function_tree)
        function_tree_layout.addWidget(self.search_field)
        functions_widget = QtGui.QWidget()
        functions_widget.setLayout(function_tree_layout)
        hsplitter.addWidget(functions_widget)

        # add widgets to global vsplitter
        vsplitter = QtGui.QSplitter()
        vsplitter.setOrientation(QtCore.Qt.Vertical)
        vsplitter.setContentsMargins(0, 0, 0, 0)
        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.current_column)
        vsplitter.addWidget(self.preview_view)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(vsplitter)
        copy_input_gui = self._parameter_root['copy_input'].gui()
        if self._multiple_input:
            hlayout = QtGui.QHBoxLayout()
            hlayout.setContentsMargins(0, 0, 0, 0)
            if show_copy_input:
                hlayout.addWidget(copy_input_gui)
            layout.addLayout(hlayout)

        else:
            if show_copy_input:
                layout.addWidget(copy_input_gui)
        layout.addWidget(self._parameter_root['fail_strategy'].gui())
        self.setLayout(layout)

        self.model_view.current_row_changed.connect(self.update_current_item)
        self.function_tree.itemDoubleClicked.connect(self.insert_function)
        self.search_field.textChanged.connect(self.search_function)
        self.current_column.calc_field.insert_function.connect(
            self.insert_text)
        self.model.data_ready.connect(self.status_changed)
        self.model.item_dropped.connect(self.model_view.item_added)

        if not self.model.rowCount():
            self.model.add_item()

        if self.model_view.model().rowCount():
            selection_model = self.model_view.selectionModel()
            first_idx = self.model_view.model().index(0, 0)
            selection_model.select(first_idx,
                                   QtGui.QItemSelectionModel.ClearAndSelect |
                                   QtGui.QItemSelectionModel.Rows)

        for idx, (cname, dtype) in enumerate(
                self.model.input_columns_and_types):
            name_item = QtGui.QTableWidgetItem(models.display_calculation(
                cname))
            type_item = QtGui.QTableWidgetItem(dtype)
            if re.search("\s'(\).data|\])$", cname):
                name_item.setBackground(QtGui.QBrush(colors.WARNING_BG_COLOR))
                name_item.setToolTip(
                    'Warning, this column name contains whitespace at the end')
            for item in [name_item, type_item]:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)

        self.model_view.setCurrentIndex(self.model.index(0, 0))
        self.update_current_item()

        # init function tree
        init_tree(self.function_tree, self.model.input_columns_and_types)
        self.tree_head = self.function_tree.invisibleRootItem()

    def save_parameters(self):
        self.current_column.save_parameters()
        self.model.save_parameters()

    def cleanup(self):
        self.model.cleanup_preview_worker()

    @property
    def valid(self):
        status, self._status_message = self.model.validate()
        return status

    @property
    def status(self):
        if self._status_message:
            return '<p>{}</p>'.format(
                cgi.escape(six.text_type(self._status_message)))
        return ''

    def insert_function(self, item):
        text = item.data(0, QtCore.Qt.UserRole)
        self.insert_text(text)

    def insert_text(self, text):
        if text:
            text = models.display_calculation(text)
            # TODO(erik): if we sometime choose to implement some way of
            # selecting signals and operations at the same time, we can use:
            # selected_items = [...] to automatically insert the selected
            # signals into functions.
            selected_items = []
            signal0 = '${signal0}'
            signal1 = '${signal1}'
            if signal0 in text:
                if len(selected_items):
                    item = selected_items[0]
                    signal = item.text()
                    text = text.replace(signal0, signal)
            if signal1 in text:
                if len(selected_items) >= 2:
                    item = selected_items[1]
                    signal = item.text()
                    text = text.replace(signal1, signal)

            # For signals 0-25 replace with letters from a-z.
            ordz = ord('z')
            for n in list(re.findall('\\${signal([0-9]+)}', text)):
                n = int(n)
                ll = n + ord('a')
                if ll <= ordz:
                    text = text.replace('${signal%s}' % n, six.unichr(ll))
            self.current_column.calc_field.insertPlainText(text)

    def update_current_item(self):
        item = self.model_view.current_item()
        self.current_column.set_item(item)
        if item is not None:
            self.preview_view.scroll_to_column(item.row())

    def search_function(self):
        def recursive_hide(node, pattern, word):
            # Using fuzzy pattern against the text and exact pattern against
            # tooltip. Fuzzy matching against long docstring can produce
            # surprising matches especially since there is no direct feedback.
            status = 0
            if node.childCount() < 1:
                # This is a leave
                text = node.text(0)
                data = node.data(0, QtCore.Qt.UserRole)
                if not (search.matches(pattern, text) or
                        word in data):
                    status = 1
            else:
                count = 0
                for index in range(0, node.childCount()):
                    count += recursive_hide(node.child(index), pattern, word)
                if count == node.childCount():
                    # All children are hidden
                    status = 1

            node.setHidden(status)
            node.setExpanded(~status)
            if not pattern:
                node.setExpanded(status)

            return status

        term = self.search_field.text()
        pattern = search.fuzzy_pattern(term)
        recursive_hide(self.tree_head, pattern, term)


class PreviewModel(QtCore.QAbstractTableModel):
    def __init__(self, source_model, parent=None):
        super(PreviewModel, self).__init__(parent=parent)

        assert(isinstance(source_model, models.CalculatorItemModel))
        self.source_model = source_model

        self.source_model.dataChanged.connect(self.update_model)
        self.source_model.data_ready.connect(self.modelReset)

    def update_model(self, topleft_index, bottomright_index):
        if topleft_index.parent() == bottomright_index.parent():
            self.modelReset.emit()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            item = self.source_model.item(section)
            if role == QtCore.Qt.DisplayRole:
                return item.name
            elif role == QtCore.Qt.ToolTipRole:
                return item.name
            elif role == QtCore.Qt.TextAlignmentRole:
                return QtCore.Qt.AlignLeft
            elif role == QtCore.Qt.BackgroundRole:
                if item.valid:
                    return None
                else:
                    return colors.DANGER_BG_COLOR  # redish color
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                return six.text_type(section)

        return super(PreviewModel, self).headerData(section, orientation, role)

    def rowCount(self, qmodel_index=None):
        source_items = self.source_model.items()
        columns_len = [len(item._column_data) for item in source_items]
        if columns_len:
            row_count = max(columns_len)
        else:
            row_count = 0
        return row_count

    def columnCount(self, qmodel_index=None):
        return self.source_model.rowCount()

    def data(self, qmodel_index, role=QtCore.Qt.DisplayRole):

        def cell_format(data):
            # TODO: Share with other previews in library.
            try:
                data = data.tolist()
            except AttributeError:
                pass

            if isinstance(data, datetime.datetime):
                data = data.isoformat()
            elif isinstance(data, six.binary_type):
                # repr will show printable ascii characters as usual
                # but will replace any non-ascii or non-printable
                # characters with an escape sequence. The slice
                # removes the quotes added by repr.
                if six.PY2:
                    data = repr(data)[1:-1]
                else:
                    data = repr(data)[2:-1]
            else:
                data = six.text_type(data)
            return data

        if not qmodel_index.isValid():
            return None
        row = qmodel_index.row()
        col = qmodel_index.column()
        column_item = self.source_model.item(col)
        data = column_item._column_data
        try:
            display_data = data[row]
        except IndexError:
            display_data = ''
        if role == QtCore.Qt.DisplayRole:
            return cell_format(display_data)
        elif role == QtCore.Qt.ToolTipRole:
            if display_data is not None:
                return cell_format(display_data)
            else:
                return ''
        elif role == QtCore.Qt.BackgroundRole:
            if not column_item.valid or column_item.duplicate:
                return colors.DANGER_BG_COLOR
            elif column_item.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
        return None

    def flags(self, qmodel_index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
