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
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QColor
import pyqtgraph as pg
import numpy as np


class ZoomShowerItem(pg.PlotDataItem):

    def __init__(self, x0, x1, ylevel, pen=None):
        self.ylevel = ylevel
        pg.PlotDataItem.__init__(self, [x0, x1], [self.ylevel, self.ylevel], pen=pen, name='zoom_region')

    def set_region(self, x0, x1):
        self.setData([x0, x1], [self.ylevel, self.ylevel])


class AverageIntensityPlot(QWidget):
    sigAnalysisRegionChange = pyqtSignal(tuple)
    sigAnalysisRegionChangeFinished = pyqtSignal(tuple)
    sigStageRangeChanged = pyqtSignal(str, list)

    def __init__(self, xdata, tdata, analysis_range):
        QWidget.__init__(self)
        self.xdata = xdata
        self.tdata = tdata
        self.stages_list = set()
        self.read_only = False

        gw = pg.GraphicsLayoutWidget()
        gw.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.plot = gw.addPlot()
        self.plot.plot(self.tdata, self.xdata, pen={'color': '000000'}, name='average_intensity')
        self.plot.setLabel('left', 'intensity', units='AU')
        self.plot.setLabel('bottom', 'time', units='s')
        #self.plot.setXRange(self.tdata[0], self.tdata[-1], padding=0)

        self.analysis_region = pg.LinearRegionItem(analysis_range)
        self.analysis_region.setBounds((self.tdata[0], self.tdata[-1]))
        self.analysis_region.setZValue(-10)
        self.plot.addItem(self.analysis_region)

        self.zoom_region = ZoomShowerItem(self.tdata[0], self.tdata[-1], 1.1*self.xdata.max(),
                                          pen={'color': '0f993499', 'width': 4})
        self.plot.addItem(self.zoom_region)

        self.plot.setXRange(self.tdata[0], self.tdata[-1], padding=0)

        # { Event bindings
        self.analysis_region.sigRegionChanged.connect(self.analysis_range_changed)
        self.analysis_region.sigRegionChangeFinished.connect(self.analysis_range_changed_finished)
        # }

        # { Creating layout
        layout = QVBoxLayout()
        layout.addWidget(gw)
        self.setLayout(layout)
        # }

    def set_read_only(self, state):
        self.read_only = state
        for lri in self.plot.items:
            if isinstance(lri, pg.LinearRegionItem):
                lri.setMovable(not self.read_only)

    @property
    def get_analysis_range(self):
        return self.analysis_region.getRegion()

    def analysis_range_changed(self, region):
        self.sigAnalysisRegionChange.emit(self.get_analysis_range)

    def analysis_range_changed_finished(self, region):
        self.sigAnalysisRegionChangeFinished.emit(self.get_analysis_range)

    def update_zoom_range(self, t0, t1):
        t0 = max(t0, self.tdata[0])
        t1 = min(t1, self.tdata[-1])
        self.zoom_region.set_region(t0, t1)

    def update_stages(self, stages, stages_list):
        if self.read_only: return
        for key in stages_list:
            stage = stages[key]
            if key not in self.stages_list:
                if stage["spark_analysis"]:
                    continue # the analysis range is handled separately
                t0, t1 = stage["start"], stage["end"]
                color = QColor('#%s' % key[:6])
                color.setAlpha(60)
                region = pg.LinearRegionItem((t0, t1), brush=color)
                region.setBounds((self.tdata[0], self.tdata[-1]))
                region.stage_id = key
                region.sigRegionChangeFinished.connect(self.update_stage_region)
                self.plot.addItem(region)
                self.stages_list.add(key)
            t0, t1 = stage["start"], stage["end"]
            self.update_stage_region_if_changed(key, t0, t1)

        keys = list(self.stages_list)
        for key in keys:
            if key not in stages_list:
                self.remove_stage(key)

    def update_stage_region_if_changed(self, stage_id, start, end):
        tol = 1e-6
        for item in self.plot.items:
            if hasattr(item, 'stage_id') and item.stage_id == stage_id:
                t0, t1 = item.getRegion()
                if abs(t0-start) > tol or abs(t1-end)>tol:
                    item.setRegion([start,end])
                return

    def update_stage_region(self, region):
        t0, t1 = region.getRegion()
        self.sigStageRangeChanged.emit(region.stage_id, [t0, t1])

    def remove_stage(self, stage_id):
        if self.read_only: return
        for item in self.plot.items:
            if hasattr(item, 'stage_id'):
                if item.stage_id == stage_id:
                    self.plot.removeItem(item)
                    break
        self.stages_list.remove(stage_id)
