# encoding: utf8
"""Load lp file knowing its path.

"""
import tkinter as tk
import tkinter.filedialog
from functools import partial

NAME = 'Open lp file'
TAGS = {'ASP', 'utils'}


INPUTS = {}
OUTPUTS = {'*/*'}  # can't predict


def run_on(context:str, *, file:(open, 'r')=None):
    """
    file -- the lp file to open. Must contains valid ASP.
    """
    if file:
        with open(file) as fd:
            yield fd.read()
