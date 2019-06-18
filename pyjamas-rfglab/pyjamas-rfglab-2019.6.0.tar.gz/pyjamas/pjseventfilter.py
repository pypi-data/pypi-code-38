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
from PyQt5 import QtCore, QtWidgets

from pyjamas.pjscore import PyJAMAS
import pyjamas.rimage as rimage


class PJSEventFilter(QtCore.QObject):
    def __init__(self, ui):
        """

        :type ui: PyJAMAS
        """
        super().__init__()

        self.pjs: PyJAMAS = ui
        self.x_prev: int = -1
        self.y_prev: int = -1
        self.x: int = -1
        self.y: int = -1

    def eventFilter(self, source, event: QtCore.QEvent):
        # Event coordinates.
        if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
            thepoint = self.pjs.gView.mapToScene(event.x(), event.y())

            self.x, self.y = (int(numpy.round(thepoint.x())), int(numpy.round(thepoint.y())))

            # Check for boundaries.
            if self.x < 0:
                self.x = 0
            elif self.x >= self.pjs.width:
                self.x = self.pjs.width - 1

            if self.y < 0:
                self.y = 0
            elif self.y >= self.pjs.height:
                self.y = self.pjs.height - 1

        # Mouse click: display pixel coordinates and value.
        if event.type() == QtCore.QEvent.MouseMove:
            if 0 <= self.x < self.pjs.width and 0 <= self.y < self.pjs.height:
                self.pjs.statusbar.showMessage(
                    str(self.pjs.curslice + 1) + '/' + str(self.pjs.n_frames) + '\t(' + str(self.x) + ', ' + str(
                        self.y) + '): ' + str(self.pjs.imagedata[self.y, self.x]))

        # Fiducials: add and remove.
        if self.pjs.annotation_mode == PyJAMAS.fiducials and event.type() == QtCore.QEvent.MouseButtonPress:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.pjs.addFiducial(self.x, self.y, self.pjs.curslice)

            elif event.buttons() == QtCore.Qt.RightButton:
                self.pjs.removeFiducial(self.x, self.y, self.pjs.curslice)

        # Rectangles.
        elif self.pjs.annotation_mode == PyJAMAS.rectangles:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                # Store first coordinate if left click ...
                if event.buttons() == QtCore.Qt.LeftButton:
                    self.pjs._poly_ = [self.x, self.y]

                # ... or delete polygon if right click.
                elif event.buttons() == QtCore.Qt.RightButton:
                    self.pjs.removePolyline(self.x, self.y,
                                            self.pjs.curslice)  # CAN WE JUST HAVE ONE removeAnnotationItem function?

            # Redraw rectangle as the user drags the cursor.
            elif event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton:  # Mouse move events will occur only when a mouse button is pressed down, unless mouse tracking has been enabled with QWidget.setMouseTracking()
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                self.pjs._agraphicsitem_ = self.pjs.drawRectangle(self.pjs._poly_[0], self.pjs._poly_[1], self.x, self.y)
                self.pjs.statusbar.showMessage(
                    '{0}/{1}\t({2}, {3}) -> w: {4}, h: {5}'.format(str(self.pjs.curslice + 1),
                                                                                       str(self.pjs.n_frames), str(
                            self.pjs._poly_[0]), str(
                            self.pjs._poly_[1]), str(abs(self.pjs._poly_[0] - self.x)+1), str(abs(self.pjs._poly_[1] - self.y)+1)))

            # Add rectangle as mouse button is released.
            elif event.type() == QtCore.QEvent.MouseButtonRelease and self.pjs._poly_ != []:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                x0 = self.pjs._poly_[0]
                y0 = self.pjs._poly_[1]
                x1 = self.x
                y1 = self.y

                if x0 > x1:
                    dummy = x1
                    x1 = x0
                    x0 = dummy

                if y0 > y1:
                    dummy = y1
                    y1 = y0
                    y0 = dummy

                self.pjs.addPolyline([[x0, y0], [x0, y1], [x1, y1], [x1, y0]], self.pjs.curslice)
                self.pjs._poly_ = []

        # Polylines.
        elif self.pjs.annotation_mode == PyJAMAS.polylines:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                # Store coordinate if left click ...
                if event.buttons() == QtCore.Qt.LeftButton:
                    self.pjs._poly_.append([self.x, self.y])

                    if self.pjs._agraphicsitem_:
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)

                # Delete last point if middle click
                elif event.buttons() == QtCore.Qt.MiddleButton and self.pjs._poly_ is not []:
                    self.pjs._poly_ = self.pjs._poly_[0:-1]
                    if self.pjs._agraphicsitem_:
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        apoly = self.pjs._poly_.copy()
                        apoly.append([self.x, self.y])

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                # ... or delete polygon if right click.
                elif event.buttons() == QtCore.Qt.RightButton:
                    self.pjs.removePolyline(self.x, self.y, self.pjs.curslice)

            # Redraw polyline as the user moves the cursor.
            elif event.type() == QtCore.QEvent.MouseMove and self.pjs._poly_ != []:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    apoly = self.pjs._poly_.copy()
                    apoly.append([self.x, self.y])

                    self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)

            # Add polyline as mouse button is released.
            elif event.type() == QtCore.QEvent.MouseButtonDblClick and self.pjs._poly_ != []:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                self.pjs.addPolyline(self.pjs._poly_, self.pjs.curslice)
                self.pjs._poly_ = []

        # Delete fiducials outside polyline.
        elif self.pjs.annotation_mode == PyJAMAS.delete_fiducials_outside_polyline:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.pjs.find_clicked_polyline(self.x, self.y)
                if index >= 0:
                    # Delete every annotation outside.
                    self.pjs.removeFiducialsPolyline(self.pjs._poly_, False)
                else:
                    return None

        # Delete fiducials inside polyline.
        elif self.pjs.annotation_mode == PyJAMAS.delete_fiducials_inside_polyline:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.pjs.find_clicked_polyline(self.x, self.y)
                if index >= 0:
                    # Delete every annotation outside.
                    self.pjs.removeFiducialsPolyline(self.pjs._poly_, True)
                else:
                    return None

        # Copy polyline.
        elif self.pjs.annotation_mode == PyJAMAS.copy_polyline:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.pjs.find_clicked_polyline(self.x, self.y)

                # Not using self.pjs._poly_ here, as other operations on the UI will overwrite it.
                self.pjs._copied_poly_ = self.pjs.polylines[self.pjs.curslice][index]

                if index < 0:
                    return None

        # LiveWire.
        elif self.pjs.annotation_mode == PyJAMAS.livewire:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                # Store coordinate if left click ...
                if event.buttons() == QtCore.Qt.LeftButton:
                    if self.pjs._poly_ != []:
                        thesource = self.pjs._poly_[-1]
                        thedest = [self.x, self.y]
                        thepoints = rimage.rimcore.rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                                       PyJAMAS.livewire_margin)  # Make livewire a static method?
                        self.pjs._poly_.extend(
                            thepoints)  ### CHANGE: STORE ALL COORDINATES GENERATED BY LIVEWIRE FROM LAST CLICKED POINT

                        if self.pjs._agraphicsitem_:
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)

                    else:
                        self.pjs._poly_.append([self.x, self.y])
                        if self.pjs._agraphicsitem_:
                            self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(self.pjs._poly_)
                # Delete last point if middle click # NOT DONE YET.
                elif event.buttons() == QtCore.Qt.MiddleButton and self.pjs._poly_ is not []:
                    self.pjs._poly_ = self.pjs._poly_[0:-1]
                    if self.pjs._agraphicsitem_:
                        self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                        apoly = self.pjs._poly_.copy()
                        apoly.append([self.x, self.y])

                        self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                # ... or delete polygon if right click.
                elif event.buttons() == QtCore.Qt.RightButton:
                    self.pjs.removePolyline(self.x, self.y, self.pjs.curslice)

            # Redraw polyline as the user moves the cursor.
            elif event.type() == QtCore.QEvent.MouseMove and self.pjs._poly_ != []:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    apoly = self.pjs._poly_.copy()
                    thesource = apoly.copy()[-1]
                    thedest = [self.x, self.y]
                    thepoints = rimage.rimcore.rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                                   PyJAMAS.livewire_margin)  # Make livewire a static method? Or make self.imagedata an RImage?
                    apoly.extend(
                        thepoints)  ### CHANGE: STORE ALL COORDINATES GENERATED BY LIVEWIRE FROM LAST CLICKED POINT

                    self.pjs._agraphicsitem_, _ = self.pjs.drawPath(apoly)
                    # self.statusbar.showMessage(str(self.curslice + 1) + '/' + str(self.n_frames) + '\t(' + str(self._poly_[0]) + ', ' + str(
                    # self._poly_[1]) + ') -> w: ' + str(abs(self._poly_[0] - self.x)) + ', h: ' + str(abs(self._poly_[1] - self.y)))

            # Add polyline as mouse button is released.
            elif event.type() == QtCore.QEvent.MouseButtonDblClick and self.pjs._poly_ != []:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                thesource = self.pjs._poly_[-1]
                thedest = self.pjs._poly_[0]
                thepoints = rimage.rimcore.rimage(self.pjs.imagedata).livewire(thesource, thedest,
                                                                               PyJAMAS.livewire_margin)  # Make livewire a static method? Or make self.imagedata an RImage?
                self.pjs._poly_.extend(thepoints)
                self.pjs.addPolyline(self.pjs._poly_, self.pjs.curslice)
                self.pjs._poly_ = []

        # Move polylines.
        elif self.pjs.annotation_mode == PyJAMAS.move_polyline:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.pjs.find_clicked_polyline(self.x, self.y)

                if index < 0:
                    return None

            # Redraw polyline as the user moves the cursor.
            elif event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.LeftButton and self.x_prev > -1 and self.y_prev > -1:
                if self.pjs._agraphicsitem_:
                    self.pjs.gScene.removeItem(self.pjs._agraphicsitem_)

                    theshift = QtCore.QPointF(self.x - self.x_prev, self.y - self.y_prev)

                    for i in range(self.pjs._poly_.size()):
                        self.pjs._poly_[i] += theshift

                    # Make sure you stay within the image: first find bounding box.
                    theboundingrect = self.pjs._poly_.boundingRect()

                    thex = theboundingrect.x()
                    they = theboundingrect.y()
                    themaxx = thex + theboundingrect.width()
                    themaxy = they + theboundingrect.height()

                    # Make sure the bounding box is within the image. If not, ...
                    if thex < 0 or they < 0 or themaxx >= self.pjs.width or themaxy >= self.pjs.height:
                        theshift = QtCore.QPointF(0, 0)

                        # Shift the X and/or Y coordinates accordingly.
                        if thex < 0:
                            theshift.setX(theshift.x() - thex)
                        if themaxx >= self.pjs.width:
                            theshift.setX(theshift.x() - (themaxx - self.pjs.width + 1))
                        if they < 0:
                            theshift.setY(theshift.y() - they)
                        if themaxy >= self.pjs.height:
                            theshift.setY(theshift.y() - (themaxy - self.pjs.height + 1))

                        # This is the shift happening!
                        for i in range(self.pjs._poly_.size()):
                            self.pjs._poly_[i] += theshift

                    self.pjs._agraphicsitem_ = self.pjs.drawPolyline(self.pjs._poly_)
                    self.pjs.repaint()

            # Update polyline as mouse button is released.
            elif event.type() == QtCore.QEvent.MouseButtonRelease and self.pjs._poly_ != []:
                self.pjs._poly_ = []

        # Export polylines associated with a fiducial.
        elif self.pjs.annotation_mode == PyJAMAS.export_fiducial_polyline:
            self.process_export_fiducial_polyline(event)

        elif event.type() == QtCore.QEvent.Resize:
            self.pjs.timeSlider.setGeometry(
                QtCore.QRect(0, self.pjs.MainWindow.height() - 43, self.pjs.MainWindow.width(), 22))

        # Store current position as previous (for mouse tracking).
        if event.type() in (QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonRelease):
            self.x_prev = self.x
            self.y_prev = self.y

        return QtCore.QObject.eventFilter(self.pjs, source, event)

    def process_export_fiducial_polyline(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            theClickedItem = self.pjs.findGraphicItem(self.x, self.y, QtWidgets.QGraphicsEllipseItem)

            # If you found an ellipse:
            if type(theClickedItem) == QtWidgets.QGraphicsEllipseItem:
                # Get coordinates.
                pos = theClickedItem.scenePos()
                fiducial_coords = [int(pos.x() + PyJAMAS.fiducial_radius / 2),
                                   int(pos.y() + PyJAMAS.fiducial_radius / 2)]

                self.pjs._cbExportPolylineAnn.export_polyline_annotations(fiducial_coords[0], fiducial_coords[1])
        return True
