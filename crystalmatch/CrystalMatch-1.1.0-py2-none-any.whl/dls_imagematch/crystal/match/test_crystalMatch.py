from pkg_resources import require
require("mock>=1.0.1")
from unittest import TestCase

from mock import create_autospec

from CrystalMatch.dls_imagematch.crystal.align.aligned_images import AlignedImages
from CrystalMatch.dls_imagematch.crystal.match.match import CrystalMatch, CRYSTAL_MATCH_STATUS_STATUS_NOT_SET, \
    CRYSTAL_MATCH_STATUS_OK, CRYSTAL_MATCH_STATUS_FAIL, CrystalMatchStatus, CRYSTAL_MATCH_STATUS_DISABLED
from CrystalMatch.dls_imagematch.feature.match.result import FeatureMatcherResult
from CrystalMatch.dls_imagematch.feature.transform.trs_affine import AffineTransformation
from CrystalMatch.dls_util.shape.point import Point


class TestCrystalMatch(TestCase):
    @staticmethod
    def mock_create_crystal_match(align_offset, resolution, starting_point, perform_poi_match=True):
        mock_aligned_images = create_autospec(AlignedImages)
        mock_aligned_images.pixel_offset.return_value = align_offset
        mock_aligned_images.get_working_resolution.return_value = resolution
        crystal_match = CrystalMatch(starting_point, mock_aligned_images, perform_poi=perform_poi_match)
        return crystal_match

    def test_create_crystal_match(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)

        # Test object starting-state
        self.failUnlessEqual(CRYSTAL_MATCH_STATUS_STATUS_NOT_SET, match.get_status())
        self.failUnlessEqual(starting_point, match.get_poi_image_1())
        self.failUnlessEqual(starting_point + align_offset, match.get_poi_image_2_pre_match())
        self.failUnlessEqual(None, match.get_poi_image_2_matched())
        self.failIf(match.is_success())
        self.failIf(match.has_matched())
        self.failUnlessEqual(None, match.feature_match_result())

    def test_setting_feature_match_generates_poi_in_image_2_reference_space(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5
        mock_transformed_point = Point(12, 34)

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        mock_feature_match, mock_transform = self.mock_feature_match_result_success(mock_transformed_point)
        match.set_feature_match_result(mock_feature_match)

        # Test transform is called on the original poi from image 1
        mock_transform.transform_points.assert_called_once_with([starting_point])

        # Test status of the object after successful match
        self.failUnless(match.is_success())
        self.failUnless(match.has_matched())
        self.failUnlessEqual(CRYSTAL_MATCH_STATUS_OK, match.get_status())
        self.failUnlessEqual(mock_transformed_point, match.get_poi_image_2_matched())

    def test_setting_failed_feature_match_results_in_fail_status(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        mock_feature_match = self.mock_feature_match_result_failure()

        match.set_feature_match_result(mock_feature_match)

        # Test object status
        self.failIf(match.is_success())
        self.failUnless(match.has_matched())
        self.failUnlessEqual(CRYSTAL_MATCH_STATUS_FAIL, match.get_status())
        self.failUnlessEqual(None, match.get_poi_image_2_matched())

    def test_failed_match_returns_poi_with_alignment_transform_applied_and_delta_0(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        mock_feature_match = self.mock_feature_match_result_failure()
        match.set_feature_match_result(mock_feature_match)

        # Test the transformed POI and delta value
        expected_poi_image_2_pre_match = starting_point + align_offset
        self.failIf(match.is_success())
        self.failUnlessEqual(expected_poi_image_2_pre_match, match.get_transformed_poi())
        self.failUnlessEqual(Point(0, 0), match.get_delta())

    def test_delta_value_is_translation_between_points_after_alignment(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5
        mock_transformed_point = Point(12, 34)

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        mock_feature_match, mock_transform = self.mock_feature_match_result_success(mock_transformed_point)
        match.set_feature_match_result(mock_feature_match)

        # Test delta value
        expected_offset = mock_transformed_point - align_offset - starting_point
        self.failUnlessEqual(expected_offset, match.get_delta())

    def test_get_real_world_offset_for_points_of_interest(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5
        mock_transformed_point = Point(12, 34)

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        mock_feature_match, mock_transform = self.mock_feature_match_result_success(mock_transformed_point)
        match.set_feature_match_result(mock_feature_match)

        # Test
        self.failUnlessEqual(starting_point * resolution, match.get_poi_image_1_real())
        self.failUnlessEqual(mock_transformed_point * resolution, match.get_poi_image_2_matched_real())
        # self.fail()

    def test_crystal_match_status_print_format(self):
        self.failUnlessEqual("code, status", str(CrystalMatchStatus("code", "status")))
        self.failUnlessEqual("-1, NOT SET", str(CRYSTAL_MATCH_STATUS_STATUS_NOT_SET))
        self.failUnlessEqual("1, OK", str(CRYSTAL_MATCH_STATUS_OK))
        self.failUnlessEqual("0, FAIL", str(CRYSTAL_MATCH_STATUS_FAIL))
        self.failUnlessEqual("2, DISABLED", str(CRYSTAL_MATCH_STATUS_DISABLED))

    def test_crystal_match_status_default_status_is_enabled(self):
        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point)
        self.failUnlessEqual(CRYSTAL_MATCH_STATUS_STATUS_NOT_SET, match.get_status())

    def test_crystal_match_status_can_be_set_to_disabled(self):

        starting_point = Point(4, 7)
        align_offset = Point(2, 2)
        resolution = 1.5

        match = self.mock_create_crystal_match(align_offset, resolution, starting_point, perform_poi_match=False)
        self.failUnlessEqual(CRYSTAL_MATCH_STATUS_DISABLED, match.get_status())

    @staticmethod
    def mock_feature_match_result_failure():
        mock_feature_match = create_autospec(FeatureMatcherResult)
        mock_feature_match.transform.return_value = None  # Denotes failure
        return mock_feature_match

    @staticmethod
    def mock_feature_match_result_success(mock_transformed_point):
        mock_feature_match = create_autospec(FeatureMatcherResult)
        mock_transform = create_autospec(AffineTransformation)
        mock_transform.transform_points.return_value = [mock_transformed_point]
        mock_feature_match.transform.return_value = mock_transform
        return mock_feature_match, mock_transform
