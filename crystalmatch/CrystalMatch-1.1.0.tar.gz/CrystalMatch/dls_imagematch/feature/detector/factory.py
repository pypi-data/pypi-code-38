from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError

from CrystalMatch.dls_imagematch.feature.detector.types import DetectorType
from CrystalMatch.dls_imagematch.feature.detector.detector import Detector
from CrystalMatch.dls_imagematch.feature.detector.detector_orb import OrbDetector
from CrystalMatch.dls_imagematch.feature.detector.detector_sift import SiftDetector
from CrystalMatch.dls_imagematch.feature.detector.detector_surf import SurfDetector
from CrystalMatch.dls_imagematch.feature.detector.detector_brisk import BriskDetector


class DetectorFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(det_type, options=None):
        if det_type not in DetectorType.LIST_ALL:
            raise FeatureDetectorError("Unknown detector type: {}".format(det_type))

        if det_type == DetectorType.ORB:
            detector = OrbDetector()
        elif det_type == DetectorType.SIFT:
            detector = SiftDetector()
        elif det_type == DetectorType.SURF:
            detector = SurfDetector()
        # MSER currently has no wrapper class due to the format of the output - need to update to reinstate this
        # elif type == DetectorType.MSER:
        #     detector = MserDetector()
        elif det_type == DetectorType.BRISK:
            detector = BriskDetector()
        else:
            detector = Detector(detector=det_type)

        if options is not None:
            detector_options = options.get_detector_options(det_type)
            detector.set_from_config(detector_options)

        if detector.is_non_free():
            licensing = options.get_licensing_options()
            use_non_free = licensing.use_non_free.value()
            if not use_non_free:
                detector.set_enabled(False)

        return detector

    @staticmethod
    def get_all_detectors(options=None):
        detectors = []

        for det in DetectorType.LIST_ALL:
            detector = DetectorFactory.create(det, options)
            detectors.append(detector)
        return detectors

    @staticmethod
    def get_all_free_detectors(options=None):
        detectors = []

        for det in DetectorType.LIST_FREE:
            detector = DetectorFactory.create(det, options)
            detectors.append(detector)
        return detectors
