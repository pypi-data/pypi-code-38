# Copyright (c) 2016, Combine Control Systems AB
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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)

import copy
import functools
import types
import weakref

import six

from sympathy.api import qt
from sympathy.platform.widget_library import SyBaseToolBar

from sylib.icons import utils as icon_utils
from sylib.tree_model import models, widgets


QtCore = qt.QtCore
QtGui = qt.QtGui


MIME = {
    'layout_tree_item_id': 'application-x-sympathy/xyz.layout.tree.item.id',
    'layout_tree_new_item': 'application-x-sympathy/xyz.layout.tree.new.item',
    'instance': 'application-x-sympathy/xyz.instance'
}


class BaseTreeItemModel(QtCore.QAbstractItemModel):
    def __init__(self, model, root_class):
        super(BaseTreeItemModel, self).__init__()
        self.model = model
        self.root_class = root_class
        self._index_to_weak_item = {}
        self.is_dragging = None

    def index_to_item(self, index):
        persistent_index = QtCore.QPersistentModelIndex(index)
        weak_item = self._index_to_weak_item.get(persistent_index, None)
        return weak_item() if weak_item is not None else None

    def item_to_index(self, item):
        for persistent_idx, weak_item in six.iteritems(
                self._index_to_weak_item):
            if item == weak_item():
                return self.index(persistent_idx.row(),
                                  persistent_idx.column(),
                                  persistent_idx.parent())
        return QtCore.QModelIndex()

    def root_item(self):
        return [x for x in self.model.root.children
                if isinstance(x, self.root_class)][0]

    def columnCount(self, parent_index=QtCore.QModelIndex()):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.index_to_item(index)
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return item.label
            elif index.column() == 1 and item.is_leaf:
                return item.data
        elif role == QtCore.Qt.FontRole:
            if index.column() == 0:
                font = QtGui.QFont()
                if item.is_leaf and models.NodeTags.deletable not in item.tags:
                    font.setItalic(True)
                elif not item.is_leaf:
                    font.setBold(True)
                return font
        elif role == QtCore.Qt.ItemDataRole:
            if index.column() == 1 and item.is_leaf:
                return six.text_type(item.data)
        elif role == QtCore.Qt.ToolTipRole:
            return item.tooltip
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return item.get_icon()
        elif role == QtCore.Qt.BackgroundRole:
            if self.is_dragging in item.get_available_children():
                return QtGui.QColor.fromRgb(204, 235, 197)
            return None
        elif role == QtCore.Qt.UserRole:
            return item
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            item = self.index_to_item(index)
            # TODO: possibly add feedback if set data fails
            if item.is_leaf:
                item.set_data(value)
            else:
                item.data = value
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        item = self.index_to_item(index)
        column = index.column()
        flags = QtCore.Qt.ItemIsEnabled
        if column == 0:
            if item.NODE_LEAFS or item.is_leaf:
                flags |= QtCore.Qt.ItemIsSelectable
            if models.NodeTags.rearrangable in item.tags:
                flags |= (QtCore.Qt.ItemIsDragEnabled |
                          QtCore.Qt.ItemIsSelectable)
            if models.NodeTags.is_container in item.tags:
                flags |= (QtCore.Qt.ItemIsDropEnabled |
                          QtCore.Qt.ItemIsSelectable)
        elif column == 1:
            if item.is_leaf:
                flags |= QtCore.Qt.ItemIsEditable
        return flags

    def index(self, row, column, parent_index=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent_index):
            return QtCore.QModelIndex()

        if not parent_index.isValid():
            parent_item = self.root_item()
        else:
            parent_item = self.data(parent_index, QtCore.Qt.UserRole)

        child_list = parent_item.children

        if len(child_list) > 0:
            child_item = child_list[row]
        else:
            return QtCore.QModelIndex()
        return self.createIndex(row, column, child_item)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = self.index_to_item(index)
        if child_item is None:
            return QtCore.QModelIndex()
        parent_item = child_item.parent

        if parent_item is None:
            return QtCore.QModelIndex()
        parent_parent_item = parent_item.parent

        if parent_parent_item is None:
            row = 0
        else:
            row = parent_parent_item.index(parent_item)
        return self.createIndex(row, 0, parent_item)

    def rowCount(self, parent_index=QtCore.QModelIndex()):
        if not parent_index.isValid():
            parent_item = self.root_item()
        else:
            parent_item = self.index_to_item(parent_index)
        return parent_item.row_count()

    def createIndex(self, row, column, item):
        index = super(BaseTreeItemModel, self).createIndex(row, column, item)
        persistent_index = QtCore.QPersistentModelIndex(index)
        self._index_to_weak_item[persistent_index] = weakref.ref(item)
        return index


class TreeItemModel(BaseTreeItemModel):
    new_item_inserted = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, model, root_cls, item_type_to_class=None, mime=MIME):
        super(TreeItemModel, self).__init__(model, root_cls)
        self.setSupportedDragActions(QtCore.Qt.MoveAction)
        self._mime = mime
        if item_type_to_class is None:
            item_type_to_class = {}
        self.item_type_to_class = item_type_to_class

        self.drop_success = False

    def mimeData(self, index_list):
        assert len(index_list) == 1
        index = index_list[0]
        item = self.data(index, QtCore.Qt.UserRole)
        data = QtCore.QMimeData()
        data.setData(self._mime['instance'], self.model.instance)
        data.setData(self._mime['layout_tree_item_id'],
                     six.text_type(id(item)).encode('ascii'))
        return data

    def mimeTypes(self):
        return list(self._mime.values())

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def dropMimeData(self, mime_data, drop_action, row, column, parent_index):
        self.drop_success = False

        # Make sure that data is coming from the same instance.
        if (mime_data.hasFormat(self._mime['instance']) and
                mime_data.data(
                    self._mime['instance']).data() != self.model.instance):
            return False

        # Don't allow to drop anything on value column
        if column > 0:
            return False

        if drop_action == QtCore.Qt.IgnoreAction:
            self.drop_success = True
            return True

        parent_item = self.data(parent_index, QtCore.Qt.UserRole)
        if parent_item is None:
            for c in self.model.root.children:
                if isinstance(c, self.root_class):
                    parent_item = c
                    break

        if row > -1:
            begin_row = row
        elif parent_index.isValid():
            begin_row = len(parent_item.children)
        else:
            begin_row = self.rowCount(QtCore.QModelIndex())

        if mime_data.hasFormat(self._mime['layout_tree_item_id']):
            # Moving something inside the tree.
            python_id = int(
                mime_data.data(self._mime['layout_tree_item_id']).data())
            item = self.model.root.find_node_by_python_id(python_id)

            # We cannot add something such that it becomes a child of itself.
            if models.is_parent_same_node(parent_item, item):
                return False

            # The parent must allow the item to be a child.
            if (item is None or
                    item.__class__ not in parent_item.valid_children()):
                return False

            self.layoutAboutToBeChanged.emit()
            models.move_node(item, parent_item, begin_row)
            self.layoutChanged.emit()

        if mime_data.hasFormat(self._mime['layout_tree_new_item']):
            # Adding something to the tree.
            item_type = str(mime_data.data(self._mime['layout_tree_new_item']))
            item_class = self.item_type_to_class[item_type]
            if item_class not in parent_item.valid_children():
                return False
            new_item = item_class.create_empty_instance(parent_item)

            begin_row = parent_item.get_insert_position(new_item, begin_row)
            self.beginInsertRows(parent_index, begin_row, begin_row)
            models.insert_node(new_item, parent_item, begin_row)
            self.endInsertRows()
            self.new_item_inserted.emit(self.index(begin_row, 0, parent_index))

        self.drop_success = True
        return True

    def insert_node(self, new_item, parent_item, parent_index, begin_row=None):
        if begin_row is None or begin_row <= 0:
            if parent_index.isValid():
                begin_row = len(parent_item.children)
            else:
                begin_row = self.rowCount(QtCore.QModelIndex())
        begin_row = parent_item.get_insert_position(new_item, begin_row)
        self.beginInsertRows(parent_index, begin_row, begin_row)
        models.insert_node(new_item, parent_item, begin_row)
        self.endInsertRows()
        self.layoutChanged.emit()
        self.new_item_inserted.emit(self.index(begin_row, 0, parent_index))

    def insertRows(self, row, count, parent_index=QtCore.QModelIndex()):
        return True

    def move_row(self, index, item, move):
        row = index.row()
        parent_index = index.parent()
        end_row = row + move
        if move > 0:
            move_to = end_row + 1
        else:
            move_to = end_row
        if end_row < 0 or end_row > len(item.parent.children):
            return
        self.beginMoveRows(parent_index, row, row, parent_index, move_to)
        models.move_node(item, item.parent, end_row)
        self.endMoveRows()

    def removeRows(self, row, count, parent_index=QtCore.QModelIndex()):
        items = [
            self.data(self.index(x, 0, parent_index), QtCore.Qt.UserRole)
            for x in range(row, row + count)]
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for item in items:
            if item.parent is not None:
                item.parent.remove_child(item)
        self.endRemoveRows()
        return True


def add_child(parent, child_name):
    child_item = QtGui.QStandardItem(six.text_type(child_name))
    parent.appendRow(child_item)
    return child_item


class SyBaseTreeCompleterModel(QtGui.QStandardItemModel):
    """
    Base class of a TreeCompleterModel as needed for the TreeModelCompleter.

    This class has to be subclassed and the _create_tree function and the
    quick_pick_list have to be reimplemented.
    """
    def __init__(self, data, parent=None):
        super(SyBaseTreeCompleterModel, self).__init__(parent)
        self.root_item = self.invisibleRootItem()
        self._data = data
        self._create_tree()

    def _create_tree(self):
        raise NotImplementedError

    @property
    def quick_pick_list(self):
        return []


class SyTableTreeCompleterModel(SyBaseTreeCompleterModel):
    def _create_tree(self):
        # TODO: (Bene) add [Table] support with the following syntax
        # "table[1].name"
        # only in cases where input "table" is of type [Table] ?!
        parent = add_child(self.root_item, 'table')
        props_to_add = sorted(
            ['name', 'attr', 'attrs', 'column_names()', 'column_type()',
             'col()', 'cols()', 'number_of_rows()', 'number_of_columns()',
             'is_empty()'])
        for prop in props_to_add:
            if prop == 'attr':
                try:
                    for attr in self._data.attrs.keys():
                        add_child(parent, "attr('{}')".format(attr))
                except (KeyError, AttributeError):
                    pass
                add_child(parent, '{}()'.format(prop))
            else:
                add_child(parent, prop)

        try:
            names = self._data.column_names()
        except AttributeError:
            names = []
        for name in names:
            child = add_child(parent, "col('{}')".format(name))

            for prop in ['name', 'data', 'attr', 'attrs']:
                if prop == 'attr':
                    try:
                        for attr in self._data.col(name).attrs.keys():
                            add_child(child, "attr('{}')".format(attr))
                    except KeyError:
                        pass
                    add_child(child, '{}()'.format(prop))
                else:
                    n_child = add_child(child, prop)
                    if prop == 'data':
                        for np_prop in ['ndim', 'dtype', 'shape']:
                            add_child(n_child, np_prop)

        for name in names:
            add_child(parent, "column_type('{}')".format(name))

    @property
    def quick_pick_list(self):
        try:
            names = self._data.column_names()
        except AttributeError:
            names = []
        return names


class TreeModelCompleter(QtGui.QCompleter):
    insert_text = QtCore.Signal(six.text_type)

    def __init__(self, *args, **kwargs):
        super(TreeModelCompleter, self).__init__(*args, **kwargs)
        self._separator = '.'
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setWrapAround(False)
        self.activated[six.text_type].connect(self.change_completion)

    def change_completion(self, completion):
        self.insert_text.emit(completion)

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, s):
        self._separator = s

    def splitPath(self, path):
        if self.separator is None:
            return super(TreeModelCompleter, self).splitPath(path)

        splitted_path = path.split(self.separator)
        return splitted_path

    def pathFromIndex(self, index):
        def get_tree_data(idx, data_list):
            if idx.isValid():
                data = self.model().data(idx, self.completionRole())
                data_list.append(data)
                get_tree_data(idx.parent(), data_list)

        if self.separator is None:
            return super(TreeModelCompleter, self).pathFromIndex(index)

        # navigate up and accumulate data
        data_list = []
        get_tree_data(index, data_list)
        return '{}'.format(self.separator).join(reversed(data_list))


class ParameterTreeDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, completer_models, parent):
        super(ParameterTreeDelegate, self).__init__(parent)
        self.completer_models = completer_models

    def createEditor(self, parent, option, index):
        if index.isValid():
            item = index.model().index_to_item(index)
            column = index.column()
            if column == 1 and item.editor is not None and item.is_leaf:
                editor = item.editor(parent=parent)
                editor.set_parent_view_widget(self.parent())
            else:
                return super(ParameterTreeDelegate, self).createEditor(
                    parent, option, index)
            return editor

    def setEditorData(self, editor, index):
        if not isinstance(editor, widgets.SyBaseEditMixin):
            super(ParameterTreeDelegate, self).setEditorData(editor, index)

        item = index.model().index_to_item(index)
        value = index.model().data(index, QtCore.Qt.ItemDataRole)

        if item.is_leaf and self.completer_models:
            cm_cls, cm_args, cm_kwargs = self.completer_models.get(
                item.completer_name)
            completer_model = cm_cls(*cm_args, **cm_kwargs)
            completer = TreeModelCompleter(parent=self)
            completer.setModel(completer_model)
            editor.set_completer(completer)
            editor.set_drop_down_items(completer_model.quick_pick_list)

        editor.set_options(item.options)
        editor.set_value(value)

    def setModelData(self, editor, model, index):
        if not isinstance(editor, widgets.SyBaseEditMixin):
            super(ParameterTreeDelegate, self).setModelData(
                editor, model, index)
        else:
            value = editor.get_value()
            model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        new_rect = option.rect
        new_rect.setHeight(self.sizeHint(option, index).height())
        editor.setGeometry(new_rect)

    def sizeHint(self, option, index):
        size_hint = super(ParameterTreeDelegate, self).sizeHint(option, index)
        return QtCore.QSize(size_hint.width(), max(22, size_hint.height()))


class BaseParameterTreeView(QtGui.QTreeView):
    item_selected = QtCore.Signal(object)

    def __init__(self, input_table, mime=MIME, parent=None):
        super(BaseParameterTreeView, self).__init__(parent)
        self.setRootIsDecorated(True)
        self.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.header().setVisible(False)
        self.header().setStretchLastSection(True)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.setUpdatesEnabled(True)
        self.setMouseTracking(True)

        self._input_table = input_table
        self._mime = mime
        self._completer_models = {'default': None}

        self._delegate = ParameterTreeDelegate(self._completer_models, self)
        self.setItemDelegate(self._delegate)

        icon = icon_utils.create_icon(icon_utils.SvgIcon.copy)
        self.duplicate_action = QtGui.QAction(icon, 'Duplicate', self)
        self.duplicate_action.setShortcut('Ctrl+d')
        self.addAction(self.duplicate_action)
        self.duplicate_action.triggered.connect(self.duplicate_selected_item)
        icon = icon_utils.create_icon(icon_utils.SvgIcon.delete)
        self.remove_action = QtGui.QAction(icon, 'Delete', self)
        self.remove_action.triggered.connect(self.remove_selected_items)

        self.collapse_all_action = QtGui.QAction('Collapse all', self)
        self.collapse_all_action.setShortcut('Ctrl+-')
        self.collapse_all_action.triggered.connect(self.collapseAll)
        self.addAction(self.collapse_all_action)
        self.expand_all_action = QtGui.QAction('Expand all', self)
        self.expand_all_action.setShortcut('Ctrl++')
        self.expand_all_action.triggered.connect(self.expandAll)
        self.addAction(self.expand_all_action)

        self.move_up_action = QtGui.QAction('Move up', self)
        self.move_up_action.setShortcut(
            QtCore.Qt.ControlModifier + QtCore.Qt.Key_Up)
        self.move_up_action.triggered.connect(self.move_selection_up)
        self.addAction(self.move_up_action)

        self.move_down_action = QtGui.QAction('Move down', self)
        self.move_down_action.setShortcut(
            QtCore.Qt.ControlModifier + QtCore.Qt.Key_Down)
        self.move_down_action.triggered.connect(self.move_selection_down)
        self.addAction(self.move_down_action)

    @property
    def completer_models(self):
        return self._completer_models

    @completer_models.setter
    def completer_models(self, models):
        if models and 'default' not in models:
            models['default'] = None
        self._completer_models = models
        self._delegate.completer_models = self._completer_models

    def set_completer_model(self, name, model):
        self._completer_models[name] = model
        self._delegate.completer_models = self._completer_models

    def end_edit(self):
        index = self.currentIndex()
        self.currentChanged(index, index)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Delete):
            self.remove_selected_items()
            event.accept()
        else:
            super(BaseParameterTreeView, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        index_at_pos = self.indexAt(event.pos())
        if not index_at_pos.isValid():
            item = self.model().root_item()
        else:
            item = self.model().index_to_item(index_at_pos)

        # create a context menu depending on which item is clicked
        context_menu, actions = self.create_context_menu(item, index_at_pos)

        result = context_menu.exec_(event.globalPos())
        if result in actions:
            func = actions[result]
            func()
            event.accept()
        else:
            event.ignore()

    def create_context_menu(self, item, index_at_pos):
        actions = {}
        context_menu = QtGui.QMenu(self)

        # duplicate menu action
        if models.NodeTags.copyable in item.tags:
            context_menu.addAction(self.duplicate_action)

        # delete menu action
        if models.NodeTags.deletable in item.tags:
            context_menu.addAction(self.remove_action)

        context_menu.addSeparator()

        # expand/collapse and rearrange actions
        context_menu.addAction(self.collapse_all_action)
        context_menu.addAction(self.expand_all_action)
        context_menu.addSeparator()

        if models.NodeTags.rearrangable in item.tags:
            context_menu.addAction(self.move_up_action)
            context_menu.addAction(self.move_down_action)

        context_menu.addSeparator()

        add_actions = []
        available_children = item.get_available_children()
        for child_cls in available_children:
            label = child_cls.prettify_class_name()
            icon = icon_utils.create_icon(child_cls.icon)
            item_action = QtGui.QAction(icon, label, self)
            actions[item_action] = functools.partial(
                self.add_child, item, child_cls, index_at_pos)
            add_actions.append(item_action)

        item_properties = item.available_leafs()
        item_property_keys = sorted(item_properties, key=lambda i: i[0])
        for prop, params in item_property_keys:
            label = params.get('label', prop)
            if params['icon'] is None:
                add_property_action = QtGui.QAction(label, context_menu)
            else:
                if isinstance(params['icon'], types.FunctionType):
                    icon = params['icon'](None)
                else:
                    icon = icon_utils.create_icon(params['icon'])
                add_property_action = QtGui.QAction(icon, label,
                                                    context_menu)
            actions[add_property_action] = functools.partial(
                self.add_leaf, item, prop, index_at_pos)
            add_actions.append(add_property_action)

        if add_actions:
            add_menu = QtGui.QMenu('Add ...', parent=self)
            for add_action in sorted(add_actions, key=lambda a: a.text()):
                add_menu.addAction(add_action)
            context_menu.addMenu(add_menu)

        return context_menu, actions

    def remove_selected_items(self):
        selected_indices = self.selectedIndexes()
        # We must sort the indices in reverse row order, otherwise the rows
        # are can become invalid.
        selected_indices.sort(key=lambda x: x.row(), reverse=True)
        deletable_indices = [i for i in selected_indices
                             if models.NodeTags.deletable in
                             self.model().index_to_item(i).tags]
        for index in deletable_indices:
            self.model().removeRow(index.row(), index.parent())

    def duplicate_selected_item(self):
        selected_indices = self.selectedIndexes()
        for selected_index in selected_indices:
            old_inst = self.model().index_to_item(selected_index)
            if type(old_inst) not in old_inst.parent.get_available_children():
                continue
            new_inst = copy.deepcopy(old_inst)
            # if (isinstance(old_inst.parent, models.Axes) and
            #         old_inst.parent.has_axes()):
            #     # add a second axes with (bottom, right) axis positions
            #     data['yaxis']['position'] = 'right'

            self.model().insert_node(
                new_inst, old_inst.parent, selected_index.parent(),
                selected_index.row() + 1)

    def move_selection_up(self):
        selected_indices = self.selectedIndexes()
        model = self.model()
        for selected_index in selected_indices:
            row = selected_index.row()
            item = model.index_to_item(selected_index)
            if models.NodeTags.rearrangable not in item.tags:
                continue
            previous_index = model.index(row - 1, 0, selected_index.parent())
            if previous_index.isValid():
                previous_item = model.index_to_item(previous_index)
                if models.NodeTags.rearrangable in previous_item.tags:
                    model.move_row(selected_index, item, -1)

    def move_selection_down(self):
        selected_indices = self.selectedIndexes()
        model = self.model()
        for selected_index in selected_indices:
            row = selected_index.row()
            item = model.index_to_item(selected_index)
            if models.NodeTags.rearrangable not in item.tags:
                continue
            next_index = model.index(row + 1, 0, selected_index.parent())
            if next_index.isValid():
                next_item = model.index_to_item(next_index)
                if models.NodeTags.rearrangable in next_item.tags:
                    model.move_row(selected_index, item, 1)

    def add(self, item_cls):
        """
        Add a new child at a selected parent.

        Used to add items from toolbar. Should be reimplemented if more
        complex logic is required.
        """
        selected_indices = self.selectedIndexes()
        model = self.model()
        root_node = self.model().root_item()
        root_index = model.item_to_index(root_node)

        if selected_indices:
            selected_index = selected_indices[0]
            selected_item = model.index_to_item(selected_index)
        else:
            self.setCurrentIndex(root_index)
            selected_index = root_index
            selected_item = root_node

        if (item_cls in selected_item.valid_children() and
                    item_cls in selected_item.get_available_children()):
            new_child = self.add_child(selected_item, item_cls, selected_index)
            new_child_idx = model.item_to_index(new_child)
            self.setCurrentIndex(new_child_idx)

    def add_child(self, parent_node, child_cls, parent_index):
        child_node = child_cls.create_empty_instance()
        self.model().insert_node(child_node, parent_node, parent_index,
                                 len(parent_node.children))
        return child_node

    def add_leaf(self, parent_node, leaf_name, parent_index):
        new_leaf = parent_node.create_leaf(leaf_name)
        self.model().insert_node(new_leaf, parent_node, parent_index,
                                 parent_node.number_of_leafs())
        return new_leaf

    def setModel(self, model):
        super(BaseParameterTreeView, self).setModel(model)
        model.new_item_inserted[QtCore.QModelIndex].connect(
            self.handle_new_item_inserted)
        model.layoutChanged.connect(self.force_update)

    def handle_new_item_inserted(self, index):
        if not index.isValid():
            return
        if index.parent().isValid():
            self.expand(index.parent())
        self.expand(index)

    @QtCore.Slot()
    def force_update(self):
        # HACK(stefan): Force redraw.
        self.setAlternatingRowColors(True)
        self.setAlternatingRowColors(False)
        self.update()

    def dropEvent(self, event):
        # Workaround for Qt-bug #6679.
        # https://bugreports.qt.io/browse/QTBUG-6679
        # QStandardItemModel::dropMimeData() regardless of its results, calls
        # QStandardItem::removeRow().
        #
        # Workaround inspired by:
        # http://www.qtcentre.org/archive/index.php/t-49819.html
        super(BaseParameterTreeView, self).dropEvent(event)
        if self.model() is not None and not self.model().drop_success:
            event.setDropAction(QtCore.Qt.IgnoreAction)
            event.ignore()
        self.model().is_dragging = None

    def dragMoveEvent(self, event):
        """
        Show indicator whether the dragged item can be dropped on the current
        item.
        """

        def class_of_item(mime_data_):
            item_class_ = None
            # TODO(stefan): Reproducing some code from dropMimeData in model
            if mime_data_.hasFormat(self._mime['layout_tree_item_id']):
                python_id = int(mime_data_.data(
                    self._mime['layout_tree_item_id']).data())
                item = self.model().model.root.find_node_by_python_id(
                    python_id)
                item_class_ = type(item)
            elif mime_data_.hasFormat(self._mime['layout_tree_new_item']):
                item_type = str(mime_data_.data(
                    self._mime['layout_tree_new_item']))
                item_class_ = self.model().item_type_to_class[item_type]
            return item_class_

        super(BaseParameterTreeView, self).dragMoveEvent(event)
        index = self.indexAt(event.pos())
        mime_data = event.mimeData()
        item_class = class_of_item(mime_data)
        self.model().is_dragging = item_class
        self.drag_move_event_handling(event, item_class, index)

    def drag_move_event_handling(self, event, item_class, index):
        """Handle the drag move event implementation dependent."""
        if index.isValid():
            drop_indicator_position = self.dropIndicatorPosition()
            parent_item = index.model().data(index, QtCore.Qt.UserRole)
            if parent_item is None:
                event.ignore()
                return
            if drop_indicator_position != QtGui.QAbstractItemView.OnItem:
                # If the drop indicator is not on the item we need to get the
                # parent item in the tree instead.
                parent_item = parent_item.parent
            if item_class in parent_item.get_available_children():
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()


class ImageWidget(QtGui.QWidget):
    mouse_release_event = QtCore.Signal()

    def __init__(self, item, mime=MIME, parent=None):
        """
        Constructor.
        :param item: models.BaseNode
            See models.BaseNode for details.
        :param parent: Parent widget.
        """
        super(ImageWidget, self).__init__(parent)
        assert issubclass(item, models.BaseNode)
        self.item = item
        self._mime = mime
        icon_name = self.item.icon
        self.icon = icon_utils.create_icon(icon_name)
        self.setMinimumHeight(icon_utils.SIZE)
        self.setMaximumHeight(icon_utils.SIZE)
        self.setMinimumWidth(icon_utils.SIZE)
        self.setMaximumWidth(icon_utils.SIZE)
        self._drag_start_position = QtCore.QPoint(0, 0)
        # create tooltip
        tooltip = '<b>{}</b>'.format(self.item.prettify_class_name())
        if self.item.description is not None:
            tooltip += '<p>{}</p>'.format(self.item.description)
        self.setToolTip(tooltip)

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        self.icon.paint(p, self.rect())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_position = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_release_event.emit()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if ((event.pos() - self._drag_start_position).manhattanLength() <
                QtGui.QApplication.startDragDistance()):
            return

        drag = QtGui.QDrag(self)
        data = QtCore.QMimeData()
        data.setData(
            self._mime['layout_tree_new_item'],
            six.text_type(self.item.node_type).encode('ascii'))
        drag.setMimeData(data)
        drag.setPixmap(self.icon.pixmap(icon_utils.SIZE, icon_utils.SIZE))
        drag.exec_(QtCore.Qt.CopyAction)


class BaseItemsToolBar(SyBaseToolBar):
    def __init__(self, view, items, mime=MIME, parent=None):
        super(BaseItemsToolBar, self).__init__(parent)
        self.setIconSize(QtCore.QSize(26, 26))
        self.view = view
        self._mime = mime
        self.add_actions()
        self.add_widgets(items)

    def add_actions(self):
        if self.view is not None:
            self.addAction(self.view.duplicate_action)
            self.addAction(self.view.remove_action)

    def add_item(self, item_cls):
        if self.view is not None:
            self.view.add(item_cls)

    def add_widgets(self, items):
        self.addWidget(QtGui.QLabel(self.windowTitle()))
        for item in items:
            if item == 'separator':
                self.addSeparator()
            else:
                widget_action = QtGui.QWidgetAction(self)
                widget = ImageWidget(item, mime=self._mime)
                widget_action.setDefaultWidget(widget)
                self.addAction(widget_action)
                widget.mouse_release_event.connect(
                    functools.partial(self.add_item, item))
