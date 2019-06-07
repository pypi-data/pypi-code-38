# -*- coding: iso-8859-1 -*-
# main.py - qt4-based hg rev log browser
#
# Copyright (C) 2007-2010 Logilab. All rights reserved.
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.
"""
Main Qt4 application for hgview
"""

import sys, os
import os.path as osp
import re
import errno
from functools import partial
from operator import methodcaller

from PyQt4 import QtCore, QtGui, Qsci

from mercurial import ui, hg
from mercurial import util
from mercurial.error import RepoError


from hgviewlib.application import HgRepoViewer as _HgRepoViewer
from hgviewlib.util import (tounicode, find_repository, rootpath, build_repo,
                            upward_path, read_nested_repo_paths, allbranches)
from hgviewlib.hggraph import diff as revdiff
from hgviewlib.decorators import timeit
from hgviewlib.config import HgConfig
from hgviewlib.util import compose

from hgviewlib.qt4.hgrepomodel import HgRepoListModel, HgFileListModel
from hgviewlib.qt4.hgfiledialog import FileViewer, FileDiffViewer
from hgviewlib.qt4.hgmanifestdialog import ManifestViewer
from hgviewlib.qt4.mixins import HgDialogMixin, ActionsMixin, ui2cls
from hgviewlib.qt4.quickbar import FindInGraphlogQuickBar
from hgviewlib.qt4.helpviewer import HgviewHelpViewer
from hgviewlib.hgpatches import hiddenrevs

from mercurial.error import RepoError

Qt = QtCore.Qt
bold = QtGui.QFont.Bold

NESTED_PREFIX = u'\N{RIGHTWARDS ARROW} '

class HgRepoViewer(ActionsMixin, HgDialogMixin, ui2cls('hgqv.ui'), QtGui.QMainWindow, _HgRepoViewer):
    """hg repository viewer/browser application"""
    def __init__(self, repo, fromhead=None):
        self.repo = repo
        # these are used to know where to go after a reload
        self._reload_rev = None
        self._reload_file = None
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        super(HgRepoViewer, self).__init__()
        self.load_ui()
        if not self.repo.root:
            repopath = self.ask_repository()
            self.repo = build_repo(ui.ui(), repopath)
        self.load_config(self.repo)

        self.setWindowTitle('hgview: %s' % os.path.abspath(str(self.repo.root)))
        self.menubar.hide()

        self.splitter_2.setStretchFactor(0, 2)
        self.splitter_2.setStretchFactor(1, 1)

        # hide bottom at startup
        self.frame_maincontent.setVisible(self.cfg.getContentAtStartUp())

        self.createActions()
        self.createToolbars()

        self.textview_status.setFont(self._font)
        self.textview_status.message_logged.connect(
                self.statusBar().showMessage)
        self.tableView_revisions.message_logged.connect(
                self.statusBar().showMessage)

        # setup tables and views
        if self.repo.root is not None:

            self.setupHeaderTextview()
            self.setupBranchCombo()
            self.setupModels(fromhead)
            self._setupQuickOpen()

        to_utf8 = methodcaller('encode', 'utf-8')
        if self.cfg.getFileDescriptionView() == 'asfile':
            fileselcallback = compose(self.displaySelectedFile, to_utf8)
        else:
            fileselcallback = compose(self.textview_status.displayFile, to_utf8)
        self.tableView_filelist.file_selected[str].connect(fileselcallback)
        self.tableView_filelist.file_selected[str, int].connect(fileselcallback)

        self.textview_status.rev_for_diff_changed.connect(
                self.textview_header.setDiffRevision)

        if fromhead:
            self.startrev_entry.setText(str(fromhead))
        self.setupRevisionTable()

        if self.repo.root is not None:
            self._repodate = self._getrepomtime()
            self._watchrepotimer = self.startTimer(500)

    def timerEvent(self, event):
        if event.timerId() == self._watchrepotimer:
            mtime = self._getrepomtime()
            if mtime > self._repodate:
                self.statusBar().showMessage("Repository has been modified, "
                                             "reloading...", 2000)

                self.reload()

    def contextMenuEvent(self, event):
        # The contextMenuEvent in this qt widgets automatically add actions.
        # If we rewrite it (as done in ActionsMixin), we cannot conserve
        # the original menu :/
        QtGui.QMainWindow.contextMenuEvent(self, event)

    def _setupQuickOpen(self):
        """Initiliaze the quick open menu

        This call utils function to search for possible nested repo setup"""
        # quick open repository
        self.quickOpen_comboBox.clear()
        repopath = osp.abspath(self.repo.root)
        #  search backward until the root folder for a master
        #  repository that contains confman or subrepo data
        for master_path in upward_path(repopath):
            if not osp.exists(osp.join(master_path, '.hg')):
                continue  # Not a repo!
            subrepos = read_nested_repo_paths(master_path)
            if not subrepos:
                continue  # Nothing nested!
            # We found a nested repo setup!
            #
            # But is it related to the viewed repo?
            involved_paths = [master_path] + [pth for _, pth in subrepos]
            if repopath in involved_paths:
                master_name = tounicode(osp.basename(master_path))
                repos = [(master_name, master_path)]
                for name, path in subrepos:
                    repos.append((NESTED_PREFIX + name, path))
                repos.sort()
                break  # I've found related! I'll survive the glaciation!
        else:
            # They migrated without me. They do this every year.
            #
            # Nothing to quick-open hide the toolbar and interrupt
            self.toolBar_quickopen.setVisible(False)
            return
        self.toolBar_quickopen.setVisible(True)
        # TODO: add a treeview with a complete graph.
        curidx = 0
        for idx, (text, data) in enumerate(repos):
            if data == self.repo.root:
                curidx = idx
            self.quickOpen_comboBox.addItem(text, data)
        self.quickOpen_comboBox.setCurrentIndex(curidx)

    def setupBranchComboAndReload(self, *args):
        self.setupBranchCombo()
        self.reload()

    def setupBranchCombo(self, *args):
        branches = allbranches(self.repo, self.branch_checkBox_action.isChecked())

        if len(branches) == 1:
            self.branch_label_action.setEnabled(False)
            self.branch_comboBox_action.setEnabled(False)
        else:
            self.branchesmodel = QtGui.QStringListModel([''] + branches)
            self.branch_comboBox.setModel(self.branchesmodel)
            self.branch_label_action.setEnabled(True)
            self.branch_comboBox_action.setEnabled(True)

    def createToolbars(self):
        # find quickbar
        self.find_toolbar = FindInGraphlogQuickBar(self)
        self.find_toolbar.attachFileView(self.textview_status)
        self.find_toolbar.attachHeaderView(self.textview_header)
        self.find_toolbar.revision_selected.connect(
                self.tableView_revisions.goto)
        self.find_toolbar.revision_selected[int].connect(
                self.tableView_revisions.goto)
        self.find_toolbar.file_selected.connect(
                self.tableView_filelist.selectFile)
        self.find_toolbar.message_logged.connect(
                self.statusBar().showMessage,
                Qt.QueuedConnection)
        self.attachQuickBar(self.find_toolbar)

        # navigation toolbar
        self.toolBar_edit.addAction(self.get_action('content'))
        self.toolBar_edit.addActions(
            self.tableView_revisions.get_actions('back', 'forward'))

        findaction = self.add_action(
            'find', self.find_toolbar.toggleViewAction(),
            menu=self.tr("edit"),
            icon='find',
            keys=['/', 'Ctrl+f'],
            tip=self.tr("Search text in all revisions metadata"),
            )
        self.toolBar_edit.addAction(findaction)

        cb = self.quickOpen_comboBox = QtGui.QComboBox()
        cb.setStatusTip("Quick open other repositories")
        self.quickOpen_action = self.toolBar_quickopen.addWidget(cb)
        _callback = lambda: self.open_repository(cb.itemData(cb.currentIndex()))
        self.quickOpen_comboBox.activated.connect(_callback)

        # tree filters toolbar
        self.toolBar_treefilters.addAction(self.get_action('showhide'))
        self.toolBar_treefilters.addAction(self.tableView_revisions.get_action('unfilter'))
        self.toolBar_treefilters.addAction(self.get_action('showhide'))

        self.branch_label = QtGui.QToolButton()
        self.branch_label.setText("Branch")
        self.branch_label.setStatusTip("Display graph the named branch only")
        self.branch_label.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.branch_menu = QtGui.QMenu()
        cbranch_action = self.branch_menu.addAction("Display closed branches")
        cbranch_action.setCheckable(True)
        self.branch_checkBox_action = cbranch_action
        self.branch_label.setMenu(self.branch_menu)
        self.branch_comboBox = QtGui.QComboBox()
        self.branch_comboBox.activated[str].connect(self.refreshRevisionTable)
        cbranch_action.toggled[bool].connect(self.setupBranchComboAndReload)

        self.toolBar_treefilters.layout().setSpacing(3)

        self.branch_label_action = self.toolBar_treefilters.addWidget(self.branch_label)
        self.branch_comboBox_action = self.toolBar_treefilters.addWidget(self.branch_comboBox)
        # separator
        self.toolBar_treefilters.addSeparator()

        self.startrev_label = QtGui.QToolButton()
        self.startrev_label.setText("Start rev.")
        self.startrev_label.setStatusTip("Display graph from this revision")
        self.startrev_label.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.startrev_entry = QtGui.QLineEdit()
        self.startrev_entry.setStatusTip("Display graph from this revision")
        self.startrev_menu = QtGui.QMenu()
        follow_action = self.startrev_menu.addAction("Follow mode")
        follow_action.setCheckable(True)
        follow_action.setStatusTip("Follow changeset history from start revision")
        self.startrev_follow_action = follow_action
        self.startrev_label.setMenu(self.startrev_menu)
        callback = lambda *a: self.tableView_revisions.start_from_rev[str, bool].emit(
            str(self.startrev_entry.text()), self.startrev_follow_action.isChecked())
        self.startrev_entry.editingFinished.connect(callback)
        self.startrev_follow_action.toggled[bool].connect(callback)

        self.revscompl_model = QtGui.QStringListModel(['tip'])
        self.revcompleter = QtGui.QCompleter(self.revscompl_model, self)
        self.startrev_entry.setCompleter(self.revcompleter)

        self.startrev_label_action = self.toolBar_treefilters.addWidget(self.startrev_label)
        self.startrev_entry_action = self.toolBar_treefilters.addWidget(self.startrev_entry)

        # diff mode toolbar
        actions = self.textview_status.sci.get_actions(
            'diffmode', 'prev', 'next', 'show-big-file')
        self.toolBar_diff.addActions(actions)

        # rev mod toolbar
        self.toolBar_rev.addAction(self.textview_header.get_action('rst'))

        self._handle_toolbar_visibility()

        self.addAction(self.actionQuit)

    def _handle_toolbar_visibility(self):
        """Initial value and event hooking

        This function read toolbar related persistent settings from QT API.
        It also setup hooks on visibility changes so to make the setting
        persistent.
        """
        toolbars = (self.toolBar_file,
                    self.toolBar_quickopen,
                    self.toolBar_edit,
                    self.toolBar_treefilters,
                    self.toolBar_diff,
                    self.toolBar_rev,
                    self.toolBar_help)
        settings = QtCore.QSettings()
        for toolbar in toolbars:
            entryname = '%s/%s/visible' % (self.objectName(), toolbar.objectName())
            # bring back persistent status
            status = settings.value(entryname)
            if status is None:
                status = 1
            else:
                try:
                    status = int(status)
                except ValueError:
                    # for backward compatibility
                    status = {'false': False , 'true': True}.get(status.lower(), status)
                    status = int(status)

            toolbar.setVisible(status)
            # update settings on visibility toggleling
            # We use integers because PyQt4 setting stores boolean as strings
            # with QVariant api version 2
            toolbar.toggleViewAction().toggled[bool].connect(
                compose(partial(settings.setValue, entryname), int)
            )


    def createActions(self):
        # main window actions (from .ui file)
        self.add_action(
            'open', self.actionOpen_repository,
            tip=self.tr("Change watched repository"),
            callback=self.open_repository,
            )

        self.add_action(
            'refresh', self.actionRefresh,
            icon='reload',
            tip=self.tr("Refresh watched repository metadata"),
            callback=self.reload,
            )

        self.add_action(
            'quit', self.actionQuit,
            icon='quit',
            tip=self.tr("Quit Hgview"),
            callback=self.close,
            )

        self.add_action(
            'help', self.actionHelp,
            icon='help',
            tip=self.tr("Display Hgview help"),
            callback=self.on_help,
            )

        act = self.add_action(
            'showhide', self.tr("self.tr('Show/Hide Hidden')"),
            icon='showhide',
            tip=self.tr('Show/Hide hidden changeset'),
            callback=self.refreshRevisionTable,
            checked=bool(self.cfg.getShowHidden()),
            )

        act = self.add_action(
            'content', self.tr("Content"),
            icon='content',
            tip=self.tr('Show/Hide changeset content'),
            keys=[Qt.Key_Space],
            callback=self.toggleMainContent,
            checked=bool(self.cfg.getContentAtStartUp()),
            )

        # Next/Prev file
        act = self.add_action(
            'nextfile', self.tr("Next file"),
            icon='back',
            tip=self.tr("Select the next file"),
            keys=['Right'],
            callback=self.tableView_filelist.nextFile
            )
        self.disab_shortcuts.append(act)

        act = self.add_action(
            'prevfile', self.tr("Previous file"),
            icon='forward',
            tip=self.tr("Select the previous file"),
            keys=['Left'],
            callback=self.tableView_filelist.prevFile
            )
        self.disab_shortcuts.append(act)

        # Next/Prev rev
        act = self.add_action(
            'nextrev', self.tr("Next revision"),
            icon='down',
            tip=self.tr("Select the next revision in the graph"),
            keys=['Down'],
            callback=self.tableView_revisions.nextRev
            )
        self.disab_shortcuts.append(act)

        act = self.add_action(
            'prevrev', self.tr("Previous revision"),
            icon='up',
            tip=self.tr("Select the previous revision in the graph"),
            keys=['Up'],
            callback=self.tableView_revisions.prevRev
            )
        self.disab_shortcuts.append(act)

        # navigate in file viewer
        self.add_action(
            'next-line', self.tr('Next line'),
            tip=self.tr('Select the next line'),
            keys=[Qt.SHIFT + Qt.Key_Down],
            callback=self.textview_status.nextLine,
            )
        self.add_action(
            'prev-line', self.tr('Previous line'),
            tip=self.tr('Select the previous line'),
            keys=[Qt.SHIFT + Qt.Key_Up],
            callback=self.textview_status.prevLine,
            )
        self.add_action(
            'next-column', self.tr('Next column'),
            tip=self.tr('Select the next column'),
            keys=[Qt.SHIFT + Qt.Key_Right],
            callback=self.textview_status.nextCol,
            )
        self.add_action(
            'prev-column', self.tr('Previous column'),
            tip=self.tr('Select the previous column'),
            keys=[Qt.SHIFT + Qt.Key_Left],
            callback=self.textview_status.prevCol,
            )

        # Activate file (file diff navigator)
        def enterkeypressed():
            w = QtGui.QApplication.focusWidget()
            if not isinstance(w, QtGui.QLineEdit):
                self.tableView_filelist.fileActivated(self.tableView_filelist.currentIndex(),)
            else:
                w.editingFinished.emit()

        self.add_action(
            'activate-file', self.tr('Activate file'),
            tip=self.tr('Activate the file'),
            keys=[Qt.Key_Return, Qt.Key_Enter],
            callback=enterkeypressed,
            )

        def altenterkeypressed():
            self.tableView_filelist.fileActivated(self.tableView_filelist.currentIndex(),
                                                  alternate=True)

        self.add_action(
            'activate-alt-file', self.tr('Activate alt. file'),
            tip=self.tr('Activate alternative file'),
            keys=[Qt.ALT+Qt.Key_Return, Qt.ALT+Qt.Key_Enter],
            callback=altenterkeypressed,
            )

    def toggleMainContent(self, visible=None):
        if visible is None:
            visible = self.get_action('content').isChecked()
        visible = bool(visible)
        if visible == self.frame_maincontent.isVisible():
            return
        self.set_action('content', checked=visible)
        self.frame_maincontent.setVisible(visible)
        if visible:
            self.revision_selected(-1)

    def setMode(self, mode):
        self.textview_status.setMode(mode)

    def load_config(self, repo):
        super(HgRepoViewer, self).load_config(repo)
        self.hidefinddelay = self.cfg.getHideFindDelay()

    def create_models(self, fromhead=None):
        self.repomodel = HgRepoListModel(self.repo, fromhead=fromhead)
        self.repomodel.filled.connect(self.on_filled)
        self.repomodel.message_logged.connect(
                self.statusBar().showMessage,
                Qt.QueuedConnection)

        self.filelistmodel = HgFileListModel(self.repo, parent=self)

    def setupModels(self, fromhead=None):
        self.create_models(fromhead)
        self.tableView_revisions.setModel(self.repomodel)
        self.tableView_filelist.setModel(self.filelistmodel)
        self.textview_status.setModel(self.repomodel)
        self.find_toolbar.setModel(self.repomodel)


    def displaySelectedFile(self, filename=None, rev=None):
        if filename == '':
            self.textview_status.hide()
            self.textview_header.show()
        else:
            self.textview_header.hide()
            self.textview_status.show()
            self.textview_status.displayFile(filename, rev)

    def setupRevisionTable(self):
        view = self.tableView_revisions
        view.installEventFilter(self)
        view.clicked.connect(self.toggleMainContent)
        view.revision_selected.connect(self.revision_selected)
        view.revision_selected[int].connect(self.revision_selected)
        view.revision_activated.connect(self.revision_activated)
        view.revision_activated[int].connect(self.revision_activated)
        view.start_from_rev.connect(self.start_from_rev)
        view.start_from_rev[int, bool].connect(self.start_from_rev)
        view.start_from_rev[str, bool].connect(self.start_from_rev)
        self.textview_header.revision_selected.connect(view.goto)
        self.textview_header.revision_selected[int].connect(view.goto)
        self.textview_header.parent_revision_selected.connect(
                self.textview_status.displayDiff)
        self.textview_header.parent_revision_selected[int].connect(
                self.textview_status.displayDiff)
        self.attachQuickBar(view.goto_toolbar)
        gotoaction = self.add_action(
            'goto', view.goto_toolbar.toggleViewAction(),
            icon='goto',
            keys=['Ctrl+g'],
            tip=self.tr("Search for revision in the graph"),
            )
        self.toolBar_edit.addAction(gotoaction)

    def start_from_rev(self, rev=None, follow=False):
        rev = rev or None # '' => None
        self.startrev_entry.setText(str(rev or ''))
        self.startrev_follow_action.setChecked(follow)
        self.refreshRevisionTable(rev=rev, follow=follow)

    def _setup_table(self, table):
        table.setTabKeyNavigation(False)
        table.verticalHeader().setDefaultSectionSize(self.rowheight)
        table.setShowGrid(False)
        table.verticalHeader().hide()
        table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)

    def setupHeaderTextview(self):
        self.header_diff_format = QtGui.QTextCharFormat()
        self.header_diff_format.setFont(self._font)
        self.header_diff_format.setFontWeight(bold)
        self.header_diff_format.setForeground(Qt.black)
        self.header_diff_format.setBackground(Qt.gray)

    def on_filled(self):
        # called the first time the model is filled, so we select
        # the first available revision
        tv = self.tableView_revisions
        if self._reload_rev is not None:
            torev = self._reload_rev
            self._reload_rev = None
            try:
                tv.goto(torev)
                self.tableView_filelist.selectFile(self._reload_file)
                self._reload_file = None
                return
            except IndexError:
                pass
        wc = self.repo[None]
        idx = tv.model().index(0, 0) # Working directory or tip
        if not wc.dirty() and wc.p1().rev() >= 0:
            # parent of working directory is not nullrev
            _idx = tv.model().indexFromRev(wc.p1().rev())
            # may appears if wc has been filtered out
            # (for example not on the filtered branch)
            if _idx is not None:
                idx = _idx
        tv.setCurrentIndex(idx)

    def revision_activated(self, rev=None):
        """
        Callback called when a revision is double-clicked in the revisions table
        """
        if rev is None:
            rev = self.tableView_revisions.current_rev
        self.toggleMainContent(True)
        self._manifestdlg = ManifestViewer(self.repo, rev)
        self._manifestdlg.show()

    def revision_selected(self, rev=None):
        """
        Callback called when a revision is selected in the revisions table
        if rev == -1: refresh the current selected revision
        """
        if not self.frame_maincontent.isVisible() or not self.repomodel.graph:
            return
        if rev == -1:
            view = self.tableView_revisions
            indexes = view.selectedIndexes()
            if not indexes:
                return
            rev = view.revFromindex(indexes[0])
        ctx = self.repomodel.repo[rev]
        filename = self.tableView_filelist.currentFile() # save before refresh
        self.textview_status.setContext(ctx)
        if self.repomodel.show_hidden:
            self.textview_header.excluded = ()
        else:
            self.textview_header.excluded = hiddenrevs(self.repo)
        self.textview_header.displayRevision(ctx)
        self.filelistmodel.setSelectedRev(ctx)
        if len(self.filelistmodel):
            if filename not in self.filelistmodel:
                filename = self.filelistmodel.file(0)
            self.tableView_filelist.selectFile(filename)
            self.tableView_filelist.file_selected[str].emit(
                filename)

    def goto(self, rev):
        if len(self.tableView_revisions.model().graph):
            self.tableView_revisions.goto(rev)
        else:
            # store rev to show once it's available (when graph
            # filling is still running)
            self._reload_rev = rev

    def _getrepomtime(self):
        """Return the last modification time for the repo"""
        watchedfiles = [(self.repo.root, ".hg", "store"),
                        (self.repo.root, ".hg", "store", "00changelog.i"),
                        (self.repo.root, ".hg", "dirstate"),
                        (self.repo.root, ".hg", "store", "phasesroots"),]
        watchedfiles = [os.path.join(*wf) for wf in watchedfiles]
        for l in (self.repo.sjoin('lock'), self.repo.vfs.join('wlock')):
            try:
                if util.readlock(l):
                    break
            except EnvironmentError, err:
                # depending on platform (win, nix) the "posix file" abstraction
                # defined and used by mercurial may raise one of both subclasses
                # of EnvironmentError
                if err.errno != errno.ENOENT:
                    raise
        else: # repo not locked by an Hg operation
            mtime = [os.path.getmtime(wf) for wf in watchedfiles \
                     if os.path.exists(wf)]
            if mtime:
                return max(mtime)
            # humm, directory has probably been deleted, exiting...
            self.close()

    def ask_repository(self):
        repopath = QtGui.QFileDialog.getExistingDirectory(
            self,
            'Select a mercurial repository',
            self.repo.root or os.path.expanduser('~'))
        repopath = find_repository(repopath)
        if not (repopath or self.repo.root):
            if not self.repo.root:
                raise RepoError("There is no Mercurial repository here (.hg not found)!")
            else:
                return None
        return repopath

    def open_repository(self, repopath=None):
        if not repopath:
            repopath = self.ask_repository()
        if repopath is None:
            return
        self.repo = build_repo(ui.ui(), repopath)
        self.setWindowTitle('hgview: %s' % os.path.abspath(self.repo.root))
        self._finish_load()

    def reload(self):
        """Reload the repository"""
        self._reload_rev = self.tableView_revisions.current_rev
        self._reload_file = self.tableView_filelist.currentFile()
        self.repo = build_repo(self.repo.ui, self.repo.root)
        self._finish_load()

    def _finish_load(self):
        self._repodate = self._getrepomtime()
        self.setupBranchCombo()
        self.setupModels()
        self._setupQuickOpen()

    #@timeit
    def refreshRevisionTable(self, *args, **kw):
        """Starts the process of filling the HgModel"""
        branch = self.branch_comboBox.currentText()
        startrev = kw.get('rev', None)
        # XXX workaround: self.sender() may provoke a core dump if
        # this method is called directly (not via a connected signal);
        # the 'sender' keyword is a way to detect that the method
        # has been called directly (thus caller MUST set this kw arg)
        sender = kw.get('sender') or self.sender()
        follow = kw.get('follow', False)
        closed = self.branch_checkBox_action.isChecked()
        startrev = self.repo[startrev].rev()
        self.repomodel.show_hidden = self.get_action('showhide').isChecked()
        self.repomodel.setRepo(self.repo, branch=branch, fromhead=startrev,
                               follow=follow, closed=closed)

    def on_about(self, *args):
        """ Display about dialog """
        from hgviewlib.__pkginfo__ import modname, version, description
        try:
            from mercurial.version import get_version
            hgversion = get_version()
        except:
            from mercurial.__version__ import version as hgversion

        msg = "<h2>About %(appname)s %(version)s</h2> (using hg %(hgversion)s)" % \
              {"appname": modname, "version": version, "hgversion": hgversion}
        msg += "<p><i>%s</i></p>" % description.capitalize()
        QtGui.QMessageBox.about(self, "About %s" % modname, msg)

    def on_help(self, *args):
        w = HgviewHelpViewer(self.repo, self)
        w.show()
        w.raise_()
        w.activateWindow()

