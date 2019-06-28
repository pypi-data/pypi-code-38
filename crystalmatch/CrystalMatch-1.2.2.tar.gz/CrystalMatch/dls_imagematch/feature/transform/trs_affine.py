import cv2
import numpy as np

from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_imagematch.feature.transform.transformation import Transformation


class AffineTransformation(Transformation):
    def __init__(self, affine_matrix):
        Transformation.__init__(self)
        self._affine_matrix = affine_matrix

    def transform_points(self, points):
        np_array = self._points_to_np_array(points)
        transformed = cv2.perspectiveTransform(np_array, self._affine_matrix)
        transformed = self._np_array_to_points(transformed)
        return transformed

    def transform_image(self, image, output_size):
        raise NotImplementedError()

    @staticmethod
    def _points_to_np_array(points):
        points_list = [[p.x, p.y] for p in points]
        np_array = np.float32(points_list).reshape(-1, 1, 2)
        return np_array

    @staticmethod
    def _np_array_to_points(np_array):
        points = []
        for p in np_array:
            points.append(Point(p[0][0], p[0][1]))
        return points
