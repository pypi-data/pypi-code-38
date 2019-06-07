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

import difflib

from mercurial import ui, hg, util

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, pyqtSignal

from hgviewlib.application import (FileViewer as _FileViewer,
                                   FileDiffViewer as _FileDiffViewer)
from hgviewlib.util import tounicode, rootpath

from hgviewlib.qt4 import icon as geticon
from hgviewlib.qt4.mixins import HgDialogMixin, ActionsMixin, ui2cls
from hgviewlib.qt4.hgrepomodel import FileRevModel
from hgviewlib.qt4.blockmatcher import BlockList, BlockMatch
from hgviewlib.qt4.quickbar import FindInGraphlogQuickBar
from hgviewlib.qt4.widgets import SourceViewer

sides = ('left', 'right')
otherside = {'left': 'right', 'right': 'left'}


class AbstractFileDialog(ActionsMixin, HgDialogMixin, QtGui.QMainWindow):
    def __init__(self, repo, filename, repoviewer=None):
        self.repo = repo
        super(AbstractFileDialog, self).__init__()
        self.load_ui()
        self.load_config(self.repo)

        self.setRepoViewer(repoviewer)
        self._show_rev = None

        self.filename = filename

        self.createActions()
        self.setupToolbars()

        self.setupViews()
        self.setupModels()

    def setRepoViewer(self, repoviewer=None):
        self.repoviewer = repoviewer
        if repoviewer:
            repoviewer.destroyed.connect(lambda x: self.setRepoViewer())

    def reload(self):
        self.repo = util.build_repo(self.repo.ui, self.repo.root)
        self.setupModels()

    def modelFilled(self):
        self.filerevmodel.filled.disconnect(self.modelFilled)
        if isinstance(self._show_rev, int):
            index = self.filerevmodel.indexFromRev(self._show_rev)
            self._show_rev = None
        else:
            index = self.filerevmodel.index(0,0)
        self.tableView_revisions.setCurrentIndex(index)

    def revisionActivated(self, rev):
        """
        Callback called when a revision is double-clicked in the revisions table
        """
        if self.repoviewer is None:
            # prevent recursive import
            from hgviewlib.qt4.hgrepoviewer import HgRepoViewer
            self.repoviewer = HgRepoViewer(self.repo)
        self.repoviewer.goto(rev)
        self.repoviewer.show()
        self.repoviewer.activateWindow()
        self.repoviewer.raise_()

class FileViewer(AbstractFileDialog, ui2cls('fileviewer.ui'), _FileViewer):
    """
    A dialog showing a revision graph for a file.
    """

    def setupViews(self):
        self.textView.setFont(self._font)
        self.setWindowTitle('hgview filelog: %s' % os.path.abspath(self.filename))
        self.textView.message_logged.connect(self.statusBar().showMessage)

    def setupToolbars(self):
        self.find_toolbar = FindInGraphlogQuickBar(self)
        self.find_toolbar.attachFileView(self.textView)
        self.find_toolbar.revision_selected.connect(
            self.tableView_revisions.goto)
        self.find_toolbar.revision_selected[int].connect(
            self.tableView_revisions.goto)
        self.find_toolbar.message_logged.connect(self.statusBar().showMessage)
        self.attachQuickBar(self.find_toolbar)

        add_actions = self.toolBar_edit.addActions
        self.toolBar_edit.addSeparator()
        add_actions(self.tableView_revisions.get_actions('back', 'forward'))
        self.toolBar_edit.addSeparator()
        add_actions(self.get_actions('diffmode', 'annmode', 'next', 'prev'))

        self.attachQuickBar(self.tableView_revisions.goto_toolbar)

    def setupModels(self):
        self.filerevmodel = FileRevModel(self.repo)
        self.tableView_revisions.setModel(self.filerevmodel)
        self.tableView_revisions.revision_selected.connect(
            self.revisionSelected)
        self.tableView_revisions.revision_selected[int].connect(
            self.revisionSelected)
        self.tableView_revisions.revision_activated.connect(
                self.revisionActivated)
        self.tableView_revisions.revision_activated[int].connect(
                self.revisionActivated)
        self.filerevmodel.message_logged.connect(
            self.statusBar().showMessage,
            Qt.QueuedConnection)
        self.filerevmodel.filled.connect(self.modelFilled)
        self.textView.setMode('file')
        self.textView.setModel(self.filerevmodel)
        self.find_toolbar.setModel(self.filerevmodel)
        self.find_toolbar.setFilterFiles([self.filename])
        self.find_toolbar.setMode('file')
        self.filerevmodel.setFilename(self.filename)

    def createActions(self):
        self.add_action(
            'close', self.actionClose,
            icon='quit',
            callback=lambda: self.close(),
            )

        self.add_action(
            'reload', self.actionReload,
            icon='reload',
            callback=lambda: self.reload(),
            )

        self.add_action(
            'diffmode', self.tr("Diff mode"),
            menu=self.tr("Mode"),
            icon='diffmode' ,
            tip=self.tr("Enable/Disable Diff mode"),
            callback=self.setMode,
            checked=False,
            )

        self.add_action(
            'annmode', self.tr("Annotate mode"),
            tip=self.tr("Enable/Disable Annotate mode"),
            callback=self.textView.setAnnotate,
            checked=False,
            )

        self.add_action(
            'next', self.tr("Next hunk"),
            menu=self.tr("Moves"),
            icon='down',
            tip=self.tr("Jump to the next hunk"),
            keys=[Qt.ALT + Qt.Key_Down],
            callback=lambda: self.nextDiff(),
            )

        self.add_action(
            'prev', self.tr("Prior hunk"),
            menu=self.tr("Moves"),
            icon='up',
            tip=self.tr("Jump to the previous hunk"),
            keys=[Qt.ALT + Qt.Key_Up],
            callback=lambda: self.prevDiff(),
            )

    def revisionSelected(self, rev):
        pos = self.textView.verticalScrollBar().value()
        ctx = self.filerevmodel.repo[rev]
        self.textView.setContext(ctx)
        self.textView.displayFile(self.filerevmodel.graph.filename(rev))
        self.textView.verticalScrollBar().setValue(pos)
        self.set_action('prev', enabled=False)
        self.textView.filled.connect(
                lambda self=self: self.set_action('next',
                                                  enabled=self.textView.fileMode() and self.textView.nDiffs()))

    def goto(self, rev):
        index = self.filerevmodel.indexFromRev(rev)
        if index is not None:
            self.tableView_revisions.setCurrentIndex(index)
        else:
            self._show_rev = rev

    def setMode(self, mode):
        self.textView.setMode(mode)
        self.set_actions('annmode', 'next', 'prev', enabled=not mode)

    def nextDiff(self):
        notlast = self.textView.nextDiff()
        enabled = self.textView.fileMode() and notlast and self.textView.nDiffs()
        self.set_action('next', enabled=(enabled if enabled is not None else True))
        enabled = self.textView.fileMode() and self.textView.nDiffs()
        self.set_action('prev', enable=(enabled if enabled is not None else True))

    def prevDiff(self):
        notfirst = self.textView.prevDiff()
        self.set_action('prev',
                        enabled=self.textView.fileMode() and notfirst and self.textView.nDiffs())
        self.set_action('next',
                        enabled=self.textView.fileMode() and self.textView.nDiffs())


class FileDiffViewer(AbstractFileDialog, ui2cls('filediffviewer.ui'), _FileDiffViewer):
    """
    Qt4 dialog to display diffs between different mercurial revisions of a file.
    """
    diff_filled = pyqtSignal()

    def setupViews(self):
        self.tableView_revisions = self.tableView_revisions_left
        self.tableViews = {'left': self.tableView_revisions_left,
                           'right': self.tableView_revisions_right}
        # viewers are Scintilla editors
        self.viewers = {}
        # block are diff-block displayers
        self.block = {}
        self.diffblock = BlockMatch(self.frame)
        lay = QtGui.QHBoxLayout(self.frame)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        for side, idx  in (('left', 0), ('right', 3)):
            textview = SourceViewer(self.frame)
            textview.setFont(self._font)
            textview.verticalScrollBar().setFocusPolicy(Qt.StrongFocus)
            textview.setFocusProxy(textview.verticalScrollBar())
            textview.verticalScrollBar().installEventFilter(self)

            lay.addWidget(textview)

            self.viewers[side] = textview
            blk = BlockList(self.frame)
            blk.linkScrollBar(textview.verticalScrollBar())
            self.diffblock.linkScrollBar(textview.verticalScrollBar(), side)
            lay.insertWidget(idx, blk)
            self.block[side] = blk

        lay.insertWidget(2, self.diffblock)

        for side in sides:
            table = getattr(self, 'tableView_revisions_%s' % side)
            table.setTabKeyNavigation(False)
            #table.installEventFilter(self)
            table.revision_selected.connect(self.revisionSelected)
            table.revision_selected[int].connect(self.revisionSelected)
            table.revision_activated.connect(self.revisionActivated)
            table.revision_activated[int].connect(self.revisionActivated)

            self.viewers[side].verticalScrollBar().valueChanged[int].connect(
                    lambda value, side=side: self.vbar_changed(value, side))
            self.attachQuickBar(table.goto_toolbar)

        self.setTabOrder(table, self.viewers['left'])
        self.setTabOrder(self.viewers['left'], self.viewers['right'])
        self.setWindowTitle('hgview diff: %s' % os.path.abspath(self.filename))

        # timer used to fill viewers with diff block markers during GUI idle time
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.idle_fill_files)

    def setupModels(self):
        self.filedata = {'left': None, 'right': None}
        self._invbarchanged = False
        self.filerevmodel = FileRevModel(self.repo, self.filename)
        self.filerevmodel.filled.connect(self.modelFilled)
        self.tableView_revisions_left.setModel(self.filerevmodel)
        self.tableView_revisions_right.setModel(self.filerevmodel)

    def createActions(self):
        self.add_action(
            'close', self.actionClose,
            icon='quit',
            callback=lambda: self.close(),
            )

        self.add_action(
            'reload', self.actionReload,
            icon='reload',
            callback=lambda: self.reload(),
            )

        self.add_action(
            'next', self.tr("Next hunk"),
            menu=self.tr("Moves"),
            icon='down',
            tip=self.tr("Jump to the next hunk"),
            keys=[Qt.ALT + Qt.Key_Down],
            callback=lambda: self.nextDiff(),
            enabled=False,
            )

        self.add_action(
            'prev', self.tr("Prior hunk"),
            menu=self.tr("Moves"),
            icon='up',
            tip=self.tr("Jump to the previous hunk"),
            keys=[Qt.ALT + Qt.Key_Up],
            callback=lambda: self.prevDiff(),
            enabled=False,
            )

    def setupToolbars(self):
        self.toolBar_edit.addSeparator()
        self.toolBar_edit.addActions(self.get_actions('next', 'prev'))

    def modelFilled(self):
        self.filerevmodel.filled.disconnect(self.modelFilled)
        if self._show_rev is not None:
            rev = self._show_rev
            self._show_rev = None
        else:
            rev = self.filerevmodel.graph[0].rev
        self.goto(rev)

    def revisionSelected(self, rev):
        if self.sender() is self.tableView_revisions_right:
            side = 'right'
        else:
            side = 'left'
        path = self.filerevmodel.graph.nodesdict[rev].extra[0]
        fc = self.repo[rev].filectx(path)
        self.filedata[side] = tounicode(fc.data()).splitlines()
        self.update_diff(keeppos=otherside[side])

    def goto(self, rev):
        index = self.filerevmodel.indexFromRev(rev)
        if index is not None:
            if index.row() == 0:
                index = self.filerevmodel.index(1, 0)
            self.tableView_revisions_left.setCurrentIndex(index)
            index = self.filerevmodel.index(0, 0)
            self.tableView_revisions_right.setCurrentIndex(index)
        else:
            self._show_rev = rev

    def setDiffNavActions(self, pos=0):
        hasdiff = (self.diffblock.nDiffs() > 0)
        self.set_action('next', enabled=hasdiff and pos != 1)
        self.set_action('prev', enabled=hasdiff and pos != -1)

    def nextDiff(self):
        self.setDiffNavActions(self.diffblock.nextDiff())

    def prevDiff(self):
        self.setDiffNavActions(self.diffblock.prevDiff())

    def update_page_steps(self, keeppos=None):
        for side in sides:
            self.block[side].syncPageStep()
        self.diffblock.syncPageStep()
        if keeppos:
            side, pos = keeppos
            self.viewers[side].verticalScrollBar().setValue(pos)

    def idle_fill_files(self):
        # we make a burst of diff-lines computed at once, but we
        # disable GUI updates for efficiency reasons, then only
        # refresh GUI at the end of the burst
        for side in sides:
            self.viewers[side].setUpdatesEnabled(False)
            self.block[side].setUpdatesEnabled(False)
        self.diffblock.setUpdatesEnabled(False)

        for n in range(30): # burst pool
            if self._diff is None or not self._diff.get_opcodes():
                self._diff = None
                self.timer.stop()
                self.setDiffNavActions(-1)
                self.diff_filled.emit()
                break

            tag, alo, ahi, blo, bhi = self._diff.get_opcodes().pop(0)

            if tag == 'replace':
                self.block['left'].addBlock('x', alo, ahi)
                self.block['right'].addBlock('x', blo, bhi)
                self.diffblock.addBlock('x', alo, ahi, blo, bhi)

                w = self.viewers['left']
                for i in range(alo, ahi):
                    w.markerAdd(i, w.markertriangle)

                w = self.viewers['right']
                for i in range(blo, bhi):
                    w.markerAdd(i, w.markertriangle)

            elif tag == 'delete':
                self.block['left'].addBlock('-', alo, ahi)
                self.diffblock.addBlock('-', alo, ahi, blo, bhi)

                w = self.viewers['left']
                for i in range(alo, ahi):
                    w.markerAdd(i, w.markerminus)

            elif tag == 'insert':
                self.block['right'].addBlock('+', blo, bhi)
                self.diffblock.addBlock('+', alo, ahi, blo, bhi)

                w = self.viewers['right']
                for i in range(blo, bhi):
                    w.markerAdd(i, w.markerplus)

            elif tag == 'equal':
                pass

            else:
                raise ValueError, 'unknown tag %r' % (tag,)

        # ok, let's enable GUI refresh for code viewers and diff-block displayers
        for side in sides:
            self.viewers[side].setUpdatesEnabled(True)
            self.block[side].setUpdatesEnabled(True)
        self.diffblock.setUpdatesEnabled(True)

    def update_diff(self, keeppos=None):
        """
        Recompute the diff, display files and starts the timer
        responsible for filling diff markers
        """
        if keeppos:
            pos = self.viewers[keeppos].verticalScrollBar().value()
            keeppos = (keeppos, pos)

        for side in sides:
            self.viewers[side].clear()
            self.block[side].clear()
        self.diffblock.clear()

        if None not in self.filedata.values():
            if self.timer.isActive():
                self.timer.stop()
            for side in sides:
                self.viewers[side].setMarginWidth(1, "00%s" % len(self.filedata[side]))

            self._diff = difflib.SequenceMatcher(None, self.filedata['left'],
                                                 self.filedata['right'])
            blocks = self._diff.get_opcodes()[:]

            self._diffmatch = {'left': [x[1:3] for x in blocks],
                               'right': [x[3:5] for x in blocks]}
            for side in sides:
                self.viewers[side].set_text(self.filename,
                                            '\n'.join(self.filedata[side]),
                                            flag='+',
                                            cfg=self.cfg)
            self.update_page_steps(keeppos)
            self.timer.start()

    def vbar_changed(self, value, side):
        """
        Callback called when the vertical scrollbar of a file viewer
        is changed, so we can update the position of the other file
        viewer.
        """
        if self._invbarchanged:
            # prevent loops in changes (left -> right -> left ...)
            return
        self._invbarchanged = True
        oside = otherside[side]

        for i, (lo, hi) in enumerate(self._diffmatch[side]):
            if lo <= value < hi:
                break
        dv = value - lo

        blo, bhi = self._diffmatch[oside][i]
        vbar = self.viewers[oside].verticalScrollBar()
        if (dv) < (bhi - blo):
            bvalue = blo + dv
        else:
            bvalue = bhi
        vbar.setValue(bvalue)
        self._invbarchanged = False
