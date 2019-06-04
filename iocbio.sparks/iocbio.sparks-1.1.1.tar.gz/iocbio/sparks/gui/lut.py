# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush
from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QLabel

import numpy as np
import pyqtgraph as pg


COLORMAPS = {0: {'lut': [(255,255,217), (237,248,177), (199,233,180), (127,205,187), (65,182,196), (29,145,192), (34,94,168),
                 (37,52,148), (8,29,88)],
                 'active roi': 'ff704d',
                 'inactive roi': '801a00'},
             1: {'lut': [(255,255,255), (255,255,233), (255,255,105),(255,237,0), (255,210,0), (255,182,0), (255,155,0),
                 (255,129,0), (250,98,0),(229,57,5), (208,16,60), (186,0,114), (166,0,169),  (134,0,218), (88,0,209),
                 (43,0,156),(0,0,91), (0,0,0)],
                 'active roi': '66ccff',
                 'inactive roi': '005580'},
             2: {'lut': [(128,0,0), (255,48,0), (255,185,0), (183,255,64), (64,255,183), (0,164,255), (0,16,255), (0,0,128)],
                 'active roi': 'f5f5f5',
                 'inactive roi': '303030'},
             3: {'lut': [(255,0,0), (0,0,255), (0,255,255), (0,255,0), (255,255,0), (255,0,0)],
                 'active roi': 'f5f5f5',
                 'inactive roi': '303030'},
             4: {'lut': [(255,255,255), (0,0,0)],
                 'active roi': 'fe642e',
                 'inactive roi': '8856a7'},
}


def draw_colormap(pixmap, color):
    painter = QPainter(pixmap)
    w, h = pixmap.width(), pixmap.height()
    for i in range(w):
        painter.fillRect(i, 0, 1, h, QBrush(QColor(*color[i])))


def get_colormaps(n):
    colormaps = {}
    for k, color_dict in COLORMAPS.items():
        color = [QColor(*c).getRgbF() for c in color_dict['lut']]
        pos =  np.linspace(0.0, 1.0, len(color))
        colormaps[str(k)] = {'lut': pg.ColorMap(pos, color).getLookupTable(1.0, 0.0, n),
                             'active roi': color_dict['active roi'],
                             'inactive roi': color_dict['inactive roi']}
    return colormaps


class LUTWidget(QWidget):
    sigUpdate = pyqtSignal(dict)

    def __init__(self, lut_name):
        QWidget.__init__(self)
        layout = QVBoxLayout()

        self.cb = QComboBox()
        w, h = 256, self.cb.iconSize().height()
        self.cb.setIconSize(QSize(w, h))
        self.colormaps = get_colormaps(w)
        keys = sorted(list(self.colormaps.keys()))
        self.lut_names = {}
        for i, k in enumerate(keys):
            pixmap = QPixmap(w, h)
            draw_colormap(pixmap, self.colormaps[k]['lut'])
            self.cb.addItem(QIcon(pixmap), '')
            self.lut_names[i] = str(k)

        lk = [k for k, v in self.lut_names.items() if v == lut_name]
        self.cb.setCurrentIndex(0 if len(lk) < 1 else lk[0])
        self.cb.currentIndexChanged.connect(self.colormap_changed)
        self.cb.setMaximumWidth(self.cb.sizeHint().width())
        layout.addWidget(QLabel('Set colormap:'))
        layout.addWidget(self.cb)
        self.setLayout(layout)

    def colormap_changed(self, i):
        self.sigUpdate.emit(self.colormaps[self.lut_names[i]])

    @property
    def get_current_colormap(self):
        return self.colormaps[self.lut_names[self.cb.currentIndex()]]

    @property
    def get_current_lut_name(self):
        return self.lut_names[self.cb.currentIndex()]
