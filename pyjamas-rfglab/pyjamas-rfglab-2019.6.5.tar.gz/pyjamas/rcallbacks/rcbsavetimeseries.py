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

from .rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils


class RCBSaveTimeSeries(RCallback):
    def cbSaveTimeSeries(self, filename: str='') -> bool:  # function cancel = cbLoadTimeSeries(fig, filename, in)
        '''
        Save a grayscale, multi-page TIFF.
        :return: boolean (True if the image was loaded with no problems, False otherwise)
        '''

        # Get file name.
        if filename == '' or filename is False:
            fname: tuple = QtWidgets.QFileDialog.getSaveFileName(None, 'Save time series ...', self.pjs.cwd,
                                                          filter='TIFF files (*.tif *.tiff)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Save image.
        rimutils.write_stack(filename, self.pjs.slices)
        self.pjs.statusbar.showMessage('Image saved: ' + filename)

        self.pjs.cwd = os.path.dirname(filename)  # Path of loaded image.
        self.pjs.filename = filename

        return True
