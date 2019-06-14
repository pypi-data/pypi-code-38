import pytest
import Utils.inputManager as inputManager
from flaky import flaky

def wrap_raw_input(_string):
    return _string

def data_getYesNoAnswer():
    yesData = [("y", True), ("Y", True), ("yes", True), ("Yes", True), ("YeS", True)]
    noData = [("n", False), ("N", False), ("no", False), ("No", False), ("NO", False)]
    return yesData + noData

def data_getInput():
    return [("Test"), ("ravegen"), ("Yes")]

@flaky(3,1)
@pytest.mark.parametrize('_string, expected', data_getYesNoAnswer())
def test_getYesNoAnswer(_string, expected):
    inputManager.raw_input = wrap_raw_input
    assert inputManager.getYesNoAnswer(_string) == expected

@flaky(3,1)
@pytest.mark.parametrize('_val', data_getInput())
def test_getInput(_val):
    inputManager.raw_input = wrap_raw_input
    assert inputManager.getInput(_val) == _val
