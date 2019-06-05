import cv2

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType, ExtractorType
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector, OPENCV_MAJOR


class OrbDetector(Detector):
    """ Implements the ORB (oriented BRIEF) keypoint detector and descriptor extractor,
    described in 'Ethan Rublee, Vincent Rabaud, Kurt Konolige, Gary R. Bradski: ORB: An efficient
    alternative to SIFT or SURF. ICCV 2011: 2564-2571'. The algorithm uses FAST in pyramids to
    detect stable keypoints, selects the strongest features using FAST or Harris response, finds
    their orientation using first-order moments and computes the descriptors using BRIEF (where
    the coordinates of random point pairs (or k-tuples) are rotated according to the measured orientation).

    For further details see:
    http://docs.opencv.org/2.4/modules/features2d/doc/feature_detection_and_description.html#orb
    """
    WTA_K_VALUES = [2, 3, 4]

    SCORE_HARRIS = "HARRIS_SCORE"
    SCORE_FAST = "FAST_SCORE"
    SCORE_TYPE_NAMES = [SCORE_HARRIS, SCORE_FAST]

    DEFAULT_EXTRACTOR = ExtractorType.ORB
    DEFAULT_KEYPOINT_LIMIT = 50

    DEFAULT_N_FEATURES = 500
    DEFAULT_SCALE_FACTOR = 1.2
    DEFAULT_N_LEVELS = 8
    DEFAULT_EDGE_THRESHOLD = 31
    DEFAULT_FIRST_LEVEL = 0
    DEFAULT_WTA_K = 2
    DEFAULT_SCORE_TYPE = SCORE_HARRIS
    DEFAULT_PATCH_SIZE = 31

    def __init__(self):
        Detector.__init__(self, DetectorType.ORB)

        self._n_features = self.DEFAULT_N_FEATURES
        self._scale_factor = self.DEFAULT_SCALE_FACTOR
        self._n_levels = self.DEFAULT_N_LEVELS
        self._edge_threshold = self.DEFAULT_EDGE_THRESHOLD
        self._first_level = self.DEFAULT_FIRST_LEVEL
        self._wta_k = self.DEFAULT_WTA_K
        self._score_type = self.DEFAULT_SCORE_TYPE
        self._patch_size = self.DEFAULT_PATCH_SIZE

    def normalization(self):
        if self._wta_k == 2:
            return cv2.NORM_HAMMING
        else:
            return cv2.NORM_HAMMING2

    def _score(self):
        if self._score_type == self.SCORE_HARRIS:
            return cv2.ORB_HARRIS_SCORE
        elif self._score_type == self.SCORE_FAST:
            return cv2.ORB_FAST_SCORE

    # -------- CONFIGURATION ------------------
    def set_n_features(self, value):
        """ The maximum number of features to retain. """
        if int(value) < 1:
            raise FeatureDetectorError("ORB number of features must be positive integer")
        self._n_features = int(value)

    def set_scale_factor(self, value):
        """ Pyramid decimation ratio, greater than 1. scaleFactor==2 means the classical pyramid, where each
        next level has 4x less pixels than the previous, but such a big scale factor will degrade feature
        matching scores dramatically. On the other hand, too close to 1 scale factor will mean that to cover
        certain scale range you will need more pyramid levels and so the speed will suffer. """
        if float(value) <= 1.0:
            raise FeatureDetectorError("ORB scale factor must be float great than 1.0")
        self._scale_factor = float(value)

    def set_n_levels(self, value):
        """ The number of pyramid levels. The smallest level will have linear size equal to
        input_image_linear_size/pow(scaleFactor, nlevels). """
        if int(value) < 1:
            raise FeatureDetectorError("ORB number of levels must be positive integer")
        self._n_levels = int(value)

    def set_edge_threshold(self, value):
        """ This is size of the border where the features are not detected. It should roughly match the
        patchSize parameter. """
        if int(value) < 1:
            raise FeatureDetectorError("ORB edge threshold must be positive integer")
        self._edge_threshold = int(value)

    def set_first_level(self, value):
        """ Should be 0 in the current implementation. """
        if int(value) != 0:
            raise FeatureDetectorError("ORB first level value must be 0")
        self._first_level = int(value)

    def set_wta_k(self, value):
        """ The number of points that produce each element of the oriented BRIEF descriptor. The default value
        2 means the BRIEF where we take a random point pair and compare their brightnesses, so we get 0/1
        response. Other possible values are 3 and 4. For example, 3 means that we take 3 random points (of
        course, those point coordinates are random, but they are generated from the pre-defined seed, so each
        element of BRIEF descriptor is computed deterministically from the pixel rectangle), find point of
        maximum brightness and output index of the winner (0, 1 or 2). Such output will occupy 2 bits, and
        therefore it will need a special variant of Hamming distance, denoted as NORM_HAMMING2 (2 bits per bin).
        When WTA_K=4, we take 4 random points to compute each bin (that will also occupy 2 bits with possible
        values 0, 1, 2 or 3)."""
        if value not in self.WTA_K_VALUES:
            raise FeatureDetectorError("ORB WTA_K value must be one of {}".format(self.WTA_K_VALUES))
        self._wta_k = value

    def set_score_type(self, value):
        """ The default HARRIS_SCORE means that Harris algorithm is used to rank features (the score is written
        to KeyPoint::score and is used to retain best nfeatures features); FAST_SCORE is alternative value of
        the parameter that produces slightly less stable keypoints, but it is a little faster to compute. """
        if value not in self.SCORE_TYPE_NAMES:
            raise FeatureDetectorError("ORB score type value must be one of {}".format(self.SCORE_TYPE_NAMES))

        self._score_type = value

    def set_patch_size(self, value):
        """ Size of the patch used by the oriented BRIEF descriptor. Of course, on smaller pyramid layers the
        perceived image area covered by a feature will be larger. """
        if int(value) < 2:
            raise FeatureDetectorError("ORB patch size must be integer >= 2")
        self._patch_size = int(value)

    def set_from_config(self, config):
        Detector.set_from_config(self, config)
        self.set_n_features(config.n_features.value())
        self.set_scale_factor(config.scale_factor.value())
        self.set_n_levels(config.n_levels.value())
        self.set_edge_threshold(config.edge_threshold.value())
        self.set_first_level(config.first_level.value())
        self.set_wta_k(config.wta_k.value())
        self.set_score_type(config.score_type.value())
        self.set_patch_size(config.patch_size.value())

    # -------- FUNCTIONALITY -------------------
    def _create_detector(self):
        if OPENCV_MAJOR == '2':
            constructor = cv2.ORB
        else:
            # noinspection PyUnresolvedReferences
            constructor = cv2.ORB_create

        detector = constructor(nfeatures=self._n_features,
                               scaleFactor=self._scale_factor,
                               nlevels=self._n_levels,
                               edgeThreshold=self._edge_threshold,
                               firstLevel=self._first_level,
                               WTA_K=self._wta_k,
                               scoreType=self._score(),
                               patchSize=self._patch_size)

        return detector
