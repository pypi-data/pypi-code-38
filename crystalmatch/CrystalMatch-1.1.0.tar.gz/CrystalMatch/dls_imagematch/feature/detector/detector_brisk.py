import cv2

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType, ExtractorType
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector


class BriskDetector(Detector):
    """ Implements the BRISK (Binary Robust Invariant Scalable Keypoints) keypoint detector
    and descriptor extractor described in 'Stefan Leutenegger, Margarita Chli and Roland Siegwart:
    BRISK: Binary Robust Invariant Scalable Keypoints. ICCV 2011: 2548-2555.'
    """
    DEFAULT_EXTRACTOR = ExtractorType.BRISK
    DEFAULT_KEYPOINT_LIMIT = 30

    DEFAULT_THRESH = 30
    DEFAULT_OCTAVES = 3
    DEFAULT_PATTERN_SCALE = 1.0

    def __init__(self):
        Detector.__init__(self, DetectorType.BRISK)

        self._thresh = self.DEFAULT_THRESH
        self._octaves = self.DEFAULT_OCTAVES
        self._pattern_scale = self.DEFAULT_PATTERN_SCALE

    # -------- CONFIGURATION ------------------
    def set_thresh(self, value):
        """ FAST/AGAST detection threshold score. """
        if int(value) < 0:
            raise FeatureDetectorError("BRISK threshold must be integer >= 0")
        self._thresh = int(value)

    def set_octaves(self, value):
        """ Detection octaves. Use 0 to do single scale. """
        if int(value) < 0:
            raise FeatureDetectorError("BRISK octaves must be integer >= 0")
        self._octaves = int(value)

    def set_pattern_scale(self, value):
        """ Apply this scale to the pattern used for sampling the neighbourhood of a keypoint. """
        self._pattern_scale = float(value)

    def set_from_config(self, config):
        Detector.set_from_config(self, config)
        self.set_thresh(config.thresh.value())
        self.set_octaves(config.octaves.value())
        self.set_pattern_scale(config.pattern_scale.value())

    # -------- FUNCTIONALITY -------------------
    def _create_detector(self):
        detector = cv2.BRISK(thresh=self._thresh,
                             octaves=self._octaves,
                             patternScale=self._pattern_scale)

        return detector
