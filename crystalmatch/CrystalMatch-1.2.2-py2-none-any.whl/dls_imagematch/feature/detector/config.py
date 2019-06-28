from os.path import join

from CrystalMatch.dls_imagematch.feature.detector import Detector
from CrystalMatch.dls_util.config.config import Config
from CrystalMatch.dls_util.config.item import IntConfigItem, RangeIntConfigItem, FloatConfigItem, RangeFloatConfigItem, \
    EnumConfigItem, BoolConfigItem
from CrystalMatch.dls_imagematch.feature.detector.detector_brisk import BriskDetector
from CrystalMatch.dls_imagematch.feature.detector.detector_orb import OrbDetector
from CrystalMatch.dls_imagematch.feature.detector.detector_types import DetectorType, ExtractorType


class DetectorConfig:
    def __init__(self, folder):
        self._folder = folder
        self.orb = OrbConfig(join(folder, "det_orb.ini"))
        self.brisk = BriskConfig(join(folder, "det_brisk.ini"))
        self.fast = FastConfig(join(folder, "det_fast.ini"))
        self.star = StarConfig(join(folder, "det_star.ini"))
        self.mser = MserConfig(join(folder, "det_mser.ini"))
        self.gftt = GfttConfig(join(folder, "det_gftt.ini"))
        self.harris = GfttConfig(join(folder, "det_harris.ini"))
        self.blob = BlobConfig(join(folder, "det_blob.ini"))

    def get_detector_options(self, detector):
        if detector == DetectorType.ORB:
            return self.orb
        elif detector == DetectorType.BRISK:
            return self.brisk
        elif detector == DetectorType.FAST:
            return self.fast
        elif detector == DetectorType.STAR:
            return self.star
        elif detector == DetectorType.MSER:
            return self.mser
        elif detector == DetectorType.GFTT:
            return self.gftt
        elif detector == DetectorType.HARRIS:
            return self.harris
        elif detector == DetectorType.BLOB:
            return self.blob
        else:
            raise ValueError("Unrecognised detector type")

class _BaseDetectorConfig(Config):
    def __init__(self, file_path, detector_type):
        Config.__init__(self, file_path)

        add = self.add
        det = detector_type

        self.extractor = add(EnumConfigItem, "Extractor", det.DEFAULT_EXTRACTOR, ExtractorType.LIST_ALL)
        self.keypoint_limit = add(RangeIntConfigItem, "Keypoint Limit", det.DEFAULT_KEYPOINT_LIMIT, [1, 100])

        self.extractor.set_comment(det.set_extractor.__doc__)
        self.keypoint_limit.set_comment(det.set_keypoint_limit.__doc__)


class OrbConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, OrbDetector)

        add = self.add
        det = OrbDetector

        self.set_title("ORB Detector Configuration")
        self.set_comment(det.__doc__)

        self.n_features = add(IntConfigItem, "Num Features", det.DEFAULT_N_FEATURES, [1, None])
        self.scale_factor = add(RangeFloatConfigItem, "Scale Factor", det.DEFAULT_SCALE_FACTOR, [1.001, None])
        self.n_levels = add(RangeIntConfigItem, "Num Levels", det.DEFAULT_N_LEVELS, [1, None])
        self.edge_threshold = add(IntConfigItem, "Edge Threshold", det.DEFAULT_EDGE_THRESHOLD, [1, None])
        self.first_level = add(RangeIntConfigItem, "First Level", det.DEFAULT_FIRST_LEVEL, [0, 0])
        self.wta_k = add(EnumConfigItem, "WTA_K", det.DEFAULT_WTA_K, det.WTA_K_VALUES)
        self.score_type = add(EnumConfigItem, "Score Type", det.DEFAULT_SCORE_TYPE, det.SCORE_TYPE_NAMES)
        self.patch_size = add(IntConfigItem, "Patch Size", det.DEFAULT_PATCH_SIZE, [2, None])

        self.n_features.set_comment(det.set_n_features.__doc__)
        self.scale_factor.set_comment(det.set_scale_factor.__doc__)
        self.n_levels.set_comment(det.set_n_levels.__doc__)
        self.edge_threshold.set_comment(det.set_edge_threshold.__doc__)
        self.first_level.set_comment(det.set_first_level.__doc__)
        self.wta_k.set_comment(det.set_wta_k.__doc__)
        self.score_type.set_comment(det.set_score_type.__doc__)
        self.patch_size.set_comment(det.set_patch_size.__doc__)

        self.initialize_from_file()

class BriskConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, BriskDetector)

        add = self.add
        det = BriskDetector

        self.set_title("BRISK Detector Configuration")
        self.set_comment(det.__doc__)

        self.thresh = add(RangeIntConfigItem, "Threshold", det.DEFAULT_THRESH, [0, None])
        self.octaves = add(RangeIntConfigItem, "Octaves", det.DEFAULT_OCTAVES, [0, None])
        self.pattern_scale = add(RangeFloatConfigItem, "Pattern Scale", det.DEFAULT_PATTERN_SCALE, [0.0, None])

        self.thresh.set_comment(det.set_thresh.__doc__)
        self.octaves.set_comment(det.set_octaves.__doc__)
        self.pattern_scale.set_comment(det.set_pattern_scale.__doc__)

        self.initialize_from_file()

class FastConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("FAST Detector Configuration")
        self.set_comment("Implements the FAST detector")
        self.initialize_from_file()

class MserConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("MSER Detector Configuration")
        self.set_comment("Implements the MSER detector")
        self.initialize_from_file()

class GfttConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("GFTT Detector Configuration")
        self.set_comment("Implements the GFTT detector")
        self.initialize_from_file()

class StarConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("STAR Detector Configuration")
        self.set_comment("Implements the STAR detector")
        self.initialize_from_file()

class HarrisConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("Harris Detector Configuration")
        self.set_comment("Implements the Harris corner detector")
        self.initialize_from_file()

class BlobConfig(_BaseDetectorConfig):
    def __init__(self, file_path):
        _BaseDetectorConfig.__init__(self, file_path, Detector)

        self.set_title("SimpleBlob Detector Configuration")
        self.set_comment("Implements the SimpleBlob detector")
        self.initialize_from_file()