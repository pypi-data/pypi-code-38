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

import gzip
import os
import pickle

from PyQt5 import QtWidgets

import pyjamas.pjscore as pjscore
from .rcallback import RCallback


class RCBSaveAnnotations(RCallback):
    def cbSaveAnnotations(self, filename: str = '', polylines: list = None, fiducials: list = None):  # Handle IO errors.
        # Get file name.
        if filename == '' or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            defaultname, _ = os.path.splitext(os.path.basename(self.pjs.filename))
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save annotations ...', self.pjs.cwd + os.sep + defaultname,
                                                          filter='PyJAMAS data (*' + pjscore.PyJAMAS.data_extension + ')')  # fname[0] is the full filename, fname[1] is the filter used.

            # If cancel ...
            if fname == '':
                return False

            # else ...
            else:
                filename = fname[0]

        self.pjs.cwd = os.path.dirname(filename)

        if filename[-4:] != pjscore.PyJAMAS.data_extension:
            filename = filename + pjscore.PyJAMAS.data_extension

        if not polylines:
            polylines = self.pjs.polylines

        if not fiducials:
            fiducials = self.pjs.fiducials

        # Prepare polygons to be stored: pickle does not support QPolygonF, so we convert the polygons to a list.
        # We store the polygons as QPolygonF because QGraphicsScene does have an addPolygon method that takes a
        # QPolygonF as the parameter.
        polyline_list = [[] for iframe in polylines]
        for iframe, theframepolylines in enumerate(polylines):
            for ipoly, thepolyline in enumerate(theframepolylines):
                polyline_list[iframe].append([])
                for ipnt, thepoint in enumerate(thepolyline):
                    polyline_list[iframe][ipoly].append([thepoint.x(), thepoint.y()])

        # Open file for writing.
        fh = None

        try:
            fh = gzip.open(filename, "wb")
            pickle.dump(fiducials, fh, pickle.HIGHEST_PROTOCOL)
            pickle.dump(polyline_list, fh, pickle.HIGHEST_PROTOCOL)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)

        self.pjs.statusbar.showMessage(f"Saved {filename}.")

        return True

