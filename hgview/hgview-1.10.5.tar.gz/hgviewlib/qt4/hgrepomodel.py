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
Qt4 model for hg repo changelogs and filelogs
"""
import sys
import re
import os, os.path as osp
from functools import partial

from mercurial.node import nullrev
from mercurial.node import hex, short as short_hex
from mercurial.error import LookupError
from mercurial import util, error

from hgviewlib.hggraph import Graph, ismerge, diff as revdiff, HgRepoListWalker
from hgviewlib.hggraph import revision_grapher, filelog_grapher, getlog, gettags
from hgviewlib.config import HgConfig
from hgviewlib.util import tounicode, isbfile, xml_escape, allbranches
from hgviewlib.qt4 import icon as geticon
from hgviewlib.decorators import timeit
from hgviewlib.hgpatches import phases

from PyQt4.QtGui import QColor, QPixmap, QPainter, QPen, QFont
from PyQt4.QtCore import Qt, pyqtSignal, QAbstractItemModel, QAbstractTableModel, \
     QObject, QDateTime, QTimer, QModelIndex, QPointF

# XXX make this better than a poor hard written list...
COLORS = [ "blue", "darkgreen", "red", "green", "darkblue", "purple",
           "cyan", Qt.darkYellow, "magenta", "darkred", "darkmagenta",
           "darkcyan", "gray", ]
COLORS = [str(QColor(x).name()) for x in COLORS]
#COLORS = [str(color) for color in QColor.colorNames()]

# We use two colors, One for even rows and one for odd rows
COLOR_BG_OBSOLETE = [QColor(255, 250, 250), QColor(243, 230, 230)]
COLOR_BG_TROUBLED = [QColor(255, 193,  71), QColor(255, 153,  51)]
COLOR_BG_HIGHLIGHT = [QColor(127, 199, 175),
                      QColor(127, 199, 175).lighter()]

BOOKMARK_CSS = "color: white; background-color: blue;"
TAG_CSS = "color: black; background-color: SandyBrown;"

def cvrt_date(date):
    """
    Convert a date given the hg way, ie. couple (date, tz), into a
    formatted string
    """
    if not date:
        return u''
    date, tzdelay = date
    return QDateTime.fromTime_t(int(date)).toString(Qt.LocaleDate)


# XXX maybe it's time to make these methods of the model...
# in following lambdas, ctx is a hg changectx
_columnmap = {'ID': lambda model, ctx, gnode: ctx.rev() is not None and tounicode(ctx.rev()) or u"",
              'Log': getlog,
              'Author': lambda model, ctx, gnode: tounicode(ctx.user()),
              'Date': lambda model, ctx, gnode: cvrt_date(ctx.date()),
              'Branch': lambda model, ctx, gnode: tounicode(ctx.branch()),
              'Filename': lambda model, ctx, gnode: tounicode(gnode.extra[0]),
              'Phase': lambda model, ctx, gnode: tounicode(ctx.phasestr()),
              }

_tooltips = {'ID': lambda model, ctx, gnode: ctx.rev() is not None and tounicode(ctx.hex()) or u"Working Directory",
             }

def auth_width(model, repo):
    auths = model._aliases.values()
    if not auths:
        return None
    return sorted(auths, cmp=lambda x,y: cmp(len(x), len(y)))[-1]

# in following lambdas, r is a hg repo
# it return the longuest entry of this column
_maxwidth = {'ID': lambda self, r: str(len(r.changelog)),
             'Date': lambda self, r: cvrt_date(r[0].date()),
             'Branch': lambda self, r: ([None] + sorted(allbranches(r), key=len))[-1],
             'Author': lambda self, r: 'author name',
             'Filename': lambda self, r: self.filename,
             'Phase': lambda self, r: sorted(phases.phasenames, key=len)[-1]
             }

def datacached(meth):
    """
    decorator used to cache 'data' method of Qt models. It will *not*
    cache None return values (so costly non-null values
    can be computed and filled as a background process)
    """
    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if (row, col, role) in self._datacache:
            return self._datacache[(row, col, role)]
        result = meth(self, index, role)
        if result is not None:
            self._datacache[(row, col, role)] = result
        return result
    return data



class HgRepoListModel(QAbstractTableModel, HgRepoListWalker):
    """
    Model used for displaying the revisions of a Hg *local* repository
    """

    message_logged = pyqtSignal(str, int)
    filled = pyqtSignal()

    _allcolumns = ('ID', 'Branch', 'Log', 'Author', 'Date')
    _columns = ('ID', 'Branch', 'Log', 'Author', 'Date')
    _stretchs = {'Log': 1, }
    _getcolumns = "getChangelogColumns"

    def __init__(self, repo, branch='', fromhead=None, follow=False, parent=None, show_hidden=False, closed=False):
        """
        repo is a hg repo instance
        """
        self._fill_timer = None
        QAbstractTableModel.__init__(self, parent)
        HgRepoListWalker.__init__(self, repo, branch, fromhead, follow, closed=closed)
        self.highlights = []

    def setRepo(self, repo, branch='', fromhead=None, follow=False, closed=False):
        HgRepoListWalker.setRepo(self, repo, branch, fromhead, follow, closed=closed)
        self.layoutChanged.emit()
        QTimer.singleShot(0, lambda: self.filled.emit())
        self._fill_timer = self.startTimer(50)

    def highlight_rows(self, rows):
        """mark ``rows`` to be highlighted."""
        self.highlights[:] = rows
        self._datacache.clear()

    def timerEvent(self, event):
        if event.timerId() == self._fill_timer:
            self.message_logged.emit(
                      'filling (%s)' % (len(self.graph)),
                      -1)
            if self.graph.isfilled():
                self.killTimer(self._fill_timer)
                self._fill_timer = None
                self.updateRowCount()
                self.message_logged.emit('', -1)
            # we fill the graph data structures without telling
            # views until we are done - this gives
            # maximal GUI responsiveness
            elif not self.graph.build_nodes(nnodes=self.fill_step):
                self.killTimer(self._fill_timer)
                self._fill_timer = None
                self.updateRowCount()
                self.message_logged.emit('', -1)

    def updateRowCount(self):
        currentlen = self.rowcount
        newlen = len(self.graph)
        if newlen > self.rowcount:
            self.beginInsertRows(QModelIndex(), currentlen, newlen-1)
            self.rowcount = newlen
            self.endInsertRows()

    @staticmethod
    def get_color(n, ignore=()):
        """
        Return a color at index 'n' rotating in the available
        colors. 'ignore' is a list of colors not to be chosen.
        """
        ignore = [str(QColor(x).name()) for x in ignore]
        colors = [x for x in COLORS if x not in ignore]
        if not colors: # ghh, no more available colors...
            colors = COLORS
        return colors[n % len(colors)]

    def user_color(self, user):
        if user in self._aliases:
            user = self._aliases[user]
        if user in self._users:
            try:
                color = self._users[user]['color']
                color = QColor(color).name()
                self._user_colors[user] = color
            except:
                pass
        return HgRepoListWalker.user_color(self, user)

    def _display_log(self, ctx, gnode, row):
        """Display the log column content."""
        content = []
        # display bookmarks
        bookmarks = [tounicode(bookmark) for bookmark in ctx.bookmarks()]
        if bookmarks:
            content.extend(u'<span style="white-space: pre; %s"> %s </span>'
                           % (BOOKMARK_CSS, xml_escape(bkm)) for bkm in bookmarks)
        # display tags
        tags = [tounicode(tag) for tag in gettags(self, ctx).split(',') if tag]
        if tags:
            content.extend(u'<span style="white-space: pre; %s"> %s </span>'
                           % (TAG_CSS, xml_escape(tag)) for tag in tags)
        # display log
        style =  "color: grey;" if ctx.obsolete() else u""
        content.append(u'<span style="white-space: pre; %s"> %s </span>'
                       % (style, xml_escape(_columnmap['Log'](self, ctx, gnode))))
        return u' '.join(content)

    @datacached
    def data(self, index, role):
        if not index.isValid():
            return None
        row = index.row()
        self.ensureBuilt(row=row)
        column = self._columns[index.column()]
        gnode = self.graph[row]
        ctx = self.repo[gnode.rev]
        if role == Qt.DisplayRole:
            if column == 'Author': #author
                user = _columnmap[column](self, ctx, gnode) if ctx.node() else u'' 
                return self.user_name(user)
            elif column == 'Log':
                return self._display_log(ctx, gnode, row)
            return _columnmap[column](self, ctx, gnode)
        elif role == Qt.ToolTipRole:
            msg = u"<b>Branch:</b> %s<br>\n" % _columnmap['Branch'](self, ctx, gnode)
            msg += u"<b>Phase:</b> %s<br>\n" % _columnmap['Phase'](self, ctx, gnode)
            if gnode.rev in self.wd_revs:
                msg += u" <i>Working Directory position"
                states = u'modified added removed deleted'.split()
                status = self.wd_status[self.wd_revs.index(gnode.rev)]
                status = [state for st, state in zip(status, states) if st]
                if status:
                    msg += ' (%s)' % (', '.join(status))
                msg += u"</i><br>\n"
            msg += _tooltips.get(column, _columnmap[column])(self, ctx, gnode)
            return msg
        elif role == Qt.ForegroundRole:
            color = None
            if column == 'Author': #author
                user = tounicode(ctx.user()) if ctx.node() else u''
                color = QColor(self.user_color(user))
                if ctx.obsolete():
                    color = color.lighter()
            elif column == 'Branch': #branch
                color = QColor(self.namedbranch_color(ctx.branch()))
                if ctx.obsolete():
                    color = color.lighter()
            elif ctx.obsolete():
                color = QColor('grey')
            if color is not None:
                return color

        elif role == Qt.BackgroundRole:
            row = index.row()
            if row in self.highlights:
                return COLOR_BG_HIGHLIGHT[row % 2]
            elif ctx.obsolete():
                return COLOR_BG_OBSOLETE[row % 2]
            elif ctx.instabilities():
                return COLOR_BG_TROUBLED[row % 2]

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columns[section]
        return None

    def maxWidthValueForColumn(self, column):
        column = self._columns[column]
        if column in _maxwidth:
            return _maxwidth[column](self, self.repo)
        return None

    def clear(self):
        """empty the list"""
        self.graph = None
        self._datacache = {}
        self.notify_data_changed()

    def notify_data_changed(self):
        self.layoutChanged.emit()

    def indexFromRev(self, rev):
        self.ensureBuilt(rev=rev)
        row = self.rowFromRev(rev)
        if row is not None:
            return self.index(row, 0)

class FileRevModel(HgRepoListModel):
    """
    Model used to manage the list of revisions of a file, in file
    viewer of in diff-file viewer dialogs.
    """
    _allcolumns = ('ID', 'Branch', 'Log', 'Author', 'Date', 'Filename')
    _columns = ('ID', 'Branch', 'Log', 'Author', 'Date', 'Filename')
    _stretchs = {'Log': 1, }
    _getcolumns = "getFilelogColumns"

    def __init__(self, repo, filename=None, parent=None):
        """
        data is a HgHLRepo instance
        """
        HgRepoListModel.__init__(self, repo, parent=parent)
        self.setFilename(filename)

    def setRepo(self, repo, branch='', fromhead=None, follow=False, closed=False):
        self.repo = repo
        self._datacache = {}
        self.load_config()

    def setFilename(self, filename):
        self.filename = filename

        self._user_colors = {}
        self._branch_colors = {}

        self.rowcount = 0
        self._datacache = {}

        if self.filename:
            grapher = filelog_grapher(self.repo, self.filename)
            self.graph = Graph(self.repo, grapher, self.max_file_size)
            fl = self.repo.file(self.filename)
            # we use fl.index here (instead of linkrev) cause
            # linkrev API changed between 1.0 and 1.?. So this
            # works with both versions.
            self.heads = [fl.index[fl.rev(x)][4] for x in fl.heads()]
            self.ensureBuilt(row=self.fill_step/2)
            QTimer.singleShot(0, lambda: self.filled.emit())
            self._fill_timer = self.startTimer(500)
        else:
            self.graph = None
            self.heads = []


replus = re.compile(r'^[+][^+].*', re.M)
reminus = re.compile(r'^[-][^-].*', re.M)

class HgFileListModel(QAbstractTableModel):
    """
    Model used for listing (modified) files of a given Hg revision
    """

    _description_desc = dict(path='', flag='', desc='Display revision description',
                             bfile=None, parent=None, fromside=None, infiles=False)

    def __init__(self, repo, parent=None):
        """
        data is a HgHLRepo instance
        """
        QAbstractTableModel.__init__(self, parent)
        self.repo = repo
        self._datacache = {}
        self.load_config()
        self.current_ctx = None
        self._files = []
        self._filesdict = {}
        self.diffwidth = 100
        self._fulllist = False
        self._fill_iter = None

    def toggleFullFileList(self):
        self._fulllist = not self._fulllist
        self.loadFiles()
        self.layoutChanged.emit()

    def load_config(self):
        cfg = HgConfig(self.repo.ui)
        self._flagcolor = {}
        self._flagcolor['='] = cfg.getFileModifiedColor()
        self._flagcolor['-'] = cfg.getFileRemovedColor()
        self._flagcolor['-'] = cfg.getFileDeletedColor()
        self._flagcolor['+'] = cfg.getFileAddedColor()
        self._flagcolor[''] = cfg.getFileDescriptionColor()
        self._displaydiff = cfg.getDisplayDiffStats()
        self._descriptionview = cfg.getFileDescriptionView()

    def setDiffWidth(self, w):
        if w != self.diffwidth:
            self.diffwidth = w
            self._datacache = {}
            self.dataChanged.emit(
                      self.index(1, 0),
                      self.index(1, self.rowCount()))

    def __len__(self):
        return len(self._files)

    def __contains__(self, filename):
        return filename in self._filesdict

    def rowCount(self, parent=None):
        return len(self)

    def columnCount(self, parent=None):
        return 1 + self._displaydiff

    def file(self, row):
        return self._files[row]['path']

    def fileflag(self, fn):
        if not fn:
            return '+'
        return self._filesdict[fn]['flag']

    def fileparentctx(self, fn, ctx=None):
        if ctx is None:
            return self._filesdict[fn]['parent']
        return ctx.parents()[0]

    def fileFromIndex(self, index):
        if not index.isValid() or index.row()>=len(self) or not self.current_ctx:
            return None
        row = index.row()
        file_info = self._files[row]
        return self._files[row]['path']

    def revFromIndex(self, index):
        if self._fulllist and ismerge(self.current_ctx):
            if not index.isValid() or index.row()>=len(self) or not self.current_ctx:
                return None
            row = index.row()
            if self._files[row]['fromside'] == 'right':
                return self.current_ctx.parents()[1].rev()
            return self.current_ctx.parents()[0].rev()
        return None

    def indexFromFile(self, filename):
        if filename in self._filesdict:
            row = self._files.index(self._filesdict[filename])
            return self.index(row, 0)
        return QModelIndex()

    def _filterFile(self, filename, ctxfiles):
        if self._fulllist:
            return True
        return filename in ctxfiles #self.current_ctx.files()

    def _buildDesc(self, parent, fromside):
        _files = []
        ctx = self.current_ctx
        ctxfiles = ctx.files()
        changes = self.repo.status(parent.node(), ctx.node())[:3]
        modified, added, removed = changes
        for lst, flag in ((added, '+'), (modified, '='), (removed, '-')):
            for f in [x for x in lst if self._filterFile(x, ctxfiles)]:
                desc = f
                bfile = isbfile(f)
                if bfile:
                    desc = desc.replace('.hgbfiles'+os.sep, '')
                desc = tounicode(desc)
                _files.append({'path': f, 'flag': flag, 'desc': desc, 'bfile': bfile,
                               'parent': parent, 'fromside': fromside,
                               'infiles': f in ctxfiles})
                # renamed/copied files are handled by background
                # filling process since it can be a bit long
        return _files

    def loadFiles(self):
        self._fill_iter = None
        self._files = []
        self._datacache = {}
        self._files = self._buildDesc(self.current_ctx.parents()[0], 'left')
        if ismerge(self.current_ctx):
            _paths = [x['path'] for x in self._files]
            _files = self._buildDesc(self.current_ctx.parents()[1], 'right')
            self._files += [x for x in _files if x['path'] not in _paths]
        self._filesdict = dict([(f['path'], f) for f in self._files])
        if self._descriptionview == 'asfile':
            self._files.insert(0, self._description_desc)
        self.fillFileStats()

    def setSelectedRev(self, ctx):
        if ctx != self.current_ctx:
            self.current_ctx = ctx
            self._datacache = {}
            self.loadFiles()
            self.layoutChanged.emit()

    def fillFileStats(self):
        """
        Method called to start the background process of computing
        file stats, which are to be displayed in the 'Stats' column
        """
        self._fill_iter = self._fill()
        self._fill_one_step()

    def _fill_one_step(self):
        if self._fill_iter is None:
            return
        try:
            nextfill = self._fill_iter.next()
            if nextfill is not None:
                row, col = nextfill
                idx = self.index(row, col)
                self.dataChanged.emit(idx, idx)
            QTimer.singleShot(10, lambda: self._fill_one_step())

        except StopIteration:
            self._fill_iter = None

    def _fill(self):
        # the generator used to fill file stats as a background process
        files = enumerate(self._files)
        if self._descriptionview == 'asfile':
            files.next() # consume description entry
        for row, desc in files:
            filename = desc['path']
            if desc['flag'] == '=' and self._displaydiff:
                try:
                    diff = revdiff(self.repo, self.current_ctx, None, files=[filename])
                    tot = tounicode(self.current_ctx.filectx(filename).data()).count('\n')
                    add = len(replus.findall(diff))
                    rem = len(reminus.findall(diff))
                except (LookupError, TypeError): # unknown revision and mq support
                    tot, add, rem = 0, 0, 0

                if tot == 0:
                    tot = max(add + rem, 1)
                desc['stats'] = (tot, add, rem)
                yield row, 1

            if desc['flag'] == '+':
                m = self.current_ctx.filectx(filename).renamed()
                if m:
                    removed = self.repo.status(desc['parent'].node(),
                                               self.current_ctx.node())[2]
                    oldname, node = m
                    if oldname in removed:
                        # removed.remove(oldname) XXX
                        desc['renamedfrom'] = (tounicode(oldname), node)
                        desc['flag'] = '='
                        desc['desc'] += u'\n (was %s)' % tounicode(oldname)
                    else:
                        desc['copiedfrom'] = (tounicode(oldname), node)
                        desc['flag'] = '='
                        desc['desc'] += u'\n (copy of %s)' % tounicode(oldname)
                    yield row, 0
            yield None

    def data(self, index, role):
        if not index.isValid() or index.row()>len(self) or not self.current_ctx:
            return None
        row = index.row()
        column = index.column()
        current_file_desc = self._files[row]
        current_file = current_file_desc['path']
        stats = current_file_desc.get('stats')
        if column == 1:
            if stats is not None:
                if role == Qt.DecorationRole:
                    tot, add, rem = stats
                    w = self.diffwidth - 20
                    h = 20

                    np = int(w*add/tot)
                    nm = int(w*rem/tot)
                    nd = w-np-nm

                    pix = QPixmap(w+10, h)
                    pix.fill(QColor(0,0,0,0))
                    painter = QPainter(pix)

                    for x0,w0, color in ((0, nm, 'red'),
                                         (nm, np, 'green'),
                                         (nm+np, nd, 'gray')):
                        color = QColor(color)
                        painter.setBrush(color)
                        painter.setPen(color)
                        painter.drawRect(x0+5, 0, w0, h-3)
                    painter.setBrush(QColor(0,0,0,0))
                    pen = QPen(Qt.black)
                    pen.setWidth(0)
                    painter.setPen(pen)
                    painter.drawRect(5, 0, w+1, h-3)
                    painter.end()
                    return pix
                elif role == Qt.ToolTipRole:
                    tot, add, rem = stats
                    msg = "Diff stats:<br>"
                    msg += "&nbsp;<b>File:&nbsp;</b>%s lines<br>" % tot
                    msg += "&nbsp;<b>added lines:&nbsp;</b> %s<br>" % add
                    msg += "&nbsp;<b>removed lines:&nbsp;</b> %s" % rem
                    return msg

        elif column == 0:
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                return tounicode(current_file_desc['desc'])
            elif role == Qt.DecorationRole:
                if self._fulllist and ismerge(self.current_ctx):
                    icn = None
                    if current_file_desc['infiles']:
                        icn = geticon('leftright')
                    elif current_file_desc['fromside'] == 'left':
                        icn = geticon('left')
                    elif current_file_desc['fromside'] == 'right':
                        icn = geticon('right')
                    if icn:
                        return icn.pixmap(20,20)
            elif role == Qt.FontRole:
                if self._fulllist and current_file_desc['infiles']:
                    font = QFont()
                    font.setBold(True)
                    return font
            elif role == Qt.ForegroundRole:
                color = self._flagcolor.get(current_file_desc['flag'], 'black')
                if color is not None:
                    return QColor(color)
        return None

    def headerData(self, section, orientation, role):
        if ismerge(self.current_ctx):
            if self._fulllist:
                header = ('File (all)', 'Diff')
            else:
                header = ('File (merged only)', 'Diff')
        else:
            header = ('File', 'Diff')

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return header[section]
        return None


class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)
        return item
    addChild = appendChild

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def __getitem__(self, idx):
        return self.childItems[idx]

    def __len__(self):
        return len(self.childItems)

    def __iter__(self):
        for ch in self.childItems:
            yield ch


class ManifestModel(QAbstractItemModel):
    """
    Qt model to display a hg manifest, ie. the tree of files at a
    given revision. To be used with a QTreeView.
    """
    def __init__(self, repo, rev, parent=None):
        QAbstractItemModel.__init__(self, parent)

        self.repo = repo
        self.changectx = self.repo[rev]
        self.setupModelData()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return tounicode(item.data(index.column()))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem is not None:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def setupModelData(self):
        if self.changectx.rev() is not None:
            rootData = ["rev %s:%s" % (self.changectx.rev(),
                                       short_hex(self.changectx.node()))]
        else:
            rootData = ['Working Directory']
        self.rootItem = TreeItem(rootData)

        for path in sorted(self.changectx.manifest()):
            path = path.split(osp.sep)
            node = self.rootItem

            for p in path:
                for ch in node:
                    if ch.data(0) == p:
                        node = ch
                        break
                else:
                    node = node.addChild(TreeItem([p], node))

    def pathFromIndex(self, index):
        idxs = []
        while index.isValid():
            idxs.insert(0, index)
            index = self.parent(index)
        return osp.sep.join([index.internalPointer().data(0) for index in idxs])

