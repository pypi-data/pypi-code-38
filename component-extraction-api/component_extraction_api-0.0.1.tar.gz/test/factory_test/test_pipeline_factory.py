from unittest import TestCase

from runnable_pkg.modules.factory.PipelineFactory import PipelineFactory
from runnable_pkg.modules.factory.ValidatorFactory import ValidatorFactory


class TestPipelineFactory(TestCase):

    def test_pipeline_factory_created_return_true(self):
        pipeline_factory_obj = PipelineFactory()
        self.assertIsInstance(pipeline_factory_obj, PipelineFactory)

    def test_pipeline_factory_created_is_not_validator_factory(self):
        pipeline_factory_obj = PipelineFactory()
        self.assertNotIsInstance(pipeline_factory_obj, ValidatorFactory)