import pytest
from vcver.scm.base import extract_tag_version


@pytest.mark.parametrize("inp, out", [("v0.1", "0.1"), ("oogabooga", None)])
def test_extract_version(inp, out):
    assert extract_tag_version(inp) == out
