# Copyright (c) 2009-2012 LOGILAB S.A. (Paris, FRANCE).
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
Qt4 high level widgets for hg repo changelogs and filelogs
"""
import os
import difflib
from itertools import imap
import tempfile



try:
    from mercurial.error import LookupError, ManifestLookupError
except ImportError:
    # ManifestLookupError is missing in older versions
    from mercurial.revlog import LookupError, LookupError as ManifestLookupError

from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.QtCore import Qt, pyqtSignal

from hgviewlib.util import exec_flag_changed, isbfile, bfilepath, tounicode
from hgviewlib.config import HgConfig

from hgviewlib.qt4.mixins import ActionsMixin
from hgviewlib.qt4.config import get_font
from hgviewlib.qt4.blockmatcher import BlockList
from hgviewlib.qt4.widgets import SourceViewer, Annotator


class HgQsci(ActionsMixin, SourceViewer):
    def __init__(self, *args, **kwargs):
        super(HgQsci, self).__init__(*args, **kwargs)
        self.createActions()

    def createActions(self):
        self.add_action(
            "diffmode", self.tr("Diff mode"),
            menu=self.tr("Mode"),
            icon='diffmode' ,
            tip=self.tr('Enable/Disable Diff mode'),
            checked=True,
            )

        self.add_action(
            "ignorews", self.tr("Ignore all space"),
            menu=self.tr("Mode"),
            tip=self.tr("Ignore all space"),
            checked=True,
            )

        self.add_action(
            "show-big-file", self.tr('Display heavy file'),
            menu=self.tr("Mode"),
            icon='heavy',
            tip=self.tr('Display file Content even if it is marked as too big'
                        '[config: maxfilesize]'),
            checked=False,
            )

        self.add_action(
            "annmode", self.tr("Annotate mode"),
            menu=self.tr("Mode"),
            tip=self.tr('Enable/Disable Annotate mode'),
            checked=True,
            )

        act = self.add_action(
            "openexternal", self.tr("Open in external application"),
            menu=self.tr("View"),
            tip=self.tr("Open file in an external application at the current "
                        "revision"),
            )

        self.add_action(
            "next", self.tr('Next hunk'),
            menu=self.tr("Moves"),
            icon='down',
            tip=self.tr('Jump to the next hunk'),
            keys=[Qt.ALT + Qt.Key_Down]
            )

        self.add_action(
            "prev", self.tr('Prior hunk'),
            menu=self.tr("Moves"),
            icon='up',
            tip=self.tr('Jump to the previous hunk'),
            keys=[Qt.ALT + Qt.Key_Up]
            )

    def toggle_openexternal(self, status=None):
        openexternal = self.get_action('openexternal')
        if status is None:
            status = not openexternal.isEnabled()
        openexternal.setEnabled(status)

class HgFileView(ActionsMixin, QtGui.QFrame):

    filled = pyqtSignal()
    message_logged = pyqtSignal(str, int)
    rev_for_diff_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        self._diff = None
        self._diffs = None
        self.cfg = None
        super(HgFileView, self).__init__(parent)
        framelayout = QtGui.QVBoxLayout(self)
        framelayout.setContentsMargins(0, 0, 0, 0)
        framelayout.setSpacing(0)

        self.info_frame = QtGui.QFrame()
        framelayout.addWidget(self.info_frame)
        l = QtGui.QVBoxLayout()
        self.info_frame.setLayout(l)
        self.filenamelabel = QtGui.QLabel()
        self.filenamelabel.setWordWrap(True)
        self.filenamelabel.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByKeyboard|
            QtCore.Qt.TextSelectableByMouse|
            QtCore.Qt.LinksAccessibleByMouse)
        self.filenamelabel.linkActivated.connect(
            lambda link: self.displayFile(show_big_file=True))
        self.execflaglabel = QtGui.QLabel()
        self.execflaglabel.setWordWrap(True)
        l.addWidget(self.filenamelabel)
        l.addWidget(self.execflaglabel)
        self.execflaglabel.hide()

        self.filedata_frame = QtGui.QFrame()
        framelayout.addWidget(self.filedata_frame)
        l = QtGui.QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(0)
        self.filedata_frame.setLayout(l)

        self.sci = HgQsci(self)
        l.addWidget(self.sci, 1)

        ll = QtGui.QVBoxLayout()
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)
        l.insertLayout(0, ll)

        ll2 = QtGui.QHBoxLayout()
        ll2.setContentsMargins(0, 0, 0, 0)
        ll2.setSpacing(0)
        ll.addLayout(ll2)

        # used to fill height of the horizontal scroll bar
        w = QtGui.QWidget(self)
        ll.addWidget(w)
        self._spacer = w

        self.blk = BlockList(self)
        self.blk.linkScrollBar(self.sci.verticalScrollBar())
        ll2.addWidget(self.blk)
        self.blk.setVisible(False)

        self.ann = Annotator(self.sci, self)
        ll2.addWidget(self.ann)
        self.ann.setVisible(False)

        self._model = None
        self._ctx = None
        self._filename = None
        self._annotate = False
        self._find_text = None
        self._mode = "diff" # can be 'diff' or 'file'
        self.filedata = None

        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.idle_fill_files)
        self.sci.set_action('diffmode', callback=self.setMode)
        self.sci.set_action('ignorews',
                            callback=lambda value: self.setUiConfig('diff', 'ignorews', value))
        self.sci.set_action('annmode', callback=self.setAnnotate)
        self.sci.set_action('prev', callback=self.prevDiff)
        self.sci.set_action('next', callback=self.nextDiff)
        self.sci.set_action('show-big-file', callback=self.showBigFile)
        self.sci.set_action('openexternal', callback=self.openexternal)
        self.sci.set_action('diffmode', checked=True)

    def resizeEvent(self, event):
        super(HgFileView, self).resizeEvent(event)
        h = self.sci.horizontalScrollBar().height()
        self._spacer.setMinimumHeight(h)
        self._spacer.setMaximumHeight(h)

    def showBigFile(self, state):
        """Force displaying the content related to a file considered previously as
        too big.
        """
        if not self._model.graph:
            return
        if not state:
            self._model.graph.maxfilesize = self.cfg.getMaxFileSize()
        else:
            self._model.graph.maxfilesize = -1
        self.displayFile()

    def setMode(self, mode):
        if isinstance(mode, bool):
            mode = ['file', 'diff'][mode]
        assert mode in ('diff', 'file')

        self.sci.set_actions('annmode', 'next', 'prev', enabled=not mode)
        if mode != self._mode:
            self._mode = mode
            self.blk.setVisible(self._mode == 'file')
            self.ann.setVisible(self._mode == 'file' and self._annotate)

            self.displayFile()

    def setUiConfig(self, section, name, value):
        if self._model.repo.ui._tcfg.get(section, name) == value:
            return
        self._model.repo.ui._tcfg.set(section, name, value, source='hgview')
        self.displayFile()

    def setAnnotate(self, ann):
        self._annotate = ann
        if ann:
            self.displayFile()

    def setModel(self, model):
        # XXX we really need only the "Graph" instance
        self._model = model
        self.cfg = HgConfig(self._model.repo.ui)
        if self._model.graph:
            is_show_big_file = self._model.graph.maxfilesize < 0
        else:
            is_show_big_file = bool(self.cfg.getMaxFileSize())
        self.sci.set_action('show-big-file', checked=is_show_big_file)
        self.sci.set_action('ignorews',
                            checked=model.repo.ui.configbool('diff', 'ignorews'))
        self.sci.setFont(get_font(self.cfg))
        self.sci.clear()


    def setContext(self, ctx):
        self._ctx = ctx
        self._p_rev = None
        self.sci.clear()

    def rev(self):
        return self._ctx.rev()

    def filename(self):
        return self._filename

    def displayDiff(self, rev):
        if rev != self._p_rev:
            self.displayFile(rev=rev)

    def displayFile(self, filename=None, rev=None, show_big_file=None):
        if filename is None:
            filename = self._filename

        self._realfilename = filename
        if isbfile(filename):
            self._filename = bfilepath(filename)
        else:
            self._filename = filename

        if rev is not None:
            self._p_rev = rev
            self.rev_for_diff_changed.emit(rev)
        self.sci.clear()
        self.ann.clear()
        self.filenamelabel.setText(" ")
        self.execflaglabel.clear()
        if filename is None:
            return
        try:
            filectx = self._ctx.filectx(self._realfilename)

        except (LookupError, ManifestLookupError): # occur on deleted files
            self.sci.toggle_openexternal(status=False)
        except HgLookupError: # occur on deleted files
            self.sci.toggle_openexternal(status=False)
            return
        if self._mode == 'diff' and self._p_rev is not None:
            mode = self._p_rev
        else:
            mode = self._mode
        if show_big_file:
            flag, data = self._model.graph.filedata(filename, self._ctx.rev(), mode, maxfilesize=-1)
        else:
            flag, data = self._model.graph.filedata(filename, self._ctx.rev(), mode)
        if data and data[-1] == '\n':
            data = data[:-1]
        if flag == 'file too big':
            self.filedata_frame.hide()
            message = (('<center>'
                        'File size (%s) greater than configured maximum value: '
                        '<font color="red"> maxfilesize=%i</font><br>'
                        '<br>'
                        '<a href="show-big-file">Click to display anyway '
                        '<img src=":/icons/heavy_small.png" width="16" height="16"></a>.'
                        '</center>') % (data, self.cfg.getMaxFileSize()))
            self.filenamelabel.setText(message)
            return
        else:
            self.filedata_frame.show()
        if flag == '-' or flag == '':
            self.sci.toggle_openexternal(status=False)
            return
        self.sci.toggle_openexternal(status=True)

        if data not in (u'file too big', u'binary file'):
            self.filedata = data
        else:
            self.filedata = None

        exec_flag = exec_flag_changed(filectx)
        if exec_flag:
            self.execflaglabel.setText(u"<b>exec mode has been <font color='red'>%s</font></b>" % exec_flag)
            self.execflaglabel.show()
        else:
            self.execflaglabel.hide()

        labeltxt = u''
        if isbfile(self._realfilename):
            labeltxt += u'[bfile tracked] '
        labeltxt += u"<b>%s</b>" % tounicode(self._filename)

        if self._p_rev is not None:
            labeltxt += u' (diff from rev %s)' % self._p_rev
        renamed = filectx.renamed()
        if renamed:
            labeltxt += u' <i>(renamed from %s)</i>' % tounicode(bfilepath(renamed[0]))
        self.filenamelabel.setText(labeltxt)

        self.sci.set_text(filename, data, flag, self.cfg)
        if self._find_text:
            self.highlightSearchString(self._find_text)
        self.sci.set_action('prev', enabled=False)
        self.updateDiffDecorations()
        if self._mode == 'file' and self._annotate:
            if filectx.rev() is None: # XXX hide also for binary files
                self.ann.setVisible(False)
            else:
                self.ann.setVisible(self._annotate)
                self.ann.setFont(self.sci.font())
                self.ann.set_line_ticks([str(f.rev()) for f, __ in filectx.annotate(follow=True)])
        return True

    def openexternal(self):
        """Open the external application with the content of the selected file at
        the selected revision"""
        # We open the current file if the selected revision is the dirty working
        # directory or if it is the working directory without any modification.
        # Else we use a temporary file.
        content_getter = lambda: self._model.graph.filedata(
            self._filename, self._ctx.rev(), 'file', maxfilesize=-1)[1]
        _open_in_external(self, self.cfg, self._ctx.filectx(self._filename),
                          content_getter)

    def updateDiffDecorations(self):
        """
        Recompute the diff and starts the timer
        responsible for filling diff decoration markers
        """
        self.blk.clear()
        if self._mode == 'file' and self.filedata is not None:
            if self.timer.isActive():
                self.timer.stop()

            parent = self._model.graph.fileparent(self._filename, self._ctx.rev())
            if parent is None:
                return
            m = self._ctx.filectx(self._filename).renamed()
            if m:
                pfilename, __ = m
            else:
                pfilename = self._filename
            _, parentdata = self._model.graph.filedata(pfilename,
                                                       parent, 'file')
            if parentdata is not None:
                filedata = self.filedata.splitlines()
                parentdata = parentdata.splitlines()
                self._diff = difflib.SequenceMatcher(None,
                                                     parentdata,
                                                     filedata,)
                self._diffs = []
                self.blk.syncPageStep()
                self.timer.start()

    def _nextDiff(self):
        if self._mode == 'file':
            row, __ = self.sci.getCursorPosition()
            lo = 0
            for i, (lo, __) in enumerate(self._diffs):
                if lo > row:
                    last = (i == (len(self._diffs)-1))
                    break
            else:
                return False
            self.sci.setCursorPosition(lo, 0)
            self.sci.verticalScrollBar().setValue(lo)
            return not last

    def nextDiff(self):
        notlast = self._nextDiff()
        self.sci.set_action('next',
                            enabled=self.fileMode() and notlast and self.nDiffs())
        self.sci.set_action('prev', enabled=self.fileMode() and self.nDiffs())

    def _prevDiff(self):
        if self._mode == 'file':
            row, __ = self.sci.getCursorPosition()
            lo = 0
            for i, (lo, hi) in enumerate(reversed(self._diffs)):
                if hi < row:
                    first = (i == (len(self._diffs)-1))
                    break
            else:
                return False
            self.sci.setCursorPosition(lo, 0)
            self.sci.verticalScrollBar().setValue(lo)
            return not first

    def prevDiff(self):
        notfirst = self._prevDiff()
        self.sci.set_action('prev',
                            enabled=self.fileMode() and notfirst and self.nDiffs())
        self.sci.set_action('next', enabled=self.fileMode() and self.nDiffs())

    def nextLine(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x+1, y)

    def prevLine(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x-1, y)

    def nextCol(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x, y+1)

    def prevCol(self):
        x, y = self.sci.getCursorPosition()
        self.sci.setCursorPosition(x, y-1)

    def nDiffs(self):
        return len(self._diffs)

    def diffMode(self):
        return self._mode == 'diff'
    def fileMode(self):
        return self._mode == 'file'

    def searchString(self, text):
        self._find_text = text
        self.sci.clear_highlights()
        findpos = self.highlightSearchString(self._find_text)
        if findpos:
            def finditer(self, findpos):
                if self._find_text:
                    for pos in findpos:
                        self.sci.highlight_current_search_string(pos, self._find_text)
                        yield self._ctx.rev(), self._filename, pos
            return finditer(self, findpos)

    def highlightSearchString(self, text):
        pos = self.sci.search_and_highlight_string(text)
        msg = u"Found %d occurrences of '%s' in current file or diff" % \
              (len(pos), tounicode(text))
        self.message_logged.emit(msg, 2000)
        return pos

    def verticalScrollBar(self):
        return self.sci.verticalScrollBar()

    def idle_fill_files(self):
        # we make a burst of diff-lines computed at once, but we
        # disable GUI updates for efficiency reasons, then only
        # refresh GUI at the end of the burst
        self.sci.setUpdatesEnabled(False)
        self.blk.setUpdatesEnabled(False)
        for __ in range(30): # burst pool
            if self._diff is None or not self._diff.get_opcodes():
                self._diff = None
                self.timer.stop()
                self.filled.emit()
                self.sci.set_action('next', enabled=self.fileMode() and self.nDiffs())
                break

            tag, __, __, blo, bhi = self._diff.get_opcodes().pop(0)
            if tag == 'replace':
                self._diffs.append([blo, bhi])
                self.blk.addBlock('x', blo, bhi)
                for i in range(blo, bhi):
                    self.sci.markerAdd(i, self.sci.markertriangle)

            elif tag == 'delete':
                pass

            elif tag == 'insert':
                self._diffs.append([blo, bhi])
                self.blk.addBlock('+', blo, bhi)
                for i in range(blo, bhi):
                    self.sci.markerAdd(i, self.sci.markerplus)

            elif tag == 'equal':
                pass

            else:
                raise ValueError, 'unknown tag %r' % (tag,)

        # ok, let's enable GUI refresh for code viewers and diff-block displayers
        self.sci.setUpdatesEnabled(True)
        self.blk.setUpdatesEnabled(True)


class HgFileListView(ActionsMixin, QtGui.QTableView):
    """
    A QTableView for displaying a HgFileListModel
    """

    file_selected = pyqtSignal([str, int], [str])

    def __init__(self, parent=None):
        super(HgFileListView, self).__init__(parent)
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(20)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
        self.setTextElideMode(Qt.ElideLeft)

        self.horizontalHeader().setToolTip('Double click to toggle merge mode')

        self.createActions()

        self.horizontalHeader().sectionDoubleClicked[int].connect(
                self.toggleFullFileList)
        self.doubleClicked.connect(self.fileActivated)

        self.horizontalHeader().sectionResized[int, int, int].connect(
                self.sectionResized)
        self._diff_dialogs = {}
        self._nav_dialogs = {}

    def setModel(self, model):
        super(HgFileListView, self).setModel(model)
        model.layoutChanged.connect(self.fileSelected)
        self.selectionModel().currentRowChanged.connect(
                self.fileSelected)
        self.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

        rowheight = HgConfig(self.model().repo.ui).getRowHeight()
        self.verticalHeader().setDefaultSectionSize(rowheight)

    def currentFile(self):
        index = self.currentIndex()
        return self.model().fileFromIndex(index)

    def toggle_openexternal(self, status=None):
        openexternal = self.get_action('openexternal')
        if status is None:
            status = not openexternal.isEnabled()
        openexternal.setEnabled(status)

    def fileSelected(self, index=None, *args):
        if index is None:
            index = self.currentIndex()
        sel_file = self.model().fileFromIndex(index)
        from_rev = self.model().revFromIndex(index)
        if sel_file is not None:
            self.toggle_openexternal(self.model().fileflag(sel_file) != '-')
        # signal get unicode as input
        if from_rev is None:
            self.file_selected[str].emit(tounicode(sel_file))
        else:
            self.file_selected[str, int].emit(tounicode(sel_file), from_rev)

    def selectFile(self, filename):
        self.setCurrentIndex(self.model().indexFromFile(filename))

    def fileActivated(self, index, alternate=False):
        sel_file = self.model().fileFromIndex(index)
        if sel_file is '':
            return
        if alternate:
            self.navigate(sel_file)
        else:
            self.diffNavigate(sel_file)

    def toggleFullFileList(self, *args):
        self.model().toggleFullFileList()

    def openexternal(self):
        """Open an external application with the content of the selected file at
        the selected revision"""
        index = self.currentIndex()
        sel_file = self.model().fileFromIndex(index)
        from_rev = self.model().current_ctx.rev()
        try:
            filectx = self.model().repo[from_rev].filectx(sel_file)
        except (LookupError, ManifestLookupError):
            return
        _open_in_external(self, HgConfig(self.model().repo.ui),
                          filectx, filectx.data)

    def navigate(self, filename=None):
        from hgviewlib.qt4.hgfiledialog import FileViewer
        self._navigate(filename, FileViewer, self._nav_dialogs)

    def diffNavigate(self, filename=None):
        from hgviewlib.qt4.hgfiledialog import FileDiffViewer
        self._navigate(filename, FileDiffViewer, self._diff_dialogs)

    def _navigate(self, filename, dlgclass, dlgdict):
        if filename is None:
            filename = self.currentFile()
        model = self.model()
        if filename and len(model.repo.file(filename))>0:
            if filename not in dlgdict:
                dlg = dlgclass(model.repo, filename,
                               repoviewer=self.window())
                dlgdict[filename] = dlg

                dlg.setWindowTitle('Hg file log viewer')
            dlg = dlgdict[filename]
            dlg.goto(model.current_ctx.rev())
            dlg.show()
            dlg.raise_()
            dlg.activateWindow()

    def createActions(self):
        self.add_action(
            'navigate', self.tr("Navigate"),
            menu=self.tr("navigate"),
            tip=self.tr('Navigate the revision tree of this file'),
            callback=lambda: self.navigate(),
            )

        self.add_action(
            'diffnavigate', self.tr("Diff-mode navigate"),
            menu=self.tr("navigate"),
            tip=self.tr('Navigate the history of this file in diff mode'),
            callback=lambda: self.diffNavigate(),
            )

        self.add_action(
            "openexternal", self.tr("Open in external application"),
            menu=self.tr("View"),
            tip=self.tr("Open file in an external application at the current "
                        "revision"),
            callback=self.openexternal,
        )

    def resizeEvent(self, event):
        vp_width = self.viewport().width()
        col_widths = [self.columnWidth(i) \
                      for i in range(1, self.model().columnCount())]
        col_width = vp_width - sum(col_widths)
        col_width = max(col_width, 50)
        self.setColumnWidth(0, col_width)
        QtGui.QTableView.resizeEvent(self, event)

    def sectionResized(self, idx, oldsize, newsize):
        if idx == 1:
            self.model().setDiffWidth(newsize)

    def nextFile(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(min(row+1,
                             self.model().rowCount() - 1), 0))
    def prevFile(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(max(row - 1, 0), 0))


def _open_in_external(parent, cfg, filectx, content_getter):
    """Open an external application on the file at the context ``filectx``.

    If the selected revision is the working directory then the original file
    opened else a temporary file is created.
    """
    if filectx.rev() is None: # dirty wd is selected
        return _open_originalfile_in_external(parent, filectx)
    if ((not filectx._repo[None].dirty()) and                    # the wd is clean and
        (filectx.changectx() in filectx._repo[None].parents())): # a wd parent is selected
        return _open_originalfile_in_external(parent, filectx)
    content = content_getter()
    suffix = '_%s-%s-%s' % (filectx.rev(), str(filectx.changectx()),
                            os.path.basename(filectx.path()))
    _open_tempfile_in_external(parent, content, suffix=suffix)


def _open_originalfile_in_external(parent, filectx):
    """Open an external application on the original file from filectx"""
    filepath = os.path.join(
        os.path.abspath(filectx._repo.root),
        filectx.path()
        )
    return QtGui.QDesktopServices.openUrl(QtCore.QUrl(filepath))


def _open_tempfile_in_external(parent, content, suffix=None):
    """Open an external application with the given ``content`` in a temporary
    file.

    ``suffix`` is the suffix for the temporary file name.
    ``parent`` is a Qt component that gets a reference to the editor process.
    """
    fid, filepath = tempfile.mkstemp(suffix=suffix)
    os.close(fid)
    with open(filepath, 'w') as fid:
        fid.write(content)
    return QtGui.QDesktopServices.openUrl(QtCore.QUrl(filepath))
