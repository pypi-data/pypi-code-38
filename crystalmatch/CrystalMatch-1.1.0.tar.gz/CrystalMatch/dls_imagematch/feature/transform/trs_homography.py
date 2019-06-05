import cv2
import numpy as np

from CrystalMatch.dls_util.imaging import Image
from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_imagematch.feature.transform.transformation import Transformation


class HomographyTransformation(Transformation):
    def __init__(self, homography_matrix):
        Transformation.__init__(self)

        self._homography = homography_matrix
        self._homography_inverse = None

        _, inv = cv2.invert(self._homography)
        self._homography_inverse = inv

    def transform_image(self, image, output_size):
        warped = cv2.warpPerspective(image.raw(), self._homography, output_size)
        warped = Image(warped)
        return warped

    def inverse_transform_image(self, image, output_size):
        warped = cv2.warpPerspective(image.raw(), self._homography_inverse, output_size)
        warped = Image(warped)
        return warped

    def transform_points(self, points):
        np_array = self._points_to_np_array(points)
        transformed = cv2.perspectiveTransform(np_array, self._homography)
        transformed = self._np_array_to_points(transformed)
        return transformed

    def inverse_transform_points(self, points):
        np_array = self._points_to_np_array(points)
        transformed = cv2.perspectiveTransform(np_array, self._homography_inverse)
        transformed = self._np_array_to_points(transformed)
        return transformed

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
