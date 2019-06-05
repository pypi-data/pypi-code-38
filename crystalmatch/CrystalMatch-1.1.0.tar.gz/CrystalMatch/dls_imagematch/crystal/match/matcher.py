from __future__ import division

from CrystalMatch.dls_focusstack.focus.point_fft_manager import PointFFTManager
from CrystalMatch.dls_util.shape import Rectangle, Point
from CrystalMatch.dls_imagematch.feature import BoundedFeatureMatcher
from CrystalMatch.dls_imagematch.crystal.match.match import CrystalMatch
from .results import CrystalMatcherResults


class CrystalMatcher:
    DEFAULT_REGION_SIZE = 100
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 400
    DEFAULT_VERTICAL_SHIFT = 0.75
    DEFAULT_Z_LEVEL_REGION_SIZE = 80

    def __init__(self, aligned_images, detector_config, crystal_config=None):
        self._perform_poi_analysis = True
        self._aligned_images = aligned_images
        self._region_size_real = self.DEFAULT_REGION_SIZE
        self._search_width_real = self.DEFAULT_WIDTH
        self._search_height_real = self.DEFAULT_HEIGHT
        self._search_vertical_shift = self.DEFAULT_VERTICAL_SHIFT
        self._z_level_region_size_real = self.DEFAULT_Z_LEVEL_REGION_SIZE
        self._transform_method = None
        self._transform_filter = None
        self._fft_images = None

        self._detector_config = detector_config
        if crystal_config is not None:
            self.set_from_crystal_config(crystal_config)

    # -------- CONFIGURATION -------------------
    def set_from_crystal_config(self, config):
        self._perform_poi_analysis = config.active_status.value()
        self._region_size_real = config.region_size.value()
        self._search_width_real = config.search_width.value()
        self._search_height_real = config.search_height.value()
        self._search_vertical_shift = config.vertical_shift.value()
        self._transform_method = config.transform_method.value()
        self._transform_filter = config.transform_filter.value()
        self._z_level_region_size_real = config.z_level_region_size.value()

    def set_detector_config(self, config):
        self._detector_config = config

    def set_real_region_size(self, size):
        self._region_size_real = size

    def set_real_z_level_region_size(self, size):
        self._z_level_region_size_real = size

    def set_real_search_size(self, width, height):
        self._search_width_real = width
        self._search_height_real = height

    def set_search_shift(self, value):
        self._search_vertical_shift = value

    def set_transform_method(self, method):
        self._transform_method = method

    def set_transform_filter(self, filter_obj):
        self._transform_filter = filter_obj

    def set_fft_images_to_stack(self, fft_images):
        self._fft_images = fft_images

    # -------- FUNCTIONALITY -------------------
    def match(self, image1_points):
        images = self._aligned_images
        match_results = CrystalMatcherResults(images)

        crystal_id = 1
        for point in image1_points:
            result = self._match_single_point(point)
            #find z-level
            z_level = PointFFTManager(self._fft_images, result.get_transformed_poi(), self._z_level_region_size_real).find_z_level_for_point()
            result.set_poi_z_level(z_level)
            result.print_to_log(crystal_id=crystal_id)
            match_results.append_match(result)
            crystal_id += 1

        return match_results

    def _match_single_point(self, point):
        crystal_match = CrystalMatch(point, self._aligned_images, perform_poi=self._perform_poi_analysis)


        if self._perform_poi_analysis:
            image1_rect = self.make_target_region(crystal_match.get_poi_image_1())
            image2_rect = self.make_search_region(crystal_match.get_poi_image_2_pre_match())

            feature_matcher = BoundedFeatureMatcher(self._aligned_images.image1.to_mono(),
                                                    self._aligned_images.image2.to_mono(),
                                                    self._detector_config,
                                                    image1_rect,
                                                    image2_rect)

            self._perform_match(feature_matcher, crystal_match)

        return crystal_match

    def _perform_match(self, feature_matcher, crystal_match):
        feature_matcher.set_use_all_detectors()
        feature_matcher.set_transform_method(self._transform_method)
        feature_matcher.set_transform_filter(self._transform_filter)

        result = feature_matcher.match()
        crystal_match.set_feature_match_result(result)

    def make_target_region(self, center):
        size = self._region_size_pixels()
        return Rectangle.from_center(center, size, size)

    def make_search_region(self, centre_point):
        """ Define a rectangle on image B in which to search for the matching crystal. Its narrow and tall
        as the crystal is likely to move downwards under the effect of gravity. """
        search_width, search_height = self._search_size_pixels()
        vertical_shift = self._search_vertical_shift

        top_left = centre_point - Point(search_width / 2, search_height * (1 - vertical_shift))
        rect = Rectangle.from_corner(top_left, search_width, search_height)

        rect = rect.intersection(self._aligned_images.image2.bounds())
        return rect

    def _region_size_pixels(self):
        return self._region_size_real / self._aligned_images.get_working_resolution()

    def _search_size_pixels(self):
        width = self._search_width_real / self._aligned_images.get_working_resolution()
        height = self._search_height_real / self._aligned_images.get_working_resolution()
        return width, height
