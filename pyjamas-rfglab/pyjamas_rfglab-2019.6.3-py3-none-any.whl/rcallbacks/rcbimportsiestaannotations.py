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

import numpy
import os
from PyQt5 import QtWidgets
import scipy.io

from pyjamas.rcallbacks.rcallback import RCallback


class RCBImportSIESTAAnnotations(RCallback):
    def cbImportSIESTAAnnotations(self, filename='', image_file: str = None):
        # Get file name.
        if filename == '' or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Import SIESTA annotations ...', self.pjs.cwd,
                                                          filter='SIESTA annotations (*.mat)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read annotations.
        try:
            matlabVars = scipy.io.loadmat(filename, struct_as_record=False)
        except (IOError, OSError) as ex:
            print(ex)
            return False

        ud = matlabVars['ud'][0][0]

        fiducials = numpy.transpose(ud.rfiducials, [2, 0, 1])
        polyline_list = numpy.transpose(ud.rpolygons, [2, 0, 1])

        if image_file == '':  # Create a blank image.
            # Find maxx, maxy, and maxz, and create a numpy.ndarray with those dimensions + 1.
            maxz = len(fiducials)
            maxx = 0
            maxy = 0

            # Fiducials and polylines are stored as (x, y) coordinates.
            # numpy.ndarrays are created with (slices, rows, cols).
            for slice_fiducials in fiducials:
                for afiducial in slice_fiducials:
                    maxx = max(maxx, afiducial[0])
                    maxy = max(maxy, afiducial[1])

            for slice_polylines in polyline_list:
                for apolyline in slice_polylines:
                    # For some reason, loadmat puts the polygons within a list.
                    if len(apolyline) == 1:
                        for afiducial in apolyline[0]:
                            if len(afiducial) > 0:
                                maxx = max(maxx, afiducial[0])
                                maxy = max(maxy, afiducial[1])

            virtual_image = numpy.zeros((maxz, int(maxy + 1), int(maxx + 1)), dtype=int)
            self.pjs._cbLoadTS.cbLoadArray(virtual_image)

        elif image_file is not False and image_file is not None:
            self.pjs._cbLoadTS.cbLoadTimeSeries(image_file)

        self.pjs.fiducials = [[] for i in range(self.pjs.n_frames)]

        for slice_fiducials in fiducials:
            for afiducial in slice_fiducials:
                if afiducial[-1] >= 0:
                    self.pjs.addFiducial(int(afiducial[0]), int(afiducial[1]), int(afiducial[2]))

        self.pjs.polylines = [[] for i in range(self.pjs.n_frames)]

        for z, slice_polylines in enumerate(polyline_list):
            for apolyline in slice_polylines:
                # For some reason, loadmat puts the polygons within a list.
                if len(apolyline[0]) > 1:
                    self.pjs.addPolyline(apolyline[0].tolist(), z)

        self.pjs.repaint()

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        return True
