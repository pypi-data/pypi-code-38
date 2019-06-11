#!/usr/bin/env python
import pytest 
from nuphy import main
#from nuphy.nubase import nubase
  
def test_1():
    assert main.mainfunc()==True
#def test_2():
#    assert nubase.unitfunc()==True
