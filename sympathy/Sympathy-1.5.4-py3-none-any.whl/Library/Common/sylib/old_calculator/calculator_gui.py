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
import keyword
import operator
import re
import tokenize
import io
import six
import cgi
from six.moves import builtins

from sympathy.api import table, qt, ParameterView
from sympathy.platform.table_viewer import fuzzy_list_filter
from sympathy.platform import widget_library as sywidgets
from sylib.old_calculator import calculator_model as models
from sylib.calculator import plugins
from sympathy.platform import colors

from sympathy.platform.widget_library import BasePreviewTable

QtGui = qt.QtGui
QtCore = qt.QtCore

if six.PY2:
    DOLLAR_SIGN = b'$'
    LEFT_CURLY_BRACKET = b'{'
    RIGHT_CURLY_BRACKET = b'}'
else:
    DOLLAR_SIGN = '$'
    LEFT_CURLY_BRACKET = '{'
    RIGHT_CURLY_BRACKET = '}'


class PythonHighlight(QtGui.QSyntaxHighlighter):
    def __init__(self, *args, **kwargs):
        super(PythonHighlight, self).__init__(*args, **kwargs)
        self._tokens = []
        self._highlighting = False

    def _format(self, token_type):
        base01 = QtGui.QColor("#586e75")  # Optional emphasized content  # noqa
        base00 = QtGui.QColor("#657b83")  # Body text / main content
        base1 = QtGui.QColor("#93a1a1")  # Comments / secondary content
        base2 = QtGui.QColor("#eee8d5")  # Background highlights         # noqa
        base3 = QtGui.QColor("#fdf6e3")  # Background                    # noqa
        yellow = QtGui.QColor("#b58900")
        orange = QtGui.QColor("#cb4b16")
        red = QtGui.QColor("#dc322f")
        magenta = QtGui.QColor("#d33682")                                # noqa
        violet = QtGui.QColor("#6c71c4")                                 # noqa
        blue = QtGui.QColor("#268bd2")                                   # noqa
        cyan = QtGui.QColor("#2aa198")
        green = QtGui.QColor("#859900")

        COLORS = {      # noqa
            'other': base00,
            'keyword': orange,
            'builtin': yellow,
            'column': green,
            tokenize.ERRORTOKEN: red,
            tokenize.STRING: orange,
            tokenize.NUMBER: cyan,
            tokenize.COMMENT: base1,
            tokenize.AT: green}

        f = QtGui.QTextCharFormat()
        try:
            f.setForeground(COLORS[token_type])
        except KeyError:
            f.setForeground(COLORS['other'])

        return f

    def _tokenize_document(self):
        if six.PY2:
            get_tokens = tokenize.generate_tokens
            encoding = 'latin1'
        else:
            get_tokens = tokenize.tokenize
            encoding = 'utf-8'
        s = io.BytesIO(self.document().toPlainText().encode(encoding))
        for token in get_tokens(s.readline):
            self._add_token(tuple(token))

    def _add_token(self, token):
        # skipping line.
        self._tokens.append(token[:4])

    def _start_and_length(self, tstart, tend, lines):
        block_start_row = self.previousBlockState() + 1
        tstart_row, tstart_col = tstart
        tend_row, tend_col = tend

        if tstart_row < block_start_row:
            # Token starts before this text block
            start_pos = 0
        elif tstart_row > block_start_row + len(lines):
            # Entire token is after this text block
            return None, None
        else:
            # Token end is inside this text block
            start_pos = 0
            for i, line in enumerate(lines, 1):
                if tstart_row > block_start_row + i:
                    start_pos += len(line)
                elif tstart_row == block_start_row + i:
                    start_pos += tstart_col

        if tend_row < block_start_row:
            # Entire token is before this text block
            return None, None
        elif tend_row > block_start_row + len(lines):
            # Token ends after this text block
            length = sum([len(line) for line in lines]) - start_pos
        else:
            # Token end is inside this text block
            end_pos = 0
            for i, line in enumerate(lines, 1):
                if tend_row > block_start_row + i:
                    end_pos += len(line)
                elif tend_row == block_start_row + i:
                    end_pos += tend_col
            length = end_pos - start_pos

        # The line with this position is not in this text block
        return start_pos, length

    def rehighlight(self):
        # Prevent highlighting calling itself
        if self._highlighting:
            return
        self._highlighting = True

        try:
            self._tokenize_document()
        except tokenize.TokenError:
            pass
        super(PythonHighlight, self).rehighlight()
        self._highlighting = False

    def highlightBlock(self, text):
        skip_to_pos = -1
        lines = text.split('\n')

        for token in self._tokens:
            token_type, token_text, tstart, tend = token
            start, length = self._start_and_length(tstart, tend, lines)
            if start is None or length is None:
                # This token is in another text block
                continue
            if start < skip_to_pos:
                # This token has already been taken care of
                continue

            # The column syntax ${mycol} isn't known to the tokenize module.
            # It also spans several tokens so it needs to be treated
            # separately.
            if (token_text == DOLLAR_SIGN and
                    text[start + 1:start + 2] == LEFT_CURLY_BRACKET):
                match = re.search(RIGHT_CURLY_BRACKET, text[start:])
                if match:
                    token_type = 'column'
                    length = match.start() + 1
                    skip_to_pos = start + length

            # The tokenize module doesn't distinguish between different types
            # of names.
            if token_type == tokenize.NAME:
                if keyword.iskeyword(token_text):
                    token_type = 'keyword'
                elif hasattr(builtins, token_text):
                    token_type = 'builtin'

            self.setFormat(start, length, self._format(token_type))

        self.setCurrentBlockState(self.previousBlockState() + len(lines))


def init_tree(function_tree, backend, generic):
    """Initialises the function tree widget with common functions with
    tooltips.

    Parameters
    ---------
    function_tree : OldTreeDragWidget
        Function tree widget.
    backend : str or unicode
        Name of the backend. Either 'matlab' or 'python'.
        :param generic:
    """
    function_tree.setDragEnabled(True)
    function_tree.setDropIndicatorShown(True)
    function_tree.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
    function_tree.setColumnCount(1)
    function_tree.headerItem().setHidden(True)

    def build_tree(root, content):
        if isinstance(content, list):
            for tree_text, eval_string, doc_string in content:
                _add_tree_item(root, tree_text, doc_string, eval_string)
        elif isinstance(content, dict):
            for tree_text, subcontent in six.iteritems(content):
                subroot = QtGui.QTreeWidgetItem(root)
                subroot.setText(0, tree_text)
                build_tree(subroot, subcontent)
        else:
            raise TypeError("Content contained ")

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

    available_plugins = sorted(plugins.available_plugins(backend),
                               key=operator.attrgetter("WEIGHT"))

    hidden_items = []
    if backend == 'python':
        for plugin in available_plugins:
            hidden_items.extend(plugin.hidden_items())
    for plugin in available_plugins:
        plugin_dict = plugin_placeholder(plugin.gui_dict(), generic)
        plugin_dict = purge_hidden_items(plugin_dict, hidden_items)
        build_tree(function_tree, plugin_dict)


def plugin_placeholder(plugin_dict, generic):
    """Replaces placeholders in plugins

    Parameters
    ---------
    plugin_dict : Dict
        Dictionary with plugins
    generic : bool
        True is calculator input is generic else False.
    Returns
    --------
    dicts : Dict
        Updated plugin dictionary
    """
    if generic:
        ph1 = "arg.col('signal0').data"
        ph2 = "arg.col('signal1').data"
    else:
        ph1 = "${signal0}"
        ph2 = "${signal1}"

    def go_deep(in_dict, my_dict):
        if isinstance(in_dict, list):
            b = []
            for idx in range(0, len(in_dict)):
                word = in_dict[idx][1].replace('${signal0}', ph1)
                word = word.replace('${signal1}', ph2)
                b.append((in_dict[idx][0], word, in_dict[idx][2]))
            return b
        else:
            for a in in_dict:
                my_dict[a] = go_deep(in_dict[a], {})
            return my_dict

    dicts = go_deep(plugin_dict, {})
    return dicts


def _add_tree_item(parent, text, tool_tip, func_name, column=0):
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
    item.setToolTip(column, tool_tip)
    item.setData(0, QtCore.Qt.UserRole, func_name)
    parent.addChild(item)
    return item


class PreviewTable(BasePreviewTable):
    def __init__(self, parent=None):
        super(PreviewTable, self).__init__(parent)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def scroll_to_column(self, column):
        try:
            self.scrollTo(self.model().index(0, column))
        except AttributeError:
            # Matlab Calculator has no columns
            pass


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


class ModelTableView(QtGui.QTableView):
    current_row_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(ModelTableView, self).__init__(parent=parent)
        # TODO (Benedikt): internal drag and drop disabled since it is not
        # working correctly
        # self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        # self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)
        # self.setDragDropMode(self.InternalMove)

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


class CalculatorModelView(QtGui.QWidget):
    new_item_added = QtCore.Signal()

    def __init__(self, model, parent=None):
        super(CalculatorModelView, self).__init__(parent=parent)

        assert(isinstance(model, models.CalculatorItemModel))
        self._model = model

        self.view = ModelTableView(parent=self)

        self.view.setModel(self._model)

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

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        layout.addWidget(toolbar)
        self.setLayout(layout)

        # Workaround to get correct header looks when loading parameters
        # and when creating a new calculator node.
        self.add_item()
        self.remove_item()

        self.view.setColumnWidth(2, 30)
        self.view.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.view.horizontalHeader().moveSection(2, 0)
        if self._model.backend == 'matlab':
            self.view.setColumnHidden(2, True)

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
        self._backend = kwargs.pop('backend', None)
        self.generic = kwargs.pop('generic', None)
        super(ItemEditBox, self).__init__(*args, **kwargs)
        self._item = None
        self.highlighter = None
        self._init_gui()
        self.set_backend(self._backend)
        self.calc_timer = QtCore.QTimer()
        self.calc_timer.setInterval(1500)  # 1s timeout before calc runs
        self.calc_timer.setSingleShot(True)
        self.calc_timer.timeout.connect(self.write_calc_line)

    def _setup_name_colouring(self):
        normal_palette = QtGui.QPalette()
        normal_palette.setColor(QtGui.QPalette.Base, colors.DEFAULT_BG_COLOR)
        normal_palette.setColor(QtGui.QPalette.Text, colors.DEFAULT_TEXT_COLOR)

        warning_palette = QtGui.QPalette()
        warning_palette.setColor(QtGui.QPalette.Base, colors.WARNING_BG_COLOR)
        warning_palette.setColor(QtGui.QPalette.Text, colors.WARNING_TEXT_COLOR)

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

        calc_line_label = QtGui.QLabel('Calculation:')
        self.calc_field = CalcFieldWidget(parent=self)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.column_name)
        layout.addWidget(calc_line_label)
        layout.addWidget(self.calc_field)
        self.setLayout(layout)

        self.setTabOrder(self.column_name, self.calc_field)

    def set_backend(self, backend):
        self._backend = backend

        if self.generic:
            self.highlighter = sywidgets.PygmentsHighlighter(
                self.calc_field, 'python')
        elif self._backend == 'python':
            self.highlighter = PythonHighlight(self.calc_field.document())
        if self.highlighter:
            self.calc_field.textChanged.connect(self.highlighter.rehighlight)

    def set_item(self, item):
        if self._item is not None:
            self.column_name.textChanged.disconnect(self.column_name_changed)
            self.calc_field.textChanged.disconnect(self.calc_line_changed)
        self._item = item

        if item is not None:
            self.column_name.setText(self._item.name)
            self.calc_field.setPlainText(self._item._func)
            self.column_name.textChanged.connect(self.column_name_changed)
            self.calc_field.textChanged.connect(self.calc_line_changed)
        else:
            self.column_name.setText('')
            self.calc_field.setPlainText('')

    def column_name_changed(self):
        if self._item is not None:
            self._item.name = self.column_name.text()

    def write_calc_line(self):
        if self._item is not None:
            self._item.update()

    def calc_line_changed(self):
        if self._item is not None:
            self._item.calculation = self.calc_field.toPlainText()

        if not self.calc_timer.isActive():
            self.calc_timer.start()
        else:
            self.calc_timer.stop()
            self.calc_timer.start()


class CalculatorWidget(ParameterView):
    def __init__(self, in_data, parameters, backend='python',
                 preview_calculator=None, parent=None, generic=False,
                 multiple_input=False, empty_input=False):
        super(CalculatorWidget, self).__init__(parent=parent)
        self.generic = generic
        self._status_message = ''
        if not generic:
            if isinstance(in_data, table.File):
                self._in_tables = table.FileList()
                self._in_tables.append(in_data)
                self._multiple_input = False
            else:
                self._in_tables = in_data
                self._multiple_input = True
        else:
            self._multiple_input = multiple_input
            if multiple_input:
                self._in_tables = in_data
            else:
                self._in_tables = []
                self._in_tables.append(in_data)

        self._parameter_root = parameters
        self._backend = backend
        self.model = models.CalculatorItemModel(
            self._in_tables, parameters, backend=backend,
            preview_calculator=preview_calculator, generic=generic,
            empty_input=empty_input)
        self.preview_model = (
            PreviewModel(self.model) if preview_calculator else None)
        self.view_model = CalculatorModelView(self.model)
        self.model_view = self.view_model.view
        self.preview_view = PreviewTable()

        # edit signal widgets
        self.current_column = ItemEditBox('Edit Signal',
                                          backend=self._backend,
                                          generic=generic)
        self.function_tree = TreeDragWidget()
        self.search_field = sywidgets.ClearButtonLineEdit(
            placeholder='Search function name')
        self.column_name_list = SignalTableWidget()
        self.search_signal_field = sywidgets.ClearButtonLineEdit(
            placeholder='Search column name')
        self.tree_head = None
        self.init_gui()
        self.init_gui_from_model()

    def init_gui(self):
        self.preview_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.preview_view.setModel(self.preview_model)
        hsplitter = QtGui.QSplitter()
        hsplitter.setOpaqueResize(QtCore.Qt.Horizontal)
        hsplitter.setContentsMargins(0, 0, 0, 0)
        hsplitter.addWidget(self.view_model)
        if self._backend == 'python':
            preview_view = PreviewTable()
            preview_view.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
            preview_view.setModel(self.preview_model)
            hsplitter.addWidget(self.preview_view)

        # function widget
        function_label = QtGui.QLabel("Common functions")
        self.function_tree.setMaximumWidth(2000)
        function_tree_layout = QtGui.QVBoxLayout()
        function_tree_layout.setContentsMargins(0, 0, 0, 0)
        function_tree_layout.setSpacing(5)
        function_tree_layout.addWidget(function_label)
        function_tree_layout.addWidget(self.function_tree)
        function_tree_layout.addWidget(self.search_field)

        # List of available Signals names
        signals_label = QtGui.QLabel("Signals")

        self.column_name_list.setMaximumWidth(2000)
        if self.generic:
            self.column_name_list.set_format('{0}')

        signal_list_layout = QtGui.QVBoxLayout()
        signal_list_layout.setContentsMargins(0, 0, 0, 0)
        signal_list_layout.setSpacing(5)
        signal_list_layout.addWidget(signals_label)
        signal_list_layout.addWidget(self.column_name_list)
        signal_list_layout.addWidget(self.search_signal_field)

        functions_n_signals = QtGui.QWidget()
        function_signal_layout = QtGui.QHBoxLayout()
        function_signal_layout.setContentsMargins(0, 5, 0, 5)
        function_signal_layout.addLayout(function_tree_layout)
        function_signal_layout.addLayout(signal_list_layout)
        functions_n_signals.setLayout(function_signal_layout)

        # add widgets to global vsplitter
        vsplitter = QtGui.QSplitter()
        vsplitter.setOrientation(QtCore.Qt.Vertical)
        vsplitter.setContentsMargins(0, 0, 0, 0)
        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.current_column)
        vsplitter.addWidget(functions_n_signals)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(vsplitter)
        copy_input_gui = self._parameter_root['copy_input'].gui()
        if self._multiple_input:
            hlayout = QtGui.QHBoxLayout()
            hlayout.setContentsMargins(0, 0, 0, 0)
            if 'same_length_res' in self._parameter_root:
                value = self._parameter_root['same_length_res'].value
                same_length_gui = self._parameter_root['same_length_res'].gui()
                hlayout.addWidget(same_length_gui)
                same_length_gui.valueChanged.connect(self.status_changed)
                same_length_gui.valueChanged[bool].connect(
                    copy_input_gui.set_enabled)
            else:
                value = True
            copy_input_gui.set_enabled(value)
            hlayout.addWidget(copy_input_gui)
            layout.addLayout(hlayout)

        else:
            layout.addWidget(copy_input_gui)
        layout.addWidget(self._parameter_root['fail_strategy'].gui())
        self.setLayout(layout)

        self.model_view.current_row_changed.connect(self.update_current_item)
        self.function_tree.itemDoubleClicked.connect(self.insert_function)
        self.column_name_list.itemDoubleClicked.connect(self.insert_signal)
        self.search_field.textChanged.connect(self.search_function)
        self.search_signal_field.textChanged[six.text_type].connect(
            self.search_signal)
        self.current_column.calc_field.insert_function.connect(
            self.insert_text)
        self.model.data_ready.connect(self.status_changed)
        self.model.item_dropped.connect(self.model_view.item_added)

    def init_gui_from_model(self):
        if not self.model.rowCount():
            self.model.add_item()

        if self.model_view.model().rowCount():
            selection_model = self.model_view.selectionModel()
            first_idx = self.model_view.model().index(0, 0)
            selection_model.select(first_idx,
                                   QtGui.QItemSelectionModel.ClearAndSelect |
                                   QtGui.QItemSelectionModel.Rows)

        # init input column names
        self.column_name_list.setRowCount(
            len(self.model.input_columns_and_types))

        for idx, (cname, dtype) in enumerate(
                self.model.input_columns_and_types):
            name_item = QtGui.QTableWidgetItem(models.display_calculation(
                cname, self.generic))
            type_item = QtGui.QTableWidgetItem(dtype)
            if re.search("\s'(\).data|\])$", cname):
                name_item.setBackground(QtGui.QBrush(colors.WARNING_BG_COLOR))
                name_item.setToolTip(
                    'Warning, this column name contains whitespace at the end')
            for item in [name_item, type_item]:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.column_name_list.setItem(idx, 0, name_item)
            self.column_name_list.setItem(idx, 1, type_item)
        self.column_name_list.resizeColumnsToContents()

        self.model_view.setCurrentIndex(self.model.index(0, 0))
        self.update_current_item()

        # init function tree
        init_tree(self.function_tree, self._backend, self.generic)
        self.tree_head = self.function_tree.invisibleRootItem()

    def save_parameters(self):
        self.model.save_parameters()

    def cleanup(self):
        if self._backend == 'python':
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

    def insert_signal(self, item):
        if item.column() > 0:
            # Double click on type column. Need to fetch the relevant item.
            item = self.column_name_list.current_items()[0]
        self.current_column.calc_field.insertPlainText(item.text())

    def insert_function(self, item):
        text = item.data(0, QtCore.Qt.UserRole)
        self.insert_text(text)

    def insert_text(self, text):
        if text:
            text = models.display_calculation(text, self.generic)
            selected_items = self.column_name_list.current_items()
            if self.generic:
                signal0 = "arg.col('signal0').data"
                signal1 = "arg.col('signal1').data"
            else:
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
            self.current_column.calc_field.insertPlainText(text)

    def update_current_item(self):
        item = self.model_view.current_item()
        self.current_column.set_item(item)
        if item is not None:
            self.preview_view.scroll_to_column(item.row())

    def search_function(self):
        term = self.search_field.text()
        recursive_hide(self.tree_head, term)

    def search_signal(self, pattern):
        items = self.column_name_list.get_items()
        item_names = [item.text() for item in items]
        filtered_item_indexes = fuzzy_list_filter(pattern, item_names)

        for row in range(self.column_name_list.rowCount()):
            if row in filtered_item_indexes:
                self.column_name_list.setRowHidden(row, False)
            else:
                self.column_name_list.setRowHidden(row, True)


def recursive_hide(node, word):
    status = 0
    if node.childCount() < 1:
        # This is a leave
        text = node.text(0)
        data = node.data(0, QtCore.Qt.UserRole)
        if word not in data and word not in text:
            status = 1
    else:
        count = 0
        for index in range(0, node.childCount()):
            count += recursive_hide(node.child(index), word)
        if count == node.childCount():
            # All children are hidden
            status = 1

    node.setHidden(status)
    node.setExpanded(~status)
    if len(word) == 0:
        node.setExpanded(status)

    return status


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
        source_items = self.source_model.get_items_gen()
        columns_len = [len(item._column_data) for item in source_items]
        if columns_len:
            row_count = max(columns_len)
        else:
            row_count = 0
        return row_count

    def columnCount(self, qmodel_index=None):
        return self.source_model.rowCount()

    def data(self, qmodel_index, role=QtCore.Qt.DisplayRole):
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
            return models.cell_format(display_data)
        elif role == QtCore.Qt.ToolTipRole:
            if display_data is not None:
                return models.cell_format(display_data)
            else:
                return ''
        elif role == QtCore.Qt.BackgroundRole:
            if not column_item.calculation_valid:
                return colors.DANGER_BG_COLOR
            elif column_item.is_computing:
                return colors.WARNING_BG_COLOR
            else:
                return None
        return None

    def flags(self, qmodel_index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
