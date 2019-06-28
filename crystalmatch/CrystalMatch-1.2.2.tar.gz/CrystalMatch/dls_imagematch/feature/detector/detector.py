import logging

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.feature.detector.opencv_detector_interface import OpencvDetectorInterface
from CrystalMatch.dls_imagematch.feature.detector.detector_types import DetectorType, AdaptationType, ExtractorType
from CrystalMatch.dls_imagematch.feature.detector.feature import Feature
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError


class Detector:
    """ Uses OpenCV algorithms to detect interesting features in an image and quantify them with an
    array of numerical descriptors.

    A range of different detector methods are available, each with different properties. Each detector
    may work more effectively on some images than on others.
    """

    # Defaults
    DEFAULT_DETECTOR = DetectorType.ORB
    DEFAULT_ADAPTATION = AdaptationType.NONE
    DEFAULT_EXTRACTOR = ExtractorType.BRIEF
    DEFAULT_KEYPOINT_LIMIT = 50

    def __init__(self, detector=DEFAULT_DETECTOR):
        """ Supply a detector name to use that detector with all its default parameters. """
        if detector not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("No such feature detector available: " + detector)

        self._detector_name = detector
        self._adaptation = self.DEFAULT_ADAPTATION
        self._extractor_name = self.DEFAULT_EXTRACTOR
        self._normalization = self._default_normalization()
        self._keypoint_limit = self.DEFAULT_KEYPOINT_LIMIT

    # -------- ACCESSORS -----------------------

    def detector_name(self):
        return self._detector_name

    def adaptation(self):
        return self._adaptation

    def extractor_name(self):
        return self._extractor_name

    def normalization(self):
        return self._normalization

    def keypoint_limit(self):
        return self._keypoint_limit

    def extractor_distance_factor(self):
        return ExtractorType.distance_factor(self._extractor_name)

    # -------- CONFIGURATION ------------------

    def set_adaptation(self, adaptation):
        if adaptation not in AdaptationType.LIST_ALL:
            raise FeatureDetectorError("No such feature detector adaptation available: " + adaptation)
        self._adaptation = adaptation

    def set_extractor(self, extractor):
        """ Set the descriptor extractor type. Possible values are 'ORB', 'BRIEF', and 'BRISK'."""
        self._extractor_name = extractor

    def set_keypoint_limit(self, limit):
        """ Largest allowable keypoint distance between two features to be considered a valid match using this
        detector. """
        self._keypoint_limit = limit

    def set_from_config(self, config):
        self.set_extractor(config.extractor.value())
        self.set_keypoint_limit(config.keypoint_limit.value())

    # -------- FUNCTIONALITY -------------------
    def detect_features(self, image):
        """ Detect interesting features in the image and generate descriptors. A keypoint identifies the
        location and orientation of a feature, and a descriptor is a vector of numbers that describe the
        various attributes of the feature. By generating descriptors, we can compare the set of features
        on two images and find matches between them.
        """
        detector = self._create_detector()

        keypoints = detector.detect(image.raw(), None)
        extractor = self._create_extractor() # not good creates an object which is not always used
        keypoints, descriptors = OpencvDetectorInterface().compute(image.raw(), keypoints, extractor, detector)

        features = []
        if descriptors is None:
            return features

        for kp, descriptor in zip(keypoints, descriptors):
            feature = Feature(kp, descriptor)
            features.append(feature)

        return features

    def _create_detector(self):

        return self._create_default_detector(self._detector_name, self._adaptation)

    def _create_extractor(self):

        return self._create_default_extractor(self._extractor_name, self._detector_name)

    @staticmethod
    def _default_normalization():
        """ Keypoint normalization type for the detector method; used for matching. """

        return OpencvDetectorInterface().get_hamming_norm()

    @staticmethod
    def _create_default_detector(detector, adaptation):
        """ Create a detector of the specified type with all the default parameters"""
        detector = OpencvDetectorInterface().feature_detector_create(detector, adaptation)

        return detector

    @staticmethod
    def _create_default_extractor(extractor, detector_name):
        """ Note: BRISK uses 64 integers, all others are arrays of 32 ints
        (in range 0 to 255). """
        extractor = OpencvDetectorInterface().create_extractor(extractor, detector_name)

        return extractor
