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

from .rcallback import RCallback
from PyQt5 import QtWidgets
from pyjamas.external import pascal_voc_io
import os


class RCBSaveAnnotationsXML(RCallback):
    def cbSaveAnnotationsXML(self, filename=''):  # Handle IO errors.
        # Get file name.
        fname = ''

        if filename == '' or filename is False:  # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            defaultname, _ = os.path.splitext(os.path.basename(self.pjs.filename))
            fname = QtWidgets.QFileDialog.getSaveFileName(None, 'Save annotations ...',
                                                          self.pjs.cwd + os.sep + defaultname,
                                                          filter='XML file (*' + pascal_voc_io.XML_EXT + ')')  # fname[0] is the full filename, fname[1] is the filter used.

        # If cancel ...
        if fname == '':
            return False

        # else ...
        else:
            filename = fname[0]
            self.pjs.cwd = os.path.dirname(filename)

        if filename[-4:] != pascal_voc_io.XML_EXT:
            filename = filename + pascal_voc_io.XML_EXT

        writer = pascal_voc_io.PascalVocWriter(os.path.split(self.pjs.cwd)[1], os.path.basename(self.pjs.filename),
                                               [self.pjs.height, self.pjs.width, 1], localImgPath=self.pjs.filename)
        writer.verified = False

        theframepolylines = self.pjs.polylines[self.pjs.curslice]
        for ipoly, thepolyline in enumerate(theframepolylines):
            points = []

            for ipnt, thepoint in enumerate(thepolyline):
                points.append([thepoint.x(), thepoint.y()])

            label = 'cell'
            difficult = 0
            bndbox = RCBSaveAnnotationsXML.convertPoints2BndBox(points)

            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, difficult)

        writer.save(targetFile=filename)

        return True

    @staticmethod
    def convertPoints2BndBox(points):
        '''
        Copied from the LabelFile class in labelImg.
        :param points: list of points
        :return: tuple containing the bounding box for the list of points with this
                format (int(xmin), int(ymin), int(xmax), int(ymax)).
        '''

        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if xmin < 1:
            xmin = 1

        if ymin < 1:
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))
