"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QRect, QPointF

from pyjamas.rcallbacks.rcallback import RCallback


class RCBSaveDisplay(RCallback):
    def cbSaveDisplay(self, filename: str = None) -> bool:
        """

        :param filename: '' for automated naming based on coordinates. If not provided, a dialog will open.
        :return: True if the display was properly saved; False if the save cannot be completed.
        """

        # Get file name.
        if filename is False or filename is None:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save time series ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        elif filename == '':
            filename = self.pjs.filename

        # Save image.
        self.save_display(filename)

        self.pjs.statusbar.showMessage('Display saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.

        return True

    def save_display(self, filename: str = None) -> QtGui.QPixmap:

        #pix_map: QtGui.QPixmap = self.pjs.gView.grab(self.pjs.gView.sceneRect().toRect())
        #pix_map: QtGui.QPixmap = self.pjs.gView.grab(QRect(0, 0, int(self.pjs.width * self.pjs.zoom_factors[self.pjs.zoom_index]), int(self.pjs.height * self.pjs.zoom_factors[self.pjs.zoom_index])))
        pix_map: QtGui.QPixmap = self.pjs.gView.grab()
        # todo: For some reason, the pix_map returned by grab is twice as large as it should (??).
        pix_map = pix_map.scaled(pix_map.width()/2, pix_map.height()/2)

        if filename and filename is not None and filename != '':
            pix_map.save(filename)

        return pix_map

    def export_movie(self, filename: str = None) -> bool:

        pass
