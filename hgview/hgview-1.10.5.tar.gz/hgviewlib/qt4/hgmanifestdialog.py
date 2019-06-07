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
Qt4 dialogs to display hg revisions of a file
"""

import sys, os
import os.path as osp

from mercurial import ui, hg
from mercurial.error import LookupError

from PyQt4 import QtGui, QtCore, Qsci
from PyQt4.QtCore import Qt

from hgviewlib.application import ManifestViewer as _ManifestViewer
from hgviewlib.util import tounicode, binary

from hgviewlib.qt4 import icon as geticon
from hgviewlib.qt4.mixins import HgDialogMixin, ActionsMixin, ui2cls
from hgviewlib.qt4.hgrepomodel import ManifestModel
from hgviewlib.qt4.widgets import SourceViewer

class ManifestViewer(ActionsMixin, HgDialogMixin, ui2cls('manifestviewer.ui'), QtGui.QMainWindow, _ManifestViewer):
    """
    Qt4 dialog to display all files of a repo at a given revision
    """
    def __init__(self, repo, noderev):
        self.repo = repo
        super(ManifestViewer, self).__init__()
        self.load_ui()
        self.load_config(repo)
        self.setWindowTitle('hgview manifest: %s revision %s' % (repo.root, noderev))

        # hg repo
        self.rev = noderev
        self.setupModels()

        self.createActions()
        self.setupTextview()

    def load_config(self, repo):
        super(ManifestViewer, self).load_config(repo)
        self.max_file_size = self.cfg.getMaxFileSize()

    def setupModels(self):
        self.treemodel = ManifestModel(self.repo, self.rev)
        self.treeView.setModel(self.treemodel)
        self.treeView.selectionModel().currentChanged.connect(
            self.fileSelected)

    def createActions(self):
        # XXX to factorize
        self.add_action(
            'close', self.actionClose,
            icon='quit',
            callback=self.close,
            )

    def setupTextview(self):
        lay = QtGui.QHBoxLayout(self.mainFrame)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        self.textView = SourceViewer(self.mainFrame)
        self.setFont(self._font)
        lay.addWidget(self.textView)

    def fileSelected(self, index, *args):
        if not index.isValid():
            return
        path = self.treemodel.pathFromIndex(index)
        try:
            fc = self.repo[self.rev].filectx(path)
        except LookupError:
            # may occur when a directory is selected
            self.textView.setMarginWidth(1, '00')
            self.textView.setText('')
            return

        if fc.size() > self.max_file_size:
            data = u"file too big"
        else:
            # return the whole file
            data = fc.data()
            if binary(data):
                data = u"binary file"
            else:
                data = tounicode(data)
        self.textView.set_text(path, data, flag='+', cfg=self.cfg)

    def setCurrentFile(self, filename):
        index = QtCore.QModelIndex()
        path = filename.split(osp.sep)
        for p in path:
            self.treeView.expand(index)
            for row in range(self.treemodel.rowCount(index)):
                newindex = self.treemodel.index(row, 0, index)
                if newindex.internalPointer().data(0) == p:
                    index = newindex
                    break
        self.treeView.setCurrentIndex(index)
