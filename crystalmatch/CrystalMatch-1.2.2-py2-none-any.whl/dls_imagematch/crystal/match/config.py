from os.path import join

from CrystalMatch.dls_imagematch.feature import TransformCalculator
from CrystalMatch.dls_util.config.config import Config
from CrystalMatch.dls_util.config.item import BoolConfigItem, EnumConfigItem, RangeIntConfigItem, RangeFloatConfigItem
from CrystalMatch.dls_imagematch.crystal.match.matcher import CrystalMatcher


class CrystalMatchConfig(Config):
    """ Configuration class that contains a number of options for the program. Stores options in a config
    file that can be edited externally to set the values of the options.
    """
    def __init__(self, config_directory):
        Config.__init__(self, join(config_directory, "crystal.ini"))

        add = self.add

        self.set_title("Crystal Matching Configuration")
        self.set_comment("Configuration for the crystal matching process including the size of the image region's "
                         "to be matched and the filter to be used in generating a transformation.")

        trans_methods = TransformCalculator.METHODS
        trans_filters = TransformCalculator.FILTERS
        def_trans = TransformCalculator.DEFAULT_METHOD
        def_filter = TransformCalculator.DEFAULT_FILTER
        def_size = CrystalMatcher.DEFAULT_REGION_SIZE
        def_width = CrystalMatcher.DEFAULT_WIDTH
        def_height = CrystalMatcher.DEFAULT_HEIGHT
        def_shift = CrystalMatcher.DEFAULT_VERTICAL_SHIFT
        def_z_level_region_size = CrystalMatcher.DEFAULT_Z_LEVEL_REGION_SIZE

        self.active_status = add(BoolConfigItem, "Perform POI Analysis", default=True)
        self.active_status.set_comment("If this option is disabled the program shall skip the image matching for "
                                       "individual POI and return results which apply only the Alignment transform "
                                       "instead.")

        self.region_size = add(RangeIntConfigItem, "Region Size (um)", default=def_size, extra_arg=[10, None])
        self.region_size.set_comment("Size of the region around the user selected point in the first image to be "
                                     "considered in the feature matching process.")

        self.z_level_region_size = add(RangeIntConfigItem, "Z Level Region Size (um)", default=def_z_level_region_size, extra_arg=[10, None])
        self.z_level_region_size.set_comment("Size of the region around the user selected point in the first image to be "
                                     "considered in finding z-level for the point.")

        self.search_width = add(RangeIntConfigItem, "Search Width (um)", default=def_width, extra_arg=[50, None])
        self.search_width.set_comment("Width of the region in the second image in which to search in the feature "
                                      "matching process.")

        self.search_height = add(RangeIntConfigItem, "Search Height (um)", default=def_height, extra_arg=[50, None])
        self.search_height.set_comment("Height of the region in the second image in which to search in the feature "
                                       "matching process.")

        self.vertical_shift = add(RangeFloatConfigItem, "Vertical Shift", default=def_shift, extra_arg=[0.0, 1.0])
        self.vertical_shift.set_comment("Controls the vertical position of the search region relative to the projected "
                                        "selected point. A value of 0.5 means the region is centered; 1.0 means the "
                                        "top of the search rectangle will be aligned with the projected point (so the "
                                        "\nsearch region will be below it); and 0.0 means the bottom of the search "
                                        "region will be aligned with the projected point (so the search region will be "
                                        "above it.")

        self.transform_filter = add(EnumConfigItem, "Transform Filter", default=def_filter, extra_arg=trans_filters)
        self.transform_filter.set_comment("Method used to filter out bad matches prior to generating the transform.")

        self.transform_method = add(EnumConfigItem, "Transform Method", default=def_trans, extra_arg=trans_methods)
        self.transform_method.set_comment("Method to be used to generate the transform mapping the crystal in first "
                                          "image to its location in the second image.")

        self.initialize_from_file()
