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
from .rcallback import RCallback
from PyQt5 import QtWidgets
import os
import scipy.io


class RCBExportSIESTAAnnotations(RCallback):
    def cbExportSIESTAAnnotations(self, filename=''):
        """
        See https://www.mathworks.com/help/matlab/matlab_external/handling-data-returned-from-python.html
        for details.

        Something important here is to send float arrays to Matlab, otherwise there are errors when
        SIESTA tries to conduct certain operations on the arrays.

        :param filename:
        :return:
        """
        fname = ''

        # Get file name.
        if filename == '' or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            defaultname, _ = os.path.splitext(os.path.basename(self.pjs.filename))

            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Export SIESTA annotations ...',
                                                          self.pjs.cwd + os.sep + defaultname,
                                                          filter='SIESTA annotations (*.mat)')  # fname[0] is the full filename, fname[1] is the filter used.
            # If cancel ...
            if fname == '':
                return False

            # else ...
            else:
                filename = fname[0]

                # Find max number of fiducials and polygons in any frame.
                rnfiducials = numpy.zeros(self.pjs.n_frames, dtype=numpy.float)
                max_n_polylines = 0
                for iSlice, thefiducials in enumerate(self.pjs.fiducials):
                    rnfiducials[iSlice] = len(thefiducials)
                    if len(self.pjs.polylines[iSlice]) > max_n_polylines:
                        max_n_polylines = len(self.pjs.polylines[iSlice])

                # Create the fiducial array to send to Matlab.
                max_n_fiducials = numpy.amax(rnfiducials)
                rfiducials = -1. * numpy.ones([numpy.int(max_n_fiducials), 3, self.pjs.n_frames], dtype=numpy.float)

                # rpolylines is a list, which in Matlab is a cell.
                # The right dimensions are (max_n_fiducials, 1, self.pjs.n_frames)
                # Need to add the singlet second dimensions. The order of the square brackets is critical here.
                rpolylines = [[[[] for iSlice in range(self.pjs.n_frames)]] for iPol in range(max_n_polylines)]

                for iSlice, thefiducials in enumerate(self.pjs.fiducials):
                    if thefiducials:
                        thefiducials_array = numpy.asarray(thefiducials, dtype=numpy.float)
                        rfiducials[0:thefiducials_array.shape[0], 0:2, iSlice] = thefiducials_array
                        rfiducials[0:thefiducials_array.shape[0], 2, iSlice] = numpy.float(iSlice)

                    thepolylines = self.pjs.polylines[iSlice]

                    if thepolylines:
                        for iPoly, thePoly in enumerate(thepolylines):
                            theintpoly = [[numpy.float(pnt.x()), numpy.float(pnt.y())] for pnt in thePoly]

                            if theintpoly != []:
                                theintpoly.append(theintpoly[0])

                            rpolylines[iPoly][0][iSlice] = theintpoly

                imsize = [numpy.float(self.pjs.width), numpy.float(self.pjs.height), numpy.float(self.pjs.n_frames)]

                # Build dictionary with the variables. Dictionaries are converted to structs
                ud = {}
                ud['rfiducials'] = rfiducials
                ud['rpolygons'] = rpolylines
                ud['rnfiducials'] = rnfiducials
                ud['imsize'] = imsize

                # Open file name and save annotations.
                try:
                    scipy.io.savemat(filename, {'ud': ud}, appendmat=True)
                except (IOError, OSError) as ex:
                    print(ex)
                    return False

        # Modify current path.
        self.pjs.cwd = os.path.dirname(filename)

        return True
