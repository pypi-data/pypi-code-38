from unittest import TestCase

from runnable_pkg.modules.validators.ImageValidator import ImageValidator


class TestImageValidator(TestCase):

    def test_image_validator_return_false_if_image_not_correct_format(self):
        image_validator = ImageValidator()
        image_validator.set_file("test.config")
        self.assertFalse(image_validator.validate(image_validator.get_file()))

    def test_image_validator_return_false_if_image_not_exists(self):
        image_validator = ImageValidator()
        image_validator.set_file("wrong path")
        self.assertFalse(image_validator.validate(image_validator.get_file()))

    def test_image_validator_return_true_if_image_is_valid(self):
        image_validator = ImageValidator()
        image_validator.set_file("image.png")
        self.assertTrue(image_validator.validate(image_validator.get_file()))