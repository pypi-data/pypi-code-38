import logging

import cv2

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType, AdaptationType, ExtractorType
from CrystalMatch.dls_imagematch.feature.detector.feature import Feature
from CrystalMatch.dls_imagematch.feature.detector.exception import OpenCvVersionError, FeatureDetectorError

OPENCV_MAJOR = cv2.__version__[0]

_OPENCV_VERSION_ERROR = "Under Windows, this function only works correctly under OpenCV v2 (with Python 2.7) " \
                        "and not under OpenCV v3. This is a widely known and reported problem but it doesn't " \
                        "seem to have been fixed yet. Install Python 2.7 with OpenCV 2.4 and try again."


class Detector:
    """ Uses OpenCV algorithms to detect interesting features in an image and quantify them with an
    array of numerical descriptors.

    A range of different detector methods are available, each with different properties. Each detector
    may work more effectively on some images than on others.
    """

    # Defaults
    DEFAULT_ENABLED = True
    DEFAULT_DETECTOR = DetectorType.ORB
    DEFAULT_ADAPTATION = AdaptationType.NONE
    DEFAULT_EXTRACTOR = ExtractorType.BRIEF
    DEFAULT_KEYPOINT_LIMIT = 50

    def __init__(self, detector=DEFAULT_DETECTOR):
        """ Supply a detector name to use that detector with all its default parameters. """
        if detector not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("No such feature detector available: " + detector)

        self._enabled = self.DEFAULT_ENABLED
        self._detector = detector
        self._adaptation = self.DEFAULT_ADAPTATION
        self._extractor = self.DEFAULT_EXTRACTOR
        self._normalization = self._default_normalization(detector)
        self._is_non_free = False
        self._keypoint_limit = self.DEFAULT_KEYPOINT_LIMIT

    # -------- ACCESSORS -----------------------
    def enabled(self):
        return self._enabled

    def detector(self):
        return self._detector

    def adaptation(self):
        return self._adaptation

    def extractor(self):
        return self._extractor

    def normalization(self):
        return self._normalization

    def is_non_free(self):
        return self._is_non_free

    def keypoint_limit(self):
        return self._keypoint_limit

    def extractor_distance_factor(self):
        return ExtractorType.distance_factor(self._extractor)

    # -------- CONFIGURATION ------------------
    def set_enabled(self, enabled):
        """ Determines whether or not the detector will be used. If set to false, attempting to
        use the detector will yield no results."""
        self._enabled = enabled

    def set_adaptation(self, adaptation):
        if adaptation not in AdaptationType.LIST_ALL:
            raise FeatureDetectorError("No such feature detector adaptation available: " + adaptation)
        self._adaptation = adaptation

    def set_extractor(self, extractor):
        """ Set the descriptor extractor type. Possible values are 'ORB', 'SURF', 'SIFT', 'BRIEF', and 'BRISK'."""
        self._extractor = extractor

    def set_keypoint_limit(self, limit):
        """ Largest allowable keypoint distance between two features to be considered a valid match using this
        detector. """
        self._keypoint_limit = limit

    def set_from_config(self, config):
        self.set_enabled(config.enabled.value())
        self.set_extractor(config.extractor.value())
        self.set_keypoint_limit(config.keypoint_limit.value())

    # -------- FUNCTIONALITY -------------------
    def detect_features(self, image):
        """ Detect interesting features in the image and generate descriptors. A keypoint identifies the
        location and orientation of a feature, and a descriptor is a vector of numbers that describe the
        various attributes of the feature. By generating descriptors, we can compare the set of features
        on two images and find matches between them.
        """
        if not self._enabled:
            logging.info("Detector {} is disabled".format(self._detector))
            return []

        detector = self._create_detector()
        extractor = self._create_extractor()

        keypoints = detector.detect(image.raw(), None)
        keypoints, descriptors = extractor.compute(image.raw(), keypoints)

        features = []
        if descriptors is None:
            return features

        for kp, descriptor in zip(keypoints, descriptors):
            feature = Feature(kp, descriptor)
            features.append(feature)

        return features

    def _create_detector(self):
        return self._create_default_detector(self._detector, self._adaptation)

    def _create_extractor(self):
        return self._create_default_extractor(self._extractor)

    @staticmethod
    def _default_normalization(detector):
        """ Keypoint normalization type for the detector method; used for matching. """
        if detector in [DetectorType.SIFT, DetectorType.SURF]:
            return cv2.NORM_L2
        else:
            return cv2.NORM_HAMMING

    @staticmethod
    def _create_default_detector(detector, adaptation):
        """ Create a detector of the specified type with all the default parameters"""
        name = adaptation + detector
        try:
            detector = cv2.FeatureDetector_create(name)
        except AttributeError:
            log = logging.getLogger(".".join([__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.error(OpenCvVersionError(_OPENCV_VERSION_ERROR))
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return detector

    @staticmethod
    def _create_default_extractor(extractor):
        """ Note: SIFT descriptors for a keypoint are an array of 128 integers; SURF descriptors are an
        array of 64 floats (in range -1 to 1); BRISK uses 64 integers, all others are arrays of 32 ints
        (in range 0 to 255). """
        try:
            extractor = cv2.DescriptorExtractor_create(extractor)
        except AttributeError:
            log = logging.getLogger(".".join([__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.error(OpenCvVersionError(_OPENCV_VERSION_ERROR))
            raise OpenCvVersionError(_OPENCV_VERSION_ERROR)
        return extractor
