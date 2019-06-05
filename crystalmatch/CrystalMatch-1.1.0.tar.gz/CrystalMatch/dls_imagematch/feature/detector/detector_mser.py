import cv2

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector


# TODO: The OpenCV MSER function returns regions, not keypoints => convert regions to keypoints
class MserDetector(Detector):
    """ Implements the MSER (Maximally stable extremal region extractor) keypoint detector.

    For further details see:
    http://docs.opencv.org/2.4/modules/features2d/doc/feature_detection_and_description.html#mser
    """
    DEFAULT_DELTA = 5
    DEFAULT_MIN_AREA = 60
    DEFAULT_MAX_AREA = 14400
    DEFAULT_MAX_VARIATION = 0.25
    DEFAULT_MIN_DIVERSITY = 0.2
    DEFAULT_MAX_EVOLUTION = 200
    DEFAULT_AREA_THRESHOLD = 1.01
    DEFAULT_MIN_MARGIN = 0.003
    DEFAULT_EDGE_BLUR_SIZE = 5

    def __init__(self):
        Detector.__init__(self, DetectorType.MSER)

        self._delta = self.DEFAULT_DELTA
        self._min_area = self.DEFAULT_MIN_AREA
        self._max_area = self.DEFAULT_MAX_AREA
        self._max_variation = self.DEFAULT_MAX_VARIATION
        self._min_diversity = self.DEFAULT_MIN_DIVERSITY
        self._max_evolution = self.DEFAULT_MAX_EVOLUTION
        self._area_threshold = self.DEFAULT_AREA_THRESHOLD
        self._min_margin = self.DEFAULT_MIN_MARGIN
        self._edge_blur_size = self.DEFAULT_EDGE_BLUR_SIZE

    # -------- CONFIGURATION ------------------
    def set_delta(self, value):
        """ Compares (sizei - sizei-delta)/sizei-delta. """
        if int(value) < 1:
            raise FeatureDetectorError("MSER delta must be positive integer")
        self._delta = int(value)

    def set_min_area(self, value):
        """ Prune the area which smaller than minArea. """
        if int(value) < 1:
            raise FeatureDetectorError("MSER minimum area must be positive integer")
        self._min_area = int(value)

    def set_max_area(self, value):
        """ Prune the area which bigger than maxArea. """
        if int(value) < 1:
            raise FeatureDetectorError("MSER maximum area must be positive integer")
        self._max_area = int(value)

    def set_max_variation(self, value):
        """ Prune the area have simliar size to its children. """
        self._max_variation = float(value)

    def set_min_diversity(self, value):
        """ For color image, trace back to cut off mser with diversity less than min_diversity. """
        self._min_diversity = float(value)

    def set_max_evolution(self, value):
        """ For color image, the evolution steps. """
        if int(value) < 1:
            raise FeatureDetectorError("MSER maximum evolution must be positive integer")
        self._max_evolution = int(value)

    def set_area_threshold(self, value):
        """ For color image, the area threshold to cause re-initialize. """
        self._area_threshold = float(value)

    def set_min_margin(self, value):
        """ For color image, ignore too small margin. """
        self._min_margin = float(value)

    def set_edge_blur_size(self, value):
        """ For color image, the aperture size for edge blur. """
        if int(value) < 1:
            raise FeatureDetectorError("MSER edge blur size must be positive integer")
        self._edge_blur_size = int(value)

    def set_from_config(self, config):
        Detector.set_from_config(self, config)
        self.set_delta(config.delta.value())
        self.set_min_area(config.min_area.value())
        self.set_max_area(config.max_area.value())
        self.set_max_variation(config.max_variation.value())
        self.set_min_diversity(config.min_diversity.value())
        self.set_max_evolution(config.max_evolution.value())
        self.set_area_threshold(config.area_threshold.value())
        self.set_min_margin(config.min_margin.value())
        self.set_edge_blur_size(config.edge_blur_size.value())

    # -------- FUNCTIONALITY -------------------
    def _create_detector(self):
        detector = cv2.MSER(_delta=self._delta,
                            _min_area=self._min_area,
                            _max_area=self._max_area,
                            _max_variation=self._max_variation,
                            _min_diversity=self._min_diversity,
                            _max_evolution=self._max_evolution,
                            _area_threshold=self._area_threshold,
                            _min_margin=self._min_margin,
                            _edge_blur_size=self._edge_blur_size)

        return detector
