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
import functools

import itertools
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from . import flow
from . import util
from . import signals
from sympathy.utils.prim import uri_to_path, format_display_string
from sympathy.platform import widget_library as sywidgets


class IndirectNode(object):
    """
    Workaround wrapper to make Lambda supported by
    QTreeWidgetItem.setData.
    """
    def __init__(self, node):
        self.node = node


class FlowOverview(QtGui.QWidget):
    select_flow = QtCore.Signal(flow.Flow)
    select_node = QtCore.Signal(flow.Node)

    icon_cache = {}

    def __init__(self, parent=None):
        super(FlowOverview, self).__init__(parent)
        self._search = sywidgets.ClearButtonLineEdit(placeholder='Filter')
        self._tree_view = QtGui.QTreeWidget()
        self._tree_view.setHeaderHidden(True)

        self._signals = signals.SignalHandler()
        self._root_flow = None
        self._set_new_root_flow(None)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._search)
        layout.addWidget(self._tree_view)
        self.setLayout(layout)
        layout.setContentsMargins(QtCore.QMargins())
        layout.setSpacing(0)

        self._search.textChanged.connect(
            self._update_filter)
        self._tree_view.itemClicked.connect(
            self._handle_item_click)

    def hideEvent(self, event):
        # Make sure to clear the view before hiding it.
        self._set_new_root_flow(None)

    def showEvent(self, event):
        self._set_new_root_flow(self._root_flow)

    def focus_search(self):
        self._search.setFocus()

    def set_flow(self, flow_window_=None):
        if flow_window_ is not None:
            root_flow = flow_ = flow_window_.flow()
            while root_flow.flow is not None:
                root_flow = root_flow.flow
            if root_flow is not self._root_flow:
                self._set_new_root_flow(root_flow)
            self._highlight_flow(flow_)
        else:
            self._set_new_root_flow(None)

    def _set_new_root_flow(self, root_flow):
        self._highlight = None
        self._node_to_item = {}
        self._tree_view.clear()
        self._remove_all_node_signals()

        if root_flow is not None:
            self._root_flow = root_flow
        if root_flow is not None and self.isVisible():
            self._populate_model(root_flow)
            self._tree_view.expandItem(self._tree_view.topLevelItem(0))
        self._update_filter()

    def _get_node_icon(self, node):
        if node.has_svg_icon:
            icon_path = uri_to_path(node.icon)
            if icon_path in self.icon_cache:
                return self.icon_cache[icon_path]
            else:
                result = QtGui.QIcon(icon_path)
                self.icon_cache[icon_path] = result
                return result
        else:
            return QtGui.QIcon(util.icon_path('missing.svg'))

    def _handle_name_changed(self, node, new_name):
        item = self._node_to_item[node]
        item.setData(0, QtCore.Qt.DisplayRole, format_display_string(new_name))
        self._update_filter()

    def _handle_node_moved(self, node, new_position):
        new_position = new_position.x(), new_position.y()
        item = self._node_to_item[node]
        parent_item = self._node_to_item[node.flow]
        parent_item.removeChild(item)

        # Loop through items siblings to find a new place for it.
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            node_ = child.data(0, QtCore.Qt.UserRole).node
            position_ = node_.position.x(), node_.position.y()
            if position_ > new_position:
                # This is first sibling with position_ > new_position, so place
                # item here.
                parent_item.insertChild(i, item)
                break
        else:
            # for-else is triggered if the for-loop was never breaked. This
            # means that no siblings of item have a position > new_position. So
            # we just append the item.
            parent_item.addChild(item)

    def _handle_node_created(self, node):
        parent_flow = node.flow
        parent_item = self._node_to_item[parent_flow]
        self._populate_model(node, parent_item)
        # Make sure the node was put at the correct position in the tree.
        self._handle_node_moved(node, node.position)
        self._update_filter()

    def _handle_node_removed(self, node):
        # When deleting a subflow it doesn't seem to emit node_removed for all
        # of its children. This loop takes care of that, but could in some
        # cases lead to nodes being deleted twice.
        if node.type == flow.Type.Flow:
            for node_ in itertools.chain(node.shallow_nodes(),
                                         node.shallow_text_fields()):
                self._handle_node_removed(node_)

        # Guard against nodes being deleted twice.
        try:
            item = self._node_to_item[node]
        except KeyError:
            return
        parent_flow = node.flow
        parent_item = self._node_to_item[parent_flow]
        parent_item.removeChild(item)
        del self._node_to_item[node]
        self._remove_node_signals(node)
        self._update_filter()

    def _handle_icon_changed(self, node):
        item = self._node_to_item[node]
        item.setData(0, QtCore.Qt.DecorationRole,
                     self._get_node_icon(node))

    def _populate_model(self, node, parent_item=None):
        def position(node_):
            return node_.position.x(), node_.position.y()

        def create_item(node_, parent_item_):
            if node_.type == flow.Type.Flow:
                desc = node_.description
                label = node_.display_name
            elif node_.type == flow.Type.TextField:
                label = node_.text()
                desc = node_.text()
            else:
                desc = node_.description
                label = node_.name

            item = QtGui.QTreeWidgetItem(
                parent_item_, [format_display_string(label)])
            item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
            indirect_node = IndirectNode(node_)
            item.setData(0, QtCore.Qt.DecorationRole,
                         self._get_node_icon(node_))
            item.setData(0, QtCore.Qt.UserRole, indirect_node)
            item.setData(0, QtCore.Qt.ToolTipRole, desc)
            return item

        if parent_item is None:
            parent_item = self._tree_view

        if node in self._node_to_item:
            # Never overwrite a node in self._node_to_item. That could lead to
            # all sorts of broken states.
            self._handle_node_removed(node)
        item = create_item(node, parent_item)
        self._node_to_item[node] = item

        self._add_node_signals(node)
        if node.type == flow.Type.Flow:
            for node_ in sorted(itertools.chain(node.shallow_nodes(),
                                                node.shallow_text_fields()),
                                key=position):
                self._populate_model(node_, item)

    def _add_node_signals(self, node):
        self._signals.connect_reference(node, [
            (node.position_changed,
             functools.partial(self._handle_node_moved, node)),
            (node.name_changed,
             functools.partial(self._handle_name_changed, node))])

        if node.type == flow.Type.Flow:
            self._signals.connect_reference(node, [
                (node.icon_changed,
                 functools.partial(self._handle_icon_changed, node)),
                (node.text_field_created, self._handle_node_created),
                (node.text_field_removed, self._handle_node_removed),
                (node.node_created, self._handle_node_created),
                (node.node_removed, self._handle_node_removed),
                (node.subflow_created, self._handle_node_created),
                (node.subflow_removed, self._handle_node_removed)])

    def _remove_node_signals(self, node):
        # Disconnect all signals
        self._signals.disconnect_all(node)

    def _remove_all_node_signals(self):
        # Disconnect all signals for all nodes
        self._signals.disconnect_all()

    def _set_bold(self, item, bold):
        if bold:
            font = QtGui.QFont()
            font.setBold(bold)
        else:
            font = None
        item.setData(0, QtCore.Qt.FontRole, font)

    def _highlight_flow(self, flow):
        # Unbolden old flow
        if self._highlight is not None:
            self._set_bold(self._highlight, False)

        # Bolden new flow
        item = self._node_to_item.get(flow)
        if item is not None:
            self._set_bold(item, True)
            # self._tree_view.expandItem(item)
        self._highlight = item

    def _handle_item_click(self, item, column):
        node = item.data(0, QtCore.Qt.UserRole).node
        if node is self._root_flow:
            self.select_flow.emit(node)
        else:
            self.select_node.emit(node)

    def _update_filter(self, filter_string=None):
        root = self._tree_view.topLevelItem(0)
        if root is None:
            return
        if filter_string is None:
            filter_string = self._search.text()

        self._filter_item(root, filter_string)
        if filter_string:
            self._tree_view.expandAll()
        else:
            self._tree_view.collapseAll()
            self._tree_view.expandItem(self._tree_view.topLevelItem(0))

    def _filter_item(self, item, filter_string):
        visible_children = []
        for i in range(item.childCount()):
            child = item.child(i)
            visible_children.append(self._filter_item(child, filter_string))
        item_visible = (
            filter_string.lower() in item.data(
                0, QtCore.Qt.DisplayRole).lower() or
            any(visible_children))
        item.setHidden(not item_visible)
        return item_visible
