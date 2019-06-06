from unittest import TestCase

from runnable_pkg.modules.validators.IPUValidator import IPUValidator


class TestIPUValidator(TestCase):

    def test_validator_return_true_if_pipeline_keys_match_class_names(self):
        ipu_validator = IPUValidator()
        self.assertTrue(ipu_validator.validate("correct_ipu.json"))

    def test_validator_return_false_if_pipeline_keys_dont_match_class_name(self):
        ipu_validator = IPUValidator()
        self.assertFalse(ipu_validator.validate("wrong_ipu.json"))
