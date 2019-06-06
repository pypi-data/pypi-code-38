from unittest import TestCase

from runnable_pkg.modules.pipeline.Pipeline import Pipeline
from runnable_pkg.modules.pipeline.PipelineRunner import PipelineRunner
from runnable_pkg.test.pipeline_test.myIPUHello import myIPUHello


class TestPipelineIterator(TestCase):

    def test_next_method_returns_correct_execution_of_pipeline_units(self):
        my_test = myIPUHello()
        pipeline = Pipeline([my_test])
        pipeline_runner = PipelineRunner(pipeline)
        self.assertEqual(pipeline_runner.execute_pipeline([]), {"Hello": ""})

    def test_next_method_returns_false_to_incorrect_execution_of_pipeline_units(self):
        my_test = myIPUHello()
        pipeline = Pipeline([my_test])
        pipeline_runner = PipelineRunner(pipeline)
        self.assertNotEqual(pipeline_runner.execute_pipeline([]), {"Fail": ""})
