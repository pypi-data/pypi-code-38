from __future__ import division

import logging

import cv2
import numpy as np

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_imagematch.feature.transform.exception import TransformCalculationError
from CrystalMatch.dls_imagematch.feature.transform.trs_affine import AffineTransformation
from CrystalMatch.dls_imagematch.feature.transform.trs_homography import HomographyTransformation
from CrystalMatch.dls_imagematch.feature.transform.trs_translation import Translation


class TransformCalculator:
    """ For a set of matches which map points between two images, this class finds the approximate
    transformation that will map any point in the first image to the equivalent point in the second.
    The transformation can include translation, rotation, scale, and skew components.

    Clients can choose from four different methods:
    * TRANSLATION - the transform will be calculated simply as the median translation.
    * HOMOGRAPHY - a full transformation
    * AFFINE_FULL - an affine transformation with 6 degrees of freedom
    * AFFINE_RIGID - an affine transformation with 5 degrees of freedom - no shearing so
        transformed shapes will maintain the same angles.

    Note: at least 4 matches are required to calculate a full transformation.

    A filter may be used to eliminate some of the poorer matches prior to calculating the transformation.
    The options are:
    * NO_FILTER -
    * LMEDS -
    * RANSAC -

    For more information on homography calculation and definition of methods, see:
    http://docs.opencv.org/2.4/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#findhomography
    """
    TRANSLATION = "Average Translation"
    HOMOGRAPHY = "Homography"
    AFFINE_FULL = "Affine - Full (6 DoF)"
    AFFINE_RIGID = "Affine - Rigid (5 DoF)"

    METHODS = [AFFINE_FULL, AFFINE_RIGID, HOMOGRAPHY, TRANSLATION]
    AFFINE_METHODS = [AFFINE_FULL, AFFINE_RIGID]

    NO_FILTER = "None"
    LMEDS = "LMEDS"
    RANSAC = "RANSAC"

    FILTERS = [NO_FILTER, LMEDS, RANSAC]

    DEFAULT_METHOD = AFFINE_FULL
    DEFAULT_FILTER = RANSAC
    DEFAULT_RANSAC_THRESHOLD = 5.0

    _MIN_TRANSFORM_MATCHES = 4

    def __init__(self):
        self._method = self.DEFAULT_METHOD
        self._filter = self.DEFAULT_FILTER
        self._ransac_threshold = self.DEFAULT_RANSAC_THRESHOLD

    # -------- CONFIGURATION -------------------
    def set_method(self, method):
        if method not in self.METHODS:
            raise TransformCalculationError("Not a valid transformation method: '{}'".format(method))
        self._method = method

    def set_filter(self, filter_obj):
        if filter_obj not in self.FILTERS:
            raise TransformCalculationError("Not a valid filter: '{}'".format(filter_obj))
        self._filter = filter_obj

    def set_ransac_threshold(self, threshold):
        self._ransac_threshold = threshold

    # -------- FUNCTIONALITY -------------------
    def calculate_transform(self, matches):
        if len(matches) == 0:
            return None

        method = self._method
        if method == self.TRANSLATION:
            transform, mask = self._calculate_median_translation(matches)
        elif method == self.HOMOGRAPHY:
            transform, mask = self._calculate_homography_transform(matches)
        elif method in self.AFFINE_METHODS:
            transform, mask = self._calculate_affine_transform(matches)
        else:
            log = logging.getLogger(".".join([__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.error(TransformCalculationError("Unrecognised transform method type"))
            raise TransformCalculationError("Unrecognised transform method type")

        if transform is None:
            self._mark_all_matches_unused(matches)
        else:
            self._set_matches_reprojection_error(matches, transform)
            self._mark_unused_matches(matches, mask)

        return transform

    def _calculate_median_translation(self, matches):
        matches, mask = self._pre_filter(matches)

        deltas = [m.point2() - m.point1() for m in matches]
        x = -np.median([d.x for d in deltas])
        y = -np.median([d.y for d in deltas])
        point = Point(x, y)
        transform = Translation(point)

        return transform, mask

    def _calculate_homography_transform(self, matches):
        transform = None
        matches, mask = self._pre_filter(matches)

        if self._has_enough_matches_for_transform(matches):
            image1_pts, image2_pts = self._get_np_points(matches)

            homography, new_mask = cv2.findHomography(image1_pts, image2_pts, 0, 0)
            mask = self._combine_masks(mask, new_mask)
            transform = HomographyTransformation(homography)

        return transform, mask

    def _calculate_affine_transform(self, matches):
        """ Note: internally, estimateRigidTransform uses some sort of RANSAC method as a filter, but with
        hardcoded (and not very good) parameters. """
        transform = None
        matches, mask = self._pre_filter(matches)

        if self._has_enough_matches_for_transform(matches):
            image1_pts, image2_pts = self._get_np_points(matches)
            use_full = self._method == self.AFFINE_FULL

            affine = cv2.estimateRigidTransform(image1_pts, image2_pts, fullAffine=use_full)

            if affine is not None:
                affine = np.array([affine[0], affine[1], [0, 0, 1]], np.float32)
                transform = AffineTransformation(affine)

        return transform, mask

    def _has_enough_matches_for_transform(self, matches):
        return len(matches) >= self._MIN_TRANSFORM_MATCHES

    def _pre_filter(self, matches):
        mask = [True] * len(matches)

        if self._filter != self.NO_FILTER:
            mask = self._make_pre_filter_mask(matches)
            matches = [m for (m, i) in zip(matches, mask) if i]

        return matches, mask

    def _make_pre_filter_mask(self, matches):
        mask = [True] * len(matches)

        if self._has_enough_matches_for_transform(matches):
            image1_pts, image2_pts = self._get_np_points(matches)
            filter_code = self._get_filter_code()
            _, mask = cv2.findHomography(image1_pts, image2_pts, filter_code, self._ransac_threshold)
            mask = self._sanitize_mask(mask)

        return mask

    def _get_filter_code(self):
        filter_code = self._filter
        if filter_code == self.NO_FILTER:
            return 0
        elif filter_code == self.LMEDS:
            return cv2.LMEDS
        elif filter_code == self.RANSAC:
            return cv2.RANSAC
        else:
            return -1

    @staticmethod
    def _combine_masks(mask1, mask2):
        """ Create a new mask by combining the two masks. Mask 2 has a length equal to the number of True elements in
        Mask 1. Each element in Mask 2 corresponds to a True element in Mask 1"""
        total_mask = []
        j = 0
        for bit in mask1:
            total_mask.append(bit and mask2[j])
            if bit:
                j += 1

        return total_mask

    @staticmethod
    def _get_np_points(matches):
        image1_pts = [m.point1().tuple() for m in matches]
        image1_pts = np.float32(image1_pts).reshape(-1, 1, 2)
        image2_pts = [m.point2().tuple() for m in matches]
        image2_pts = np.float32(image2_pts).reshape(-1, 1, 2)
        return image1_pts, image2_pts

    @staticmethod
    def _sanitize_mask(mask):
        return [m in [1, [1], True] for m in mask]

    @staticmethod
    def _mark_unused_matches(matches, mask):
        mask = TransformCalculator._sanitize_mask(mask)
        for match, include in zip(matches, mask):
            match.set_in_transformation(include)

    @staticmethod
    def _mark_all_matches_unused(matches):
        for match in matches:
            match.set_in_transformation(False)

    @staticmethod
    def _set_matches_reprojection_error(matches, transform):
        point1s = [m.point1() for m in matches]
        projected_point2s = transform.transform_points(point1s)

        for i, match in enumerate(matches):
            match.set_point2_projected(projected_point2s[i])
