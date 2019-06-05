from pkg_resources import require
require("mock>=1.0.1")
from unittest import TestCase

from mock import create_autospec, MagicMock, patch

from CrystalMatch.dls_imagematch.crystal.align.aligned_images import AlignedImages
from CrystalMatch.dls_imagematch.crystal.align.aligner import ImageAligner
from CrystalMatch.dls_imagematch.crystal.align.exception import ImageAlignmentError
from CrystalMatch.dls_imagematch.crystal.align.sized_image import SizedImage
from CrystalMatch.dls_imagematch.feature.detector.config import DetectorConfig
from CrystalMatch.dls_imagematch.feature.detector.exception import FeatureDetectorError
from CrystalMatch.dls_util.shape.point import Point


class TestImageAligner(TestCase):
    @staticmethod
    def create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size):
        image1 = create_autospec(SizedImage)
        image1.pixel_size = MagicMock(return_value=image_1_pixel_size)
        image2 = create_autospec(SizedImage)
        image2.pixel_size = MagicMock(return_value=image_2_pixel_size)
        align_config = MagicMock()
        align_config.pixel_size_1.value = MagicMock(return_value=image_1_pixel_size)
        align_config.pixel_size_2.value = MagicMock(return_value=image_2_pixel_size)
        SizedImage.from_image = MagicMock()
        SizedImage.from_image.side_effect = [image1, image2]
        aligner = ImageAligner(image1, image2, align_config)
        return aligner, image1, image2

    def test_aligner_cannot_be_created_without_setting_config_file(self):
        # Setup
        image1 = create_autospec(SizedImage, spec_set=True)
        image2 = create_autospec(SizedImage, spec_set=True)
        self.failUnlessRaises(AssertionError, ImageAligner, image1, image2, None)

    def test_smaller_image_1_is_rescaled_to_size_of_image_2(self):
        # Setup
        image_1_pixel_size = 2.5
        image_2_pixel_size = 5.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size)

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        #image2.rescale.assert_not_called() # for newer versions

    def test_larger_image_1_is_rescaled_to_size_of_image_2(self):
        # Setup
        image_1_pixel_size = 6.0
        image_2_pixel_size = 3.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size, image_2_pixel_size)

        # Test image1 is rescaled
        scale_factor = image_1_pixel_size / image_2_pixel_size
        image1.rescale.assert_called_with(scale_factor)

        # Test image2 is not rescaled
        #image2.rescale.assert_not_called()

    def test_that_resolution_is_taken_from_image_2(self):
        # Setup
        image_1_pixel_size = 6.0
        image_2_pixel_size = 3.0

        # Run Test
        aligner, image1, image2 = self.create_aligner_with_mock_images(image_1_pixel_size,
                                                                       image_2_pixel_size)

        # Test internal value for resolution after initial config
        self.failUnlessEqual(image_2_pixel_size, aligner._resolution, "Resolution not set to pixel_size of image 2.")

    def test_array_of_points_scaled_by_image_1_scale_factor_greater_than_1(self):
        aligner, image1, image2 = self.create_aligner_with_mock_images(1.0, 0.5)
        input_array = [Point(4, 7), Point(277, 568)]
        expected = [Point(8, 14), Point(554, 1136)]

        # Test
        self.failUnlessEqual(expected, aligner.scale_points(input_array))

    def test_array_of_points_scaled_by_image_1_scale_factor_less_than_1(self):
        aligner, image1, image2 = self.create_aligner_with_mock_images(0.5, 1.0)
        input_array = [Point(4, 7), Point(277, 568)]
        expected = [Point(2, 3.5), Point(138.5, 284)]

        # Test
        self.failUnlessEqual(expected, aligner.scale_points(input_array))

    def test_array_of_points_scaled_by_image_1_scale_factor_equal_to_0(self):
        aligner, image1, image2 = self.create_aligner_with_mock_images(0.5, 0.5)
        input_array = [Point(4, 7), Point(277, 568)]
        expected = [Point(4, 7), Point(277, 568)]

        # Test
        self.failUnlessEqual(expected, aligner.scale_points(input_array))

    def test_align_images_fails_when_detector_config_not_set(self):
        aligner, image1, image2 = self.create_aligner_with_mock_images(0.5, 0.5)
        self.failUnlessRaises(ImageAlignmentError, aligner.align)

    def test_align_images_fails_when_detector_config_not_recognised(self):
        aligner, image1, image2 = self.create_aligner_with_mock_images(0.5, 0.5)
        aligner.set_detector_config(create_autospec(DetectorConfig))
        self.failUnlessRaises(FeatureDetectorError, aligner.align)

    # noinspection PyUnusedLocal
    @patch("CrystalMatch.dls_imagematch.feature.FeatureMatcher.set_detector")
    @patch("CrystalMatch.dls_imagematch.feature.FeatureMatcher.match_translation_only")
    def test_smoke_test_align_images(self, mock_set_detector, mock_match_translation_only):
        """ Dev Note: the logic here is not easy to unit test - system tests will cover this more accurately. """
        # FeatureMatcher.set_detector = MagicMock()
        aligner, image1, image2 = self.create_aligner_with_mock_images(2.0, 0.5)
        aligner.set_detector_config(create_autospec(DetectorConfig))
        aligned_images = aligner.align()

        # Test
        self.failUnless(isinstance(aligned_images, AlignedImages))
        self.failIfEqual(image1, aligned_images.image1)  # This should have been rescaled
        self.failUnlessEqual(image2, aligned_images.image2)
        self.failUnlessEqual(4, aligned_images._scale_factor)
        self.failUnlessEqual(0.5, aligned_images.get_working_resolution())
