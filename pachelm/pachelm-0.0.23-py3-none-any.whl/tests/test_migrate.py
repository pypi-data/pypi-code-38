import pytest
from pachelm.migration import PachydermMigration

updated_config_path = './tests/updated_configs/2019_06_04_221735_test-pipeline_pipeline_test-pipeline.json'

def test_get_pipeline(ctx):
    emptyMigration = PachydermMigration(ctx)
    assert emptyMigration.get_pipeline('test-pipeline') != None

def test_get_repo(ctx):
    emptyMigration = PachydermMigration(ctx)
    assert emptyMigration.get_repo('test-input') != None

def test_not_exist_pipeline(ctx):
    emptyMigration = PachydermMigration(ctx)
    assert emptyMigration.get_pipeline('not-existed-pipeline') == None

def test_not_exist_repo(ctx):
    emptyMigration = PachydermMigration(ctx)
    assert emptyMigration.get_repo('not-existed-repo') == None

def test_diff_and_has_changed(ctx):
    emptyMigration = PachydermMigration(ctx)
    testPipeline = emptyMigration.get_pipeline('test-pipeline')
    diff = emptyMigration._diff('test-pipeline', updated_config_path)
    has_changed = emptyMigration._has_pipeline_config_changed('test-pipeline', updated_config_path)
    expected_changed = {
        'values_changed': {
            "root['parallelism_spec']['constant']": {
                'new_value': 3,
                'old_value': 1
            }
        }
    }
    assert diff == expected_changed
    assert has_changed == True

def test_none_diff_compare_to_current_config(ctx):
    emptyMigration = PachydermMigration(ctx)
    diff = emptyMigration._diff('test-pipeline')
    assert diff == {}

def test_is_resource_already_exist(ctx):
    emptyMigration = PachydermMigration(ctx)
    assert emptyMigration.is_resource_already_exist('test-pipeline') == True
    assert emptyMigration.is_resource_already_exist('test-input') == True
    assert emptyMigration.is_resource_already_exist('not-exist') == False

