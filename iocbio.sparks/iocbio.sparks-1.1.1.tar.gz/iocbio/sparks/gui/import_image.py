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
from PyQt5.QtCore import Qt, QByteArray, QSettings
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPalette, QTransform
import pyqtgraph as pg

from iocbio.sparks.constants import application_name
from .custom_widgets import CustomQLineEdit, SmallLabel, EmptyContextMenuViewBox
from ..handler.experiment import ExperimentHandler


class ImportImage(QWidget):
    """Class for importing tiff files"""
    settingGeometry = "Import Tiff image GUI/geometry"

    def __init__(self, database, experiment_id, image):
        QWidget.__init__(self)

        self.database = database
        self.experiment_id = experiment_id
        self.start_analysis = False
        self.dx = 0.1 # micrometers
        self.dt = 1.0 # milliseconds
        self.image = image
        self.transposed = 0

        psql = 'filename, duration, length, pixels_time, pixels_space, transposed'
        if self.database.has_record(ExperimentHandler.database_table, experiment_id=experiment_id):
            record = self.database.query("SELECT %s FROM " % psql +
                                         self.database.table(ExperimentHandler.database_table) +
                                         " WHERE experiment_id=:eid", eid=experiment_id)[0]
        else:
            record = None

        self.new_record = True
        if record is not None:
            self.new_record = False
            self.start_analysis = True
            self.dx = record['length'] / record['pixels_space']
            self.dt = record['duration'] / record['pixels_time']
            self.transposed = record['transposed']
            if self.transposed:
                self.image = self.image.T

        main_layout = QVBoxLayout()

        layout = QGridLayout()
        layout.setVerticalSpacing(1)
        layout.setAlignment(Qt.AlignTop)

        self.pixel_space = CustomQLineEdit(self.dx, float, 'space')
        self.pixel_time = CustomQLineEdit(self.dt, float, 'time')
        transpose_image_btn = QPushButton('Flip dimensions')
        start_btn = QPushButton('Start analysis')
        btn_layout = QHBoxLayout()

        # { Connecting events
        self.pixel_space.sigValueUpdated.connect(self.update_resolution)
        self.pixel_time.sigValueUpdated.connect(self.update_resolution)
        transpose_image_btn.clicked.connect(self.transpose_image)
        start_btn.clicked.connect(self.start)
        # }

        layout.addWidget(QLabel('Pixel size X:'), 0, 0)
        layout.addWidget(self.pixel_space, 0, 1)
        layout.addWidget(SmallLabel('Specify space resolution in micrometers'), 1, 0, 1, 2)
        layout.addWidget(SmallLabel(''), 2, 0, 1, 2)
        layout.addWidget(QLabel('Pixel size T:'), 3, 0)
        layout.addWidget(self.pixel_time, 3, 1)
        layout.addWidget(SmallLabel('Specify time resolution in milliseconds'), 4, 0, 1, 2)

        btn_layout.addWidget(transpose_image_btn)
        btn_layout.addWidget(start_btn)

        # { Setting graphics general properites
        pg.setConfigOption('antialias', True)
        pg.setConfigOption('background', self.palette().color(QPalette.Window))
        pg.setConfigOption('foreground', '000000')
        # }

        gw = pg.GraphicsLayoutWidget()
        self.plot_item = gw.addPlot(viewBox=EmptyContextMenuViewBox())
        self.set_range()
        self.image_item = pg.ImageItem(autoDownsample=True)
        self.plot_item.addItem(self.image_item)
        self.plot_item.setLabel('left', 'x', units='m')
        self.plot_item.setLabel('bottom', 't', units='s')
        self.update_image()

        layout_widget = QWidget()
        layout_widget.setLayout(layout)

        main_layout.addWidget(layout_widget)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(gw)

        self.setWindowTitle(application_name + ': open a *.tiff image')
        self.setLayout(main_layout)

        # load settings
        settings = QSettings()
        self.restoreGeometry(settings.value(ImportImage.settingGeometry, QByteArray()))

    def transpose_image(self):
        self.image = self.image.T
        self.transposed = abs(self.transposed-1)
        self.update_image()

    def update_resolution(self, dimention):
        self.dx = self.pixel_space.get_value
        self.dt = self.pixel_time.get_value
        self.update_image()

    def update_image(self):
        tr = QTransform()
        tr.scale(self.dt*1e-3, self.dx*1e-6)
        self.image_item.setTransform(tr)
        self.image_item.setImage(self.image)
        self.set_range()

    def set_range(self):
        t1, x1 = self.image.shape
        self.plot_item.setRange(xRange=[0, self.dt*1e-3*t1],
                                yRange=[0, self.dx*1e-6*x1],
                                padding=0)

    def start(self):
        self.start_analysis = True
        self.close()

    @property
    def metadata(self):
        dimTime, dimX = self.image.shape
        return self.image, self.dx*1e-6, self.dt*1e-3, dimX, dimTime, self.transposed

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(ImportImage.settingGeometry, self.saveGeometry())
        self.close()
        event.accept()
