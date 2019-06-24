# encoding: utf8
"""Load lp file knowing its path.

"""
import tkinter as tk
import tkinter.filedialog
from functools import partial

NAME = 'Open lp file'
TAGS = {'ASP', 'utils'}


INPUTS = {}
OUTPUTS = {}  # in fact, we do not know. Sorry.

OPEN_LP_FILE = partial(tk.filedialog.askopenfilename, defaultextension='.lp')


def run_on(context:str, *, file:OPEN_LP_FILE=None):
    """
    file -- the lp file to open. Must contains valid ASP.
    """
    if file:
        with open(file) as fd:
            yield fd.read()
