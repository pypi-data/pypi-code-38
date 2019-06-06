from unittest import TestCase

from runnable_pkg.modules.validators.ConfigValidator import ConfigValidator


class TestConfigValidator(TestCase):

    def test_validator_return_false_if_file_not_json(self):
        config_validator = ConfigValidator()
        data = "image.png"
        self.assertFalse(config_validator.validate(data))

    def test_validator_return_false_if_json_keys_missing(self):
        config_validator = ConfigValidator()
        data = "test.json"
        self.assertFalse(config_validator.validate(data))

    def test_validator_return_false_if_file_not_exists(self):
        config_validator = ConfigValidator()
        data = "wrong path"
        self.assertFalse(config_validator.validate(data))

    def test_validator_return_true_if_file_json_correctly_configured(self):
        config_validator = ConfigValidator()
        data = {
                    "pipelineUnits": {
                        "extractComponents": "image.png",
                        "compareComponents": "test.json"
                    },
                    "pipelineOrder": [
                        "extractComponents",
                        "compareComponents"
                    ]
                }
        self.assertTrue(config_validator.validate(data))

    def test_validator_return_false_if_pipeline_order_fails(self):
        config_validator = ConfigValidator()
        data = "wrongPipelineOrder.json"
        self.assertFalse(config_validator.validate(data))

    def test_validator_return_false_if_pipeline_units_fail(self):
        data = {
                  "pipelineUnits": {
                    "extractComponents": "image.png",
                    "failingTrigger": "failing",
                    "compareComponents": "test.json"
                  },
                  "pipelineOrder": [
                    "extractComponents",
                    "compareComponents"
                  ]
                }

        config_validator = ConfigValidator()
        self.assertFalse(config_validator.validate(data))


