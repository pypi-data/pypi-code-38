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
Qt4 widgets to display diffs as blocks
"""
import sys, os
from functools import partial

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt, pyqtSignal

class BlockList(QtGui.QWidget):
    """
    A simple widget to be 'linked' to the scrollbar of a diff text
    view.

    It represents diff blocks with colored rectangles, showing
    currently viewed area by a semi-transparant rectangle sliding
    above them.
    """

    value_changed = pyqtSignal(int)
    range_changed = pyqtSignal(int, int)
    page_step_changed = pyqtSignal(int)

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self._blocks = set()
        self._minimum = 0
        self._maximum = 100
        self.blockTypes = {'+': QtGui.QColor(0xA0, 0xFF, 0xB0, ),#0xa5),
                           '-': QtGui.QColor(0xFF, 0xA0, 0xA0, ),#0xa5),
                           'x': QtGui.QColor(0xA0, 0xA0, 0xFF, ),#0xa5),
                           }
        self._sbar = None
        self._value = 0
        self._pagestep = 10
        self._vrectcolor = QtGui.QColor(0x00, 0x00, 0x55, 0x25)
        self._vrectbordercolor = self._vrectcolor.darker()
        self.sizePolicy().setControlType(QtGui.QSizePolicy.Slider)
        self.setMinimumWidth(20)

    def clear(self):
        self._blocks = set()

    def addBlock(self, typ, alo, ahi):
        self._blocks.add((typ, alo, ahi))

    def setMaximum(self, maximum):
        self._maximum = maximum
        self.update()
        self.range_changed[int, int].emit(self._minimum, self._maximum)

    def setMinimum(self, minimum):
        self._minimum = minimum
        self.update()
        self.range_changed[int, int].emit(self._minimum, self._maximum)

    def setRange(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum
        self.update()
        self.range_changed[int, int].emit(self._minimum, self._maximum)

    def setValue(self, val):
        if val != self._value:
            self._value = val
            self.update()
            self.value_changed[int].emit(val)

    def setPageStep(self, pagestep):
        if pagestep != self._pagestep:
            self._pagestep = pagestep
            self.update()
            self.page_step_changed[int].emit(pagestep)

    def linkScrollBar(self, sbar):
        """
        Make the block list displayer be linked to the scrollbar
        """
        self._sbar = sbar
        self.setUpdatesEnabled(False)
        self.setMaximum(sbar.maximum())
        self.setMinimum(sbar.minimum())
        self.setPageStep(sbar.pageStep())
        self.setValue(sbar.value())
        self.setUpdatesEnabled(True)
        sbar.valueChanged[int].connect(self.setValue)
        sbar.rangeChanged[int, int].connect(self.setRange)
        # use partial to bypass the slot overload checking that fails with
        # pyqt4 4.10.1 on debian
        self.value_changed[int].connect(partial(sbar.setValue))
        self.range_changed[int, int].connect(partial(sbar.setRange))
        self.page_step_changed[int].connect(partial(sbar.setPageStep))

    def syncPageStep(self):
        self.setPageStep(self._sbar.pageStep())

    def paintEvent(self, event):
        w = self.width() - 1
        h = self.height()
        p = QtGui.QPainter(self)
        p.scale(1.0, float(h)/(self._maximum - self._minimum + self._pagestep))
        p.setPen(Qt.NoPen)
        for typ, alo, ahi in self._blocks:
            p.save()
            p.setBrush(self.blockTypes[typ])
            p.drawRect(1, alo, w-1, ahi-alo)
            p.restore()

        p.save()
        p.setPen(self._vrectbordercolor)
        p.setBrush(self._vrectcolor)
        p.drawRect(0, self._value, w, self._pagestep)
        p.restore()

class BlockMatch(BlockList):
    """
    A simple widget to be linked to 2 file views (text areas),
    displaying 2 versions of a same file (diff).

    It will show graphically matching diff blocks between the 2 text
    areas.
    """

    value_changed = pyqtSignal([int], [int, str])
    range_changed = pyqtSignal([int, int], [int, int, str])
    page_step_changed = pyqtSignal([int], [int, str])

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self._blocks = set()
        self._minimum = {'left': 0, 'right': 0}
        self._maximum = {'left': 100, 'right': 100}
        self.blockTypes = {'+': QtGui.QColor(0xA0, 0xFF, 0xB0, ),#0xa5),
                           '-': QtGui.QColor(0xFF, 0xA0, 0xA0, ),#0xa5),
                           'x': QtGui.QColor(0xA0, 0xA0, 0xFF, ),#0xa5),
                           }
        self._sbar = {}
        self._value =  {'left': 0, 'right': 0}
        self._pagestep =  {'left': 10, 'right': 10}
        self._vrectcolor = QtGui.QColor(0x00, 0x00, 0x55, 0x25)
        self._vrectbordercolor = self._vrectcolor.darker()
        self.sizePolicy().setControlType(QtGui.QSizePolicy.Slider)
        self.setMinimumWidth(20)

    def nDiffs(self):
        return len(self._blocks)

    def showDiff(self, delta):
        ps_l = float(self._pagestep['left'])
        ps_r = float(self._pagestep['right'])
        mv_l = self._value['left']
        mv_r = self._value['right']
        Mv_l = mv_l + ps_l
        Mv_r = mv_r + ps_r

        vblocks = []
        blocks = sorted(self._blocks, key=lambda x:(x[1],x[3],x[2],x[4]))
        for i, (typ, alo, ahi, blo, bhi) in enumerate(blocks):
            if (mv_l<=alo<=Mv_l or mv_l<=ahi<=Mv_l or
                mv_r<=blo<=Mv_r or mv_r<=bhi<=Mv_r):
                break
        else:
            i = -1
        i += delta

        if i < 0:
            return -1
        if i >= len(blocks):
            return 1
        typ, alo, ahi, blo, bhi = blocks[i]
        self.setValue(alo, "left")
        self.setValue(blo, "right")
        if i == 0:
            return -1
        if i == len(blocks)-1:
            return 1
        return 0

    def nextDiff(self):
        return self.showDiff(+1)

    def prevDiff(self):
        return self.showDiff(-1)

    def addBlock(self, typ, alo, ahi, blo=None, bhi=None):
        if bhi is None:
            bhi = ahi
        if blo is None:
            blo = alo
        self._blocks.add((typ, alo, ahi, blo, bhi))

    def paintEvent(self, event):
        w = self.width()
        h = self.height()
        p = QtGui.QPainter(self)
        p.setRenderHint(p.Antialiasing)

        ps_l = float(self._pagestep['left'])
        ps_r = float(self._pagestep['right'])
        v_l = self._value['left']
        v_r = self._value['right']

        # we do integer divisions here cause the pagestep is the
        # integer number of fully displayed text lines
        scalel = self._sbar['left'].height()//ps_l
        scaler = self._sbar['right'].height()//ps_r

        ml = v_l
        Ml = v_l + ps_l
        mr = v_r
        Mr = v_r + ps_r

        p.setPen(Qt.NoPen)
        for typ, alo, ahi, blo, bhi in self._blocks:
            if not (ml<=alo<=Ml or ml<=ahi<=Ml or mr<=blo<=Mr or mr<=bhi<=Mr):
                continue
            p.save()
            p.setBrush(self.blockTypes[typ])

            path = QtGui.QPainterPath()
            path.moveTo(0, scalel * (alo - ml))
            path.cubicTo(w/3.0, scalel * (alo - ml),
                         2*w/3.0, scaler * (blo - mr),
                         w, scaler * (blo - mr))
            path.lineTo(w, scaler * (bhi - mr) + 2)
            path.cubicTo(2*w/3.0, scaler * (bhi - mr) + 2,
                         w/3.0, scalel * (ahi - ml) + 2,
                         0, scalel * (ahi - ml) + 2)
            path.closeSubpath()
            p.drawPath(path)

            p.restore()

    def setMaximum(self, maximum, side):
        self._maximum[side] = maximum
        self.update()
        self.range_changed[int, int, str].emit(
                  self._minimum[side], self._maximum[side], side)

    def setMinimum(self, minimum, side):
        self._minimum[side] = minimum
        self.update()
        self.range_changed[int, int, str].emit(
                  self._minimum[side], self._maximum[side], side)

    def setRange(self, minimum, maximum, side=None):
        if side is None:
            if self.sender() == self._sbar['left']:
                side = 'left'
            else:
                side = 'right'
        self._minimum[side] = minimum
        self._maximum[side] = maximum
        self.update()
        self.range_changed[int, int, str].emit(
                  self._minimum[side], self._maximum[side], side)

    def setValue(self, val, side=None):
        if side is None:
            if self.sender() == self._sbar['left']:
                side = 'left'
            else:
                side = 'right'
        if val != self._value[side]:
            self._value[side] = val
            self.update()
            self.value_changed[int, str].emit(val, side)

    def setPageStep(self, pagestep, side):
        if pagestep != self._pagestep[side]:
            self._pagestep[side] = pagestep
            self.update()
            self.page_step_changed[int, str].emit(pagestep, side)

    def syncPageStep(self):
        for side in ['left', 'right']:
            self.setPageStep(self._sbar[side].pageStep(), side)

    def resizeEvent(self, event):
        self.syncPageStep()

    def linkScrollBar(self, sb, side):
        """
        Make the block list displayer be linked to the scrollbar
        """
        if self._sbar is None:
            self._sbar = {}
        self._sbar[side] = sb
        self.setUpdatesEnabled(False)
        self.setMaximum(sb.maximum(), side)
        self.setMinimum(sb.minimum(), side)
        self.setPageStep(sb.pageStep(), side)
        self.setValue(sb.value(), side)
        self.setUpdatesEnabled(True)
        sb.valueChanged[int].connect(self.setValue)
        sb.rangeChanged[int, int].connect(self.setRange)

        self.value_changed[int, str].connect(
                     lambda v, s: side==s and sb.setValue(v))
        self.range_changed[int, int, str].connect(
                     lambda v1, v2, s: side==s and sb.setRange(v1, v2))
        self.page_step_changed[int, str].connect(
                     lambda v, s: side==s and sb.setPageStep(v))
