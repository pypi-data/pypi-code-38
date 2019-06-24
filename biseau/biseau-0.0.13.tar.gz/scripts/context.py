# encoding: utf8
"""Widget helping user picking a formal context to use.

If the choosen file is in ASP format, the data will be output as-is.

"""

import os
import glob
import tempfile
import tkinter as tk
from tkinter import ttk
from biseau import format_converters


NAME = 'Context Picker'
TAGS = {'FCA', 'ASP', 'initial example'}
INPUTS = {}
OUTPUTS = {'rel/2'}


def run_on(context:str, *, fname:open=None):
    """
    file -- the lp/cxt/slf/csv file to open. Must contains valid ASP or FCA format.
    """
    if not fname: return f'% {NAME}: no file given.\n'
    if not os.path.exists(fname): return f'% {NAME}: invalid file name: {fname}.\n'
    delete = False
    if os.path.splitext(fname)[1] != '.lp':
        with tempfile.NamedTemporaryFile('w', suffix='.lp', delete=False) as fd:
            format_converters.convert(fname, fd.name)
            fname = fd.name
            delete = True
    with open(fname) as fd:
        return fd.read()
    if delete:
        os.unlink(fname)
