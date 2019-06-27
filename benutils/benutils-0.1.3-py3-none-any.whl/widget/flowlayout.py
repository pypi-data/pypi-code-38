# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright Digia Plc and/or it's subsidiaries
licence   BSD
brief     Port to pyQt of flowlayout example from Qt project. The Flow Layout
          is a custom layout that arranges child widgets from left to right and
          top to bottom in a top-level widget.
details   See on https://qt-project.org/doc/qt-4.7/layouts-flowlayout.html
"""

from PyQt5.QtCore import Qt, QRect, QSize, QPoint
from PyQt5.QtWidget import QLayout, QLayoutItem, QStyle, QSizePolicy, QWidget


class FlowLayout(QLayout):
    """A custom layout that arranges child widgets from left to right and top
    to bottom in a top-level widget.
    """
    
    def __init__(self, parent=None, margin=-1, hSpacing=-1, vSpacing=-1):
        
        super(FlowLayout, self).__init__(parent)
        self._m_hSpace = hSpacing
        self._m_vSpace = vSpacing
        self._item_list = list()
        self.setContentsMargins(margin, margin, margin, margin)

    """def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)"""

    def addItem(self, item):
        self._item_list.append(item)

    def horizontalSpacing(self):
        if self._m_hSpace >= 0:
            return self._m_hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._m_vSpace >= 0:
            return self._m_vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        try:
            item = self._item_list[index]
        except IndexError:
            pass
        else:
            return item

    def takeAt(self, index):
        if index >= 0 and index < len(self._item_list):
            return self._item_list.remove(index)
        else:
            return 0

    def expandingDirections(self):
        return 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2*self.margin(), 2*self.margin())
        return size

    def doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        for item in self._item_list:
            wid = item.widget()
            spaceX = self.horizontalSpacing()
            if spaceX == -1:
                spaceX = wid.style().layoutSpacing(QSizePolicy.PushButton, \
                                                   QSizePolicy.PushButton, \
                                                   Qt.Horizontal)
            spaceY = self.verticalSpacing()
            if spaceY == -1:
                spaceY = wid.style().layoutSpacing(QSizePolicy.PushButton, \
                                                   QSizePolicy.PushButton, \
                                                   Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if (nextX - spaceX) > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y() + bottom

    def smartSpacing(self, pm):
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            pw = QWidget(parent)
            return pw.style().pixelMetric(pm, None, pw)
        else:
            return QLayout(parent).spacing()

