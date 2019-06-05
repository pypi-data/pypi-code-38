from os.path import join

from CrystalMatch.dls_imagematch.feature.detector import DetectorType
from CrystalMatch.dls_util.config.config import Config
from CrystalMatch.dls_util.config.item import EnumConfigItem, BoolConfigItem, RangeFloatConfigItem


class AlignConfig(Config):
    """ Configuration class that contains a number of options for the program. Stores options in a config
    file that can be edited externally to set the values of the options.
    """
    def __init__(self, config_directory, scale_override=None):
        """
        Create an Alignment configuration object from the given config directory.
        :param config_directory:
        :param scale_override: Optionally declare overrides for the pixel sizes - must be a
        tuple of the format ([formulatrix image pixel size], [beam line image pixel size]).
        """
        Config.__init__(self, join(config_directory, "align.ini"))

        add = self.add

        self.set_title("Image Alignment Configuration")
        self.set_comment("Configuration for the initial image alignment process used in the crystal matching, "
                         "including the detector to be used and limits quantifying the quality of the alignment.")

        self.use_alignment = add(BoolConfigItem, "Perform Alignment", True)
        self.use_alignment.set_comment("Automatically perform bulk image alignment using feature matching when a new "
                                       "image is selected. If disabled, the images will just be lined up by the top "
                                       "left corner, which is fine if you know that the images are already lined up. "
                                       "The alignment metric will still be calculated, indicating whether the fit is "
                                       "any good.")

        self.align_detector = add(EnumConfigItem, "Detector", default=DetectorType.ORB, extra_arg=DetectorType.LIST_ALL)
        self.align_detector.set_comment("Feature detection algorithm to be used for the initial image alignment "
                                        "process.")

        self.pixel_size_1 = add(RangeFloatConfigItem, "Pixel Size 1 (um)", default=1.0, extra_arg=[0.01, None])
        self.pixel_size_1.set_comment("The real size (in micrometers) represented by a single pixel in Image 1 (the "
                                      "formulatrix image).")

        self.pixel_size_2 = add(RangeFloatConfigItem, "Pixel Size 2 (um)", default=1.0, extra_arg=[0.01, None])
        self.pixel_size_2.set_comment("The real size (in micrometers) represented by a single pixel in Image 2 (the "
                                      "beamline image).")

        if scale_override is not None:
            self.pixel_size_1.set_override(scale_override[0])
            self.pixel_size_2.set_override(scale_override[1])

        self.metric_limit_low = add(RangeFloatConfigItem, "Metric Limit Low", 30.0, [0.0, None])
        self.metric_limit_low.set_comment("A metric quantifying the quality of the alignment is calculated. If the "
                                          "metric is below this value, it is considered a good fit; if it is above, "
                                          "then the fit is considered poor.")

        self.metric_limit_high = add(RangeFloatConfigItem, "Metric Limit High", 40.0, [0.0, None])
        self.metric_limit_high.set_comment("A metric quantifying the quality of the alignment is calculated. If the "
                                           "metric is below this value, it is considered a poor fit; if it is above, "
                                           "then the fit is considered to have failed totally, i.e. the images are "
                                           "completely dissimilar.")

        self.initialize_from_file()
