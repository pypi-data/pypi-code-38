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

import os
import sys
import argparse
import six
import svgutils

from PySide import QtCore, QtGui, QtSvg

from .. types.types import TypeList, TypeTuple
from .. utils import filebase, prim
from . import message
from . import message_util
from . import state
from . import version_support as vs
from . import os_support as oss
from . viewerbase import ViewerBase
from . lambda_viewer import LambdaViewer
from . settings import get_default_dir


class MessageViewer(QtGui.QWidget):
    def __init__(self, label=None, parent=None):
        super(MessageViewer, self).__init__(parent)
        if label is None or not isinstance(label, (str, six.text_type)):
            label = ('There is no data available!\n'
                     'You probably need to execute this node!')
        q_label = QtGui.QLabel(label)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(q_label)
        self.setLayout(layout)


class ListViewer(ViewerBase):
    def __init__(self, viewer_cls=None, data_list=None, viewer=None,
                 parent=None):
        super(ListViewer, self).__init__(parent)

        self.VIEWER_CLS = viewer_cls
        self._viewer = viewer
        self._data_list = data_list

        self._init_gui()
        self._init_list_view()

    def _init_gui(self):
        self._select_listview = QtGui.QListWidget(self)
        self._select_listview.setMinimumWidth(20)
        if self._viewer is None:
            self._viewer = self.VIEWER_CLS(parent=self)
        else:
            self._viewer.setParent(self)
        splitter = QtGui.QSplitter()
        splitter.addWidget(self._select_listview)
        splitter.addWidget(self._viewer)
        splitter.setSizes([20, 300])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setHandleWidth(1)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(splitter)
        self.setLayout(hlayout)

        self._select_listview.currentRowChanged[int].connect(self._row_changed)

    def _init_list_view(self):
        for index in range(len(self._data_list)):
            self._select_listview.addItem(six.text_type(index))

    def _row_changed(self, index):
        self._select_listview.setCurrentRow(index)
        try:
            self._viewer.update_data(self._data_list[index])
        except IndexError:
            pass

    def custom_menu_items(self):
        return self._viewer.custom_menu_items()

    def update_data(self, data):
        self._data_list = data
        row = self._select_listview.currentRow()
        self._select_listview.clear()
        self._init_list_view()

        if row > len(data):
            self._row_changed(0)
        else:
            self._row_changed(row)


class TupleViewer(ViewerBase):
    def __init__(self, viewer_clss=None, data_list=None, viewers=None,
                 parent=None):
        super(TupleViewer, self).__init__(parent)

        self.VIEWER_CLSS = viewer_clss
        self._viewers = viewers
        self._data_list = data_list
        self._tabwidget = QtGui.QTabWidget()
        self._init_gui()
        self._init_data_view()

    def _init_gui(self):
        vlayout = QtGui.QVBoxLayout()

        self._select_splitter = QtGui.QSplitter()

        if self._viewers is None:
            self._viewers = []
            for i, viewer_cls in enumerate(self.VIEWER_CLSS):
                viewer = viewer_cls(parent=self._select_splitter)
                self._viewers.append(viewer)
                self._tabwidget.addTab(viewer, str(i))
        else:
            for i, viewer in enumerate(self._viewers):
                self._tabwidget.addTab(viewer, str(i))

        self._init_data_view()

        self._tabwidget.setParent(self._select_splitter)

        vlayout.addWidget(self._select_splitter)
        self.setLayout(vlayout)

    def _init_data_view(self):
        for i in range(len(self._viewers)):
            self._viewers[i].update_data(self._data_list[i])

    def custom_menu_items(self):
        # Currently not implemented, may be difficult to support given the
        # current interface.

        # TODO(Erik): Make the interface more flexible so that menu items
        # change with the context.
        return []

    def update_data(self, data):
        self._data_list = data
        self._init_data_view()


def viewer_from_instance_factory(instance):

    if instance is None:
        return MessageViewer(label='The data on this port '
                                   'cannot be viewed.')

    def inner_basic(type_):

        data = filebase.empty_from_type(type_)

        if str(data) == 'lambda()':
            viewer = LambdaViewer(data)
        else:
            viewer = data.viewer()(data)

        if viewer is None:
            viewer = MessageViewer(label='The data-type of this port '
                                         'is currently not supported.')
        return viewer

    def inner_list(type_):
        child_viewer = inner_main(type_[0])
        return ListViewer(viewer=child_viewer,
                          data_list=filebase.empty_from_type(type_))

    def inner_tuple(type_):
        child_viewers = [inner_main(child_type)
                         for child_type in type_]
        return TupleViewer(viewers=child_viewers,
                           data_list=filebase.empty_from_type(type_))

    def inner_main(type_):

        if isinstance(type_, TypeList):
            viewer = inner_list(type_)
        elif isinstance(type_, TypeTuple):
            viewer = inner_tuple(type_)
        else:
            viewer = inner_basic(type_)

        return viewer

    if instance is not None:
        viewer = inner_main(instance.container_type)
        viewer.update_data(instance)
    else:
        viewer = None

    return viewer


class ViewerManager(object):
    def __init__(self, window):
        self._window = window
        self._viewer = None

    @property
    def viewer(self):
        return self._viewer

    @viewer.setter
    def viewer(self, value):
        self._viewer = value

    def data(self):
        return self._viewer.data()

    def update(self, data):
        self.viewer = viewer_from_instance_factory(data)
        self._window.setCentralWidget(self.viewer)

    def clear(self):
        """Clear the viewer."""
        self._viewer = None
        self.update(self._viewer)

    def _create_syinode_widget(self, syinode):
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        tabwidget = QtGui.QTabWidget()

        for port in syinode.io.outputs():
            data = port.to_data()
            viewer = viewer_from_instance_factory(data)
            viewer.layout().setContentsMargins(0, 0, 0, 0)
            tabwidget.addTab(viewer, port.name)

        layout.addWidget(tabwidget)
        widget.setLayout(layout)
        return widget


class MainWindow(QtGui.QMainWindow):
    _window_title = 'Data Viewer'

    def __init__(self, window_title=None, socket_bundle=None, icon=None,
                 parent=None):
        super(MainWindow, self).__init__(parent)
        self.window_title = window_title or self._window_title
        self._input_comm = socket_bundle
        self._dtype = None
        self._icon = icon

        self._input_reader = None
        if socket_bundle is not None:
            self._input_reader = message_util.QtMessageReader(
                socket_bundle.socket, self)
            self._input_reader.received.connect(self.handle_input)

        self._viewer_manager = ViewerManager(self)
        self._fq_filename = None

        self._init_gui()

    def handle_input(self, msgs):
        for msg in msgs:
            if msg.type == message.RaiseWindowMessage:
                self.raise_window()
            elif msg.type == message.PortDataReadyMessage:
                self._reload()
            elif msg.type == message.NotifyWindowMessage:
                self.notify_in_taskbar()

    def raise_window(self):
        if not self.isActiveWindow():
            oss.raise_window(self)

    def notify_in_taskbar(self):
        QtGui.QApplication.alert(self, 2000)

    def _init_gui(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        open_action = QtGui.QAction('&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open')
        open_action.triggered.connect(self._open)

        clear_action = QtGui.QAction('Clear', self)
        clear_action.setStatusTip('Clear')
        clear_action.triggered.connect(self._clear)

        quit_action = QtGui.QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Quit')
        quit_action.triggered.connect(self.close)

        manual_action = QtGui.QAction('&User Manual', self)
        manual_action.setStatusTip('Open User Manual in browser')
        manual_action.triggered.connect(self.open_documentation)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        view_menu = menubar.addMenu('&View')
        help_menu = menubar.addMenu('&Help')
        filemenu.addAction(open_action)
        filemenu.addAction(quit_action)

        view_menu.addAction(clear_action)

        help_menu.addAction(manual_action)

        self.setWindowTitle(self.window_title)

    def build_icon(self):
        path = prim.uri_to_path(self._icon)
        node_icon = svgutils.transform.fromfile(path)
        overlay = svgutils.transform.fromfile(prim.get_icon_path('viewer.svg'))
        viewer_icon = svgutils.transform.SVGFigure(64, 64)
        if node_icon:
            viewer_icon.append(node_icon.getroot())
        viewer_icon.append(overlay.getroot())
        icon_str = viewer_icon.to_str().replace(b'ASCII', b'UTF-8')

        renderer = QtSvg.QSvgRenderer()
        renderer.load(QtCore.QByteArray(icon_str))
        icon = QtGui.QImage(64, 64, QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(icon)
        renderer.render(painter)
        painter.end()
        pixmap = QtGui.QPixmap()
        pixmap.setAlphaChannel(pixmap)
        pixmap.convertFromImage(icon)
        return pixmap

    def viewer_from_filename_factory(self, fq_sydata_filename):
        fileobj = filebase.from_file(fq_sydata_filename)
        data = fileobj
        viewer = viewer_from_instance_factory(data)
        # Do not remove due to gc.
        viewer._fileobj = fileobj
        return viewer

    def open_from_filename(self, filename):
        def is_file_valid(filename):
            return (
                filename is not None and
                os.path.isfile(filename) and
                os.stat(filename).st_size)
        viewer = None
        old_viewer = self._viewer_manager.viewer
        dtype = filebase.filetype(filename)

        if is_file_valid(filename):
            self._fq_filename = filename
            if dtype == self._dtype and old_viewer is not None:
                fileobj = filebase.from_file(filename)
                old_viewer.update_data(fileobj)
            else:
                viewer = self.viewer_from_filename_factory(filename)
        else:
            viewer = MessageViewer()

        if viewer is None and old_viewer is not None:
            viewer = old_viewer
        else:
            self.setCentralWidget(viewer)
            self._viewer_manager.viewer = viewer

        self._dtype = dtype

    def _clear(self):
        self._viewer_manager.clear()

    def _reload(self):
        state.hdf5_state().clear()
        self.open_from_filename(self._fq_filename)

    def _open(self):
        if self._fq_filename:
            default_directory = os.path.dirname(self._fq_filename)
        else:
            default_directory = get_default_dir()
        filename, _ = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', default_directory,
            'Sympathy data file (*.sydata)')
        if filename:
            self.open_from_filename(filename)

    def open_documentation(self):
        """Open the documentation at the Viewer chapter."""
        # TODO: implementation
        pass

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Escape):
            self.close()


def run(default_icon_path=None):
    parser = argparse.ArgumentParser(
        'Open a viewer for *.sydata files.')

    # Filename is a positional argument.
    parser.add_argument(
        'filename', action='store', nargs='?', default=None,
        help='A .sydata file.')
    args = parser.parse_args()
    oss.set_high_dpi_unaware()
    oss.set_application_id()

    application = QtGui.QApplication(sys.argv)

    window = MainWindow()
    if default_icon_path is not None:
        window.setWindowIcon(QtGui.QIcon(default_icon_path))

    if args.filename:
        window.open_from_filename(vs.fs_decode(args.filename))

    application.setApplicationName(window.window_title)

    window.setMinimumWidth(800)
    window.setMinimumHeight(600)
    window.show()
    window.activateWindow()
    window.raise_()

    sys.exit(application.exec_())
