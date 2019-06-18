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

import csv
import gzip
from itertools import chain
import os.path
import pickle
import re
from typing import Iterable, List

import numpy
from PyQt5 import QtGui, QtWidgets
from scipy.spatial import ConvexHull, Delaunay
from scipy.spatial.distance import cdist

import shapely.geometry


class RUtils:
    @classmethod
    def qpolygonf2polygon(cls, aqpolygonf: QtGui.QPolygonF) -> shapely.geometry.Polygon:
        if aqpolygonf is False or type(aqpolygonf) != QtGui.QPolygonF:
            return shapely.geometry.Polygon(None)

        qpointf_list = list(aqpolygonf)

        point_list = [[qpointf.x(), qpointf.y()] for qpointf in qpointf_list]

        return shapely.geometry.Polygon(point_list)

    @classmethod
    def qpolygonf2list(cls, aqpolygonf: QtGui.QPolygonF) -> list:
        if aqpolygonf is False or type(aqpolygonf) != QtGui.QPolygonF:
            return list(None)

        qpointf_list = list(aqpolygonf)

        point_list = [[qpointf.x(), qpointf.y()] for qpointf in qpointf_list]

        return point_list

    @classmethod
    def qpolygonf2ndarray(cls, aqpolygonf: QtGui.QPolygonF) -> numpy.ndarray:
        return numpy.asarray(RUtils.qpolygonf2list(aqpolygonf))

    @classmethod
    def isperipheralpoint(cls, point_array: numpy.ndarray, index: int, concave_hull: bool = False,
                          alpha: float = -1.) -> bool:

        """
        Checks if a point is in the convex hull of a point array.
        (aka alpha shape - https://plot.ly/python/alpha-shapes/)
        :param point_array:
        :param index:
        :param concave_hull:
        :param alpha:
        :return:
        """

        if index < 0 or index >= len(point_array):
            return False

        if concave_hull:
            hull = cls.concave_hull(point_array, alpha)

        else:
            hull = ConvexHull(point_array)

        return index in hull.vertices

    @classmethod
    def circumcircle(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> ((numpy.float, numpy.float), numpy.float):
        """
        A circle which passes through all three vertices of a triangle. Also "Circumscribed circle".
        Blatantly stolen from plotly: https://plot.ly/python/alpha-shapes/


        This function returns exactly the same radius value as the circumcircle, with a tiny bit less precision,
        but this one is one order of magnitude slower (100 us vs 10 us).

        :param points: a numpy.ndarray of points
        :param simplex: three indexes into the points array for the three vertices of a triangle
        :return: the center and the radius of the circumcircle for the triangle defined by simplex
        """
        A = [points[simplex[k]] for k in range(3)]  # [pnt1, pnt2, pnt3] of a triangle
        M = [[1.0] * 4]  # [[1.0, 1.0, 1.0, 1.0]]
        M += [[cls.squared_norm(A[k]), A[k][0], A[k][1], 1.0] for k in range(
            3)]  # [[1.0, 1.0, 1.0, 1.0], [norm2_pnt1, pnt1_x, pnt1_y, 1.0], [norm2_pnt2, pnt2_x, pnt2_y, 1.0], [norm2_pnt3, pnt3_x, pnt3_y, 1.0]]
        M = numpy.asarray(M, dtype=numpy.float32)
        S = numpy.array([0.5 * numpy.linalg.det(M[1:, [0, 2, 3]]), -0.5 * numpy.linalg.det(M[1:, [0, 1, 3]])])
        a = numpy.linalg.det(M[1:, 1:])
        b = numpy.linalg.det(M[1:, [0, 1, 2]])
        return S / a, numpy.sqrt(
            b / a + cls.squared_norm(S) / a ** 2)  # center=S/a, radius=numpy.sqrt(b/a+sq_norm(S)/a**2)

    @classmethod
    def circumcircle_radius(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> float:
        """
        Radius of the circumcircle for the triangle defined by the 3 points indexed by the elements in simplex.
        Stolen from https://stackoverflow.com/questions/23073170/calculate-bounding-polygon-of-alpha-shape-from-the-delaunay-triangulation/23073229#comment35336369_23073229

        See also www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle

        This function returns exactly the same value as the circumcircle, with a tiny bit more precision, but this
        one is one order of magnitude faster (10 us vs 100 us).

        :param points: a numpy.ndarray of points
        :param simplex: three indexes into the points array for the three vertices of a triangle
        :return: the center of the circumcircle for the triangle defined by simplex
        """
        pa: numpy.ndarray = points[simplex[0]]
        pb: numpy.ndarray = points[simplex[1]]
        pc: numpy.ndarray = points[simplex[2]]

        a: float = numpy.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b: float = numpy.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c: float = numpy.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s: float = (a + b + c) / 2.0
        area: float = numpy.sqrt(s * (s - a) * (s - b) * (s - c))

        return a * b * c / (4.0 * area)

    @classmethod
    def squared_norm(cls, v):  # squared norm
        return numpy.linalg.norm(v) ** 2

    @classmethod
    def concave_hull(cls, point_array: numpy.ndarray, alpha: float) -> numpy.ndarray:
        """
        Returns points in the concave hull (with no particular order).

        :param point_array:
        :param alpha:
        :return:
        """

        delaunay_triang = Delaunay(point_array)
        simplices = delaunay_triang.simplices  # indices of the points forming the triangles.

        hull_edges = list()

        for thetriangle in simplices:
            radius_circumcircle = cls.circumcircle_radius(point_array, thetriangle)

            if radius_circumcircle < alpha:
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[0], thetriangle[1])
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[1], thetriangle[2])
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[2], thetriangle[0])

        return numpy.asarray(numpy.unique(hull_edges))

    @staticmethod
    def __add_edge_to_concave_hull__(hull_edges: list, idx1: int, idx2: int) -> bool:
        # If we are adding an edge for the second time, that means that it belongs to two triangles, and in that
        # case it does not belong to the hull. Remove it.
        if [idx1, idx2] in hull_edges:
            hull_edges.remove([idx1, idx2])
        elif [idx2, idx1] in hull_edges:
            hull_edges.remove([idx2, idx1])

        # Otherwise, add the edge to the hull.
        else:
            hull_edges.append([idx1, idx2])

        return True

    @staticmethod
    def __parse_range__(r: str) -> Iterable[int]:
        """
        Finds positive integers before and after a hyphen.
        :param r: a string with one hyphen in (e.g. '15-18')
        :return: iterable going from first to last in the string (inclusive).
        """
        if len(r) == 0:
            return []

        parts = r.split("-")
        if len(parts) > 2:
            raise ValueError("Invalid range: {}".format(r))
        return range(int(parts[0]), int(parts[-1]) + 1)

    @classmethod
    def parse_range_list(cls, rl: str) -> List[int]:
        """
        Splits the input chain in comma-separated segments.
        Runs __parse_range__ on each segment.
        Returns a sorted list with all the ranges.

        :param rl: a range-string (e.g.: '0, 2, 4-10, 15').
        :return: a list of sorted indices.
        """
        return sorted(set(chain.from_iterable(map(cls.__parse_range__, rl.split(",")))))

    @classmethod
    def natural_sort(cls, s):
        nsre = re.compile('([0-9]+)')
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(nsre, s)]

    @classmethod
    def point2point_distances(cls, points_orig: numpy.ndarray, points_dest: numpy.ndarray) -> numpy.ndarray:
        return cdist(points_orig, points_dest, 'euclidean')

    @classmethod
    def open_folder_dialog(cls, title: str, starting_folder: str) -> str:
        return QtWidgets.QFileDialog.getExistingDirectory(None, title, starting_folder)

    @classmethod
    def write_dict_csv(cls, filename: str = None, adictionary: dict = None) -> bool:
        """
        DELETE THIS METHOD?
        :param filename:
        :param adictionary:
        :return:
        """
        if filename == '' or filename is None or filename is False or adictionary is None or adictionary is False:
            return False

        # Make sure file extension is .csv.
        thefile, extension = os.path.splitext(filename)
        if extension != '.csv':
            filename = thefile + '.csv'

        with open(filename, "w") as fh:
            writer = csv.writer(fh)

            for akey, avalue in adictionary.items():
                writer.writerow([akey])  # Putting a string in a list is the way to write the entire string into a single cell. Otherwise, each character in the string is written in a different cell.

                if type(avalue) == list:
                    writer.writerow(avalue)
                else:
                    writer.writerow([avalue])
        return True

    @classmethod
    def read_csv_dict(cls, filename: str = None) -> dict:
        """
        DELETE THIS METHOD?
        :param filename:
        :return:
        """
        if filename == '' or filename is None or filename is False:
            return None

        if not os.path.exists(filename):
            return None

        thedict: dict = {}

        with open(filename, "r") as fh:
            reader = csv.reader(fh)

            for akey in reader:
                avalue = next(reader)
                thedict[akey] = [avalue]

        print(thedict)

        return thedict

    @classmethod
    def set_extension(cls, filename: str, extension: str) -> str:
        """
        Generates a string based on filename that concludes in the desired extension.
        If the filename string already had an extension, it will be substituted with
        the provided one.

        :param filename:
        :param extension:
        :return:
        """
        # Make sure file extension is extension.
        thefile, old_ext = os.path.splitext(filename)
        if old_ext != extension:
            return thefile + extension
        else:
            return filename

    @classmethod
    def pickle_this(cls, an_object: object, filename: str) -> bool:
        """
        Saves a python object into a file after zipping.
        Sample use: saving scikit-learn classifiers after they have been trained.

        :param an_object: object to zip and pickle.
        :param filename: include the desired extension!
        :return:
        """
        fh = None

        try:
            fh = gzip.open(filename, "wb")
            pickle.dump(an_object, fh, pickle.HIGHEST_PROTOCOL)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        return True

    @classmethod
    def pjsfiducials_to_array(cls, fiducials: List) -> numpy.ndarray:
        """
        Converts a list of fiducials from PyJAMAS (a sparse list) into a numpy.ndarray with a constant
        number of elements.

        Empty space in the array is filled with -1 (if we used nans, the array
        would be of type float and take up a lot more space; this is because ndarrays can only
        contain one data type and type(numpy.nan) returns float).

        :param fiducials:
        :return:
        """
        # Find dimension with the most elements.
        n_fiducials_per_slice = [len(a_slice) for a_slice in fiducials]
        max_n_fiducials: int = max(n_fiducials_per_slice)
        n_slices = len(fiducials)


        coordinates: numpy.ndarray = numpy.full((n_slices, max_n_fiducials, 2), -1, dtype=int)

        for a_slice in range(n_slices):
            if n_fiducials_per_slice[a_slice] > 0:
                coordinates[a_slice, 0:n_fiducials_per_slice[a_slice], :] = fiducials[a_slice]

        return coordinates
