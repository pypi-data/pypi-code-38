from ..tools import *

def test_conversions():
    t = 2454123.123
    assert(bkjd2bjd(bjd2bkjd(t))==t)
    assert(btjd2bjd(bjd2btjd(t))==t)
