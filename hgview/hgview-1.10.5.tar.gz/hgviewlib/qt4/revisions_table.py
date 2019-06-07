# Copyright (c) 2013 LOGILAB S.A. (Paris, FRANCE).
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
from operator import le, ge, lt, gt

from mercurial import cmdutil, ui
from mercurial.error import (RepoError, ParseError, LookupError,
                             RepoLookupError, Abort)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt, pyqtSignal

from hgviewlib.config import HgConfig
from hgviewlib.hgpatches.scmutil import revrange
from hgviewlib.util import tounicode
from hgviewlib.qt4.mixins import ActionsMixin
from hgviewlib.qt4.widgets import StyledTableView, SmartResizeTableView, \
     QueryLineEdit
from hgviewlib.qt4.quickbar import QuickBar
from hgviewlib.qt4.helpviewer import HgHelpViewer
from hgviewlib.qt4.styleditemdelegate import GraphItemDelegate

class GotoQuery(QtCore.QThread):
    """A dedicated thread that queries a revset to the repo related to
    the model"""

    failed_revset = pyqtSignal(str)
    new_revset = pyqtSignal(tuple, str)

    def __init__(self):
        super(GotoQuery, self).__init__()
        self.rows = None
        self.revexp = None
        self.model = None

    def __del__(self):
        self.terminate()

    def run(self):
        revset = None
        try:
            revset = revrange(self.model.repo, [self.revexp.encode('utf-8')])
        except (RepoError, ParseError, LookupError, RepoLookupError, Abort), err:
            self.rows = None
            self.failed_revset.emit(tounicode(err))
            return
        if revset is None:
            self.rows = ()
            self.new_revset.emit(self.rows, self.revexp)
            return
        rows = (idx.row() for idx in
                (self.model.indexFromRev(rev) for rev in revset)
                if idx is not None)
        self.rows = tuple(sorted(rows))
        self.new_revset.emit(self.rows, self.revexp)

    def perform(self, revexp, model):
        self.terminate()
        self.revexp = revexp
        self.model = model
        self.start()

    def perform_now(self, revexp, model):
        self.revexp = revexp
        self.model = model
        self.run()

    def get_last_results(self):
        return self.rows

class CompleterModel(QtGui.QStringListModel):
    def add_to_string_list(self, *values):
        strings = self.stringList()
        for value in values:
            if value not in strings:
                strings.append(value)
        self.setStringList(strings)

class GotoQuickBar(QuickBar):

    goto_strict_next_from = pyqtSignal(tuple)
    goto_strict_prev_from = pyqtSignal(tuple)
    new_set = pyqtSignal([], [tuple])
    goto_next_from = pyqtSignal(tuple)

    def __init__(self, parent, name='Goto'):
        self._parent = parent
        self._goto_query = None
        self.compl_model = None
        self.completer = None
        self.row_before = 0
        self._standby_revexp = None # revexp that requires an action from user
        QuickBar.__init__(self, parent, name)

    def createActions(self):

        QuickBar.createActions(self)

        self.add_action(
            'next', self.tr("Select Next"),
            icon='forward',
            tip=self.tr("Select the next matched revision"),
            callback=lambda: self.goto(forward=True),
        )

        self.add_action(
            'prev', self.tr("Select Previous"),
            icon='back',
            tip=self.tr("Select the Previous matched revision"),
            callback=lambda: self.goto(forward=False),
        )

        self.add_action(
            'help', self.tr("advanced help"),
            icon='help',
            tip=self.tr("Display avanced search help on 'revset'"),
            callback=self.show_help,
        )

    def createContent(self):
        # completer
        self.compl_model = CompleterModel(['tip'])
        self.completer = QtGui.QCompleter(self.compl_model, self)
        cb = lambda text: self.search(text)
        self.completer.activated[str].connect(cb)
        # entry
        self.entry = QueryLineEdit(self)
        self.entry.setCompleter(self.completer)
        self.entry.setStatusTip("Enter a 'revset' to query a set of revisions")
        self.addWidget(self.entry)
        self.entry.text_edited_no_blank.connect(self.auto_search)
        self.entry.returnPressed.connect(lambda: self.goto(True))
        # actions (better placed here)
        self.addActions(self.get_actions('prev', 'next', 'help'))
        # querier (threaded)
        self._goto_query = GotoQuery()
        self._goto_query.failed_revset.connect(self.on_failed)
        self._goto_query.new_revset.connect(self.on_queried)

    def setVisible(self, visible=True):
        QuickBar.setVisible(self, visible)
        if visible:
            self.entry.setFocus()
            self.entry.selectAll()

    def __del__(self):
        #  QObject::startTimer: QTimer can only be used with threads
        #  started with QThread
        self.entry.setCompleter(None)

    def show_help(self):
        w = HgHelpViewer(self._parent.model().repo, 'revset', self)
        w.show()
        w.raise_()
        w.activateWindow()

    def auto_search(self, revexp):
        # Do not automatically search for revision number.
        # The problem is that the auto search system will
        # query for lower revision number: users may type the revision
        # number by hand which induce that the first numeric char will be
        # queried alone.
        # But the first found revision is automatically selected, so to much
        # revision tree will be loaded.
        if revexp.isdigit():
            self.entry.status = 'normal'
            self.set_actions('next', 'prev', enabled=True)
            self.show_message(
                'Hit [Enter] because '
                'revision number is not automatically queried '
                'for optimization purpose.')
            self._standby_revexp = revexp
            return
        self.search(revexp)

    def goto(self, forward=True):
        # returnPressed from the `entry` also call this slot
        # We check if the main corresponding action is enabled
        if not self.get_action('next').isEnabled():
            if self.entry.status == 'failed':
                self.show_message("Invalid revset expression.")
            else:
                self.show_message("Querying, please wait (or edit to cancel).")
            return
        if self._standby_revexp is not None:
            self.search(self._standby_revexp, threaded=False)
        rows = self._goto_query.get_last_results()
        if rows is None:
            self.entry.status = 'failed'
            return
        if forward:
            signal = self.goto_strict_next_from[tuple]
        else:
            signal = self.goto_strict_prev_from[tuple]
        signal.emit(rows)
        # usecase: enter a nodeid and hit enter to go on,
        #          so the goto tool bar is no more required and may be
        #          annoying
        if rows and len(rows) == 1:
            self.setVisible(False)

    def search(self, revexp, threaded=True):
        if revexp is None:
            revexp = self._standby_revexp
        self._standby_revexp = None
        if not revexp:
            self.new_set.emit()
            self.goto_next_from[tuple].emit((self.row_before,))
            return
        self.show_message("Querying ... (edit the entry to cancel)")
        self.set_actions('next', 'prev', enabled=False)
        self.entry.status = 'query'
        if threaded:
            self._goto_query.perform(revexp, self._parent.model())
        else:
            self._goto_query.perform_now(revexp, self._parent.model())

    def show_message(self, message, delay=-1):
        self.parent().statusBar().showMessage(message, delay)

    def on_queried(self, rows=None, revexp=u''):
        """Slot to handle new revset."""
        self.entry.status = 'valid'
        self.new_set[tuple].emit(rows)
        self.goto_next_from[tuple].emit(rows)
        self.set_actions('next', 'prev', enabled=True)
        if rows and revexp:
            self.compl_model.add_to_string_list(revexp)

    def on_failed(self, err):
        self.entry.status = 'failed'
        self.show_message(tounicode(err))
        self.set_actions('next', 'prev', enabled=False)


class RevisionsTableView(ActionsMixin, StyledTableView, SmartResizeTableView):
    """
    A QTableView for displaying a FileRevModel or a HgRepoListModel,
    with actions, shortcuts, etc.
    """

    start_from_rev = pyqtSignal([], [int, bool], [str, bool])
    revision_activated = pyqtSignal([], [int])
    revision_selected = pyqtSignal([], [int])
    message_logged = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super(RevisionsTableView, self).__init__(parent)
        self.init_variables()
        self.setShowGrid(False)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(20)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)

        self.createActions()
        self.createToolbars()

        self.doubleClicked.connect(self.revisionActivated)

        self.styled_item_delegate = GraphItemDelegate(self)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        self.pointed_rev = self.revFromindex(self.indexAt(event.pos()))
        if event.button() == Qt.MidButton:
            self.gotoAncestor()
            return
        elif event.button() == Qt.LeftButton:
            super(RevisionsTableView, self).mousePressEvent(event)

    def createToolbars(self):
        self.goto_toolbar = GotoQuickBar(self)
        goto = self.on_goto_next_from
        self.goto_toolbar.goto_strict_next_from[tuple].connect(
                lambda revs: goto(revs, strict=True, forward=True))
        self.goto_toolbar.goto_strict_prev_from[tuple].connect(
                lambda revs: goto(revs, strict=True, forward=False))
        self.goto_toolbar.goto_next_from[tuple].connect(goto)
        self.goto_toolbar.new_set.connect(self.highlight_rows)
        self.goto_toolbar.new_set[tuple].connect(self.highlight_rows)

    def createActions(self):
        self.add_action(
            'copycs', self.tr("Export to clipboard"),
            menu=self.tr("Content"),
            tip=self.tr("Export changeset metadata the window manager "
                        "clipboard [see configuration entry "
                        "'exporttemplate']"),
            callback=self.copy_cs_to_clipboard,
        )

        self.add_action(
            'manifest', self.tr("Manifest"),
            menu=self.tr("Content"),
            tip=self.tr("Show the manifest at selected revision"),
            keys=[Qt.SHIFT + Qt.Key_Enter, Qt.SHIFT + Qt.Key_Return],
            callback=self.showAtRev,
        )

        self.add_action(
            'back', self.tr("Previous visited"),
            menu=self.tr("Select"),
            icon='back',
            tip=self.tr("Backward to the previous visited changeset"),
            keys=[QtGui.QKeySequence(QtGui.QKeySequence.Back)],
            callback=self.back,
        )

        self.add_action(
            'forward', self.tr("Next visited"),
            menu=self.tr("Select"),
            icon='forward',
            tip=self.tr("Forward to the next visited changeset"),
            keys=[QtGui.QKeySequence(QtGui.QKeySequence.Forward)],
            callback=self.forward,
        )

        self.add_action(
            'gotoancestor', self.tr('ancestor of this and selected'),
            menu=self.tr("Select"),
            icon='goto',
            tip=self.tr("Select the common ancestor of current pointed "
                        "and selected revisions"),
            callback=self.gotoAncestor,
        )

        self.add_action(
            'start', self.tr("Hide higher revisions"),
            menu=self.tr("Filter"),
            tip=self.tr("Start graph from this revision"),
            keys=[Qt.Key_Backspace],
            callback=self.startFromRev,
        )

        self.add_action(
            'follow', self.tr("Show ancestors only"),
            menu=self.tr("Filter"),
            tip=self.tr("Follow revision history from this revision"),
            keys=[Qt.SHIFT + Qt.Key_Backspace],
            callback=self.followFromRev,
        )

        self.add_action(
            'unfilter', self.tr("Show all changesets"),
            menu=self.tr("Filter"),
            icon='unfilter',
            tip=self.tr("Remove filter and show all changesets"),
            keys=[Qt.ALT + Qt.CTRL + Qt.Key_Backspace],
            callback=self.removeFilter,
            enabled=False,
        )

        self.start_from_rev.connect(self.update_filter_action)
        self.start_from_rev[int, bool].connect(self.update_filter_action)
        self.start_from_rev[str, bool].connect(self.update_filter_action)

    def update_filter_action(self, rev=None, follow=None):
        self.set_action('unfilter', enabled=rev is not None)

    def copy_cs_to_clipboard(self):
        """ Copy changeset metadata into the window manager clipboard."""
        repo = self.model().repo
        rev = self.pointed_rev if self.pointed_rev is not None else self.current_rev
        ctx = repo[rev]
        u = ui.ui(repo.ui)
        template = HgConfig(u).getExportTemplate()
        u.pushbuffer()
        cmdutil.show_changeset(u, repo, {'template':template}, False).show(ctx)
        QtGui.QApplication.clipboard().setText(u.popbuffer())

    def showAtRev(self):
        rev = self.pointed_rev if self.pointed_rev is not None else self.current_rev
        if rev is None:
            self.revision_activated.emit()
        else:
            self.revision_activated[int].emit(rev)

    def startFromRev(self):
        rev = self.current_rev if self.pointed_rev is None else self.pointed_rev
        if rev is None:
            self.start_from_rev.emit()
        else:
            self.start_from_rev[int, bool].emit(rev, False)

    def followFromRev(self):
        rev = self.pointed_rev if self.pointed_rev is not None else self.current_rev
        if rev is None:
            self.start_from_rev.emit()
        else:
            self.start_from_rev[int, bool].emit(rev, True)

    def removeFilter(self):
        self.start_from_rev.emit()

    def init_variables(self):
        # member variables
        self.current_rev = None # revision selected for which details are shown
        self.pointed_rev = None # revision pointed by mouse but not selected
        # rev navigation history (manage 'back' action)
        self._rev_history = []
        self._rev_pos = -1
        self._in_history = False # flag set when we are "in" the
        # history. It is required cause we cannot known, in
        # "revision_selected", if we are creating a new branch in the
        # history navigation or if we are navigating the history

    def setModel(self, model):
        self.init_variables()
        super(RevisionsTableView, self).setModel(model)
        self.selectionModel().currentRowChanged.connect(self.revisionSelected)
        tags = (tounicode(tag) for tag in model.repo.tags().keys())
        self.goto_toolbar.compl_model.add_to_string_list(*tags)
        revaliases = [tounicode(item[0]) for item in model.repo.ui.configitems("revsetalias")]
        self.goto_toolbar.compl_model.add_to_string_list(*revaliases)
        col = list(model._columns).index('Log')
        self.horizontalHeader().setResizeMode(col, QtGui.QHeaderView.Stretch)

    def is_styled_column(self, index):
        return self.model()._columns[index] == 'Log'

    def get_column_stretch(self, index):
        model = self.model()
        return model._stretchs.get(model._columns[index])

    def revFromindex(self, index):
        if not index.isValid():
            return
        model = self.model()
        if model and model.graph:
            row = index.row()
            gnode = model.graph[row]
            return gnode.rev

    def revisionActivated(self, index):
        rev = self.revFromindex(index)
        if rev is not None:
            self.revision_activated[int].emit(rev)

    def revisionSelected(self, index, index_from):
        """
        Callback called when a revision is selected in the revisions table
        """
        rev = self.revFromindex(index)
        if True:#rev is not None:
            model = self.model()
            if self.current_rev is not None and self.current_rev == rev:
                return
            if not self._in_history:
                del self._rev_history[self._rev_pos+1:]
                self._rev_history.append(rev)
                self._rev_pos = len(self._rev_history)-1

            self._in_history = False
            self.current_rev = rev

            if rev is None:
                self.revision_selected.emit()
            else:
                self.revision_selected[int].emit(rev)
            self.set_navigation_button_state()

    def gotoAncestor(self):
        """goto and select the common ancestor of self.pointed_rev and
        self.current_rev."""
        repo = self.model().repo
        pointed = self.pointed_rev if self.pointed_rev is not None else repo[None].rev()
        current = self.current_rev if self.current_rev is not None else repo[None].rev()
        ctx = repo[current]
        ctx2 = repo[pointed]
        ancestor = ctx.ancestor(ctx2)
        self.message_logged.emit(
            "Goto ancestor of %s and %s"%(ctx.rev(), ctx2.rev()),
            5000)
        self.goto(ancestor.rev())

    def set_navigation_button_state(self):
        if len(self._rev_history) > 0:
            back = self._rev_pos > 0
            forw = self._rev_pos < len(self._rev_history)-1
        else:
            back = False
            forw = False
        self.set_action('back', enabled=back)
        self.set_action('forward', enabled=forw)

    def back(self):
        if self._rev_history and self._rev_pos>0:
            self._rev_pos -= 1
            idx = self.model().indexFromRev(self._rev_history[self._rev_pos])
            if idx is not None:
                self._in_history = True
                self.setCurrentIndex(idx)
        self.set_navigation_button_state()

    def forward(self):
        if self._rev_history and self._rev_pos<(len(self._rev_history)-1):
            self._rev_pos += 1
            idx = self.model().indexFromRev(self._rev_history[self._rev_pos])
            if idx is not None:
                self._in_history = True
                self.setCurrentIndex(idx)
        self.set_navigation_button_state()

    def goto(self, rev=None):
        """
        Select revision 'rev'.
        It can be anything understood by repo.changectx():
          revision number, node or tag for instance.
        """
        if isinstance(rev, basestring) and ':' in rev:
            rev = rev.split(':')[1]
        repo = self.model().repo
        try:
            rev = repo[rev].rev()
        except RepoError:
            self.message_logged.emit(
                      "Can't find revision '%s'" % rev, 2000)
        else:
            idx = self.model().indexFromRev(rev)
            if idx is not None:
                self.goto_toolbar.setVisible(False)
                self.setCurrentIndex(idx)

    def on_goto_next_from(self, rows, strict=False, forward=True):
        """Select the next row available in rows."""
        if not rows:
            return
        currow = self.currentIndex().row()
        if strict:
            greater, less = gt, lt
        else:
            greater, less = ge, le
        if forward:
            comparer, _rows = greater, rows
        else:
            comparer, _rows = less, reversed(rows)
        try:
            row = (row for row in _rows if comparer(row, currow)).next()
        except StopIteration:
            self.visual_bell()
            row = rows[0 if forward else -1]
        self.setCurrentIndex(self.model().index(row, 0))
        pos = rows.index(row) + 1
        self.message_logged.emit(
                  "revision #%i of %i" % (pos, len(rows)),
                  -1)

    def nextRev(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(min(row+1,
                             self.model().rowCount() - 1), 0))
    def prevRev(self):
        row = self.currentIndex().row()
        self.setCurrentIndex(self.model().index(max(row - 1, 0), 0))

    def highlight_rows(self, rows=None):
        if rows is None:
            self.visual_bell()
            self.message_logged.emit('Revision set cleared.', 2000)
        else:
            self.message_logged.emit(
                      '%i revisions found.' % len(rows),
                      2000)
        self.model().highlight_rows(rows or ())
        self.refresh_display()

    def refresh_display(self):
        for item in self.children():
            try:
                item.update()
            except AttributeError:
                pass

    def visual_bell(self):
        self.hide()
        QtCore.QTimer.singleShot(0.01, lambda: self.show())

