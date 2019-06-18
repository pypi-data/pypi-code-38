import pytest
from lantern_sl.utils.dynamo import unique_id


@pytest.mark.parametrize("custom_id, expected", [
        (unique_id(), True),
        (unique_id(), True),
        (unique_id(), True),
    ])
def test_unique_id(custom_id, expected):
    assert (type(custom_id) == str) == expected, "New Id is String"
    assert (len(custom_id) == 32) == expected, "New Id has size==32"
