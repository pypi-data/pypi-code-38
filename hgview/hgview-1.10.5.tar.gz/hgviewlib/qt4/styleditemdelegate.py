# Copyright (c) 2009-2013 LOGILAB S.A. (Paris, FRANCE).
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
Contains the StyledItemDelegate used as item deleate by qt to render log table cell.
"""

from functools import wraps

from PyQt4.QtCore import QSize, Qt, QPointF
from PyQt4.QtGui import QStyledItemDelegate, QStyleOptionViewItemV4, \
     QStyle, QPixmap, QColor, QPen, QPainter, QTextDocument, \
     QAbstractTextDocumentLayout, QPalette

from hgviewlib.hgpatches import phases
from hgviewlib.qt4 import icon as geticon


def secured(func):
    """A Decorator that call ``func(self, painter, *ags, **kws)`` in a secured way,
    e.g.  the painter is returned to the state it was supplied in when
    ``func`` was called.
    """
    @wraps(func)
    def _func(self, painter, *ags, **kws):
        painter.save()
        try:
            out = func(self, painter, *ags, **kws)
        finally:
            painter.restore()
        return out
    return _func


class StyledItemDelegate(QStyledItemDelegate):
    """Render styled column content."""
    def __init__(self, parent=0):
        super(StyledItemDelegate, self).__init__(parent)
        self._model = None

    def paint(self, painter, option, index):
        """Render the Delegate using the given ``painter`` and style ``option``
        for the item specified by ``index``.
        """
        self._model = index.model()
        # draw selection
        option = QStyleOptionViewItemV4(option)
        self.parent().style().drawControl(QStyle.CE_ItemViewItem, option, painter)
        self._draw_content(painter, option, index)

    def _draw_content(self, painter, option, index):
        self._draw_background(painter, option, index)
        self._draw_text(painter, option, index)

    @secured
    def _draw_background(self, painter, option, index):
        """Draw the background if specified by the model excepts when the row is selected
        in which case the selection color has precedence.
        """
        background = self._model.data(index, Qt.BackgroundRole)
        # we draw specified background except when row is selected as selection color
        # always have precedence
        if background is not None and not option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, background)

    @secured
    def _draw_text(self, painter, option, index):
        """Draw the content text in the cell.
        We currently use the default styled item delegate to render the cell content.
        """
        doc = QTextDocument()
        text = self._model.data(index, Qt.DisplayRole)
        doc.setHtml(text)
        painter.setClipRect(option.rect)
        painter.translate(QPointF(
            option.rect.left(),
            option.rect.top() + (option.rect.height() - doc.size().height()) / 2))
        layout = QAbstractTextDocumentLayout.PaintContext()
        layout.palette = option.palette
        if option.state & QStyle.State_Selected:
            if option.state & QStyle.State_Active:
                layout.palette.setCurrentColorGroup(QPalette.Active)
            else:
                layout.palette.setCurrentColorGroup(QPalette.Inactive)
            layout.palette.setBrush(QPalette.Text, layout.palette.highlightedText())
        elif not option.state & QStyle.State_Enabled:
            layout.palette.setCurrentColorGroup(QPalette.Disabled)

        doc.documentLayout().draw(painter, layout)

class GraphItemDelegate(StyledItemDelegate):
    """Render revisions tree graph and styled column content."""

    def _graph_width(self, nb_branches):
        """Return graph width in pix for ``nb_branches``.
        """
        return (self._model.dot_radius + 2) * nb_branches + 2  # max pen width

    def _draw_content(self, painter, option, index):
        self._draw_background(painter, option, index)
        self._draw_graph(painter, option, index)
        self._draw_text(painter, option, index)

    @secured
    def _draw_graph(self, painter, option, index):
        """
        Draw the tree edges for the mercurial context ``ctx`` at the graph
        node ``gnode``.

        ..note:: ``ctx`` and ``gnode`` is quite redundant as
                 ``ctx=self.repo[gnode.rev]``. But this avoids
                 computing ``ctx`` twice.
        """
        painter.setClipRect(option.rect)
        painter.translate(QPointF(option.rect.left(), option.rect.top()))

        row = index.row()
        gnode = index.model().graph[row]
        ctx = index.model().repo[gnode.rev]

        w = self._graph_width(gnode.cols)
        h = option.rect.height()

        pix = QPixmap(w, h)
        pix.fill(QColor(0,0,0,0))
        self._draw_graph_ctx(painter, pix, ctx, gnode)
        option.rect.setLeft(option.rect.left() + w + 5)

    def _draw_graph_ctx(self, painter, pix, ctx, gnode):
        h = pix.height()
        radius = self._model.dot_radius
        dot_x = self._graph_width(gnode.x)
        dot_y = h / 2

        painter.setRenderHint(QPainter.Antialiasing)

        for y1, y2, lines in ((dot_y, dot_y + h, gnode.bottomlines),
                              (dot_y - h, dot_y, gnode.toplines)):
            for start, end, color, fill in lines:
                x1 = self._graph_width(start) + radius / 2
                x2 = self._graph_width(end) + radius / 2
                color = QColor(self._model.get_color(color))
                _draw_graph_line(painter, x1, x2, y1, y2, color, not fill)

        dot_color = QColor(self._model.namedbranch_color(ctx.branch()))
        self._draw_graph_node(painter, dot_x, dot_y, radius, dot_color, ctx)

    def _draw_graph_node(self, painter, x, y, r, color, ctx):
        y -= r / 2 # middle -> border

        tags = set(ctx.tags())
        phase = ctx.phase()

        if ctx.rev() is None:
            # WD is displayed only if there are local
            # modifications, so let's use the modified icon
            _draw_graph_node_modified(painter, x, y)
        elif tags.intersection(self._model.mqueues):
            _draw_graph_node_mqpatch(painter, x, y)
        elif phase == phases.draft:
            self._draw_graph_node_draft(painter, x, y, r, color, ctx)
        elif phase == phases.secret:
            self._draw_graph_node_secret(painter, x, y, r, color, ctx)
        else:
            self._draw_graph_node_public(painter, x, y, r, color, ctx)

    def _set_graph_node_style(self, painter, dot_color, ctx):
        rev = ctx.rev()
        dotcolor = QColor(dot_color)
        if ctx.obsolete():
            penradius = 1
            pencolor = QColor(dotcolor)
            pencolor.setAlpha(150)
        elif rev in self._model.heads:
            penradius = 2
            pencolor = dotcolor.darker()
        else:
            penradius = 1
            pencolor = Qt.black

        if rev in self._model.wd_revs:
            pen = QPen(Qt.red)
            pen.setWidth(2)
        else:
            pen = QPen(pencolor)
            pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(dotcolor)

    def _draw_graph_node_public(self, painter, x, y, r, color, ctx):
        if ctx.rev() in self._model.wd_revs:
            geticon('clean').paint(painter, x - 5, y - 5, 17, 17)
        else:
            self._set_graph_node_style(painter, color, ctx)
            painter.drawEllipse(x, y, r, r)

    def _draw_graph_node_draft(self, painter, x, y, r, color, ctx):
        self._set_graph_node_style(painter, color, ctx)
        painter.drawRect(x, y, r, r)

    def _draw_graph_node_secret(self, painter, x, y, r, color, ctx):
        self._set_graph_node_style(painter, color, ctx)
        painter.drawPolygon(
            QPointF(x + (r // 2), y),
            QPointF(x, y + r),
            QPointF(x + r, y + r)
        )

def _draw_graph_node_mqpatch(painter, x, y):
    geticon('mqpatch').paint(painter, x - 5, y - 5, 17, 17)

def _draw_graph_node_modified(painter, x, y):
    geticon('modified').paint(painter, x - 5, y - 5, 17, 17)

def _draw_graph_line(painter, x1, x2, y1, y2, color, isobsolete):
    lpen = QPen(color)
    if isobsolete:
        lpen.setStyle(Qt.DotLine)
        color.setAlpha(150)
    lpen.setWidth(2)
    painter.setPen(lpen)
    painter.drawLine(x1, y1, x2, y2)
