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
"""
Generic Qt4 usefull widgets.
"""
from itertools import imap

from PyQt4.QtGui import QTableView, QFontMetrics, QHeaderView, QLineEdit, \
     QPalette, QPainter, QSizePolicy, QFrame
from PyQt4.QtCore import QTimer, pyqtSignal, Qt
from PyQt4.Qsci import QsciScintilla as qsci

from hgviewlib.util import tounicode
from hgviewlib.qt4 import icon as geticon
from hgviewlib.qt4.styleditemdelegate import StyledItemDelegate
from hgviewlib.qt4.lexers import get_lexer

class StyledTableView(QTableView):
    """An Abstract QTableView with some Columns rendered with css. """

    def __init__(self, parent=None):
        super(StyledTableView, self).__init__(parent)
        self.standard_delegate = self.itemDelegate()
        self.styled_item_delegate = StyledItemDelegate(self)

    def setModel(self, model):
        super(StyledTableView, self).setModel(model)
        self._reset_delegate()
        model.layoutChanged.connect(self._reset_delegate)

    def _reset_delegate(self):
        # Model column layout has changed so we need to move
        # our column delegate to correct location
        model = self.model()
        if not model:
            return
        for index in xrange(model.columnCount()):
            if self.is_styled_column(index):
                self.setItemDelegateForColumn(index, self.styled_item_delegate)
            else:
                self.setItemDelegateForColumn(index, self.standard_delegate)

    def is_styled_column(self, index):
        """ Return True if the column at ``index`` is rendered with style. """
        raise NotImplementedError()


class SmartResizeTableView(QTableView):
    """A smart header resizable table."""
    def __init__(self, parent=None):
        super(SmartResizeTableView, self).__init__(parent)
        self._autoresize = True
        self.horizontalHeader().sectionResized[int, int, int].connect(
            self.disableAutoResize)

    def enableAutoResize(self, *args):
        self._autoresize =  True

    def disableAutoResize(self, *args):
        self._autoresize =  False
        QTimer.singleShot(100, lambda: self.enableAutoResize())

    def resizeEvent(self, event):
        # we catch this event to resize smartly tables' columns
        super(SmartResizeTableView, self).resizeEvent(event)
        if self._autoresize:
            self.resizeColumns()

    def resizeColumns(self, *args):
        # resize columns the smart way: the column holding Log
        # is resized according to the total widget size.
        model = self.model()
        if not model:
            return
        col1_width = self.viewport().width()
        fontm = QFontMetrics(self.font())
        tot_stretch = 0.0
        for index in range(model.columnCount()):
            stretch = self.get_column_stretch(index)
            if stretch is not None:
                tot_stretch += stretch
                continue
            width = model.maxWidthValueForColumn(index)
            if width is not None:
                width = fontm.width(tounicode(width) + u'W')
                self.setColumnWidth(index, width)
            else:
                width = self.sizeHintForColumn(index)
                self.setColumnWidth(index, width)
            col1_width -= self.columnWidth(index)
        col1_width = max(col1_width, 100)
        for index in range(model.columnCount()):
            stretch = self.get_column_stretch(index)
            if stretch is not None:
                width = stretch / tot_stretch
                self.setColumnWidth(index, col1_width * width)

    def setModel(self, model):
        super(SmartResizeTableView, self).setModel(model)
        col = col = list(model._columns).index('Log')
        self.horizontalHeader().setResizeMode(col, QHeaderView.Stretch | QHeaderView.Interactive)

    def get_column_stretch(self, index):
        raise NotImplementedError


class QueryLineEdit(QLineEdit):
    """Special LineEdit class with visual marks for the revset query status"""

    text_edited_no_blank = pyqtSignal(str)

    FORGROUNDS = {'normal':Qt.color1,
                  'valid':Qt.color1,
                  'failed':Qt.darkRed,
                  'query':Qt.darkGray}

    ICONS = {'valid':'valid', 'query':'loading'}

    def __init__(self, parent):
        self._parent = parent
        self._status = None # one of the keys of self.FORGROUNDS and self.ICONS
        super(QueryLineEdit, self).__init__(parent)
        self.setTextMargins(0,0,-16,0)
        self.textEdited.connect(self.on_text_edited)
        self.previous_text = ''

    def set_status(self, status=None):
        self._status = status
        color = self.FORGROUNDS.get(status, None)
        if color is not None:
            palette = self.palette()
            palette.setColor(QPalette.Text, color)
            self.setPalette(palette)

    def get_status(self):
        return self._status

    status = property(get_status, set_status, None, "query status")

    def paintEvent(self, event):
        super(QueryLineEdit, self).paintEvent(event)
        icn = geticon(self.ICONS.get(self._status))
        if icn is None:
            return
        painter = QPainter(self)
        icn.paint(painter, self.width() - 18, (self.height() - 18) / 2, 16, 16)

    def on_text_edited(self):
        current_text = self.text().strip()
        if  current_text == self.previous_text:
            return
        self.previous_text = current_text
        self.text_edited_no_blank.emit( current_text)


class Annotator(qsci):
    # we use a QScintilla for the annotator cause it makes
    # it much easier to keep the text area and the annotator sync
    # (same font rendering etc). However, it have the drawback of making much
    # more difficult to implement things like QTextBrowser.anchorClicked, which
    # would have been nice to directly go to the annotated revision...
    def __init__(self, textarea, parent=None):
        super(Annotator, self).__init__(parent)

        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setReadOnly(True)
        self.sizePolicy().setControlType(QSizePolicy.Slider)
        self.setMinimumWidth(20)
        self.setMaximumWidth(40) # XXX TODO make this computed
        self.setFont(textarea.font())
        self.setMarginWidth(0, '')
        self.setMarginWidth(1, '')

        self.SendScintilla(qsci.SCI_SETCURSOR, 2)
        self.SendScintilla(qsci.SCI_SETCARETSTYLE, 0)

        # used to set a background color for every annotating rev
        N = 32
        self.markers = []
        for i in range(N):
            marker = self.markerDefine(qsci.Background)
            color = 0x7FFF00 + (i-N/2)*256/N*256*256 - i*256/N*256 + i*256/N
            self.SendScintilla(qsci.SCI_MARKERSETBACK, marker, color)
            self.markers.append(marker)

        textarea.verticalScrollBar().valueChanged[int].connect(
                self.verticalScrollBar().setValue)

    def set_line_ticks(self, ticks):
        """Specify line ticks instead of line numbers.

        A background color is automatically added.
        A new background color is used when the tick changes.
        """
        self.setText('\n'.join(ticks))
        uniq_ticks = list(sorted(set(ticks)))
        for i, tick in enumerate(ticks):
            idx = uniq_ticks.index(tick)
            self.markerAdd(i, self.markers[idx % len(self.markers)])


class SourceViewer(qsci):

    def __init__(self, *args, **kwargs):
        super(SourceViewer, self).__init__(*args, **kwargs)
        self.setUtf8(True)
        self.setFrameStyle(0)
        self.setFrameShape(QFrame.NoFrame)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setReadOnly(True)

        self.SendScintilla(qsci.SCI_SETSELEOLFILLED, True)
        self.SendScintilla(qsci.SCI_SETCARETSTYLE, 0)

        # margin 1 is used for line numbers
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, '000')

        self.SendScintilla(qsci.SCI_INDICSETSTYLE, 8, qsci.INDIC_ROUNDBOX)
        self.SendScintilla(qsci.SCI_INDICSETUNDER, 8, True)
        self.SendScintilla(qsci.SCI_INDICSETFORE, 8, 0xBBFFFF)
        self.SendScintilla(qsci.SCI_INDICSETSTYLE, 9, qsci.INDIC_ROUNDBOX)
        self.SendScintilla(qsci.SCI_INDICSETUNDER, 9, True)
        self.SendScintilla(qsci.SCI_INDICSETFORE, 9, 0x58A8FF)

        # hide margin 0 (markers)
        self.SendScintilla(qsci.SCI_SETMARGINTYPEN, 0, 0)
        self.SendScintilla(qsci.SCI_SETMARGINWIDTHN, 0, 0)
        # setup margin 1 for line numbers only
        self.SendScintilla(qsci.SCI_SETMARGINTYPEN, 1, 1)
        self.SendScintilla(qsci.SCI_SETMARGINWIDTHN, 1, 20)
        self.SendScintilla(qsci.SCI_SETMARGINMASKN, 1, 0)

        # define markers for colorize zones of diff
        self.markerplus = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markerplus, 0xB0FFA0)
        self.markerminus = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markerminus, 0xA0A0FF)
        self.markertriangle = self.markerDefine(qsci.Background)
        self.SendScintilla(qsci.SCI_MARKERSETBACK, self.markertriangle, 0xFFA0A0)

    def clear_highlights(self):
        n = self.length()
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 8) # highlight
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, n)
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 9) # current found
                                                            # occurrence
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, n)

    def highlight_current_search_string(self, pos, text):
        line = self.SendScintilla(qsci.SCI_LINEFROMPOSITION, pos)
        self.ensureLineVisible(line)
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 9)
        self.SendScintilla(qsci.SCI_INDICATORCLEARRANGE, 0, pos)
        self.SendScintilla(qsci.SCI_INDICATORFILLRANGE, pos, len(text))

    def search_and_highlight_string(self, text):
        data = unicode(self.text())
        self.SendScintilla(qsci.SCI_SETINDICATORCURRENT, 8)
        pos = [data.find(text)]
        n = len(text)
        while pos[-1] > -1:
            self.SendScintilla(qsci.SCI_INDICATORFILLRANGE, pos[-1], n)
            pos.append(data.find(text, pos[-1]+1))
        return [x for x in pos if x > -1]

    def set_text(self, filename, data, flag=None, cfg=None):
        lexer = get_lexer(filename, data, flag, cfg)
        if lexer:
            # lexer.setFont(self.font())
            self.setLexer(lexer)
        nlines = data.count('\n')
        self.setMarginWidth(1, str(nlines)+'00')
        self.setText(data)
