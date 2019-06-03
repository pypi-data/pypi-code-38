from imagine_client_py.utils import normalize_metadata_headers
import pytest


@pytest.mark.parametrize("test_input,expected",
                         [
                             ({'foo': 'foo'}, {'x-imagine-meta-foo': 'foo'}),
                             ({'bar': 'bar'}, {'x-imagine-meta-bar': 'bar'}),
                             ({'x-imagine-meta-dog': 42}, {'x-imagine-meta-dog': 42}),
                             ({'x-imagine-meta-cat': 'cat'}, {'x-imagine-meta-cat': 'cat'}),
                             ({'X-IMAGINE-META-CAPS': 'AHHHHH'}, {'x-imagine-meta-caps': 'AHHHHH'})
                         ])
def test_utilities_normalize_metadata_headers(test_input, expected):
    assert(normalize_metadata_headers(test_input) == expected)
