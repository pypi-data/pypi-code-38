import cv2

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType, ExtractorType
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector


class SurfDetector(Detector):
    """ Implements the SURF (Speeded Up Robust Features) keypoint detector and feature extractor
    detailed in the paper 'Bay, H. and Tuytelaars, T. and Van Gool, L. SURF: Speeded Up Robust
    Features, 9th European Conference on Computer Vision, 2006'.

    For further details see:
    http://docs.opencv.org/3.1.0/d5/df7/classcv_1_1xfeatures2d_1_1SURF.html
     or
    http://docs.opencv.org/2.4/modules/nonfree/doc/feature_detection.html
    """
    DEFAULT_EXTRACTOR = ExtractorType.SURF
    DEFAULT_KEYPOINT_LIMIT = 30

    DEFAULT_HESSIAN_THRESHOLD = 100
    DEFAULT_N_OCTAVES = 4
    DEFAULT_N_OCTAVE_LAYERS = 2
    DEFAULT_EXTENDED = True
    DEFAULT_UPRIGHT = False

    def __init__(self):
        Detector.__init__(self, DetectorType.SURF)

        # SURF is not free and a licence should be obtained if using for commercial purposes
        self._is_non_free = True

        self._hessian_threshold = self.DEFAULT_HESSIAN_THRESHOLD
        self._n_octaves = self.DEFAULT_N_OCTAVES
        self._n_octave_layers = self.DEFAULT_N_OCTAVE_LAYERS
        self._extended = self.DEFAULT_EXTENDED
        self._upright = self.DEFAULT_UPRIGHT

    # -------- CONFIGURATION ------------------
    def set_hessian_threshold(self, value):
        """ Threshold for the keypoint detector. Only features, whose hessian is larger than hessianThreshold
        are retained by the detector. Therefore, the larger the value, the less keypoints you will get. A
        good default value could be from 300 to 500, depending from the image contrast. """
        self._hessian_threshold = float(value)

    def set_n_octaves(self, value):
        """ The number of a gaussian pyramid octaves that the detector uses. It is set to 4 by default. If you
        want to get very large features, use the larger value. If you want just small features, decrease it. """
        if int(value) < 0:
            raise FeatureDetectorError("SURF number of octaves must be integer >= 0")
        self._n_octaves = int(value)

    def set_n_octave_layers(self, value):
        """ The number of images within each octave of a gaussian pyramid. """
        if int(value) < 0:
            raise FeatureDetectorError("SURF number of octave layers must be integer >= 1")
        self._n_octaves = int(value)

    def set_extended(self, value):
        """ Extended descriptor flag (true - use extended 128-element descriptors; false - use 64-element
        descriptors). """
        self._extended = bool(value)

    def set_upright(self, value):
        """ Up-right or rotated features flag (true - do not compute orientation of features; false -
        compute orientation). """
        self._upright = bool(value)

    def set_from_config(self, config):
        Detector.set_from_config(self, config)
        self.set_hessian_threshold(config.hessian_threshold.value())
        self.set_n_octaves(config.n_octaves.value())
        self.set_n_octave_layers(config.n_octave_layers.value())
        self.set_extended(config.extended.value())
        self.set_upright(config.upright.value())

    # -------- FUNCTIONALITY -------------------
    def _create_detector(self):
        detector = cv2.SURF(hessianThreshold=self._hessian_threshold,
                            nOctaves=self._n_octaves,
                            nOctaveLayers=self._n_octave_layers,
                            extended=self._extended,
                            upright=self._upright)

        return detector
