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
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import numpy as np
import pyqtgraph as pg


class Histogram(QWidget):

    def __init__(self, title, data=None):
        QWidget.__init__(self)

        gw = pg.GraphicsLayoutWidget()
        gw.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.histogram = gw.addPlot(title=title)
        self.histogram.setLabel('left', 'counts', units=' ')
        self.histogram.setLabel('bottom', 'intensity')
        if data is not None:
            self.set_data(data)

        layout = QVBoxLayout()
        layout.addWidget(gw)
        self.setLayout(layout)

    def set_data(self, data):
        self.histogram.clear()
        def minmax(d):
            return d.min(), d.max()
        #y, x = np.histogram(data, bins=np.arange(0, 256, 1))
        y, x = np.histogram(data, bins=np.linspace(data.min(), data.max(), 256))
        self.histogram.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))
        self.histogram.setRange(xRange=minmax(x), yRange=minmax(y), padding=0)
