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
import scipy.ndimage.morphology as morphology
from pyjamas.rannotations import *
import PyQt5.QtGui


class RPolyline(rannotation.RAnnotation):
    '''
    Represents a multisegment line (open) or polygon (closed) by providing a list of points (list, tuple, ndarray, etc),
    and a flag to indicate whether the curve is closed (1) or open (1).
    '''
    # Define static variables here.

    def __init__(self, point_list: object, closed_flag: int = 1):
        """
        Creates a polyline (closed_flag = 1) or a trajectory (closed_flag = 0).
        point_list is a list or tuple that will be converted into an ndarray. It can have matching first and last
          points if it is a polyline.

        :param point_list: list, tuple, ndarray, ... Internally, a numpy.ndarray.
        :param closed_flag: bool
        """

        super().__init__()

        # Define object variables here.
        if type(point_list) == PyQt5.QtGui.QPolygonF:
            thepoints = [[apoint.x(), apoint.y()] for _, apoint in enumerate(point_list)]
            self.points = numpy.asarray(thepoints)
            self.closed_flag = 1

        else:
            self.points = numpy.asarray(point_list)  # Points that define the polyline.
            self.closed_flag = closed_flag  # 1 for polyline, 0 for trajectory.

        self._area = -1  # Calculate automatically as the polygon is created?
        self._perimeter = -1  # Calculate automatically as the polygon is created?

        # If polyline, the last point should match the first one.
        if self.closed_flag and (
                (self.points[0, 0] != self.points[-1, 0]) or (self.points[0, 1] != self.points[-1, 1])):
            self.points = numpy.concatenate([self.points, [self.points[0]]])

    def area(self) -> numpy.double:
        """
        Calculate the area of a planar, not self intersecting polygon:
        http://mathworld.wolfram.com/PolygonArea.html.
        Note that the area of a convex polygon is defined to be positive if the points are arranged in a
        counterclockwise order, and negative if they are in clockwise order (Beyer 1987).
        Beyer, W. H. (Ed.). CRC Standard Mathematical Tables, 28th ed. Boca Raton, FL: CRC Press, pp. 123-124, 1987.

        todo: Good candidate for cythonizing.
        :return: double
        """
        if not self.closed_flag:
            raise TypeError("Open polylines do not have an area.")

        area = 0.0

        n = len(self.points)

        for i in range(n - 1):
            area += self.points[i, 0] * self.points[i + 1, 1] - self.points[i + 1, 0] * self.points[i, 1]

        area += self.points[n - 1, 0] * self.points[0, 1] - self.points[0, 0] * self.points[n - 1, 1]

        self._area = abs(area / 2)

        return self._area

    def perimeter(self) -> numpy.double:
        """
        Calculate the perimeter of a polygon.

        todo: Good candidate for cythonizing.
        :return: double
        """

        n = len(self.points)

        shifted_points = numpy.roll(self.points[0:n], 2)
        diff_points = self.points[0:n] - shifted_points

        self._perimeter = numpy.sum(numpy.linalg.norm(diff_points, 2, axis=1))

        return self._perimeter

    def pixel_values(self, image: numpy.ndarray, line_width: numpy.uint8 = 3) -> (numpy.double, numpy.double):
        """
        Calculate the mean pixel value under a polygon and inside the same polygon, and return as a tuple.

        :param image: numpy.ndarray
        :param line_width: brush size used to calculate boundary and interior, numpy.uint8 = 3
        :return: (numpy.double, numpy.double)
        """
        perimeter_intensity = numpy.nan
        interior_intensity = numpy.nan

        # Find points under the annotation and calculate their mean intensity.
        edge_mask, inside_mask = self.tomask(image.shape,
                                             line_width)  # RPolyline.bresenham_wide_line2d(self.points, line_width) # todo: store this coordinates as a class property?

        if edge_mask.size > 0:
            perimeter_intensity = numpy.mean(image[edge_mask[::, 0], edge_mask[::, 1]]) # image is indexed like this: image[(rows), (cols)]

        if inside_mask.size > 0:
            interior_intensity = numpy.mean(image[inside_mask[::, 0], inside_mask[::, 1]])

        return perimeter_intensity, interior_intensity

    @classmethod
    def bresenham_singlepix_line3d(cls, p1: numpy.ndarray, p2: numpy.ndarray, precision: numpy.double = 0.) -> (
    numpy.ndarray, numpy.ndarray, numpy.ndarray):
        """"
        Generate X Y Z coordinates of a 3D Bresenham's line between
        two given points. The line has a width of one pixel.

              Usage: [X Y Z] = bresenham_line3d(p1, p2, precision)

              p1	- vector for Point1, where p1 = [x1 y1 z1]

              p2	- vector for Point2, where p2 = [x2 y2 z2]

              precision (optional) - Although according to Bresenham's line
                algorithm, point coordinates x1 y1 z1 and x2 y2 z2 should
                be integer numbers, this program extends its limit to all
                real numbers. If any of them are floating numbers, you
                should specify how many digits of decimal that you would
                like to preserve. Be aware that the length of output X Y
                Z coordinates will increase in 10 times for each decimal
                digit that you want to preserve. By default, the precision
                is 0, which means that they will be rounded to the nearest
                integer.

              X	- a set of x coordinates on Bresenham's line

              Y	- a set of y coordinates on Bresenham's line

              Z	- a set of z coordinates on Bresenham's line

              Therefore, all points in XYZ set (i.e. P(i) = [X(i) Y(i) Z(i)])
              will constitute the Bresenham's line between p1 and p2.

              Example:
                p1 = [12 37 6]     p2 = [46 3 35]
                [X Y Z] = bresenham_line3d(p1, p2)
                figure plot3(X,Y,Z,'s','markerface','b')

              This program is ported to MATLAB from:

              B.Pendleton.  line3d - 3D Bresenham's (a 3D line drawing algorithm)
              ftp://ftp.isc.org/pub/usenet/comp.sources.unix/volume26/line3d, 1992

              Which is also referenced by:

              Fischer, J., A. del Rio (2004).  A Fast Method for Applying Rigid
              Transformations to Volume Data, WSCG2004 Conference.
              http://wscg.zcu.cz/wscg2004/Papers_2004_Short/M19.pdf

              - Jimmy Shen (jimmy@rotman-baycrest.on.ca)


        :param p1: numpy.ndarray (x1, y1, z1)
        :param p2: numpy.ndarray (x2, y2, z2)
        :param precision: numpy.double=0. Although according to Bresenham's line
                algorithm, point coordinates x1 y1 z1 and x2 y2 z2 should
                be integer numbers, this program extends its limit to all
                real numbers. If any of them are floating numbers, you
                should specify how many digits of decimal that you would
                like to preserve. Be aware that the length of output X Y
                Z coordinates will increase in 10 times for each decimal
                digit that you want to preserve. By default, the precision
                is 0, which means that they will be rounded to the nearest
                integer.
        :return: (numpy.ndarray, numpy.ndarray. numpy.ndarray), X, Y, and Z coordinates, respectively, of the points
                in the Bresenham line.

        """

        if numpy.round(precision) == 0:
            precision = 0.
            p1 = numpy.round(p1)
            p2 = numpy.round(p2)

        else:
            precision = numpy.round(precision)
            p1 = numpy.round(p1 * (10 ^ precision))
            p2 = numpy.round(p2 * (10 ^ precision))

        d = numpy.int16(numpy.max(numpy.abs(p2 - p1) + 1))
        X = numpy.zeros(d)
        Y = numpy.zeros(d)
        Z = numpy.zeros(d)

        x1 = p1[0]
        y1 = p1[1]
        z1 = p1[2]

        x2 = p2[0]
        y2 = p2[1]
        z2 = p2[2]

        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        ax = numpy.abs(dx) * 2
        ay = numpy.abs(dy) * 2
        az = numpy.abs(dz) * 2

        sx = numpy.sign(dx)
        sy = numpy.sign(dy)
        sz = numpy.sign(dz)

        x = x1
        y = y1
        z = z1
        idx = 0

        if ax >= numpy.maximum(ay, az):  # x dominant
            yd = ay - ax / 2
            zd = az - ax / 2

            while True:
                X[idx] = x
                Y[idx] = y
                Z[idx] = z
                idx += 1

                if x == x2:
                    break

                if yd >= 0:  # move along y
                    y += sy
                    yd -= ax

                if zd >= 0:  # move along z
                    z += sz
                    zd -= ax

                x += sx  # move along x
                yd += ay
                zd += az

        elif ay >= numpy.maximum(ax, az):  # y dominant
            xd = ax - ay / 2
            zd = az - ay / 2

            while True:
                X[idx] = x
                Y[idx] = y
                Z[idx] = z
                idx += 1

                if y == y2:
                    break

                if xd >= 0:  # move along x
                    x += sx
                    xd -= ay

                if zd >= 0:  # move along z
                    z += sz
                    zd -= ay

                y += sy  # move along y
                xd += ax
                zd += az

        elif az >= numpy.maximum(ax, ay):  # z dominant
            xd = ax - az / 2
            yd = ay - az / 2

            while True:
                X[idx] = x
                Y[idx] = y
                Z[idx] = z
                idx += 1

                if z == z2:
                    break

                if xd >= 0:  # move along x
                    x += sx
                    xd -= az

                if yd >= 0:  # move along y
                    y += sy
                    yd -= az

                z += sz  # move along z
                xd += ax
                yd += ay

        if precision != 0:
            X = X / numpy.power(10, precision)
            Y = Y / numpy.power(10, precision)
            Z = Z / numpy.power(10, precision)

        return X, Y, Z

    @classmethod
    def bresenham_wide_line2d(cls, p1: numpy.ndarray, p2: numpy.ndarray, width: numpy.uint = 0) -> (
    numpy.ndarray, numpy.ndarray):
        """
        Generate (x, y) coordinates of a 2D Bresenham line of arbitrary width.

        :param p1: (x, y) coordinates of source point.
        :param p2: (x, y) coordinates of destination point.
        :param width: line width (in pixels).
        :return: (numpy.ndarray, numpy.ndarray), first output array are x coordinates, second are y coordinates.
        """

        x1 = p1[0]
        x2 = p2[0]
        y1 = p1[1]
        y2 = p2[1]

        hw = numpy.int(numpy.floor(width / 2.))

        dx = numpy.abs(x2 - x1)
        dy = numpy.abs(y2 - y1)

        x = numpy.asarray([])
        y = numpy.asarray([])

        if dx > dy:
            for ii in range(-hw, hw + 1):
                y1new = y1 + ii
                y2new = y2 + ii
                tmpx, tmpy, _ = numpy.int16(cls.bresenham_singlepix_line3d(numpy.asarray([x1, y1new, 0]),
                                                               numpy.asarray([x2, y2new, 0])))
                x = numpy.append(x, tmpx)
                y = numpy.append(y, tmpy)
        else:
            for ii in range(-hw, hw + 1):
                x1new = x1 + ii
                x2new = x2 + ii
                tmpx, tmpy, _ = numpy.int16(cls.bresenham_singlepix_line3d(numpy.asarray([x1new, y1, 0]),
                                                               numpy.asarray([x2new, y2, 0])))
                x = numpy.append(x, tmpx)
                y = numpy.append(y, tmpy)

        # print(x, y)

        return x, y

    def tomask(self, imshape: numpy.ndarray, brushsz: numpy.uint8) -> (numpy.ndarray, numpy.ndarray):
        '''
        Convert polygon to a mask and return the coordinates of the pixels under the polygon and inside the polygon.

        Note that numpy.ndarrays are indexed (and shaped) by (row, column), starting at (0,0).
        However, PyJAMAS stores point coordinates as (x, y) (equivalent to (col, row)) starting at (0, 0).
        :param imshape: (rows, cols)
        :param brushsz: line width.
        :return: numpy.ndarray (x, y), numpy.ndarray (x, y) coordinates of perimeter pixels and interior pixels.
        '''
        binary_image = numpy.zeros(imshape, dtype=bool)

        x = numpy.asarray([])
        y = numpy.asarray([])

        # Find the coordinates of the points under the polyline.
        for ii in range(len(self.points)-1):
            thex, they = self.bresenham_wide_line2d(self.points[ii], self.points[ii + 1], brushsz)

            # Avoid repeating the start points by not including the first point of each segments.
            x = numpy.append(x, thex)
            y = numpy.append(y, they)

        # Get rid of any pixels not on the image.
        ind_good = numpy.nonzero((x >= 0) & (x < imshape[1]) & (y >= 0) & (y < imshape[0]))
        x = x[ind_good]
        y = y[ind_good]

        # Those points form an edge mask (we remove repeated points) after inverting coordinates
        # to go from (x, y) to (row, col).
        themask_perimeter = numpy.unique((y, x), axis=1)

        # Set all the pixels under the polyline to True in the mask.
        perimeter_pixel_indices = [(numpy.int(x), numpy.int(y)) for x, y in zip(themask_perimeter[0], themask_perimeter[1])]
        perimeter_pixel_indices = numpy.asarray(perimeter_pixel_indices)
        binary_image[perimeter_pixel_indices[:, 0], perimeter_pixel_indices[:, 1]] = True

        # The internal mask is the difference between a solid fill of the polyline and the polyline.
        binary_image2 = morphology.binary_fill_holes(binary_image) ^ binary_image
        themask_inside = binary_image2.nonzero()

        inside_pixel_indices = [(numpy.int(x), numpy.int(y)) for x, y in zip(themask_inside[0], themask_inside[1])]
        inside_pixel_indices = numpy.asarray(inside_pixel_indices)

        return perimeter_pixel_indices, inside_pixel_indices
