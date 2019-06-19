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
from __future__ import (
    print_function, division, absolute_import, unicode_literals)
import copy
import json
import re
import functools
import collections
import uuid
import weakref
import os.path
import six

import pygments
import pygments.lexers
import pygments.formatters

import sylib.report.builder as builder
import sylib.report.binding as binding
import sylib.report.plugins as plugins
import sylib.report.data_manager as data_manager
import sylib.report.models as models
import sylib.report.editor_type as editor_type
import sylib.report.icons as icons
import sylib.report.patterns as patterns

from sympathy.utils.parameter_helper_gui import ClampedButton
from sympathy.api import qt
from sylib.util import mock_wrap
QtGui = qt.QtGui
QtCore = qt.QtCore

# Debug flag for enabling source view
SHOW_JSON_MODEL = False


MIME_LAYOUT_TREE_ITEM_ID = 'application-x-sympathy/report.layout.tree.item.id'
MIME_LAYOUT_TREE_NEW_ITEM = (
    'application-x-sympathy/report.layout.tree.new.item')
MIME_LAYOUT_TREE_LAYER_TYPE = (
    'application-x-sympathy/report.layout.tree.layer.type')
MIME_INSTANCE = 'application-x-sympathy/report.instance'


class MainWindow(QtGui.QMainWindow):
    docks = None
    item_views = None
    model = None
    data_source_model = None
    scales_model = None
    page_model = None

    def __init__(self, sy_parameters, input_data, data_type,
                 async_build=True, signal_mapping=None, parent=None):
        super(MainWindow, self).__init__(parent)

        self.sy_parameters = sy_parameters
        if input_data:
            data_manager.init_data_source(input_data, data_type)

        if signal_mapping is not None:
            data_manager.data_source.set_signal_mapping(signal_mapping)

        self.setWindowTitle('Report Template Editor')
        self.init_docks()
        self.init_views()
        self.init_models()

        # Quick fix to make rebuild_widgets "atomic" and not trigger again
        # until it is done. Triggered by multiple deletions using fast keyboard
        # presses A less hacky (mutex) solution may be preferable later on.
        self._rebuild_done = True

        self.docks['properties'].setWidget(self.item_views['properties'])

        self.binding_context = binding.BindingContext()
        # Use a stacked widget to avoid resizing of layout when changing
        # widgets in the central widget view.
        self.root_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.root_widget)

        self.init_actions()
        self.init_window()

        # This construction is needed to be able to generate images in
        # the report apply node where the single shot is not feasible. For
        # the template editor we want to open the window as soon as possible
        # to show the user that something is happening. The plots are
        # generated later.
        if async_build:
            # Update plot after window has been opened.
            QtCore.QTimer.singleShot(0, self.rebuild_widgets)
        else:
            self.rebuild_widgets()

    def cleanup(self):
        # TODO: Refactor preview to thread instead of relying on singleShot and
        # processEvents. Somehow, multiple calls to processEvents is currently
        # needed to clean the queue.
        QtGui.QApplication.instance().processEvents()
        QtGui.QApplication.instance().processEvents()
        QtGui.QApplication.instance().processEvents()

    def sizeHint(self):
        rect = QtGui.QApplication.desktop().screenGeometry()
        adj_width = rect.width() * 0.05
        adj_height = rect.height() * 0.05
        rect.adjust(adj_width, adj_height, -adj_width, -adj_height)
        return rect.size()

    def init_docks(self):
        """Initialize all dock widgets."""
        # Storage for all docks.
        self.docks = collections.OrderedDict((
            ('scales', QtGui.QDockWidget('Scales')),
            ('pages', QtGui.QDockWidget('Pages')),
            ('properties', QtGui.QDockWidget('Properties')),
            ('source', QtGui.QDockWidget('Model Source'))
        ))
        for key, dock in six.iteritems(self.docks):
            if key == 'source':
                if SHOW_JSON_MODEL:
                    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            else:
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
            dock.setFeatures(
                QtGui.QDockWidget.DockWidgetFloatable |
                QtGui.QDockWidget.DockWidgetMovable)
        self.tabifyDockWidget(self.docks['scales'], self.docks['pages'])

    def init_views(self):
        """Initialize all views."""
        self.item_views = {
            'scales': ScaleView(),
            'pages': PageView(),
            'properties': PropertyView(),
            'source': ModelSourceView()
        }

        self.item_views['scales'].data_changed.connect(self.rebuild_widgets)

        for key, item_view in six.iteritems(self.item_views):
            if key == 'scales':
                container = QtGui.QWidget()
                container_layout = QtGui.QVBoxLayout()
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.setSpacing(0)
                container.setLayout(container_layout)
                item_widget = ScaleViewToolBar()
                item_widget.new_scale_action.triggered.connect(
                    self.add_new_scale)
                container_layout.addWidget(item_widget)
                container_layout.addWidget(item_view)
                self.docks[key].setWidget(container)
            elif key == 'pages':
                container = QtGui.QWidget()
                container_layout = QtGui.QVBoxLayout()
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.setSpacing(0)
                container.setLayout(container_layout)
                item_widget = PageViewToolBar()
                item2d_widget = PageView2DToolBar()
                container_layout.addWidget(item_widget)
                container_layout.addWidget(item2d_widget)
                container_layout.addWidget(item_view)
                self.docks[key].setWidget(container)
            else:
                self.docks[key].setWidget(self.item_views[key])
        self.item_views['pages'].item_selected[object].connect(
            self.switch_property_view)
        self.item_views['pages'].force_rebuild.connect(
            self.rebuild_widgets)
        self.item_views['pages'].force_rebuild_source.connect(
            self.rebuild_source)
        self.item_views['properties'].force_rebuild.connect(
            self.rebuild_widgets)
        self.item_views['properties'].force_rebuild_source.connect(
            self.rebuild_source)
        self.item_views['properties'].force_update_pages.connect(
            self.item_views['pages'].force_update)

    def init_models(self, file_name=None):
        """Initialize all data models."""
        value = self.sy_parameters['document'].value
        self.model = DataModel(value if len(value) > 0 else None)
        if file_name is not None:
            self.model.load(file_name)
        self.scales_model = ScaleItemModel(self.model)
        self.item_views['scales'].setModel(self.scales_model)
        self.page_model = PageItemModel(self.model)
        self.item_views['pages'].setModel(self.page_model)
        self.page_model.layoutChanged.connect(self.rebuild_widgets)
        self.page_model.rowsInserted[QtCore.QModelIndex, int, int].connect(
            self.rebuild_widgets)

    def init_window(self):
        """Initialize window geometry."""
        rect = QtGui.QApplication.desktop().availableGeometry()
        rect.adjust(64, 64, -64, -64)
        self.setGeometry(rect)

    def init_actions(self):
        def clear_model():
            self.init_models()
            self.init_views()
            self.rebuild_widgets()
            self.rebuild_source()

        def load_file():
            filename = QtGui.QFileDialog.getOpenFileName(
                self, 'Load Configuration')
            if len(filename[0]) > 0:
                self.init_models(filename[0])
                self.rebuild_widgets()
                self.rebuild_source()

        def save_file():
            pass

        def save_as_file():
            filename = QtGui.QFileDialog.getSaveFileName(
                self, 'Save Configuration As')
            if len(filename[0]) > 0:
                self.model.save(filename[0])

        self.clear_action = QtGui.QAction('Clear', self)
        self.clear_action.triggered.connect(clear_model)
        self.load_action = QtGui.QAction('Load', self)
        self.load_action.triggered.connect(load_file)
        self.save_action = QtGui.QAction('Save', self)
        self.save_action.triggered.connect(save_file)
        self.save_as_action = QtGui.QAction('Save As...', self)
        self.save_as_action.triggered.connect(save_as_file)

    def init_menu(self):
        """Add menu bar to window."""
        menu_bar = QtGui.QMenuBar()
        file_menu = QtGui.QMenu('File')
        file_menu.addAction(self.clear_action)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        menu_bar.addMenu(file_menu)

        settings_menu = QtGui.QMenu('Style')
        for style in list(QtGui.QStyleFactory.keys()):
            action = settings_menu.addAction(style)
            action.triggered.connect(functools.partial(self.set_style, style))

        menu_bar.addMenu(settings_menu)
        self.setMenuBar(menu_bar)

    @staticmethod
    def set_style(style_name):
        """
        Set GUI-style of application.
        :param style_name: Name of style.
        """
        app = QtGui.QApplication.instance()
        app.setStyle(style_name)

    @QtCore.Slot()
    def rebuild_widgets(self):
        """Rebuild all widgets."""
        if not self._rebuild_done:
            return
        self._rebuild_done = False
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.rebuild_source()
        QtGui.QApplication.processEvents()

        current_index = 0
        current_text = None
        current_stack_widget = self.root_widget.widget(0)
        wait_label = QtGui.QLabel('Redrawing plot area, please wait...')
        wait_label.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.root_widget.insertWidget(0, wait_label)
        self.root_widget.setCurrentIndex(0)
        QtGui.QApplication.processEvents()
        if current_stack_widget is not None:
            try:
                # Save current tab index such that we can return to the same
                # page again.
                if isinstance(current_stack_widget, QtGui.QTabWidget):
                    current_index = current_stack_widget.currentIndex()
                    current_text = current_stack_widget.tabText(current_index)
            except RuntimeError:
                pass
        new_stack_widget = builder.build(self.model.root,
                                         self.binding_context,
                                         'mpl')
        # This pattern keeps the widget size of the stack widget such that
        # sizes are not changed resulting in flickering or strange behavior
        # when the visible widget is changed.
        self.root_widget.addWidget(new_stack_widget)
        self.root_widget.removeWidget(current_stack_widget)
        self.root_widget.removeWidget(wait_label)
        wait_label.deleteLater()
        if current_stack_widget is not None:
            current_stack_widget.deleteLater()
        # If a page has been deleted the current index do not match the tab
        # text. If the tab text has changed we check if the index to the left
        # is correct. The UUID of the page is currently not used since the
        # model has already changed when this function is entered.
        if (current_index > 0 and
                new_stack_widget.tabText(current_index) != current_text and
                new_stack_widget.tabText(current_index - 1) == current_text):
            current_index -= 1
        new_stack_widget.setCurrentIndex(current_index)

        # Force update property view by setting its model again.
        self.item_views['properties'].setModel(
            self.item_views['properties'].model)

        QtGui.QApplication.processEvents()
        QtGui.QApplication.restoreOverrideCursor()
        self._rebuild_done = True

    @QtCore.Slot()
    def rebuild_source(self):
        if SHOW_JSON_MODEL:
            """Rebuild source view."""
            html = pygments.highlight(
                json.dumps(self.model.root.data, indent=2),
                pygments.lexers.get_lexer_by_name('json'),
                pygments.formatters.get_formatter_by_name('html', full=True))

            self.item_views['source'].setHtml(html)

        self.sy_parameters['document'].value = json.dumps(self.model.model)

    def switch_property_view(self, item):
        """
        Switch the current property view to what item contains.
        :param item: An object from the models module.
        """
        property_model = PropertyItemModel(item)
        self.item_views['properties'].setModel(property_model)
        if item is not None:
            self.docks['properties'].setWindowTitle('Properties for {}'.format(
                item.label))
        else:
            self.docks['properties'].setWindowTitle('Properties')

    def add_new_data_source(self):
        """Add new data source to model and update GUI."""
        data = models.create_empty_data_source(self.model.root)
        root_data = [x for x in self.model.root.children
                     if isinstance(x, models.RootData)][0]
        new_data_node = models.DataSource(data, root_data)
        models.insert_node(new_data_node, root_data)
        self.item_views['data'].update()
        self.data_source_model.force_update()
        self.rebuild_source()

    def add_new_scale(self):
        """Add new scale to model and update GUI."""
        scale = models.create_empty_scale(self.model.root)
        root_scales = [x for x in self.model.root.children
                       if isinstance(x, models.RootScales)][0]
        new_scale_node = models.RootScale(scale, root_scales)
        models.insert_node(new_scale_node, root_scales)
        self.item_views['scales'].update()
        self.scales_model.force_update()
        self.rebuild_source()


class ModelSourceView(QtGui.QTextBrowser):
    def __init__(self, parent=None):
        super(ModelSourceView, self).__init__(parent)
        self.setFontFamily('courier')

    def set_html(self, html):
        self.setHtml(html)

# Some views.


class ScaleView(QtGui.QTableView):
    data_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(ScaleView, self).__init__(parent)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setShowGrid(False)
        self.setGridStyle(QtCore.Qt.NoPen)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.context_menu = QtGui.QMenu(self)
        self.remove_action = QtGui.QAction('Delete', self)
        self.context_menu.addAction(self.remove_action)

    def launch_configuration(self, index):
        item = self.model().data(index, QtCore.Qt.UserRole)
        data = copy.deepcopy(item.data)
        dialog = ScaleConfigurationDialog(item, data, self)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            p = item.properties_as_dict()
            for key, value in six.iteritems(data):
                p[key].set(value)
            self.data_changed.emit()

    def mouseDoubleClickEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        self.launch_configuration(index)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Delete):
            self.remove_selected_items()
            event.accept()
        else:
            super(ScaleView, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        index_at_pointer = self.indexAt(event.pos())
        if not index_at_pointer.isValid():
            event.ignore()
            return
        result = self.context_menu.exec_(event.globalPos())
        if result == self.remove_action:
            self.remove_selected_items()
            event.accept()
        else:
            event.ignore()

    def remove_selected_items(self):
        index_list = self.selectedIndexes()
        # We must sort the indices in reverse row order, otherwise the rows
        # are can become invalid.
        index_list.sort(key=lambda x: x.row(), reverse=True)
        for index in index_list:
            self.model().removeRow(index.row())
        self.data_changed.emit()


class ImageWidget(QtGui.QWidget):
    def __init__(self, item, parent=None):
        """
        Constructor.
        :param item: Dictionary containing:
                     type: type of item
                     label: item label
                     icon: item icon
                     See PageItems for details.
        :param parent: Parent widget.
        """
        super(ImageWidget, self).__init__(parent)
        self.item = item

        if item['type'].decode('utf8') == 'layer':
            icon_name = plugins.get_layer_meta(self.item['kind'])['icon']
        else:
            icon_name = self.item['icon']
        self.icon = icons.create_icon(icon_name)
        self.setMinimumHeight(icons.SIZE)
        self.setMaximumHeight(icons.SIZE)
        self.setMinimumWidth(icons.SIZE)
        self.setMaximumWidth(icons.SIZE)
        self._drag_start_position = QtCore.QPoint(0, 0)
        self.setToolTip(self.item['label'])

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        self.icon.paint(p, self.rect())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if ((event.pos() - self._drag_start_position).manhattanLength() <
                QtGui.QApplication.startDragDistance()):
            return
        drag = QtGui.QDrag(self)
        data = QtCore.QMimeData()
        if self.item['type'].decode("utf-8") == 'layer':
            data.setData(MIME_LAYOUT_TREE_LAYER_TYPE, self.item['kind'])
        data.setData(MIME_LAYOUT_TREE_NEW_ITEM, self.item['type'])
        drag.setMimeData(data)
        drag.setPixmap(self.icon.pixmap(icons.SIZE, icons.SIZE))

        drag.exec_(QtCore.Qt.CopyAction)


class PageViewToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(PageViewToolBar, self).__init__(parent)

        self.setWindowTitle('Items')

        items = [
            {
                'type': b'page',
                'label': 'Page',
                'icon': icons.SvgIcon.page
            },
            {
                'type': b'layout',
                'label': 'Layout',
                'icon': icons.SvgIcon.layout
            },
            {
                'type': b'textbox',
                'label': 'TextBox',
                'icon': icons.SvgIcon.text
            },
            {
                'type': b'image',
                'label': 'Image',
                'icon': icons.SvgIcon.picture
            },
            {
                'type': b'graph',
                'label': 'Graph 2D',
                'icon': icons.SvgIcon.plot
            }
        ]

        self.add_widgets(items)

    def add_widgets(self, items):
        self.addWidget(QtGui.QLabel(self.windowTitle()))
        for item in items:
            if item['type'] == 'separator':
                self.addSeparator()
            else:
                self.addWidget(ImageWidget(item))


class PageView2DToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        super(PageView2DToolBar, self).__init__(parent)
        self.setWindowTitle('Layers (2D)')

        items = []

        for layer_name in plugins.available_plugins['layers']:
            items.append({
                'type': b'layer',
                'kind': layer_name,
                'label': layer_name.title(),
                'icon': icons.SvgIcon.layer
            })

        self.add_widgets(items)

    def add_widgets(self, items):
        self.addWidget(QtGui.QLabel(self.windowTitle()))
        for item in items:
            if item['type'] == 'separator':
                self.addSeparator()
            else:
                self.addWidget(ImageWidget(item))


class ScaleViewToolBar(QtGui.QToolBar):
    new_scale_requested = QtCore.Signal()

    def __init__(self, parent=None):
        super(ScaleViewToolBar, self).__init__(parent)
        self.setMaximumHeight(icons.SIZE)
        self.new_scale_action = QtGui.QAction(
            icons.create_icon(icons.SvgIcon.plus), 'scale', self)
        self.addAction(self.new_scale_action)


class PageView(QtGui.QTreeView):
    item_selected = QtCore.Signal(object)
    force_rebuild = QtCore.Signal()
    force_rebuild_source = QtCore.Signal()

    def __init__(self, parent=None):
        super(PageView, self).__init__(parent)
        self.setRootIsDecorated(True)
        self.header().setResizeMode(QtGui.QHeaderView.Stretch)
        self.header().setVisible(False)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

        self.setUpdatesEnabled(True)
        self.setMouseTracking(True)

        self.context_menu = QtGui.QMenu(self)
        self.remove_action = QtGui.QAction('Delete', self)
        self.context_menu.addAction(self.remove_action)

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Delete):
            self.remove_selected_items()
            event.accept()
        else:
            super(PageView, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        index_at_pointer = self.indexAt(event.pos())
        if not index_at_pointer.isValid():
            event.ignore()
            return
        result = self.context_menu.exec_(event.globalPos())
        if result == self.remove_action:
            self.remove_selected_items()
            event.accept()
        else:
            event.ignore()

    def remove_selected_items(self):
        index_list = self.selectedIndexes()
        # We must sort the indices in reverse row order, otherwise the rows
        # are can become invalid.
        index_list.sort(key=lambda x: x.row(), reverse=True)
        deletable_indices = [i for i in index_list
                             if models.NodeTags.is_deletable in
                             self.model().index_to_item(i).tags]
        for index in deletable_indices:
            self.model().removeRow(index.row(), index.parent())
        self.force_rebuild.emit()
        self.force_rebuild_source.emit()

    def setModel(self, model):
        super(PageView, self).setModel(model)
        selection_model = self.selectionModel()
        selection_model.selectionChanged[QtGui.QItemSelection,
                                         QtGui.QItemSelection].connect(
            self.handle_selection_changed)
        model.layoutChanged.connect(selection_model.clear)
        model.rowsInserted[QtCore.QModelIndex, int, int].connect(
            selection_model.clear)
        model.new_item_inserted[QtCore.QModelIndex].connect(
            self.handle_new_item_inserted)
        model.layoutChanged.connect(self.force_update)

    def handle_new_item_inserted(self, index):
        self._expandParents(index.child(0, 0))

    def _expandParents(self, index):
        if not index.isValid():
            return
        self._expandParents(index.parent())
        self.setExpanded(index, True)

    def handle_selection_changed(self, selected, deselected):
        index_list = selected.indexes()
        try:
            item = self.model().index_to_item(index_list[0])
            if len(item.properties) > 0:
                self.item_selected.emit(item)
            else:
                self.item_selected.emit(None)
        except IndexError:
            self.item_selected.emit(None)

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
        # For our case removeRows should never be called when
        # dropping something.
        super(PageView, self).dropEvent(event)
        event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()

    def dragMoveEvent(self, event):
        """
        Show indicator whether the dragged item can be dropped on the current
        item.
        """
        def class_of_item(mime_data_):
            item_class_ = None
            # TODO(stefan): Reproducing some code from dropMimeData in model
            if mime_data.hasFormat(MIME_LAYOUT_TREE_ITEM_ID):
                python_id = int(mime_data_.data(
                    MIME_LAYOUT_TREE_ITEM_ID).data())
                item = self.model().model.root.find_node_by_python_id(
                    python_id)
                item_class_ = type(item)
            elif mime_data.hasFormat(MIME_LAYOUT_TREE_NEW_ITEM):
                item_type = six.text_type(
                    mime_data_.data(MIME_LAYOUT_TREE_NEW_ITEM))
                item_class_ = self.model().ITEM_TYPE_TO_CLASS[item_type]
            return item_class_

        super(PageView, self).dragMoveEvent(event)
        index = self.indexAt(event.pos())
        drop_indicator_position = self.dropIndicatorPosition()
        try:
            parent_item = index.model().data(index, QtCore.Qt.UserRole)
        except AttributeError:
            parent_item = None
        if parent_item is None:
            mime_data = event.mimeData()
            item_class = class_of_item(mime_data)
            event.accept()
            return
        if drop_indicator_position != QtGui.QAbstractItemView.OnItem:
            # If the drop indicator is not on the item we need to get the
            # parent item in the tree instead.
            parent_item = parent_item.parent
        mime_data = event.mimeData()
        item_class = class_of_item(mime_data)
        if (isinstance(parent_item, models.Page) and
                parent_item.has_children() and
                item_class.__name__ == 'Layout'):
            # Only one layout per page is allowed
            event.ignore()
        else:
            event.accept()


class DataModel(object):
    """Convenience wrapper around the model coming from the models module."""

    def __init__(self, json_model=None):
        self.instance = uuid.uuid4().bytes
        if json_model is None:
            self.model = models.create_empty_data()
        else:
            self.model = json.loads(json_model)
        self.root = models.Root(self.model)

    def load(self, filename):
        # Filter comments from JSON-file since those are not allowed.
        comment_re = re.compile(
            '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
            re.DOTALL | re.MULTILINE)
        with open(filename, 'r') as f:
            content = ''.join(f.readlines())
        match = comment_re.search(content)
        while match:
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
        # self.json = content
        self.model = json.loads(content)
        self.root = models.Root(self.model)

    def save(self, filename):
        content = json.dumps(self.model, indent=2)
        with open(filename, 'w') as f:
            f.write(content)


@mock_wrap
class BaseTableModel(QtCore.QAbstractTableModel):
    def __init__(self, model, root_class):
        super(BaseTableModel, self).__init__()
        self.model = model
        self.root_class = root_class
        self._index_to_weak_item = {}

    def force_update(self):
        self.layoutChanged.emit()

    def root_item(self):
        return [x for x in self.model.root.children
                if isinstance(x, self.root_class)][0]

    def index_to_item(self, index):
        weak_item = self._index_to_weak_item.get(index.internalId(), None)
        return weak_item() if weak_item is not None else None

    def rowCount(self, parent_index):
        if not parent_index.isValid():
            return self.root_item().row_count()
        return 0

    def columnCount(self, parent_index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.index_to_item(index)
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                try:
                    return item.label
                except KeyError:
                    return '*** No Label ***'
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return icons.create_icon(item.icon)
        elif role == QtCore.Qt.UserRole:
            return item
        return None

    def flags(self, index):
        if not index.isValid():
            return 0
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsDragEnabled |
                QtCore.Qt.ItemIsSelectable)

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QtCore.QModelIndex()

        if not parent_index.isValid():
            item = self.root_item().child(row)
        else:
            return QtCore.QModelIndex()

        return self.createIndex(row, column, item)

    def createIndex(self, row, column, item):
        index = super(BaseTableModel, self).createIndex(row, column, item)
        self._index_to_weak_item[index.internalId()] = weakref.ref(item)
        return index


class ScaleItemModel(BaseTableModel):
    def __init__(self, model):
        super(ScaleItemModel, self).__init__(model, models.RootScales)

    def removeRows(self, row, count, parent_index=QtCore.QModelIndex()):
        scale_items = [
            self.data(self.index(x, 0, parent_index), QtCore.Qt.UserRole)
            for x in six.moves.range(row, row + count)]
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for scale_item in scale_items:
            models.remove_node(scale_item)
        self.endRemoveRows()
        return True


@mock_wrap
class BasePageItemModel(QtCore.QAbstractItemModel):
    def __init__(self, model, root_class):
        super(BasePageItemModel, self).__init__()
        self.model = model
        self.root_class = root_class
        self._index_to_weak_item = {}

    def force_update(self):
        self.layoutChanged.emit()

    def index_to_item(self, index):
        weak_item = self._index_to_weak_item.get(index.internalId(), None)
        return weak_item() if weak_item is not None else None

    def root_item(self):
        return [x for x in self.model.root.children
                if isinstance(x, self.root_class)][0]

    def columnCount(self, parent_index):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.index_to_item(index)
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                try:
                    return item.label
                except KeyError:
                    return '*** No Label ***'
            else:
                try:
                    return item.editor.get()
                except (AttributeError, KeyError):
                    pass
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return icons.create_icon(item.icon)
        elif role == QtCore.Qt.UserRole:
            return item
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            item = self.index_to_item(index)
            item.editor.set(value)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsDropEnabled
        item = self.index_to_item(index)
        flags = QtCore.Qt.ItemIsEnabled
        if index.column() == 0:
            if len(item.properties) > 0:
                flags |= QtCore.Qt.ItemIsSelectable
            if models.NodeTags.is_rearrangable in item.tags:
                flags |= (QtCore.Qt.ItemIsDragEnabled |
                          QtCore.Qt.ItemIsSelectable)
            if models.NodeTags.is_container in item.tags:
                flags |= QtCore.Qt.ItemIsDropEnabled
        return flags

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QtCore.QModelIndex()

        if not parent_index.isValid():
            parent_item = self.root_item()
        else:
            parent_item = self.data(parent_index, QtCore.Qt.UserRole)

        child_list = self.children_of_parent_item(parent_item)

        if len(child_list) > 0:
            child_item = child_list[row]
        else:
            return QtCore.QModelIndex()

        return self.createIndex(row, column, child_item)

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        child_item = self.index_to_item(index)

        parent_item = self.parent_of_child_item(child_item)

        if parent_item is None:
            return QtCore.QModelIndex()
        parent_parent_item = parent_item.parent

        if parent_parent_item is None:
            row = 0
        else:
            row = parent_parent_item.index(parent_item)

        return self.createIndex(row, 0, parent_item)

    def rowCount(self, parent_index):
        if parent_index.column() > 0:
            return 0

        if not parent_index.isValid():
            parent_item = self.root_item()
        else:
            parent_item = self.index_to_item(parent_index)

        # row_count = parent_item.row_count()
        row_count = len(self.children_of_parent_item(parent_item))

        return row_count

    def createIndex(self, row, column, item):
        index = super(BasePageItemModel, self).createIndex(row, column, item)
        self._index_to_weak_item[index.internalId()] = weakref.ref(item)
        return index

    @staticmethod
    def children_of_parent_item(parent_item):
        """
        Find children of the given parent item. This function is used to be
        able to skip unnecessary levels in the visible tree, but which are
        necessary in the underlying data model.
        :param parent_item: Parent item to find children for.
        :return: List of children.
        """
        # Key is parent class and value is tuple of child classes which should
        # be invisible in the tree. The children of the invisible classes
        # should listed in parent_of_child_item below, otherwise the tree
        # structure is invalid.
        class_pairs = {models.Graph: (models.GraphDimensions,),
                       models.GraphLayer: (models.GraphLayerData,)}

        # Check if the parent item is among the keys, return the children to
        # be invisible.
        child_class = None
        for key, value in six.iteritems(class_pairs):
            if isinstance(parent_item, key):
                child_class = value

        if child_class is None:
            child_list = parent_item.children
        else:
            # Append grandchildren to list of children if we encounter an
            # invisible child, otherwise we just use take the child as is.
            child_list = []
            for child in parent_item.children:
                if isinstance(child, child_class):
                    for grandchild in child.children:
                        child_list.append(grandchild)
                else:
                    child_list.append(child)

        return child_list

    @staticmethod
    def parent_of_child_item(child_item):
        child_classes = (models.GraphDimension,
                         models.GraphLayerDataDimension)

        # We can only skip one level right now, and there is no need to skip
        # more than this anyway.
        if isinstance(child_item, child_classes):
            return child_item.parent.parent
        return child_item.parent


class PageItemModel(BasePageItemModel):
    new_item_inserted = QtCore.Signal(QtCore.QModelIndex)

    ITEM_TYPE_TO_CLASS = {
        'page': models.Page,
        'layout': models.Layout,
        'textbox': models.TextBox,
        'image': models.Image,
        'graph': models.Graph,
        'layer': models.GraphLayer
    }

    def __init__(self, model):
        super(PageItemModel, self).__init__(model, models.Pages)
        self.setSupportedDragActions(QtCore.Qt.MoveAction)

        # Flag for workaround for Qt bug #6679.
        # https://bugreports.qt.io/browse/QTBUG-6679
        # See dropEvent in PageView for the rest of the workaround.
        self.drop_success = False

    def mimeData(self, index_list):
        assert len(index_list) == 1
        index = index_list[0]
        item = self.data(index, QtCore.Qt.UserRole)
        data = QtCore.QMimeData()
        data.setData(MIME_INSTANCE, self.model.instance)
        data.setData(
            MIME_LAYOUT_TREE_ITEM_ID, str('{}'.format(id(item))))
        return data

    def mimeTypes(self):
        return (MIME_LAYOUT_TREE_ITEM_ID,
                MIME_INSTANCE,
                MIME_LAYOUT_TREE_NEW_ITEM)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def dropMimeData(self, mime_data, drop_action, row, column, parent_index):
        self.drop_success = False

        # Make sure that data is coming from the same instance.
        if (mime_data.hasFormat(MIME_INSTANCE) and
                mime_data.data(MIME_INSTANCE).data() != self.model.instance):
            return False

        if drop_action == QtCore.Qt.IgnoreAction:
            self.drop_success = True
            return True
        parent_item = self.data(parent_index, QtCore.Qt.UserRole)
        if parent_item is None:
            parent_item = [x for x in self.model.root.children
                           if isinstance(x, models.Pages)][0]

        if row != -1:
            begin_row = row
        elif parent_index.isValid():
            begin_row = parent_index.row()
        else:
            begin_row = self.rowCount(QtCore.QModelIndex())

        if mime_data.hasFormat(MIME_LAYOUT_TREE_ITEM_ID):
            # Moving something inside the tree.
            python_id = (
                mime_data.data(MIME_LAYOUT_TREE_ITEM_ID).data())
            python_id = int(python_id)
            item = self.model.root.find_node_by_python_id(python_id)

            # We cannot add something such that it becomes a child of itself.
            if models.is_parent_same_node(parent_item, item):
                return False

            # The parent must allow the item to be a child.
            if (item is None or
                    item.__class__ not in parent_item.valid_children):
                return False

            self.layoutAboutToBeChanged.emit()
            models.move_node(item, parent_item, begin_row)
            self.layoutChanged.emit()

        if mime_data.hasFormat(MIME_LAYOUT_TREE_NEW_ITEM):
            # Adding something to the tree.
            item_type = str(mime_data.data(MIME_LAYOUT_TREE_NEW_ITEM))
            item_class = self.ITEM_TYPE_TO_CLASS[item_type]
            if item_class not in parent_item.valid_children:
                self._autoCreate(
                    item_class, item_type, mime_data, parent_item,
                    parent_index, begin_row)
            else:
                self._createItem(
                    item_class, item_type, mime_data, parent_item,
                    parent_index, begin_row)
            if parent_index.isValid():
                self.new_item_inserted.emit(parent_index)
            else:
                self.new_item_inserted.emit(
                    self.index(begin_row, 0, parent_index))

        self.drop_success = True
        return True

    def _autoCreate(
        self, item_class, item_type, mime_data, parent_item, parent_index,
            begin_row):
        page_class = models.VIEW_TO_CLASS['page']
        layout_class = models.VIEW_TO_CLASS['layout']
        for item_type in models.NODE_DEPENDENCIES[item_class]:
            item_class = models.VIEW_TO_CLASS[item_type]
            parent_class = parent_item.__class__
            if ((parent_class == layout_class and item_class == page_class) or
                    item_class == parent_class):
                # Skip dependency items already in tree
                if parent_class == page_class and parent_item.has_children():
                    # If the page has a layout, use it.
                    parent_item = parent_item.child(0)
                continue
            if item_type == 'layer':
                parent_item = parent_item.child(1)
            parent_item = self._createItem(
                item_class, item_type, mime_data, parent_item, parent_index,
                begin_row)

    def _createItem(
        self, item_class, item_type, mime_data, parent_item, parent_index,
            begin_row):
        if item_type == 'layer':
            # Change default data based on layer type.
            layer_type = mime_data.data(MIME_LAYOUT_TREE_LAYER_TYPE)
            layer_meta = plugins.get_layer_meta(
                layer_type.data().decode('utf8'))
            item_class.default_data = layer_meta['default-data']
        new_item = item_class.create_empty_instance(parent_item)
        self.beginInsertRows(parent_index, begin_row, begin_row)
        models.insert_node(new_item, parent_item, begin_row)
        self.endInsertRows()
        return new_item

    def insertRows(self, row, count, parent_index=QtCore.QModelIndex()):
        return True

    def removeRows(self, row, count, parent_index=QtCore.QModelIndex()):
        items = [
            self.data(self.index(x, 0, parent_index), QtCore.Qt.UserRole)
            for x in six.moves.range(row, row + count)]
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for item in items:
            models.remove_node(item)
        self.endRemoveRows()
        return True


class PropertyView(QtGui.QScrollArea):
    force_rebuild = QtCore.Signal()             # Rebuild widgets.
    force_rebuild_source = QtCore.Signal()      # Rebuild source code view.
    force_update_pages = QtCore.Signal()        # Update page view.

    update_pending = False
    rebuild_pending = False

    def __init__(self, parent=None):
        super(PropertyView, self).__init__(parent)
        self.row_offset = 2
        self.label_column = 0
        self.editor_column = 1
        self.checkbox_column = 2

        self.setMinimumWidth(300)
        self.setWidgetResizable(True)
        self.container = QtGui.QWidget()
        self.setWidget(self.container)
        self.vbox_layout = QtGui.QVBoxLayout()
        self.grid_layout = QtGui.QGridLayout()
        self.grid_layout.setVerticalSpacing(1)
        self.container.setLayout(self.vbox_layout)
        self.vbox_layout.addLayout(self.grid_layout)
        self.vbox_layout.addStretch()
        self.model = None
        self._first_init = True

    def setModel(self, model):
        self.model = model

        while self.grid_layout.count() > 0:
            child = self.grid_layout.takeAt(0)
            child.widget().deleteLater()
        if not self._first_init:
            last_index = self.vbox_layout.count() - 1
            widget = self.vbox_layout.itemAt(last_index)
            if isinstance(widget, QtGui.QSpacerItem):
                self.vbox_layout.takeAt(last_index)
        else:
            self._first_init = False

        # Headers.
        self.grid_layout.addWidget(QtGui.QLabel('Property Name'), 0, 0)
        self.grid_layout.addWidget(QtGui.QLabel('Property Value'), 0, 1)
        self.grid_layout.addWidget(PropertyView.BindIcon(), 0, 2)

        self.grid_layout.addWidget(PropertyView.HLine(), 1, 0, 1, 3,
                                   QtCore.Qt.AlignVCenter)

        # We cannot add anything else if there is no model present.
        if model is None:
            return

        add_stretch = True
        for row in six.moves.range(
                0, self.model.rowCount(QtCore.QModelIndex())):
            label_index = self.model.index(row, self.label_column,
                                           QtCore.QModelIndex())
            value_index = self.model.index(row, self.editor_column,
                                           QtCore.QModelIndex())
            label_text = self.model.data(label_index, QtCore.Qt.DisplayRole)
            item = self.model.data(value_index, QtCore.Qt.UserRole)
            if item.has_binding:
                scale_binding = item.scale_binding
                value_widget, _ = self.create_bind_button(
                    value_index, '{} : {}'.format(scale_binding.data_id,
                                                  scale_binding.scale_id))
            else:
                value_widget = self.create_editor(value_index)
                if isinstance(value_widget, QtGui.QTextEdit):
                    add_stretch = False
            self.grid_layout.addWidget(
                QtGui.QLabel(label_text),
                row + self.row_offset, self.label_column)
            self.grid_layout.addWidget(value_widget, row + self.row_offset,
                                       self.editor_column)

            if item.is_bindable:
                bind_button = PropertyView.ScaleBindButton()
                bind_button.setChecked(item.has_binding)
                self.grid_layout.addWidget(
                    QtGui.QLabel('Scale'), row + self.row_offset,
                    self.checkbox_column)
                self.grid_layout.addWidget(
                    bind_button, row + self.row_offset,
                    self.checkbox_column + 1)
                bind_button.toggled[bool].connect(
                    functools.partial(self.handle_bind_button, row))
        if add_stretch:
            self.vbox_layout.addStretch()

        self.grid_layout.setColumnStretch(self.editor_column, 1)

    def create_bind_button(self, model_index, label=None):
        button = QtGui.QPushButton()
        if label is not None:
            button.setText(label)
        button.setIcon(icons.create_icon('bind'))
        callback = functools.partial(self.launch_bind_dialog,
                                     model_index, button)
        button.clicked.connect(callback)
        return button, callback

    def remove_previous_widget(self, row):
        """
        Remove a widget in the grid.
        :param row: Row in data model, offset is added to grid row.
        """
        old_item = self.grid_layout.itemAtPosition(row + self.row_offset,
                                                   self.editor_column)
        old_item.widget().deleteLater()
        self.grid_layout.removeItem(old_item)

    def handle_bind_button(self, row, checked):
        value_index = self.model.index(row, self.editor_column,
                                       QtCore.QModelIndex())
        item = self.model.data(value_index, QtCore.Qt.UserRole)
        ok = True
        if checked:
            w, callback = self.create_bind_button(value_index)
            if item.last_scale_binding is None:
                # Only show dialog if there is no previous binding.
                ok = callback()
            else:
                item.set_scale_binding(item.last_scale_binding.data_id,
                                       item.last_scale_binding.scale_id)
                if item.has_valid_binding():
                    w.setText('{} : {}'.format(item.scale_binding.data_id,
                                               item.scale_binding.scale_id))
                else:
                    # If we have no valid binding we have to start over again.
                    item.clear_scale_binding()
                    item.last_scale_binding = None
                    ok = callback()
        else:
            item.clear_scale_binding()
            w = self.create_editor(value_index)
        if ok:
            self.remove_previous_widget(row)
            self.grid_layout.addWidget(w, row + self.row_offset, 1)
        self.force_rebuild_source.emit()
        self.force_rebuild.emit()

    def model(self):
        return self.model

    def launch_bind_dialog(self, index, widget):
        """
        Launch a dialog to make it possible to change data binding
        configuration.
        :param index: QModelIndex for the item to bind.
        :param widget: pushbutton which shows the current binding.
        :returns: True if everything went ok.
        """
        item = self.model.data(index, QtCore.Qt.UserRole)
        dialog = PropertyView.BindScaleDialog(item, self)
        result = dialog.exec_()
        if result == QtGui.QDialog.Accepted:
            widget.setText('{} : {}'.format(dialog.data_id,
                                            dialog.scale_id))
            item.set_scale_binding(dialog.data_id, dialog.scale_id)
            self.force_rebuild_source.emit()
            self.force_rebuild.emit()
        elif result == QtGui.QDialog.Rejected:
            return True

        if not item.has_valid_binding():
            item.clear_scale_binding()
            layout_item = self.grid_layout.itemAtPosition(
                index.row() + self.row_offset, self.checkbox_column)
            checkbox = layout_item.widget()
            checkbox.setChecked(False)
            self.remove_previous_widget(index.row())
            w = self.create_editor(index)
            self.grid_layout.addWidget(w, index.row() + self.row_offset,
                                       self.editor_column)
            return False
        return True

    class BindScaleDialog(QtGui.QDialog):
        def __init__(self, property_node, parent=None):
            super(PropertyView.BindScaleDialog, self).__init__(parent)
            self.setWindowTitle('Data and Scale Binding')

            self.data_combo = None
            self.scale_combo = None

            scale_binding = property_node.scale_binding
            if scale_binding is None:
                self.data_id = None
                self.scale_id = None
            else:
                self.data_id = scale_binding.data_id
                self.scale_id = scale_binding.scale_id

            layout = QtGui.QVBoxLayout()
            self.setLayout(layout)
            self.container = self.build_form(property_node)
            layout.addWidget(self.container)
            self.button_box = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
            layout.addWidget(self.button_box)

            self.button_box.button(
                QtGui.QDialogButtonBox.Ok).clicked.connect(self.accept)
            self.button_box.button(
                QtGui.QDialogButtonBox.Cancel).clicked.connect(self.reject)

            def move_window():
                cursor_position = QtGui.QCursor.pos()
                self.move(int(cursor_position.x() - self.width() / 2),
                          int(cursor_position.y() - self.height() / 2))

            # Single shot needed to allow the dialog window to resize and
            # layout properly, otherwise the width and height are invalid.
            QtCore.QTimer.singleShot(0, move_window)

        def build_form(self, scale_model_node):

            def set_data_id(data_list_, value):
                self.data_id = data_list_[value]

            def set_scale_id(scale_list_, value):
                self.scale_id = scale_list_[value]

            w = QtGui.QWidget()
            layout = QtGui.QFormLayout()
            layout.setFieldGrowthPolicy(
                QtGui.QFormLayout.AllNonFixedFieldsGrow)
            w.setLayout(layout)

            # Build combo box for data selection.
            self.data_combo = QtGui.QComboBox()
            data_list = data_manager.data_source.signal_list()
            for key in data_list:
                self.data_combo.addItem(key)
            try:
                current_data_index = (data_list.index(self.data_id)
                                      if self.data_id is not None else -1)
            except ValueError:
                current_data_index = -1
            self.data_combo.setCurrentIndex(current_data_index)
            layout.addRow('Data Source', self.data_combo)
            self.data_combo.currentIndexChanged[int].connect(
                functools.partial(set_data_id, data_list))

            # Build combo box for scale selection.
            self.scale_combo = QtGui.QComboBox()
            scale_list = models.list_of_scales(scale_model_node)
            for key in scale_list:
                self.scale_combo.addItem(key)
            try:
                current_scale_index = (scale_list.index(self.scale_id)
                                       if self.scale_id is not None else -1)
            except ValueError:
                current_scale_index = -1
            self.scale_combo.setCurrentIndex(current_scale_index)
            layout.addRow('Scale', self.scale_combo)
            self.scale_combo.currentIndexChanged[int].connect(
                functools.partial(set_scale_id, scale_list))
            return w

    class BindIcon(QtGui.QWidget):
        def __init__(self, parent=None):
            super(PropertyView.BindIcon, self).__init__(parent)
            self.setMinimumWidth(12)
            self.setMinimumHeight(12)

        def paintEvent(self, event):
            p = QtGui.QPainter(self)
            icon = icons.create_icon('bind')
            rect = self.rect()
            width = height = min(rect.width(), rect.height())
            x = int((rect.width() - width) / 2)
            y = int((rect.height() - height) / 2)
            icon.paint(p, x, y, width, height)

    class HLine(QtGui.QWidget):
        def __init__(self, parent=None):
            super(PropertyView.HLine, self).__init__(parent)
            self.setMaximumHeight(3)
            self.setMinimumHeight(3)

        def paintEvent(self, event):
            p = QtGui.QPainter(self)
            rect = self.rect()
            palette = QtGui.QApplication.palette()
            p.setPen(palette.dark().color())
            p.drawLine(rect.x(), 1, rect.right(), 1)

    class ScaleBindButton(QtGui.QPushButton):
        def __init__(self, parent=None):
            super(PropertyView.ScaleBindButton, self).__init__(parent)
            self.setCheckable(True)
            self.setMaximumWidth(self.check_box_rect().width() + 4)

        def mousePressEvent(self, event):
            rect = self.check_box_rect()
            if rect.contains(event.pos()):
                super(PropertyView.ScaleBindButton, self).mousePressEvent(
                    event)

        def sizeHint(self):
            return self.check_box_rect().size()

        def paintEvent(self, event):
            style = QtGui.QApplication.style()
            p = QtGui.QPainter(self)
            options = QtGui.QStyleOptionButton()
            options.state = (QtGui.QStyle.State_Enabled |
                             QtGui.QStyle.State_Active)
            if self.isChecked():
                options.state |= QtGui.QStyle.State_On
            else:
                options.state |= QtGui.QStyle.State_Off
            options.rect = self.check_box_rect()
            style.drawControl(QtGui.QStyle.CE_CheckBox, options, p)

        def check_box_rect(self):
            check_box_style_option = QtGui.QStyleOptionButton()
            check_box_rect = QtGui.QApplication.style().subElementRect(
                QtGui.QStyle.SE_CheckBoxIndicator, check_box_style_option,
                None)
            check_box_point = QtCore.QPoint(
                int((self.rect().width() - check_box_rect.height()) / 2),
                int((self.rect().height() - check_box_rect.height()) / 2))
            return QtCore.QRect(check_box_point, check_box_rect.size())

    class ColorEditor(QtGui.QWidget):
        color_changed = QtCore.Signal(six.text_type)

        def __init__(self, color, parent=None):
            super(PropertyView.ColorEditor, self).__init__(parent)
            self._color = color
            self.dialog = QtGui.QColorDialog()
            self.dialog.setCurrentColor(color)
            self.setMinimumHeight(24)

        def show_dialog(self):
            result = self.dialog.exec_()
            if result == QtGui.QDialog.Accepted:
                self._color = self.dialog.currentColor().name()
            self.color_changed.emit(self._color)

        def set_color(self, color):
            self._color = color

        def get_color(self):
            return self._color

        def mousePressEvent(self, event):
            if event.button() != QtCore.Qt.LeftButton:
                return
            hotbox = QtCore.QRectF(self.rect().adjusted(1, 1, -1, -1))
            hotbox.setWidth(hotbox.height())
            if hotbox.contains(event.pos()):
                self.show_dialog()

        def paintEvent(self, event):
            p = QtGui.QPainter(self)
            p.setRenderHint(QtGui.QPainter.Antialiasing, True)
            rect = QtCore.QRectF(self.rect().adjusted(1, 1, -1, -1))
            rect.setWidth(rect.height())
            circle = QtGui.QPainterPath()
            circle.addEllipse(rect)
            p.fillPath(circle, QtGui.QColor(self._color))
            p.setPen(QtCore.Qt.black)
            p.drawPath(circle)

        color = QtCore.Property(QtGui.QColor, get_color, set_color)

    def _create_text_editor(self, editor, index):
        widget = QtGui.QLineEdit()
        widget.setText(editor.get())

        def write_string(editor_, widget_, index_, model):
            value = widget_.text()
            model.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.editingFinished.connect(
            functools.partial(write_string, editor, widget,
                              index, self.model))
        return widget

    def _create_textbox_editor(self, editor, index):
        widget = QtGui.QTextEdit()
        widget.setPlainText(editor.get())
        size_policy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        widget.setSizePolicy(size_policy)
        widget.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)

        def write_string(editor_, widget_, index_, model):
            value = widget_.toPlainText()
            model.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.textChanged.connect(
            functools.partial(write_string, editor, widget,
                              index, self.model))
        return widget

    def _create_integer_editor(self, editor, index):
        widget = QtGui.QSpinBox()
        if editor.value_range is not None:
            widget.setRange(editor.value_range['min'],
                            editor.value_range['max'])
            widget.setSingleStep(editor.value_range['step'])
        widget.setValue(editor.get())

        def write_integer(editor_, widget_, index_, model):
            value = widget_.value()
            model.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.editingFinished.connect(
            functools.partial(write_integer, editor, widget,
                              index, self.model))
        return widget

    def _create_float_editor(self, editor, index):
        if editor.value_range is not None:
            widget = QtGui.QDoubleSpinBox()
            widget.setRange(editor.value_range['min'],
                            editor.value_range['max'])
            widget.setSingleStep(editor.value_range['step'])
            widget.setValue(editor.get())

            def write_float(editor_, widget_, index_, model):
                value = widget_.value()
                model.setData(index_, value, QtCore.Qt.EditRole)
                self.process_updates(editor_)
        else:
            widget = QtGui.QLineEdit()
            validator = QtGui.QDoubleValidator()
            widget.setValidator(validator)
            widget.setText(QtCore.QLocale().toString(editor.get()))

            def write_float(editor_, widget_, index_, model):
                value, ok = QtCore.QLocale().toDouble(widget_.text())
                if not ok:
                    # Fall back to interpreting the text in the C locale
                    value, ok = QtCore.QLocale('C').toDouble(widget_.text())
                if not ok:
                    # If all else fails (empty line edit?) set value to zero
                    value = 0.0
                model.setData(index_, value, QtCore.Qt.EditRole)
                self.process_updates(editor_)

        widget.editingFinished.connect(
            functools.partial(write_float, editor, widget,
                              index, self.model))
        return widget

    def _create_color_editor(self, editor, index):
        widget = PropertyView.ColorEditor(editor.get())

        def write_color(editor_, index_, model, value):
            model.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)
            self.update()

        widget.color_changed[six.text_type].connect(
            functools.partial(write_color, editor, index, self.model))
        return widget

    def _create_boolean_editor(self, editor, index):
        widget = QtGui.QComboBox()
        widget.addItem('false')
        widget.addItem('true')
        widget.setCurrentIndex(1 if editor.get() else 0)

        def write_boolean(editor_, index_, model, value):
            model.setData(index_, bool(value), QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.currentIndexChanged[int].connect(
            functools.partial(write_boolean, editor, index, self.model))
        return widget

    def _create_immutable_list_editor(self, editor, index, item):
        widget = QtGui.QComboBox()
        for option_item in item.editor.options():
            widget.addItem(option_item)
        # Handle case when an option might have disappeared.
        try:
            if editor.options()[editor.current_index] != editor.get():
                editor.current_index = -1
        except IndexError:
            editor.current_index = -1
        widget.setCurrentIndex(editor.current_index)

        def write_immutable_list(editor_, index_, model, current_index):
            try:
                text_value = editor_.options()[current_index]
            except IndexError:
                text_value = None
            model.setData(index_, text_value, QtCore.Qt.EditRole)
            editor_.current_index = current_index
            self.process_updates(editor_)

        widget.currentIndexChanged[int].connect(
            functools.partial(write_immutable_list, editor, index,
                              self.model))
        return widget

    def _create_image_editor(self, editor, index):
        def select_image_file(editor_, edit_widget_, index_):
            result = QtGui.QFileDialog.getOpenFileName(self, 'Select image')
            if result is not None:
                text = result[0]
                edit_widget_.setText(text)
                self.model.setData(index_, text, QtCore.Qt.EditRole)
                self.process_updates(editor_)

        def write_string(editor_, widget_, index_):
            value = widget_.text()
            self.model.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        top_widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        top_widget.setLayout(layout)

        edit_widget = QtGui.QLineEdit()
        file_completer = QtGui.QCompleter(edit_widget)
        # QDirModel is deprecated and should be replaced by QFileSystemModel.
        # The new class is however not working properly with QCompleter for
        # unknown reasons. QFileSystemModel is asynchronous while QDirModel
        # is synchronous. See:
        # http://blog.qt.io/blog/2010/01/08/
        # qdirmodel-is-now-obsolete-qfilesystemmodel-is-taking-the-job/
        file_completer.setModel(QtGui.QDirModel(file_completer))
        edit_widget.setCompleter(file_completer)
        editor_text = editor.get()
        edit_widget.setText(editor_text)

        layout.addWidget(edit_widget)

        ellipsis_button = ClampedButton('...')
        ellipsis_button.setChecked(os.path.isabs(editor.get()))
        layout.addWidget(ellipsis_button)

        ellipsis_button.clicked.connect(functools.partial(
            select_image_file, editor, edit_widget, index))

        edit_widget.editingFinished.connect(
            functools.partial(write_string, editor, edit_widget, index))
        return top_widget

    class DataSourceValidator(QtGui.QValidator):
        def __init__(self, string_list, parent=None):
            super(PropertyView.DataSourceValidator, self).__init__(parent)
            self._string_list = string_list

        def validate(self, input_string, pos):
            equal = [x == input_string for x in self._string_list]
            if any(equal):
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate

    class DataSourceCompleter(QtGui.QCompleter):
        """
        http://www.stackoverflow.com/questions/5129211/
        qcompleter-custom-completion-rules
        """

        def __init__(self, parent=None):
            super(PropertyView.DataSourceCompleter, self).__init__(parent)
            self.local_completion_prefix = ''
            self.source_model = None

        def setModel(self, model):
            self.source_model = model
            super(PropertyView.DataSourceCompleter, self).setModel(model)

        def updateModel(self):
            local_completion_prefix = self.local_completion_prefix

            class InnerProxyModel(QtGui.QSortFilterProxyModel):
                def filterAcceptsRow(self, source_row, source_parent):
                    index0 = self.sourceModel().index(source_row, 0,
                                                      source_parent)
                    return (local_completion_prefix.lower() in
                            self.sourceModel().data(
                            index0, QtCore.Qt.DisplayRole).lower())
            proxy_model = InnerProxyModel()
            proxy_model.setSourceModel(self.source_model)
            super(PropertyView.DataSourceCompleter, self).setModel(proxy_model)

        def splitPath(self, path):
            self.local_completion_prefix = path
            self.updateModel()
            return ''

    def _create_data_source_editor(self, editor, index):
        widget = QtGui.QComboBox()
        try:
            data_source_list = data_manager.data_source.signal_list()
        except AttributeError:
            widget.addItem('Input data missing')
            return widget

        model = QtGui.QStringListModel(data_source_list)
        widget.setEditable(True)
        widget.setInsertPolicy(QtGui.QComboBox.NoInsert)
        widget.setModel(model)
        try:
            list_index = data_source_list.index(editor.get())
        except ValueError:
            list_index = -1
        widget.setCurrentIndex(list_index)

        completer = PropertyView.DataSourceCompleter(widget)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        completer.setModel(model)
        widget.setCompleter(completer)

        validator = PropertyView.DataSourceValidator(data_source_list)
        widget.setValidator(validator)

        def write_data_source(editor_, index_, model_, value):
            model_.setData(index_, value, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.currentIndexChanged[six.text_type].connect(functools.partial(
            write_data_source, editor, index, self.model))

        def change_completion_system(completer_, text):
            if len(text) < 2:
                completer_.setCompletionMode(
                    QtGui.QCompleter.UnfilteredPopupCompletion)
            else:
                completer_.setCompletionMode(
                    QtGui.QCompleter.PopupCompletion)

        widget.editTextChanged[six.text_type].connect(functools.partial(
            change_completion_system, completer))

        return widget

    def _create_color_scale_editor(self, editor, index, item):
        color_scale_list = models.list_of_scales(item)
        color_scale_list += models.COLOR_SCALES

        widget = QtGui.QComboBox()
        for color_scale_name in color_scale_list:
            widget.addItem(color_scale_name)

        current_value = item.get()
        try:
            current_index = color_scale_list.index(current_value)
        except ValueError:
            current_index = -1

        widget.setCurrentIndex(current_index)

        def color_scale_changed(editor_, index_, model_, color_scale_name_):
            model_.setData(index_, color_scale_name_, QtCore.Qt.EditRole)
            self.process_updates(editor_)

        widget.currentIndexChanged[six.text_type].connect(
            functools.partial(color_scale_changed, editor, index, self.model))

        return widget

    def create_editor(self, index):
        item = self.model.data(index, QtCore.Qt.UserRole)
        editor = item.editor
        widget = None

        if isinstance(item.editor, editor_type.String):
            widget = self._create_text_editor(editor, index)

        elif isinstance(item.editor, editor_type.MultiLineString):
            widget = self._create_textbox_editor(editor, index)

        elif isinstance(item.editor, editor_type.Integer):
            widget = self._create_integer_editor(editor, index)

        elif isinstance(item.editor, editor_type.Float):
            widget = self._create_float_editor(editor, index)

        elif isinstance(item.editor, editor_type.Color):
            widget = self._create_color_editor(editor, index)

        elif isinstance(item.editor, editor_type.Boolean):
            widget = self._create_boolean_editor(editor, index)

        elif isinstance(item.editor, editor_type.ImmutableList):
            widget = self._create_immutable_list_editor(editor, index, item)

        elif isinstance(item.editor, editor_type.DataSource):
            widget = self._create_data_source_editor(editor, index)

        elif isinstance(item.editor, editor_type.ColorScale):
            widget = self._create_color_scale_editor(editor, index, item)

        elif isinstance(item.editor, editor_type.Image):
            widget = self._create_image_editor(editor, index)

        return widget

    def process_updates(self, editor):
        """
        Update everything based on tags in update.
        :param editor: Editor
        :return:
        """
        self.force_rebuild_source.emit()
        if editor_type.EditorTags.force_update_after_edit in editor.tags:
            self.send_force_update()
        if editor_type.EditorTags.force_rebuild_after_edit in editor.tags:
            self.send_force_rebuild()

    def send_force_update(self):
        if not self.update_pending:
            self.update_pending = True
            QtCore.QTimer.singleShot(0, self.exec_force)

    def send_force_rebuild(self):
        if not self.rebuild_pending:
            self.rebuild_pending = True
            QtCore.QTimer.singleShot(0, self.exec_force)

    def exec_force(self):
        if self.update_pending or self.rebuild_pending:
            self.force_update_pages.emit()
        if self.update_pending:
            self.model.force_update()
        if self.rebuild_pending:
            self.force_rebuild.emit()
        self.update_pending = False
        self.rebuild_pending = False


class PropertyItemModel(QtCore.QAbstractTableModel):
    def __init__(self, model):
        super(PropertyItemModel, self).__init__()
        self.model = model
        if model is None:
            self.properties = []
            self.property_keys = []
        else:
            self.properties = self.model.properties_as_dict()
            self.property_keys = list(self.properties.keys())
        self._index_to_item = {}

    def force_update(self):
        self.layoutChanged.emit()

    def index_to_item(self, index):
        return self._index_to_item.get(index.internalId(), None)

    def rowCount(self, parent_index):
        if not parent_index.isValid():
            return len(self.properties)
        return 0

    def columnCount(self, parent_index):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        item = self.index_to_item(index)
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                try:
                    return item.label
                except KeyError:
                    return '*** No Label ***'
            else:
                try:
                    return item.editor.get()
                except (AttributeError, KeyError):
                    pass
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return icons.create_icon(item.icon)
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.UserRole:
            return item
        return None

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            if section == 0:
                return 'Property'
            elif section == 1:
                return 'Value'

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.EditRole:
            item = self.index_to_item(index)
            item.editor.set(value)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return 0
        item = self.index_to_item(index)
        if index.column() == 1 and models.NodeTags.editable in item.tags:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QtCore.QModelIndex()

        if not parent_index.isValid():
            item_key = list(self.property_keys)[row]
            item = self.properties[item_key]
        else:
            return QtCore.QModelIndex()

        return self.createIndex(row, column, item)

    def createIndex(self, row, column, item):
        index = super(PropertyItemModel, self).createIndex(row, column, item)
        self._index_to_item[index.internalId()] = item
        return index

    def removeRows(self, row, count, parent_index=QtCore.QModelIndex()):
        items = [
            self.data(self.index(x, 0, parent_index), QtCore.Qt.UserRole)
            for x in six.moves.range(row, row + count)]
        self.beginRemoveRows(parent_index, row, row + count - 1)
        for item in items:
            models.remove_node(item)
        self.endRemoveRows()
        return True


# Configuration dialogs.
@mock_wrap
class AbstractConfigurationDialog(QtGui.QDialog):
    def __init__(self, data, parent=None):
        super(AbstractConfigurationDialog, self).__init__(parent)
        self.data = data
        self.button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                                 QtGui.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        widget = self.build_widget()
        layout.addWidget(widget)
        layout.addWidget(self.button_box)

        def move_window():
            cursor_position = QtGui.QCursor.pos()
            self.move(int(cursor_position.x() - self.width() / 2),
                      int(cursor_position.y() - self.height() / 2))

        # Single shot needed to allow the dialog window to resize and
        # layout properly, otherwise the width and height are invalid.
        QtCore.QTimer.singleShot(0, move_window)

    def build_widget(self):
        raise NotImplementedError()

    def build_line_edit(self, name):
        """
        Build a line edit widget.
        :param name: Name of property to edit.
        :return: Line Edit widget.
        """
        editor = QtGui.QLineEdit()
        editor.setText(self.data[name])

        def set_property(text):
            self.data[name] = text

        editor.textEdited[six.text_type].connect(set_property)
        return editor

    def build_combo_box(self, items, name):
        """
        Build a combo box widget.
        :param items: List of items to choose from.
        :param name: Name of property in self.data
        :return: Combo Box widget.
        """
        editor = QtGui.QComboBox()
        editor.addItems(items)

        def set_property(text):
            self.data[name] = text

        try:
            index = items.index(self.data[name])
        except ValueError:
            index = 0
        self.data[name] = items[index]
        editor.setCurrentIndex(index)
        editor.currentIndexChanged[six.text_type].connect(set_property)
        return editor


class ScaleConfigurationDialog(AbstractConfigurationDialog):
    domain_editor = None
    data_extent_editor = None
    range_editor = None
    id_editor = None

    class DomainValidator(QtGui.QValidator):
        def __init__(self, parent=None):
            super(ScaleConfigurationDialog.DomainValidator, self).__init__(
                parent)

        def validate(self, input_string, pos):
            if patterns.re_number_list.match(input_string) is not None:
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate

    class RangeValidator(QtGui.QValidator):
        def __init__(self, parent=None):
            super(ScaleConfigurationDialog.RangeValidator, self).__init__(
                parent)

        def validate(self, input_string, pos):
            if patterns.re_number_or_color_list.match(
                    input_string) is not None:
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate

    class ValueValidator(QtGui.QValidator):
        def __init__(self, parent=None):
            super(ScaleConfigurationDialog.ValueValidator, self).__init__(
                parent)

        def validate(self, input_string, pos):
            if (patterns.re_numeric.match(input_string) is not None or
                    patterns.re_color.match(input_string) is not None):
                return QtGui.QValidator.Acceptable
            return QtGui.QValidator.Intermediate

    def __init__(self, item, data, parent=None):
        """
        Constructor.
        :param item: Some node in the model tree. Must not be touched.
        :param data: Dict of raw data from raw model.
        :param parent: Parent Qt-object.
        """
        super(ScaleConfigurationDialog, self).__init__(data, parent)
        self.setWindowTitle('Scale Configuration')
        self.item = item

    @staticmethod
    def data_to_text(x):
        # skip brackets
        y = [('{}'.format(z)).strip() for z in x]
        return ', '.join(y)

    @staticmethod
    def text_to_data(x):
        def convert(n):
            if patterns.re_numeric.match(n):
                return float(n)
            return n
        y = x.split(',')
        y = [convert(z.strip()) for z in y]
        return y

    @staticmethod
    def text_item_count(x):
        y = x.split(',')
        if len(y[-1].strip()) == 0:
            return None
        return len(y)

    def build_widget(self):
        layout = QtGui.QFormLayout()
        layout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        widget = QtGui.QWidget()
        widget.setLayout(layout)

        self.domain_editor = QtGui.QLineEdit()
        self.domain_editor.setText(self.data_to_text(self.data['domain']))
        # match list of numbers
        self.domain_editor.setValidator(self.DomainValidator())
        self.domain_editor.textEdited[six.text_type].connect(
            self.validate_form)

        extent = self.data.get('extent', False)
        self.data_extent_editor = QtGui.QCheckBox('Use Data Extent as Domain')
        self.data_extent_editor.setChecked(extent)
        self.data_extent_editor.clicked[bool].connect(
            self.domain_editor.setHidden)
        self.data_extent_editor.clicked[bool].connect(
            self.set_extent)
        self.data_extent_editor.clicked[bool].connect(
            self.validate_form)
        if extent:
            self.domain_editor.setHidden(True)

        self.range_editor = QtGui.QLineEdit()
        self.range_editor.setText(self.data_to_text(self.data['range']))
        # match list of numbers or colors
        self.range_editor.setValidator(self.RangeValidator())
        self.range_editor.textEdited[six.text_type].connect(
            self.validate_form)

        self.id_editor = self.build_line_edit('id')
        self.id_editor.textEdited[six.text_type].connect(self.validate_form)

        for label, editor in (
                ('Id', self.id_editor),
                ('Extent', self.data_extent_editor),
                ('Domain', self.domain_editor),
                ('Range', self.range_editor)):
            layout.addRow(label, editor)

        # Hide label for domain if necessary.
        domain_label = layout.labelForField(self.domain_editor)
        if extent:
            domain_label.setHidden(True)
        self.data_extent_editor.clicked[bool].connect(domain_label.setHidden)

        return widget

    @QtCore.Slot(bool)
    def set_extent(self, value):
        self.data['extent'] = value

    def build_validated_line_edit(self, name):
        """
        Build a line edit widget.
        :param name: Name of property to edit.
        :return: Line Edit widget.
        """
        editor = QtGui.QLineEdit()
        editor.setText(self.data[name])

        def set_property(text):
            self.data[name] = text

        editor.textEdited[six.text_type].connect(set_property)
        return editor

    def validate_form(self):
        """Validate form values."""
        ok_button = self.button_box.button(QtGui.QDialogButtonBox.Ok)
        if (self.validate_domain_and_range() and
                self.validate_scale_id_uniqueness()):
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def validate_domain_and_range(self):
        """
        Check that domain and range values are ok.
        :return: True if validation is successful.
        """
        domain_count = self.text_item_count(self.domain_editor.text())
        range_count = self.text_item_count(self.range_editor.text())
        domain_ok = (patterns.re_number_list.match(self.domain_editor.text())
                     is not None)
        range_ok = (patterns.re_number_or_color_list.match(
                    self.range_editor.text()) is not None)
        extent = self.data_extent_editor.isChecked()

        if extent and range_ok and range_count is not None:
            self.data['range'] = self.text_to_data(self.range_editor.text())
            return True
        elif (not extent and
              domain_ok and
              range_ok and
              domain_count is not None and
              range_count is not None and
              domain_count == range_count):
            self.data['domain'] = self.text_to_data(self.domain_editor.text())
            self.data['range'] = self.text_to_data(self.range_editor.text())
            return True
        return False

    def validate_scale_id_uniqueness(self):
        """
        Validate uniqueness of scale id.
        :return: True if validation is successful.
        """
        scale_id = self.id_editor.text()
        scale_list = models.list_of_scales(self.item,
                                           filter_type_compatibility=False)
        try:
            # Remove previous name, we must be able to return to the old name.
            scale_list.remove(self.item.data['id'])
        except ValueError:
            pass
        ok = scale_id not in scale_list
        return ok
