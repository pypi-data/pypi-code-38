"""test_dfUlg."""
from context import DfUlg
import pytest


def test_file_does_not_exist():
    """test for non-existing file."""
    file = "mickeymouse_file.ulg"
    with pytest.raises(Exception):
        DfUlg._check_file(file)


def test_file_is_not_ulg():
    """test for file that is not ulg."""
    file = "testlogs/no_ulg.txt"
    with pytest.raises(Exception):
        DfUlg._check_file(file)


def test_existing_file():
    """test for file that exists."""
    file = "testlogs/position.ulg"
    DfUlg._check_file(file)
