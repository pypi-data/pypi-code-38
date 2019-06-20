import pytest

from ..validation import _validate_start_end


def test_normal():
    _validate_start_end(1, 3)


def test_end_smaller_than_start():
    with pytest.raises(ValueError):
        _validate_start_end(18, 10)
