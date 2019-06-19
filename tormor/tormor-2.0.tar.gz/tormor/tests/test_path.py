from tormor.path_helper import get_schema_path
from tormor.exceptions import SchemaPathNotFound
import pytest, os

def test_get_schema_path_exist():
    current_path = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(current_path, "Schema")
    os.environ['SCHEMA_PATH'] = schema_path
    expected_result = schema_path
    actual_result = get_schema_path()
    os.environ.pop('SCHEMA_PATH')
    assert actual_result == [expected_result]

def test_get_schema_path_exist_not_exist():
    paths = get_schema_path()
    match = [each_path for each_path in paths if "/test/Schema2" or "/test/Schema" in each_path]
    assert match