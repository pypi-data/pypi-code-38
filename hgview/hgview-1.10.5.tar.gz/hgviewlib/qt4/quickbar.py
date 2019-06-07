# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Qt4 QToolBar-based class for quick bars XXX
"""

from functools import partial

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal

from hgviewlib.util import tounicode, binary
from hgviewlib.qt4.mixins import ActionsMixin
from hgviewlib.qt4 import icon as geticon

Qt = QtCore.Qt


class QuickBar(QtGui.QToolBar, ActionsMixin):

    esc_shortcut_disabled = pyqtSignal(bool)
    unhidden = pyqtSignal()

    def __init__(self, parent=None, name='Absctract'):
        # used to remember who had the focus before bar steel it
        self.name = name
        self._focusw = None
        QtGui.QToolBar.__init__(self, self.name, parent)
        ActionsMixin.__init__(self)
        self.setIconSize(QtCore.QSize(16,16))
        self.setFloatable(False)
        self.setMovable(False)
        self.setAllowedAreas(Qt.BottomToolBarArea)
        self.createActions()
        self.createContent()
        if parent:
            parent = parent.window()
        if isinstance(parent, QtGui.QMainWindow):
            parent.addToolBar(Qt.BottomToolBarArea, self)
        self.setVisible(False)

    def createActions(self):
        self.add_action(
            'close', self.tr("Close"),
            icon='close',
            tip=self.tr("Close toolbar"),
            callback=self.hide,
        )

    def setVisible(self, visible=True):
        if visible and not self.isVisible():
            self.unhidden.emit()
            self._focusw = QtGui.QApplication.focusWidget()
        QtGui.QToolBar.setVisible(self, visible)
        self.esc_shortcut_disabled[bool].emit(not visible)
        if not visible and self._focusw:
            self._focusw.setFocus()
            self._focusw = None

    def createContent(self):
        raise NotImplementedError

    def hide(self):
        self.setVisible(False)

    def unhide(self):
        self.setVisible(True)

    def cancel(self):
        self.hide()


class FindQuickBar(QuickBar):

    to_find = pyqtSignal(str)
    to_find_next = pyqtSignal(str)
    canceled = pyqtSignal()
    message_logged = pyqtSignal(str, int)

    def __init__(self, parent, name='find'):
        QuickBar.__init__(self, parent, name)
        self.currenttext = ''

    def createActions(self):

        QuickBar.createActions(self)

        self.add_action(
            'findnext', self.tr("Find next"),
            icon='forward',
            keys=QtGui.QKeySequence("Ctrl+N"),
            tip=self.tr("Search for the next occurence"),
            callback=self.find,
        )

        self.add_action(
            'cancel', self.tr('Cancel'),
            tip=self.tr("Cancel processing search"),
            callback=self.cancel
        )

    def find(self, *args):
        '''Scan the repository metadata and search for occurrences of the
        text in the entry.
        :note: do not scan if no text was provided'''
        text = self.entry.text()
        if not text: # do not strip() as user may want to find space sequences
            self.message_logged.emit('Nothing to look for.', 1000)
            return
        if text == self.currenttext:
            self.to_find_next.emit(text)
        else:
            self.currenttext = text
            self.to_find.emit(text)

    def cancel(self):
        self.canceled.emit()

    def setCancelEnabled(self, enabled=True):
        self.set_action('cancel', enabled=enabled)
        self.set_action('findnext', enabled=not enabled)

    def createContent(self):
        self.compl_model = QtGui.QStringListModel()
        self.completer = QtGui.QCompleter(self.compl_model, self)
        self.entry = QtGui.QLineEdit(self)
        self.entry.setCompleter(self.completer)
        self.addWidget(self.entry)
        self.addActions(self.get_actions('findnext', 'cancel'))
        self.setCancelEnabled(False)

        self.entry.returnPressed.connect(self.find)
        self.entry.textEdited[str].connect(self.find)

    def setVisible(self, visible=True):
        QuickBar.setVisible(self, visible)
        if visible:
            self.entry.setFocus()
            self.entry.selectAll()

    def text(self):
        if self.isVisible() and self.currenttext.strip():
            return self.currenttext

    def __del__(self):
        # prevent a warning in the console:
        # QObject::startTimer: QTimer can only be used with threads started with QThread
        self.entry.setCompleter(None)

class FindInGraphlogQuickBar(FindQuickBar):

    revision_selected = pyqtSignal([], [int])
    file_selected = pyqtSignal(str)

    def __init__(self, parent, name='find'):
        FindQuickBar.__init__(self, parent, name)
        self._findinfile_iter = None
        self._findinlog_iter = None
        self._findindesc_iter = None
        self._fileview = None
        self._headerview = None
        self._filter_files = None
        self._mode = 'diff'
        self.to_find.connect(self.on_find_text_changed)
        self.to_find_next.connect(self.on_findnext)
        self.canceled.connect(self.on_cancelsearch)

    def setFilterFiles(self, files):
        self._filter_files = files

    def setModel(self, model):
        self._model = model

    def setMode(self, mode):
        assert mode in ('diff', 'file')
        self._mode = mode

    def attachFileView(self, fileview):
        self._fileview = fileview

    def attachHeaderView(self, view):
        self._headerview = view

    def find_in_graphlog(self, fromrev, fromfile=None):
        """
        Find text in the whole repo from rev 'fromrev', from file
        'fromfile' (if given) *excluded*
        """
        text = self.entry.text()
        graph = self._model.graph
        idx = graph.index(fromrev)
        for node in graph[idx:]:
            rev = node.rev
            ctx = self._model.repo[rev]
            # XXX should be an re search with undecoded chars as '?'
            if text in tounicode(ctx.description()):
                yield rev, None
            files = ctx.files()
            if self._filter_files:
                files = [x for x in files if x in self._filter_files]
            if fromfile is not None and fromfile in files:
                files = files[files.index(fromfile)+1:]
                fromfile = None
            for filename in files:
                if self._mode == 'diff':
                    flag, data = self._model.graph.filedata(filename, rev)
                else:
                    data = ctx.filectx(filename).data()
                    if binary(data):
                        data = "binary file"
                if data and text in data:
                    yield rev, filename
                else:
                    yield None

    def cancel(self):
        if self.get_action('cancel').isEnabled():
            self.canceled.emit()
        else:
            self.hide()

    def on_cancelsearch(self, *args):
        self._findinlog_iter = None
        self.setCancelEnabled(False)
        self.message_logged.emit('Search cancelled!', 2000)

    def on_findnext(self):
        """
        callback called by 'Find' quicktoolbar (on findnext signal)
        """
        if self._findindesc_iter is not None:
            for pos in self._findindesc_iter:
                # just highlight next found text in fileview
                # (handled by _findinfile_iter)
                return
            # no more found text in currently displayed file
            self._findindesc_iter = None

        if self._findinfile_iter is not None:
            for pos in self._findinfile_iter:
                # just highlight next found text in descview
                # (handled by _findindesc_iter)
                return
            # no more found text in currently displayed file
            self._findinfile_iter = None

        if self._findinlog_iter is None:
            # start searching in the graphlog from current position
            rev = self._fileview.rev()
            filename = self._fileview.filename()
            self._findinlog_iter = self.find_in_graphlog(rev, filename)

        self.setCancelEnabled(True)
        self.find_next_in_log()

    def find_next_in_log(self, step=0):
        """
        to be called from 'on_find' callback (or recursively). Try to
        find the next occurrence of searched text (as a 'background'
        process, so the GUI is not frozen, and as a cancellable task).
        """
        if self._findinlog_iter is None:
            # when search has been cancelled
            return
        for next_find in self._findinlog_iter:
            if next_find is None: # not yet found, let's animate a bit the GUI
                if (step % 20) == 0:
                    self.message_logged.emit(
                              'Searching'+'.'*(step/20),
                              -1)
                step += 1
                QtCore.QTimer.singleShot(0, lambda: self.find_next_in_log(step % 80))
            else:
                self.message_logged.emit('', -1)
                self.setCancelEnabled(False)

                rev, filename = next_find
                if rev is None:
                    self.revision_selected.emit()
                else:
                    self.revision_selected[int].emit(rev)
                text = self.entry.text()
                if filename is None and self._headerview:
                    self._findindesc_iter = self._headerview.searchString(text)
                    self.on_findnext()
                else:
                    self.file_selected.emit(tounicode(filename))
                    if self._fileview:
                        self._findinfile_iter = self._fileview.searchString(text)
                        self.on_findnext()
            return
        self.message_logged.emit(
                  'No more matches found in repository',
                  2000)
        self.setCancelEnabled(False)
        self._findinlog_iter = None

    def on_find_text_changed(self, newtext):
        """
        callback called by 'Find' quicktoolbar (on find signal)
        """
        newtext = newtext
        self._findinlog_iter = None
        self._findinfile_iter = None
        if self._headerview:
            self._findindesc_iter = self._headerview.searchString(newtext)
        if self._fileview:
            self._findinfile_iter = self._fileview.searchString(newtext)
        if newtext.strip():
            if self._findindesc_iter is None and self._findindesc_iter is None:
                self.message_logged.emit(
                          'Search string not found in current diff. '
                          'Hit "Find next" button to start searching '
                          'in the repository',
                          2000)
            else:
                self.on_findnext()

