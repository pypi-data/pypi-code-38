import pytest


def test_raises_error():
    with pytest.raises(ImportError):
        from directory_cms_client import constants  # NOQA
