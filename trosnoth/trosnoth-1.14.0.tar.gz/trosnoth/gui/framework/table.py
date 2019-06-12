import logging

import pygame

from trosnoth.gui.framework.framework import CompoundElement
from trosnoth.gui.framework.elements import TextElement, TextButton
from trosnoth.gui.framework.prompt import InputBox
from trosnoth.gui.fonts.font import Font
from trosnoth.gui import colours
from trosnoth.gui.common import Location, AttachedPoint, addPositions, Area
from trosnoth.utils.event import Event
from trosnoth.utils.utils import BasicContextManager

log = logging.getLogger(__name__)


# Styles work thusly:
# When looking for a particular attribute (say backColour),
# a cell will search first in its own style object, then in
# its row's style object, then it its column's style object,
# then in the table's. As soon as it finds a non-None value,
# it will use that.
class TableStyle(BasicContextManager):
    def __init__(self):
        self.backColour = None
        self.foreColour = None
        self.hoverColour = None
        self.hasShadow = None
        self.shadowColour = None
        self.font = None
        self.padding = None
        self.textAlign = None


class StyleUser(CompoundElement):
    def __init__(self, app, style):
        super(StyleUser, self).__init__(app)
        self.style = style


class CellAggregator(StyleUser):
    def __init__(self, app, table):
        super(CellAggregator, self).__init__(app, TableStyle())
        self._table = table
        self._cells = []
        self.index = -1
        self.elements = self._cells

    def setIndex(self, index):
        self.index = index

    def _newCell(self, cell, index=None):
        if index is None:
            index = len(self._cells)
        assert index <= len(self._cells)
        self._cells.insert(index, cell)

    def _anotherInsertedBefore(self):
        self.index += 1

    def _anotherDeletedBefore(self):
        self.index -= 1
        assert self.index >= 0

    def _delCell(self, index):
        del self._cells[index]

    def __len__(self):
        return len(self._cells)

    def __getitem__(self, i):
        return self._cells[i]

    def styleUpdate(self):
        '''
        Informs the row or column that the style of some part of the table has
        changed.  This is provided because it is too expensive for every cell
        to check its style every draw() call, so you must manually tell the
        table, row, column or cell that the style has been updated before the
        update is reflected.
        '''
        for cell in self._cells:
            cell.styleUpdate()


class Row(CellAggregator):
    def __init__(self, app, table, index, height):
        super(Row, self).__init__(app, table)
        assert hasattr(height, 'getVal')
        self.setHeight(height)
        self.setIndex(index)

    def setHeight(self, height):
        assert hasattr(height, 'getVal')
        self._height = height

    def _getHeight(self):
        return self._height.getVal(self.app)

    def _getPt(self):
        return self._table._getRowPt(self.index)


class Column(CellAggregator):
    def __init__(self, app, table, width=0):
        super(Column, self).__init__(app, table)
        self.setWidth(width)

    def onClicked(self, sender):
        self.setFocus(sender)
        self._table.onClicked(self)

    def lostFocus(self):
        self.setFocus(None)

    def setWidth(self, width):
        self._width = width

    def setDefaultWidth(self, width):
        if self._width == 0:
            self._width = width

    def _getWidth(self):
        if hasattr(self._width, 'getVal'):
            return self._width.getVal(self.app)
        else:
            return self._width

    def _getPt(self):
        return self._table._getColPt(self.index)


class TextColumn(Column):
    def createCell(self, row):
        return TextCell(self.app, row, self)


class TextBoxColumn(Column):
    def createCell(self, row):
        return TextBoxCell(self.app, row, self)


class TextButtonColumn(Column):
    def createCell(self, row):
        return TextButtonCell(self.app, row, self)


class Cell(StyleUser):
    def __init__(self, app, row, column):
        super(Cell, self).__init__(app, TableStyle())
        self._row = row
        self._column = column
        self._styleChanged = True
        self.rect = None
        self.usableRect = None

    def layoutChanged(self):
        self.rect = None
        self.usableRect = None

    @property
    def rowNum(self):
        return self._row.index

    @property
    def columnNum(self):
        return self._column.index

    def styleUpdate(self):
        '''
        Informs the cell that the style of some part of the table has changed.
        This is provided because it is too expensive for every cell to check
        its style every draw() call, so you must manually tell the table, row,
        column or cell that the style has been updated before the update is
        reflected.
        '''
        self._styleChanged = True

    def styleGet(self, field):
        toSearch = [self, self._row, self._column, self._row._table]
        for s in toSearch:
            val = getattr(s.style, field)
            if val is not None:
                return val

        return None

    def _getPt(self):
        rowPt = self._row._getPt()
        colPt = self._column._getPt()
        return (colPt[0], rowPt[1])

    def _getSize(self):
        rowHeight = self._row._getHeight()
        colWidth = self._column._getWidth()
        return (colWidth, rowHeight)

    def _getRect(self):
        if self.rect is None:
            self.rect = pygame.Rect(self._getPt(), self._getSize())
        return self.rect

    def _getUsableRect(self):
        if self.usableRect is not None:
            return self.usableRect
        pt = self._getPt()
        padding = self.styleGet('padding')
        usablePt = addPositions(pt, padding)
        size = self._getSize()
        usableSize = tuple([size[i] - padding[i] * 2 for i in (0, 1)])
        self.usableRect = pygame.Rect(usablePt, usableSize)
        return self.usableRect

    def _boxClicked(self, sender):
        self.setFocus(sender)
        self._column.onClicked(self)

    def draw(self, surface):
        if self._styleChanged:
            self._styleChanged = False
            self._update()
        bgColour = self.styleGet('backColour')
        if bgColour is not None:
            surface.fill(bgColour, self._getRect())

        clipRect = surface.get_clip()
        newClipRect = clipRect.clip(self._getUsableRect())
        surface.set_clip(newClipRect)
        try:
            super(Cell, self).draw(surface)
        finally:
            surface.set_clip(clipRect)


class TextCell(Cell):
    def __init__(self, app, row, column):
        super(TextCell, self).__init__(app, row, column)
        textAlign = self.styleGet('textAlign')
        self.textElement = TextElement(
            self.app, '', self.styleGet('font'),
            Location(CellAttachedPoint((0, 0), self, textAlign), textAlign),
            colour=self.styleGet('foreColour'))
        self.elements = [self.textElement]
        self._oldText = ''

    def setText(self, text):
        if text != self._oldText:
            self.textElement.setText(text)
            self._styleChanged = True
            self._oldText = text

    def _update(self):
        self.textElement.setFont(self.styleGet('font'))
        self.textElement.setColour(self.styleGet('foreColour'))
        textAlign = self.styleGet('textAlign')
        self.textElement.pos.anchor = textAlign
        self.textElement.pos.point.attachedAt = textAlign
        self.textElement.setShadow(self.styleGet('hasShadow'))
        self.textElement.setShadowColour(self.styleGet('shadowColour'))


class TextBoxCell(Cell):
    def __init__(self, app, row, column):
        super(TextBoxCell, self).__init__(app, row, column)
        textAlign = self.styleGet('textAlign')
        self.inputBox = InputBox(
            self.app,
            Area(
                CellAttachedPoint((0, 0), self, textAlign),
                self._getUsableRect().size, textAlign),
            font=self.styleGet('font'),
            colour=self.styleGet('foreColour'))
        self.inputBox.onEdit.addListener(self._valueChanged)
        self.elements = [self.inputBox]
        self._oldText = ''
        self._readOnly = True
        self.setReadOnly(False)
        self.onValueChanged = Event()

    def _valueChanged(self, sender):
        self._oldText = self.inputBox.getValue()
        self.onValueChanged.execute(self)

    def setReadOnly(self, readOnly):
        if readOnly == self._readOnly:
            return
        self._readOnly = readOnly

        if readOnly:
            self.inputBox.onClick.removeListener(self._boxClicked)
        else:
            self.inputBox.onClick.addListener(self._boxClicked)
            self.setFocus(None)

    def lostFocus(self):
        self.setFocus(None)

    def setText(self, text):
        if text != self._oldText:
            self.inputBox.setValue(text)
            self._styleChanged = True
            self._oldText = text

    def getText(self):
        return self._oldText

    def setMaxLength(self, length):
        self.inputBox.setMaxLength(length)

    def setValidator(self, validator):
        self.inputBox.setValidator(validator)

    def _update(self):
        self.inputBox.setFont(self.styleGet('font'))
        self.inputBox.setFontColour(self.styleGet('foreColour'))
        bgColour = self.styleGet('backColour')
        if bgColour is not None:
            self.inputBox.setBackColour(bgColour)
        textAlign = self.styleGet('textAlign')
        self.inputBox.area.anchor = textAlign
        self.inputBox.area.point.attachedAt = textAlign


class TextButtonCell(Cell):
    def __init__(self, app, row, column):
        super(TextButtonCell, self).__init__(app, row, column)
        textAlign = self.styleGet('textAlign')
        pos = Location(CellAttachedPoint((0, 0), self, textAlign), textAlign)
        self.textButton = TextButton(
            self.app, pos, '', self.styleGet('font'),
            self.styleGet('foreColour'), self.styleGet('hoverColour'))
        self.elements = [self.textButton]
        self._oldText = ''

    def setOnClick(self, onClick):
        self.textButton.onClick.addListener(onClick)
        self._boxClicked(None)

    def setText(self, text):
        if text != self._oldText:
            self.textButton.setText(text)
            self._styleChanged = True
            self._oldText = text

    def _update(self):
        self.textButton.setFont(self.styleGet('font'))
        self.textButton.setColour(self.styleGet('foreColour'))
        self.textButton.setHoverColour(self.styleGet('hoverColour'))
        self.textButton.setBackColour(self.styleGet('backColour'))
        textAlign = self.styleGet('textAlign')
        self.textButton.pos.anchor = textAlign
        self.textButton.pos.point.attachedAt = textAlign


class CellAttachedPoint(AttachedPoint):
    def __init__(self, val, cell, attachedAt='topleft'):
        super(CellAttachedPoint, self).__init__(
            val, cell._getUsableRect, attachedAt)


class Value(object):
    def __init__(self, value):
        self._value = value

    def getVal(self):
        return self._value


class Table(StyleUser):
    def __init__(self, app, pos, rows=None, columns=None, topPadding=0):
        defaultStyle = TableStyle()
        defaultStyle.backColour = (255, 255, 255)
        defaultStyle.padding = (5, 5)
        defaultStyle.foreColour = (0, 0, 0)
        defaultStyle.hoverColour = (0, 0, 0)
        defaultStyle.font = Font('FreeSans.ttf', 36)
        defaultStyle.textAlign = 'topleft'
        defaultStyle.hasShadow = False
        defaultStyle.shadowColour = colours.shadowDefault
        super(Table, self).__init__(app, defaultStyle)
        self.pos = pos
        self.topPadding = topPadding

        self._columns = []
        self._rows = []
        self.elements = self._columns

        # Style Settings:
        self._borderColour = (192, 192, 192)
        self._borderWidth = 10
        self._defaultWidth = 200
        self.setDefaultHeight(Value(60))

        if rows is not None:
            self.addRows(rows)

        if columns is not None:
            self.addEmptyColumns(columns)

        self._sizes = {}
        self._appSize = None
        app.screenManager.onResize.addListener(self.appResized)

    def appResized(self):
        for row in self._rows:
            for cell in row._cells:
                cell.layoutChanged()

    def onClicked(self, sender):
        self.setFocus(sender)

    def setDefaultHeight(self, height):
        self._defaultHeight = height

    def styleUpdate(self):
        '''
        Informs the table that the style of some part of the table has changed.
        This is provided because it is too expensive for every cell to check
        its style every draw() call, so you must manually tell the table, row,
        column or cell that the style has been updated before the update is
        reflected.
        '''
        for row in self._rows:
            row.styleUpdate()

    def setBorderWidth(self, width):
        if width != self._borderWidth:
            self._borderWidth = width
            self._sizes = {}

    def setBorderColour(self, colour):
        self._borderColour = colour

    def addRow(self, index=None):
        if index is None:
            index = len(self._rows)
        assert index <= len(self._rows)
        # Create and Insert
        newRow = Row(self.app, self, index, self._defaultHeight)
        self._rows.insert(index, newRow)
        for x in range(0, len(self._columns)):
            newCell = self._columns[x].createCell(newRow)
            newRow._newCell(newCell, x)
            self._columns[x]._newCell(newCell, index)

        for x in range(index+1, len(self._rows)):
            self._rows[x]._anotherInsertedBefore()
        self._sizes = {}
        return newRow

    def addColumn(self, column, index=None):
        if index is None:
            index = len(self._columns)
        if index > len(self._columns):
            raise ValueError('invalid index %r' % (index,))

        column.setIndex(index)
        column.setDefaultWidth(self._defaultWidth)

        self._columns.insert(index, column)
        for rowIndex, row in enumerate(self._rows):
            newCell = Cell(self.app, row, column)
            column._newCell(newCell, rowIndex)
            row._newCell(newCell, index)

        for column in self._columns[index+1:]:
            column._anotherInsertedBefore()
        self._sizes = {}

    def addColumns(self, columns):
        for column in columns:
            self.addColumn(column)

    def addRows(self, count, firstIndex=None):
        if count < 1:
            return

        index = firstIndex

        for i in range(count):
            self.addRow(index)
            if index is not None:
                index += 1

    def addEmptyColumns(self, count, firstIndex=None):
        if count < 1:
            return

        index = firstIndex

        for i in range(count):
            self.addColumn(
                TextColumn(self.app, self, self._defaultWidth), index)
            if index is not None:
                index += 1

    def clear(self):
        while self._rows:
            self.delRow(self.rowCount() - 1)

    def delRow(self, index):
        del self._rows[index]
        for col in self._columns:
            col._delCell(index)
        for x in range(index, len(self._rows)):
            self._rows[x]._anotherDeletedBefore()
        self._sizes = {}

    def delColumn(self, index):
        del self._columns[index]
        for row in self._rows:
            row._delCell(index)
        for x in range(index, len(self._columns)):
            self._columns[x]._anotherDeletedBefore()
        self._sizes = {}

    def rowCount(self):
        return len(self._rows)

    def columnCount(self):
        return len(self._columns)

    def getRect(self, app):
        assert app == self.app
        return self._getRect()

    def _getRect(self):
        r = pygame.Rect((0, 0), self._getSize())
        self.pos.apply(self.app, r)
        return r

    def _getPt(self):
        x, y = self._getRect().topleft
        y += self.topPadding
        return x, y

    def _getSize(self, rowStart=0, rowEnd=None, colStart=0, colEnd=None):
        if rowEnd is None:
            rowEnd = len(self._rows)
        if colEnd is None:
            colEnd = len(self._columns)

        appSize = self.app.screenManager.size
        if appSize != self._appSize:
            self._sizes = {}
            self._appSize = appSize
        else:
            try:
                return self._sizes[rowStart, rowEnd, colStart, colEnd]
            except KeyError:
                pass

        y = self._borderWidth
        for j in range(rowStart, rowEnd):
            y += self._rows[j]._getHeight()
            y += self._borderWidth

        x = self._borderWidth
        for i in range(colStart, colEnd):
            x += self._columns[i]._getWidth()
            x += self._borderWidth

        self._sizes[rowStart, rowEnd, colStart, colEnd] = (x, y)
        return (x, y)

    def _getRowPt(self, index):
        pt = self._getPt()
        offset = self._getSize(0, index)
        return (pt[0], pt[1]+offset[1])

    def _getColPt(self, index):
        pt = self._getPt()
        offset = self._getSize(colStart=0, colEnd=index)
        return (pt[0]+offset[0], pt[1])

    def draw(self, surface):
        super(Table, self).draw(surface)
        if self._borderColour is not None:
            self._drawBorders(surface)

    def _getBorderWidth(self):
        if hasattr(self._borderWidth, 'getVal'):
            return self._borderWidth.getVal(self.app)
        else:
            return self._borderWidth

    def _drawBorders(self, surface):
        width = self._getBorderWidth()
        if width == 0:
            return
        if self.rowCount() == 0 or self.columnCount() == 0:
            return
        # Draw Horizontals:
        # Use rect filling, because drawing lines usually round the ends
        horRect = pygame.Rect(
            (0, 0), (self._getSize(rowStart=0, rowEnd=1)[0], width))
        for row in self._rows:
            horRect.bottomleft = row._getPt()
            surface.fill(self._borderColour, horRect)
        horRect.top += row._getHeight() + width
        surface.fill(self._borderColour, horRect)

        # Draw Verticals:
        # Use rect filling, because drawing lines usually round the ends
        verRect = pygame.Rect(
            (0, 0), (width, self._getSize(colStart=0, colEnd=1)[1]))
        for col in self._columns:
            verRect.topright = col._getPt()
            surface.fill(self._borderColour, verRect)
        verRect.left += col._getWidth() + width
        surface.fill(self._borderColour, verRect)

    def __getitem__(self, index):
        return self.getColumn(index)

    def getRow(self, index):
        return self._rows[index]

    def getColumn(self, index):
        return self._columns[index]
