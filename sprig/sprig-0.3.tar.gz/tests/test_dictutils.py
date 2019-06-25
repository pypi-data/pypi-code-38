from sprig import dictutils

import pytest

deflated_examples = [
    {
        'a/i': 11,
        'a/j': 13,
        'b/i/x': '17'
    },  # Arbitrary tree
]


@pytest.mark.parametrize('deflated_before', deflated_examples)
def test_deflate_reverses_inflate(deflated_before):
    inflated_before = dictutils.inflate(deflated_before)
    deflated_after = dictutils.deflate(inflated_before)
    assert deflated_before == deflated_after
