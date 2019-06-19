# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
"""
Hierarchical view of the node library.

- LibraryItemInterface: Items in the view (folders or nodes).
- LibraryItem: Folder
- LibraryNodeItem: Node
- LibraryModel: Qt Library Model
- LibraryWidgetIcons: Alternative view with icons instead of a tree view
- LibraryWidget: Widget containing the library
- LibraryFilterProxyModel: Proxy model that supports filtering and sorting
- LibraryView: Widget with a filter and the library
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import json
import itertools
import six
import numpy as np
import os
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from . import util
from . import appcore
from . import settings
from sympathy.utils.prim import uri_to_path
from sympathy.utils import search
from sympathy.platform import widget_library as sywidgets
from sympathy.utils import library_info
from Gui import flow
from Gui.datatypes import DataType


class LibraryItemInterface(object):
    """Interface that both nodes and library models must fulfill."""

    def __init__(self):
        super(LibraryItemInterface, self).__init__()
        self._name = ''
        self._parent = None

    @property
    def name(self):
        """Returns the node name"""
        return self._name

    @property
    def parent(self):
        """Returns the node parent [library/sub library]"""
        return self._parent

    def is_node(self):
        """True if the item is a node, False if it is a Library"""
        raise NotImplementedError('Not implemented for interface')

    def child_count(self):
        """Number of children (valid for libraries)"""
        raise NotImplementedError('Not implemented for interface')

    def icon(self):
        """Node icon"""
        raise NotImplementedError('Not implemented for interface')

    def node_identifier(self):
        """Unique node identifier, used for drag operations"""
        raise NotImplementedError('Not implemented for interface')

    def tool_tip(self):
        """Node information tool tip"""
        raise NotImplementedError('Not implemented for interface')

    def row(self):
        """Find out which row the current node has (below its parent)"""
        if self._parent:
            return self._parent.index(self)
        else:
            return 0


class LibraryItem(LibraryItemInterface):
    """A LibraryItem is a folder item in the library model."""

    def __init__(self, name, parent, style):
        super(LibraryItem, self).__init__()
        self._name = name
        self._highlighted_text = ""
        self._parent = parent
        self._style = style
        self._children = []
        self._icon = QtGui.QIcon()
        self._icon.addPixmap(
            style.standardPixmap(QtGui.QStyle.SP_DirClosedIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self._icon.addPixmap(
            style.standardPixmap(QtGui.QStyle.SP_DirOpenIcon),
            QtGui.QIcon.Normal, QtGui.QIcon.On)

    def is_node(self):
        return False

    def child_count(self):
        return len(self._children)

    def icon(self):
        return self._icon

    def node_identifier(self):
        return self._name

    def tool_tip(self):
        return ''

    def add_child(self, child):
        """Add a child"""
        self._children.append(child)

    def index(self, child):
        """Returns the index of child"""
        return self._children.index(child)

    def child(self, row):
        """Returns the child at row"""
        return self._children[row]

    def node(self):
        """Not valid for parents"""
        return None

    def highlighted(self):
        """Highlighted text"""
        return self._highlighted_text


class FlatLibraryItem(LibraryItem):
    """A FlatLibraryItem is a header item for a sequence of tags."""

    def __init__(self, name, parent, style):
        super(FlatLibraryItem, self).__init__(name, parent, style)
        self._icon = QtGui.QIcon()
        self._brush = QtCore.Qt.lightGray

    def highlighted(self):
        """Highlighted text"""
        return '<font color="#999999">{}</font>'.format(self._highlighted_text)


class LibraryNodeItem(LibraryItemInterface):
    """A LibraryNodeItem is a leaf item in the library model representing a
    Node.
    """

    icon_cache = {}

    def __init__(self, node, parent):
        super(LibraryNodeItem, self).__init__()

        def escape(s):
            return (s.replace('&', '&amp;')
                     .replace('<', '&lt;')
                     .replace('>', '&gt;'))

        self._parent = parent
        self._node = node
        self._name = node.name
        self._highlighted_text = ""
        self._tool_tip = '<b>{}</b><p>{}</p>{} -> {}'.format(
            self._node.name, self._node.description,
            ', '.join([escape(str(p.datatype)) for p in self._node.inputs]),
            ', '.join([escape(str(p.datatype)) for p in self._node.outputs]))

    def is_node(self):
        return True

    def child_count(self):
        return 0

    def icon(self):
        if self._node.has_svg_icon:
            icon_path = uri_to_path(self._node.icon)
            if icon_path in self.icon_cache:
                return self.icon_cache[icon_path]
            else:
                result = QtGui.QIcon(icon_path)
                self.icon_cache[icon_path] = result
                return result
        else:
            return QtGui.QIcon(util.icon_path('sub_application.svg'))

    def node_identifier(self):
        return self._node.node_identifier

    def tool_tip(self):
        return self._tool_tip

    def node(self):
        return self._node

    def highlighted(self):
        """Highlighted text"""
        return self._highlighted_text


class LibraryModel(QtCore.QAbstractItemModel):
    """The library model. Responsible for building and updating the (viewed)
    library.
    """

    def __init__(
            self, library_root, style, exclude_builtins=False, parent=None):
        super(LibraryModel, self).__init__(parent)
        self._library_root = library_root
        self._style = style
        self._root = None
        self._old_root = None
        self._index_to_item = {}
        self._exclude_builtins = exclude_builtins
        self._build_model()

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        def hidden_node(node):
            if settings.instance()['Gui/library_hide']:
                tags = node.tags if node.tags else self.tags
                for tag in tags:
                    if tag.startswith('Hidden.'):
                        return True
            return False

        libraries = self._library_root.libraries
        paths = set()
        all_nodes = set()
        for lib in libraries:
            all_nodes.update({n for n in lib.nodes})
            paths.update({tuple(n.path) for n in lib.nodes})

        # Add possibly missing levels
        subpaths = set()
        for path in paths:
            subpaths.update({path[:i + 1] for i, _ in enumerate(path)})

        paths.update(subpaths)
        max_depth = max([len(n) for n in paths]) if paths else 0
        # Attempt to avoid crash in gc.
        self._old_root = self._root
        self._root = LibraryItem('Root', None, self._style)
        self._index_to_item = {}
        try:
            self._old_root.deleteLater()
        except AttributeError:
            pass
        libs = {}
        for depth_ in range(max_depth):
            depth = depth_ + 1
            libraries = [p for p in sorted(paths) if len(p) == depth]
            for lib in libraries:
                if (self._exclude_builtins and
                        (lib[0] == 'sympathy' or lib[0] == 'internal')):
                    continue
                else:
                    if depth == 1:
                        parent = self._root
                    else:
                        parent = libs[lib[:-1]]
                    item = LibraryItem(lib[-1], parent, self._style)
                    parent.add_child(item)
                    libs[lib] = item
                    for node in (n for n in all_nodes if tuple(n.path) == lib):
                        if not hidden_node(node):
                            node_item = LibraryNodeItem(node, item)
                            item.add_child(node_item)

    @QtCore.Slot()
    def update_model(self):
        """Rebuild the model by querying the library."""
        self.beginResetModel()
        self._build_model()
        self.endResetModel()

    def createIndex(self, row, column, item):
        # Internal ID is set based on the attached pointer.
        # We manage this ourselves since putting an object as internalPointer
        # seems to be unstable in Python.
        # http://www.riverbankcomputing.com/pipermail/pyqt/2009-April/022709.html
        index = super(LibraryModel, self).createIndex(row, column, item)
        self._index_to_item[index.internalId()] = item
        return index

    #
    # QAbstractItemModel interface
    #

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 1

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            item = self._index_to_item.get(parent.internalId())
            if item is None:
                return 0
            return item.child_count()
        else:
            return self._root.child_count()

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if parent.isValid():
            parent_item = self._index_to_item.get(parent.internalId())
        else:
            parent_item = self._root

        child_item = None
        if parent_item is not None:
            child_item = parent_item.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        empty_index = QtCore.QModelIndex()

        if not index.isValid():
            return empty_index
        try:
            item = self._index_to_item.get(index.internalId())
            parent = item.parent
            grand_parent = parent.parent
            return self.createIndex(grand_parent.index(parent), 0, parent)
        except AttributeError:
            return empty_index

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._index_to_item.get(index.internalId())

        if item is None:
            pass
        elif role == QtCore.Qt.DisplayRole:
            return item.name[:1].upper() + item.name[1:]
        elif role == QtCore.Qt.DecorationRole:
            return item.icon()
        elif role == QtCore.Qt.ToolTipRole:
            return item.tool_tip()
        elif role == QtCore.Qt.UserRole:
            return item.node_identifier()
        elif role == QtCore.Qt.UserRole + 1:
            return item.highlighted()

    def setData(self, index, value, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.UserRole + 1:
            item = self._index_to_item.get(index.internalId())
            item._highlighted_text = value
        else:
            super(LibraryModel, self).setData(index, value, role)

    def itemData(self, index):
        item = self._index_to_item.get(index.internalId())
        data = None
        if item is not None:
            data = item.node()
        return {'node_info': data}

    def flags(self, index):
        if not index.isValid():
            return 0

        item = self._index_to_item.get(index.internalId())

        if item is not None and item.is_node():
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsDragEnabled |
                    QtCore.Qt.ItemIsSelectable)
        else:
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable)

    def mimeTypes(self):
        return [appcore.AppCore.mime_type_node()]

    def mimeData(self, indices):
        nodes = []
        for index in indices:
            nodes.append(self.data(index, QtCore.Qt.UserRole))

        mime_data = QtCore.QMimeData()
        mime_data.setData(appcore.AppCore.mime_type_node(), json.dumps(nodes))
        return mime_data

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
            else:
                return QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return 'Node name'
            else:
                return section + 1
        else:
            return None


class SeparateTagLibraryModel(LibraryModel):
    def __init__(self, library_root, style, model_type='Disk', parent=None):
        self._model_type = model_type
        super(SeparateTagLibraryModel, self).__init__(
            library_root, style, parent=parent)

    def _build_tags(self, parent, tags, path):
        if tags and not tags.term:
            for tag in tags:
                child = LibraryItem(tag.name, parent, self._style)
                parent.add_child(child)
                self._build_tags(
                    child, tag, '.'.join([path, tag.key]) if path else tag.key)
        else:
            self._tag_mapping[path] = parent

    def _build_node(self, node):
        tags = node.tags
        if not tags:
            tags = self.tags

        # Filter hidden nodes.
        for tag in tags:
            try:
                if tag.startswith('Hidden.'):
                    return
            except:
                return

        for tag in tags:
            parent = self._tag_mapping.get(tag, None)
            if parent:
                child = LibraryNodeItem(node, parent)
                parent.add_child(child)
                # Insert based on the first available tag.
                return

        for tag in self.tags:
            parent = self._tag_mapping[tag]
            child = LibraryNodeItem(node, parent)
            parent.add_child(child)

    def _build_model(self):
        """
        Build the tree model using tags separated by libraries for hierarchy.
        """
        if self._model_type == 'Disk':
            return super(SeparateTagLibraryModel, self)._build_model()

        self._tag_mapping = {
            tag: LibraryItem(tag, None, self._style) for tag in self.tags}

        lib_paths = set()
        all_nodes = set()
        for lib in self._library_root.libraries:
            for n in lib.nodes:
                all_nodes.add(n)
                lib_paths.add(uri_to_path(n.library))
        libraries = {}
        for path in lib_paths:
            library_info.create_library_info(
                os.path.join(path, '..', 'library.ini'), path)
            try:
                name = library_info.instance()[path]['General']['name']
            except KeyError:
                # Illegal path or something, skip it. A warning will be
                # displayed later when library.ini can't be read.
                continue
            libraries[name] = [
                n for n in all_nodes if path == uri_to_path(n.library)]
        if 'sympathy' in libraries.keys() and 'Internal' in libraries.keys():
            libraries['sympathy'] = (
                libraries['sympathy'] + libraries['Internal'])
            del libraries['Internal']

        self._root = LibraryItem('Root', None, self._style)
        for library in libraries.keys():
            child = LibraryItem(library, self._root, self._style)
            self._root.add_child(child)
            if self._library_root.tags:
                self._build_tags(child, self._library_root.tags.root, None)
            for node in libraries[library]:
                self._build_node(node)


class TagLibraryModel(SeparateTagLibraryModel):
    tags = ['Unknown']

    def __init__(self, library_root, style, model_type='Disk',
                 parent=None):
        super(TagLibraryModel, self).__init__(library_root, style,
                                              model_type=model_type,
                                              parent=parent)

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        if self._model_type in ['Disk', 'Separated']:
            return super(TagLibraryModel, self)._build_model()
        elif self._model_type != 'Tag':
            return

        # Proceed with 'Tag Layout'.

        self._tag_mapping = {}
        libraries = self._library_root.libraries
        all_nodes = set()

        for lib in libraries:
            all_nodes.update({n for n in lib.nodes})

        self._root = LibraryItem('Root', None, self._style)

        for tag in self.tags:
            if tag not in self._tag_mapping:
                child = LibraryItem(tag, self._root, self._style)
                self._root.add_child(child)
                self._tag_mapping[tag] = child

        if self._library_root.tags:
            self._build_tags(self._root, self._library_root.tags.root, None)

        for node in all_nodes:
            self._build_node(node)

    def set_type(self, model_type):
        model_type_prev = self._model_type
        self._model_type = model_type
        if self._model_type != model_type_prev:
            self.update_model()


class FlatTagLibraryModel(TagLibraryModel):
    tags = ['Unknown']

    def __init__(self, library_root, style, model_type='Disk',
                 parent=None):
        super(FlatTagLibraryModel, self).__init__(library_root, style,
                                                  model_type=model_type,
                                                  parent=parent)

    def _all_tags(self):
        def inner(tags, path, res):
            if tags:
                if tags.term:
                    res['.'.join(tag.key for tag in path)] = path
                else:
                    for tag in tags:
                        inner(tag, path + [tag], res)
        res = {}
        inner(self._library_root.tags.root, [], res)
        return res

    def _build_model(self):
        """Build the tree model using path for hierarchy."""
        if self._model_type in ['Disk', 'Tag', 'Separated']:
            return super(FlatTagLibraryModel, self)._build_model()
        elif self._model_type != 'FlatTag':
            return

        # Proceed with 'FlatTag Layout'.

        def build_node(node):
            tags = node.tags
            if not tags:
                tags = self.tags
            else:
                tags = [tags[0]]

            # Filter hidden nodes.
            for tag in tags:
                if tag.startswith('Hidden.'):
                    return

            parent = tag_mapping.get('.'.join(tags), None)
            if parent:
                child = LibraryNodeItem(node, parent)
                parent.add_child(child)
                # Insert based on the first available tag.
                return

            for tag in self.tags:
                parent = tag_mapping[tag]
                child = LibraryNodeItem(node, parent)
                parent.add_child(child)

        tag_mapping = {}
        libraries = self._library_root.libraries
        all_nodes = set()
        all_tags = self._all_tags()

        for lib in libraries:
            all_nodes.update({n for n in lib.nodes})

        self._root = LibraryItem('Root', None, self._style)

        for tag in itertools.chain(all_tags, self.tags):
            if tag not in tag_mapping:
                tags = all_tags.get(tag)
                name = self.tags[0]
                if tags:
                    name = '/'.join(tag.name for tag in tags)

                child = FlatLibraryItem(name, self._root, self._style)
                self._root.add_child(child)
                tag_mapping[tag] = child

        for node in all_nodes:
            build_node(node)

    def flags(self, index):
        if self._model_type != 'FlatTag':
            return super(FlatTagLibraryModel, self).flags(index)

        if not index.isValid():
            return 0

        item = self._index_to_item.get(index.internalId())

        if item is not None and item.is_node():
            return (QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsDragEnabled |
                    QtCore.Qt.ItemIsSelectable)
        else:
            return QtCore.Qt.NoItemFlags


class LibraryWidgetIcons(QtGui.QListView):
    """Alternative, graphical library view."""

    selection_changed = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super(LibraryWidgetIcons, self).__init__(parent)
        self._init()

    def _init(self):
        highlighter = Highlighter(highlight_on=False, parent=self)
        self.setObjectName('Gui::MainWindow::Library::View')
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setViewMode(QtGui.QListView.IconMode)
        self.setMovement(QtGui.QListView.Static)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.setFlow(QtGui.QListView.LeftToRight)
        self.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setUniformItemSizes(True)
        self.setSpacing(10)
        self._font.setPointSize(10)
        self.setFont(self._font)
        self.setItemDelegate(highlighter)

    def selectionChanged(self, selected, deselected):
        if len(selected.indexes()) > 0:
            index = self.model().mapToSource(selected.indexes()[0])

            self.selection_changed.emit(
                self.model().sourceModel().itemData(index))


def font_color_highlighter(color='#990000', **kw):
    return 'color="{}"'.format(color)


def font_background_highlighter(color='#EECC22', **kw):
    return 'style="background-color: {}"'.format(color)


def font_weight_highlighter(**kw):
    return 'style="font-weight: bold"'


highlighters = {
    'color': font_color_highlighter,
    'background-color': font_background_highlighter,
    'font-weight': font_weight_highlighter
}


class Highlighter(QtGui.QStyledItemDelegate):
    def __init__(self, highlight_on, parent, *args):
        super(Highlighter, self).__init__(parent, *args)
        self._highlight_on = highlight_on

    def set_highlight_on(self, state):
        self._highlight_on = state

    def paint(self, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        if options.widget is None:
            style = QtGui.QApplication.style()
        else:
            style = options.widget.style()

        doc = QtGui.QTextDocument()
        text = index.data(QtCore.Qt.UserRole + 1)
        doc.setHtml(text)

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        if self._highlight_on and options.state & QtGui.QStyle.State_Selected:
            ctx.palette.setColor(
                QtGui.QPalette.Text,
                options.palette.color(
                    QtGui.QPalette.Active, QtGui.QPalette.HighlightedText))

        text_rect = style.subElementRect(
            QtGui.QStyle.SE_ItemViewItemText, options, None)
        painter.save()
        painter.translate(text_rect.topLeft())
        painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        size_hint = super(Highlighter, self).sizeHint(option, index)
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        doc = QtGui.QTextDocument()
        doc.setHtml(index.data(QtCore.Qt.UserRole + 1))
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(
            doc.idealWidth(), max(doc.size().height(), size_hint.height()))


class LibraryWidget(QtGui.QTreeView):
    """Tree view of the library. It is separated from the regular tree view
    in order to support selection_changed signalling (for quick views) and
    contained settings.
    """

    selection_changed = QtCore.Signal(dict)
    switch_to_filter = QtCore.Signal()
    item_accepted = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(LibraryWidget, self).__init__(parent)
        self._font = QtGui.QApplication.font()
        self._init()

    def _init(self):
        highlighter = Highlighter(highlight_on=False, parent=self)

        self.setObjectName('Gui::MainWindow::Library::View')
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setIndentation(15)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.setTextElideMode(QtCore.Qt.ElideMiddle)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setFont(self._font)
        self.setItemDelegate(highlighter)
        self.doubleClicked.connect(self._accept_index)

    def set_highlight_mode(self, highlight_on=False):
        item_delegate = self.itemDelegate()
        item_delegate.set_highlight_on(highlight_on)
        if highlight_on:
            # this is prevents showing the branch icons in the FlatTag mode
            self.setStyleSheet(
                'QTreeView::branch { border-image: url(none.png); }')
        else:
            self.setStyleSheet(
                'QTreeView { selection-background-color: transparent; }')

    def selectionChanged(self, selected, deselected):
        if len(selected.indexes()) > 0:
            index = self.model().mapToSource(selected.indexes()[0])
            self.selection_changed.emit(
                self.model().sourceModel().itemData(index))

    def keyPressEvent(self, event):
        index = self.currentIndex()
        parent = index.parent()
        if (event.key() == QtCore.Qt.Key_Up and parent and
                parent.row() == 0 and index.row() == 0):
            self.switch_to_filter.emit()
        elif event.key() == QtCore.Qt.Key_Return:
            proxy_index = self.currentIndex()
            self._accept_index(proxy_index)
            event.accept()
        else:
            super(LibraryWidget, self).keyPressEvent(event)

    def focusOutEvent(self, event):
        self.setCurrentIndex(QtCore.QModelIndex())
        super(LibraryWidget, self).focusOutEvent(event)

    def _accept_index(self, index):
        index = self.model().mapToSource(index)
        item = self.model().sourceModel().itemData(index)
        self._accept_item(item)

    def _accept_item(self, item):
        if 'node_info' in item:
            self.item_accepted.emit(item['node_info'])
        else:
            self.item_accepted.emit(None)


class LibraryFilterProxyModel(QtGui.QSortFilterProxyModel):
    """Proxy model that supplies sorting and filtering for the library model.
    """

    def __init__(self, parent=None):
        super(LibraryFilterProxyModel, self).__init__(parent)
        self._filter = ''
        self._input_type = None
        self._output_type = None
        self._cache = {}
        self._matcher_type = 'character'
        self._highlighter_attr = 'style="background-color: #EECC22"'
        self._filter_regex = None
        self._highlight_regex = []
        self._current_libraries = set()
        self.highlighted = set()

    @property
    def matcher_type(self):
        return self._matcher_type

    @matcher_type.setter
    def matcher_type(self, matcher_type):
        self._matcher_type = matcher_type
        self.update_filter(self._filter)

    @property
    def highlighter_attr(self):
        return self._highlighter_attr

    @highlighter_attr.setter
    def highlighter_attr(self, attr):
        self._highlighter_attr = attr
        self.update_filter(self._filter)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(
            source_row, self.sourceModel().columnCount() - 1, source_parent)
        return self._show_row(index)

    def _show_row(self, index):
        ret_val = False
        number_of_rows = self.sourceModel().rowCount(index)

        if number_of_rows > 0:
            for i in range(number_of_rows):
                child_index = self.sourceModel().index(i, 0, index)
                if not child_index.isValid():
                    break
                else:
                    ret_val = self._show_row(child_index)
                if ret_val:
                    break
        else:
            parent_types = []
            parents = []

            parent = self.sourceModel().index(index.row(), 0, index.parent())
            parent_type = self.sourceModel().data(parent)

            node = self.sourceModel().itemData(parent)['node_info']
            if node is None:
                return False
            if (os.path.normcase(os.path.abspath(os.path.dirname(
                    uri_to_path(node.library))))
                    not in self._current_libraries):
                return False

            input_match = self._match_port_type(self._input_type, node._inputs)
            output_match = self._match_port_type(
                self._output_type, node._outputs)

            while parent_type:
                parent_types.append(parent_type)
                parents.append(parent)
                parent = self.sourceModel().parent(parent)
                parent_type = self.sourceModel().data(parent)

            parent_types_r = list(reversed(parent_types))

            ret_val = search.matches(self._filter_regex,
                                     ' '.join(parent_types_r))

            for parent, parent_type in zip(parents, parent_types):
                if self._matcher_type == 'word':
                    full_label = self.highlight_word(parent_type)
                elif self._matcher_type == 'character':
                    full_label = self.highlight_character(parent_type)
                else:
                    full_label = parent_type

                self.sourceModel().setData(
                    parent, full_label, QtCore.Qt.UserRole + 1)

            ret_val = all([ret_val, input_match, output_match])
        return ret_val

    def highlight_character(self, parent_type):
        seq_to_highlight = set()
        for rx in self._highlight_regex:
            org_filter = rx.pattern.replace('\\S*?', '')
            text = parent_type.replace('/', ' ')
            for c in '(*^-.?${},+[])':
                org_filter = org_filter.replace('\\{}'.format(c), c)
            for m in rx.finditer(text):
                i = 0
                sub_string = m.group().lower()
                for c in org_filter:
                    i += sub_string[i:].index(c.lower()) + 1
                    seq_to_highlight.add(i + m.start())

        seq_to_highlight = np.atleast_1d(list(seq_to_highlight))
        seq_to_highlight.sort()
        if len(seq_to_highlight) == 0:
            sub_matches = []
        elif len(seq_to_highlight) == 1:
            sub_matches = [seq_to_highlight]
        else:
            pos_diff = np.diff(seq_to_highlight)
            is_not_consecutive = np.hstack(
                ([False], pos_diff > 1))
            split_indices = np.where(is_not_consecutive)[0]
            sub_matches = np.split(seq_to_highlight, split_indices)

        highlighted_text = list(parent_type)
        addon = 0
        for sub_match in sub_matches:
            highlighted_text.insert(
                min(sub_match) + addon - 1,
                '<font {}>'.format(self.highlighter_attr))
            addon += 1
            highlighted_text.insert(
                max(sub_match) + addon, '</font>')
            addon += 1
        full_label = ''.join(highlighted_text)
        return full_label

    def highlight_word(self, parent_type):
        full_label = []
        for word in parent_type.split(' '):
            matches = [f.search(word) for f in
                       self._highlight_regex]
            matches = [m for m in matches if m is not None]
            matches.sort(key=lambda x: x.start())
            highlighted_text = list(word)
            addon = 0
            for match in matches:
                if match.start() < match.end():
                    highlighted_text.insert(
                        match.start() + addon,
                        '<font {}>'.format(self.highlighter_attr))
                    addon += 1
                    highlighted_text.insert(match.end() + addon,
                                            '</font>')
                    addon += 1
            full_label.append(''.join(highlighted_text))
        full_label = ' '.join(full_label)
        return full_label

    def update_filter(self, new_filter):
        if new_filter is not None:
            self._highlight_regex = search.highlight_patterns(new_filter)
            self._filter = new_filter
            self._filter_regex = search.fuzzy_pattern(new_filter)
        self.invalidateFilter()
        self.sort(0, QtCore.Qt.AscendingOrder)
        return self._filter

    def _match_port_type(self, type_, ports):
        if type_ is not None:
            return any(port.datatype.match(type_) for port in ports)
        return True

    def update_port_type(self, datatype, output):
        if not isinstance(datatype, DataType):
            datatype = None
        if output:
            self._output_type = datatype
        else:
            self._input_type = datatype
        self.update_filter(self._filter)
        return datatype

    def set_current_libraries(self, libraries):
        prev = self._current_libraries
        self._current_libraries = set([os.path.normcase(l) for l in libraries])
        if prev != self._current_libraries:
            self.invalidateFilter()
            self.sort(0, QtCore.Qt.AscendingOrder)


class AdvancedFilter(QtGui.QWidget):
    switch_to_list = QtCore.Signal()
    filter_changed = QtCore.Signal(six.text_type)

    def __init__(self, parent=None):
        super(AdvancedFilter, self).__init__(parent=parent)

        self._init_gui()

    def _init_gui(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(QtCore.QMargins())

        self._filter = FilterLineEdit(parent=self)
        layout.addWidget(self._filter)
        self._filter.switch_to_list.connect(self.switch_to_list)
        self._filter.textChanged[six.text_type].connect(self.filter_changed)
        self.setLayout(layout)

    def set_focus(self):
        # TODO: if enhanced mode is open, set focus to lowest LineEdit widget
        self._filter.setFocus()


class FilterLineEdit(sywidgets.ClearButtonLineEdit):
    switch_to_list = QtCore.Signal()

    def __init__(self, placeholder="Filter", clear_button=True, parent=None):
        super(FilterLineEdit, self).__init__(placeholder, clear_button, parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Down:
            self.switch_to_list.emit()
            # event.accept()
        else:
            super(FilterLineEdit, self).keyPressEvent(event)


class LibraryView(QtGui.QWidget):
    """Library view combination widget - library view and filter edit."""

    item_accepted = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(LibraryView, self).__init__(parent)
        self._proxy_model = LibraryFilterProxyModel()
        self._model = None
        self._model_type = 'Disk'
        self._init()

    def _init(self):
        """Initialize gui"""
        self._layout = QtGui.QVBoxLayout()
        self._layout.setContentsMargins(QtCore.QMargins())
        self._layout.setSpacing(0)

        self.setObjectName('Gui::MainWindow::Library::ViewWidget')
        self._filter = AdvancedFilter(parent=self)
        self._layout.addWidget(self._filter)
        self._view = LibraryWidget(parent=self)
        self._view.setModel(self._proxy_model)
        self._layout.addWidget(self._view, stretch=10)

        self.update_filter('')

        self._filter.filter_changed[six.text_type].connect(
            self.update_filter)
        self._filter.switch_to_list.connect(self._handle_switch_to_list_view)
        self._view.switch_to_filter.connect(self._handle_switch_to_filter)
        self._view.item_accepted.connect(self.item_accepted)
        self.setLayout(self._layout)

    def set_model(self, model):
        """Set the library model"""
        # Store model as a private member to avoid shiboken
        # deallocation problem.
        self._model = model
        self.set_model_type(model._model_type)
        self._model.modelReset.connect(self._reset_model)
        self._reset_model()

    @QtCore.Slot(str)
    def set_model_type(self, model_type):
        self._model_type = model_type
        if self._model_type == 'FlatTag':
            self._view.setIndentation(0)
            self._view.setItemsExpandable(False)
            self._view.expandAll()
            self._view.set_highlight_mode(True)
        else:
            self._view.setIndentation(15)
            self._view.setItemsExpandable(True)
            self._view.collapseAll()
            self._view.set_highlight_mode(False)
        self._model.set_type(model_type)

    @QtCore.Slot()
    def update_model(self):
        self._model.update_model()

    def update_libraries(self, flow):
        self._proxy_model.set_current_libraries(util.library_paths(flow))

    @QtCore.Slot(tuple)
    def set_highlighter(self, highlighter_param):
        matcher_type, highlighter_type, highlighter_color = highlighter_param
        highlighter_func = highlighters.get(highlighter_type,
                                            font_color_highlighter)
        highlighter_attr = highlighter_func(color=highlighter_color)
        self._proxy_model.highlighter_attr = highlighter_attr
        self._proxy_model.matcher_type = matcher_type

    @QtCore.Slot()
    def _reset_model(self):
        """Reset (reload) model"""
        self._proxy_model.setSourceModel(self._model)
        self.update_filter()
        self._proxy_model.sort(0, QtCore.Qt.AscendingOrder)

    @QtCore.Slot(six.text_type)
    def update_filter(self, new_filter=None):
        """Change the library filter"""
        used_filter = self._proxy_model.update_filter(new_filter)
        self._handle_expanding(used_filter != '')

    @QtCore.Slot(six.text_type)
    def update_input_filter(self, new_type=None):
        self._update_port_filter(new_type, output=False)

    @QtCore.Slot(six.text_type)
    def update_output_filter(self, new_type=None):
        self._update_port_filter(new_type, output=True)

    @QtCore.Slot()
    def clear_filter(self):
        """Clear the library filter"""
        self._filter.setText('')
        self.update_filter('')
        self._view.collapseAll()

    def _get_port_datatype(self, new_type):
        if isinstance(new_type, DataType):
            return new_type
        elif new_type:
            return DataType.from_str(new_type)
        return None

    def _update_port_filter(self, new_type, output):
        datatype = self._get_port_datatype(new_type)
        used_datatype = self._proxy_model.update_port_type(
            datatype, output=output)
        self._handle_expanding(isinstance(used_datatype, DataType))

    def _handle_expanding(self, state):
        if state or (self._model and self._model_type == 'FlatTag'):
            self._view.expandAll()
        else:
            self._view.collapseAll()

    def _handle_switch_to_list_view(self):
        self._view.setFocus()
        try:
            proxy_index = self._proxy_model.index(0, 0)
            if self._model_type == 'FlatTag':
                if not proxy_index.parent().isValid():
                    proxy_index = self._proxy_model.index(0, 0, proxy_index)
                self._view.setCurrentIndex(proxy_index)
            else:
                self._view.setCurrentIndex(proxy_index)
        except:
            pass

    def _handle_switch_to_filter(self):
        self._filter.set_focus()
        self._view.setCurrentIndex(QtCore.QModelIndex())

    @QtCore.Slot(dict)
    def handle_selection_changed(self, node):
        """Update the node preview when the selection has changed"""
        if node['node_info'] is not None:
            info = node['node_info']
            inputs_ = ', '.join(['{} ({})'.format(p.description, p.datatype)
                                 for p in info.inputs])
            outputs_ = ', '.join(['{} ({})'.format(p.description, p.datatype)
                                  for p in info.outputs])
            if info:
                info = (
                    '<b>{}</b><br/><i>{}</i><br/>{}<p><b>Inputs:</b> {}<br/>'
                    '<b>Outputs:</b> {}</p>'.format(
                        info.name, info.node_identifier, info.description,
                        inputs_, outputs_))
                self._quick_view.setText(info)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            view = self._view
            proxy_index = view.currentIndex()
            index = self._proxy_model.mapToSource(proxy_index)
            item = self._proxy_model.sourceModel().itemData(index)
            if 'node_info' in item:
                self.item_accepted.emit(item['node_info'])
            else:
                self.item_accepted.emit(None)
            event.accept()
        super(LibraryView, self).keyPressEvent(event)

    @QtCore.Slot(flow.Flow)
    def current_flow_changed(self, flow):
        self._proxy_model.set_current_libraries(util.library_paths(flow))
        if self._proxy_model._filter != '':
            self._handle_expanding(self._proxy_model._filter != '')


class QuickSearchDialog(QtGui.QDialog):
    item_accepted = QtCore.Signal(object, object, QtCore.QPointF)

    def __init__(
            self, library_root, flow_, port, scene_position, title=None,
            parent=None):
        super(QuickSearchDialog, self).__init__(
            parent, QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self._library_root = library_root
        self._port = port
        self._title = title

        model_type = 'FlatTag'

        self._model = FlatTagLibraryModel(
            self._library_root, self.style(),
            model_type=model_type,
            parent=self)
        self.scene_position = scene_position

        self._view = LibraryView(parent=self)
        self._view.current_flow_changed(flow_)
        self._view.set_model(self._model)

        settings_ = settings.instance()
        matcher_type = settings_['Gui/library_matcher_type']
        highlighter_type = settings_['Gui/library_highlighter_type']
        highlighter_color = settings_['Gui/library_highlighter_color']

        self._view.set_highlighter(
            (matcher_type, highlighter_type, highlighter_color))

        if self._port is not None:
            if self._port.type == flow.Type.InputPort:
                self._view.update_output_filter(self._port.datatype)
            else:
                self._view.update_input_filter(self._port.datatype)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        if self._title is not None:
            title_label = QtGui.QLabel(self._title)
            layout.addWidget(title_label)
        layout.addWidget(self._view)
        self.setLayout(layout)
        self._view.item_accepted.connect(self._accept)

    def _accept(self, item):
        self.item_accepted.emit(item, self._port, self.scene_position)
        self.accept()
