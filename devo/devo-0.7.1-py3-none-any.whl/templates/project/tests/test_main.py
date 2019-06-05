import pytest


def test_main():
    assert True


@pytest.mark.xfail()
def test_fails():
    assert False
