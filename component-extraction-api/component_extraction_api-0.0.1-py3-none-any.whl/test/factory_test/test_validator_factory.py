from unittest import TestCase

from runnable_pkg.modules.factory.ValidatorFactory import ValidatorFactory
from runnable_pkg.modules.validators.ConfigValidator import ConfigValidator
from runnable_pkg.modules.validators.ImageValidator import ImageValidator


class TestValidatorFactory(TestCase):

    def test_image_validator_return_true(self):
        validator_factory = ValidatorFactory()
        image_validator_obj = validator_factory.create_image_validator()
        self.assertIsInstance(image_validator_obj, ImageValidator)

    def test_image_validator_return_false(self):
        validator_factory = ValidatorFactory()
        image_validator_obj = validator_factory.create_image_validator()
        self.assertNotIsInstance(image_validator_obj, ConfigValidator)

    def test_config_validator_return_true(self):
        validator_factory = ValidatorFactory()
        config_validator_obj = validator_factory.create_config_validator()
        self.assertIsInstance(config_validator_obj, ConfigValidator)

    def test_config_validator_return_false(self):
        validator_factory = ValidatorFactory()
        config_validator_obj = validator_factory.create_config_validator()
        self.assertNotIsInstance(config_validator_obj, ImageValidator)



