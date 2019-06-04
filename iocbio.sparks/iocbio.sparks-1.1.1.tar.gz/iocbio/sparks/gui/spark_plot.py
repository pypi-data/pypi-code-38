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
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtGui import QTransform, QAction
import pyqtgraph as pg

from .custom_widgets import EmptyContextMenuViewBox
from ..io.export import save_image


class Action(QAction):
    sigTriggered = pyqtSignal(object)

    def __init__(self, text, parent, obj):
        QAction.__init__(self, text, parent)
        self.triggered.connect(lambda x: self.sigTriggered.emit(obj))


class SparkPlot(QWidget):
    pens = {'central line': {'color': 'aaaaaa', 'width': 2},
            'original line': {'color': '333333', 'width': 2},
            'spline line': {'color': 'ff0000', 'width': 2},
            'isoline': {'color': 'ff0000', 'width': 1.5},
            'isoline outline': {'color': '000000', 'width': 3}
            }

    def __init__(self, dx, dt):
        QWidget.__init__(self)

        self.dx = dx
        self.dt = dt

        # Is a spark object that hold spark data, corresponding plots and stats
        self.spark = None
        self.data_coordinates = None
        self.last_image_save_path = None

        self.tmx = 0.0
        self.xmx = 0.0

        self.image_levels = [0, 1]

        data_transformer = QTransform()
        data_transformer.scale(self.dt, self.dx)

        self.image_list = ['original', 'corrected', 'medblu']
        self.switches = []
        for key in self.image_list:
            vb = EmptyContextMenuViewBox()
            plot = pg.PlotWidget(title=key.title(), viewBox=vb)
            plot.setAspectLocked(False)
            image = pg.ImageItem()
            image.setTransform(data_transformer)
            plot.addItem(image)
            plot.setLabel('left', 'space', 'm')
            plot.setLabel('bottom', 'time', 's')
            setattr(self, 'spark_plot_%s' % key, plot)
            setattr(self, 'spark_image_%s' % key, image)

            isoline = pg.IsocurveItem(level=0.9, pen=self.pens['isoline'])
            isoline.setTransform(data_transformer)
            setattr(self, 'spark_isoline_%s' % key, isoline)

            v_line = pg.InfiniteLine(angle=90, pen=self.pens['central line'], movable=False)
            h_line = pg.InfiniteLine(angle=0, pen=self.pens['central line'], movable=False)
            plot.addItem(v_line)
            plot.addItem(h_line)
            setattr(self, 'v_line_%s' % key, v_line)
            setattr(self, 'h_line_%s' % key, h_line)
            plot.setRange(xRange=[0,1], yRange=[0,1], padding=0)

            # { Creating new context menu
            view_all = Action('View All', self, plot)
            view_all.sigTriggered.connect(self.update_spark_image_view)
            save_image = Action('Save image', self, key)
            save_image.sigTriggered.connect(self.save_image)
            vb.menu.addAction(view_all)
            vb.menu.addAction(save_image)
            # }

        self.spark_space_plot = pg.PlotWidget()
        self.spark_space_plot.setLabel('left', 'intensity', units='AU')
        self.spark_space_plot.setLabel('bottom', 'space', units='microns')

        self.spark_time_plot = pg.PlotWidget()
        self.spark_time_plot.setLabel('left', 'intensity', units='AU')
        self.spark_time_plot.setLabel('bottom', 'time', units='ms')

        layout = QGridLayout()
        layout.addWidget(self.spark_plot_original, 0, 0, 1, 2)
        layout.addWidget(self.spark_plot_corrected, 0, 2, 1, 2)
        layout.addWidget(self.spark_plot_medblu, 0, 4, 1, 2)
        layout.addWidget(self.spark_time_plot, 1, 0, 1, 3)
        layout.addWidget(self.spark_space_plot, 1, 3, 1, 3)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def save_image(self, key):
        if self.spark is None: return
        if key not in self.spark.images: return
        self.last_image_save_path = save_image(self.spark.images[key].T,
                                               'spark_' + key,
                                               self.last_image_save_path,
                                               parent=self)

    def update_center_location(self):
        if self.spark is None:
            for key in self.image_list:
                getattr(self, 'v_line_%s' % key).setPos(0)
                getattr(self, 'h_line_%s' % key).setPos(0)
        else:
            data = self.spark.stats
            if 'location_space' and 'location_time' in data:
                self.tmx = data['location_time'] * 1e-3
                self.xmx = data['location_space'] * 1e-6
                for key in self.image_list:
                    getattr(self, 'v_line_%s' % key).setPos(self.tmx)
                    getattr(self, 'h_line_%s' % key).setPos(self.xmx)
            else:
                for key in self.image_list:
                    getattr(self, 'v_line_%s' % key).setPos(0)
                    getattr(self, 'h_line_%s' % key).setPos(0)

    def update_spark_image_view(self, plot):
        x0, y0, x1, y1 = self.data_coordinates
        plot.setRange(xRange=[0,self.dt*(x1-x0)], yRange=[0,self.dx*(y1-y0)], padding=0)

    def update_spark_image(self):
        if self.spark is None or self.data_coordinates is None: return

        for key in self.image_list:
            plot = getattr(self, 'spark_plot_%s' % key)
            self.update_spark_image_view(plot)

        for key in self.image_list:
            if key in self.spark.images:
                image = getattr(self, 'spark_image_%s' % key)
                image.clear()
                image.setImage(self.spark.images[key].T)
                self.set_image_levels(*self.image_levels)

        if 'spark watermark' in self.spark.images:
            watermark = self.spark.images['spark watermark'].T
            for key in self.image_list:
                isoline = getattr(self, 'spark_isoline_%s' % key)
                isoline.setData(watermark)
                getattr(self, 'spark_plot_%s' % key).addItem(isoline)
        else:
            for key in self.image_list:
                getattr(self, 'spark_plot_%s' % key).removeItem(getattr(self, 'spark_isoline_%s' % key))

    def set_lut(self, cmap_dict):
        """ Set lookup table for the image """
        for key in self.image_list:
            getattr(self, 'spark_image_%s' % key).setLookupTable(cmap_dict['lut'])
        self.pens['isoline']['color'] = cmap_dict['active roi']
        self.update_isoline_color()

    def set_image_levels(self, mn, mx):
        """ Sets intensity levels of the image """
        self.image_levels = [mn, mx]

        if self.spark is None or self.data_coordinates is None: return
        for key in self.image_list:
            getattr(self, 'spark_image_%s' % key).setLevels([mn, mx])

    def update_isoline_color(self):
        for key in self.image_list:
            isoline = getattr(self, 'spark_isoline_%s' % key, None)
            if isoline is not None:
                isoline.setPen(self.pens['isoline'])

    def update_graphs(self):
        for key in ['time', 'space']:
            if self.spark.graphs[key] != {}:
                getattr(self, 'update_spark_%s_plot' % key)()

    def update_spark_space_plot(self):
        self.spark_space_plot.clear()
        if self.spark is None: return
        data = self.spark.graphs['space']
        ymin = 0
        ymax = 1
        for key in ['original', 'spline']:
            if key in data:
                x = data[key]['x']
                y = data[key]['y']
                if abs(y.min()-y.max()) < 1.e-20:
                    y[y<1.e-20] = 1.e-20
                self.spark_space_plot.plot(x, y, pen=self.pens['%s line' % key], name=key)
                self.spark_space_plot.setXRange(x.min(), x.max(), padding=0)
                ymin = min(y.min(), ymin)
                ymax = max(y.max(), ymax)

        self.spark_space_plot.setYRange(ymin, ymax)

        peak_line = pg.InfiniteLine(angle=90, pen=self.pens['central line'], movable=False)
        peak_line.setPos(self.xmx*1e6)
        self.spark_space_plot.addItem(peak_line)

        zero_line = pg.InfiniteLine(angle=0, pen=self.pens['central line'], movable=False)
        zero_line.setPos(0)
        self.spark_space_plot.addItem(zero_line)

    def update_spark_time_plot(self):
        self.spark_time_plot.clear()
        if self.spark is None: return
        data = self.spark.graphs['time']
        ymin = 0
        ymax = 1
        for key in ['original', 'spline']:
            if key in data:
                x = data[key]['x']
                y = data[key]['y']
                self.spark_time_plot.plot(x, y, pen=self.pens['%s line' % key], name=key)
                self.spark_time_plot.setXRange(x.min(), x.max(), padding=0)
                ymin = min(y.min(), ymin)
                ymax = max(y.max(), ymax)

        self.spark_time_plot.setYRange(ymin, ymax)

        peak_line = pg.InfiniteLine(angle=90, pen=self.pens['central line'], movable=False)
        peak_line.setPos(self.tmx*1e3)
        self.spark_time_plot.addItem(peak_line)

        zero_line = pg.InfiniteLine(angle=0, pen=self.pens['central line'], movable=False)
        zero_line.setPos(0)
        self.spark_time_plot.addItem(zero_line)

    def set_spark(self, spark, data_coordinates):
        """ Updates spark object if roi id is changed """
        if self.spark is not None:
            self.spark.sigUpdateImage.disconnect(self.update_spark_image)
            self.spark.sigUpdateGraph.disconnect(self.update_graphs)
            self.spark.sigUpdateStats.disconnect(self.update_center_location)
            self.spark.sigNewAnalysis.disconnect(self.clear_all)
            if self.last_image_save_path is None:
                self.last_image_save_path = self.spark.image.get_image_filepath

        self.spark = spark
        self.data_coordinates = data_coordinates
        self.clear_all()

        if self.spark is None:
            self.update_center_location()
            for key in self.image_list:
                getattr(self, 'spark_plot_%s' % key).removeItem(getattr(self, 'spark_isoline_%s' % key))
            return

        # { Event bindings with spark object and plot updates
        self.spark.sigUpdateStats.connect(self.update_center_location)
        self.spark.sigUpdateImage.connect(self.update_spark_image)
        self.spark.sigUpdateGraph.connect(self.update_graphs)
        self.spark.sigNewAnalysis.connect(self.clear_all)
        # }
        self.update_center_location()
        self.update_spark_image()
        self.update_graphs()

    def clear_all(self):
        self.spark_time_plot.clear()
        self.spark_space_plot.clear()
        self.spark_image_original.clear()
        self.spark_image_corrected.clear()
        self.spark_image_medblu.clear()
