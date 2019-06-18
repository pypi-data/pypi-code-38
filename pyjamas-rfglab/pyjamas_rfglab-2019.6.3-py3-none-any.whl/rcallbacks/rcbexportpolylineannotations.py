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

from PyQt5 import QtCore, QtWidgets

import pyjamas.pjscore as pjscore
from .rcallback import RCallback


class RCBExportPolylineAnnotations(RCallback):
    FILENAME_BASE = "cell_"
    FILENAME_FIDUCIAL_LENGTH = 5

    def cbExportPolylineAnnotations(self, folder_name: str = '') -> bool:
        if folder_name != '' and folder_name is not False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            self.pjs.cwd = folder_name

        self.pjs.annotation_mode = pjscore.PyJAMAS.export_fiducial_polyline
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

        return True

    def export_polyline_annotations(self, x: int, y: int) -> bool:
        # Make sure the fiducial is in the list.
        assert [x, y] in self.pjs.fiducials[self.pjs.curslice], "Fiducial not found!"

        # Identify the fiducial.
        fiducial_index: int = self.pjs.fiducials[self.pjs.curslice].index([x, y])

        # List of polygons and fiducials for new annotation file.
        fiducial_list: list = [[] for i in range(self.pjs.n_frames)]
        polyline_list: list = [[] for i in range(self.pjs.n_frames)]

        # In every image:
        for slice in range(self.pjs.n_frames):
            # If there are enough fiducials and any polylines.
            if self.pjs.fiducials[slice] and fiducial_index < len(self.pjs.fiducials[slice]) and self.pjs.polylines[slice]:
                # Store the fiducial.
                fiducial_list[slice].append(self.pjs.fiducials[slice][fiducial_index])

                # Find the first polygon that contains the fiducial and store it as well.
                thefiducial: list = self.pjs.fiducials[slice][fiducial_index]
                thepolylines: list = [one_polyline for one_polyline in self.pjs.polylines[slice]]

                for index_polyline, one_polyline in enumerate(thepolylines):
                    if one_polyline.containsPoint(QtCore.QPointF(thefiducial[0], thefiducial[1]), QtCore.Qt.OddEvenFill):
                        polyline_list[slice].append(self.pjs.polylines[slice][index_polyline])
                        break

        # Save new annotation file.
        filename: str = os.path.join(self.pjs.cwd, self.FILENAME_BASE + str(fiducial_index+1).zfill(self.FILENAME_FIDUCIAL_LENGTH))
        self.pjs._cbSaveAnn.cbSaveAnnotations(filename, polyline_list, fiducial_list)

        return True





