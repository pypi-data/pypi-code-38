import pytest
from pachelm.migration import PachydermMigration

# need to test all find methods
examplePipeline = {'time': 1559661455.0, 'resource': 'example-pipeline', 'resource_type': 'pipeline', 'migration': 'example-pipeline', 'class_name': 'ExamplePipeline', 'extension': 'py', 'path': './tests/migrations/2019_06_04_221735_example-pipeline_pipeline_example-pipeline.py'}
examplePipelineConfig = {'time': 1559661455.0, 'resource': 'example-pipeline', 'resource_type': 'pipeline', 'migration': 'example-pipeline', 'class_name': 'ExamplePipeline', 'extension': 'json', 'path': './tests/configs/2019_06_04_221735_example-pipeline_pipeline_example-pipeline.json'}

def test_find_pipeline_config(example_ctx):
    assert example_ctx.find_pipeline_config('example-pipeline') == examplePipelineConfig

def test_find_migration(example_ctx):
    assert example_ctx.find_migration('example-pipeline') == examplePipeline

def test_lookup(example_ctx):
    assert len(example_ctx.migrations) == 4
    assert len(example_ctx.pachydermConfigs) == 2
