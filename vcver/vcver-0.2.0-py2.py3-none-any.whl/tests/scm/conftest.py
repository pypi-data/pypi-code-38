import os
import sys
import pytest

ALL = set("darwin linux win32".split())


def pytest_runtest_setup(item):
    supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
    plat = sys.platform
    if "darwin" in plat:
        plat = "linux"
    if supported_platforms and plat not in supported_platforms:
        pytest.skip("cannot run on platform %s" % (plat))


@pytest.fixture()
def no_fs(monkeypatch):
    def mockreturn(path):
        return False

    monkeypatch.setattr(os.path, "exists", mockreturn)
