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

from PyQt5 import QtWidgets

from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils


class RCBSaveImage(RCallback):
    def cbSaveImage(self, filename: str=False, x_range: tuple=False, y_range: tuple=False, z_range: tuple=False) -> bool:  # function cancel = cbLoadTimeSeries(fig, filename, in)
        """

        :param filename: '' for automated naming based on coordinates. If not provided, a dialog will open.
        :param x_range: tuple containing the min and max X values to save. If False, take the coordinates of the first polygon.
        :param y_range: tuple containing the min and max Y values to save. If False, take the coordinates of the first polygon.
        :param z_range: tuple containing the min and max Z values to save. If False, use just the current Z.
        :return: True if the image was properly saved; False if the save cannot be completed.
        """

        # Check X, Y, and Z parameters or assign default values.
        if z_range is False:
            z_range = tuple([self.pjs.curslice, self.pjs.curslice+1])

        if x_range is False:
            thepolylines = self.pjs.polylines[self.pjs.curslice]
            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = self.pjs.polylines[self.pjs.curslice][0].boundingRect()
                x_range = tuple([int(thepolyline.x()), int(thepolyline.x()+thepolyline.width()+1)])
            else:
                return False

        if y_range is False and thepolylines != [] and thepolylines[0] != []:
            thepolylines = self.pjs.polylines[self.pjs.curslice]
            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = self.pjs.polylines[self.pjs.curslice][0].boundingRect()
                y_range = tuple([int(thepolyline.y()), int(thepolyline.y() + thepolyline.height() + 1)])
            else:
                return False

        # Get file name.
        if filename is False:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save time series ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        elif filename == '':
            filename = self.pjs.filename + '_X' + str(x_range[0]) + '_' + str(x_range[1]-1) + '_Y' + str(y_range[0]) + \
                       '_' + str(y_range[1]-1) + '_Z' + str(z_range[0]) + '_' + str(z_range[1]-1) + '.tif'

        # Save image.
        rimutils.write_stack(filename,
                             self.pjs.slices[z_range[0]:z_range[1], y_range[0]:y_range[1], x_range[0]:x_range[1]])
        self.pjs.statusbar.showMessage('Image saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.

        return True
