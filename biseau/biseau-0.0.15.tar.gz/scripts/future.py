# encoding: utf8
"""Experiments about the scripting API.

"""
import tkinter as tk
from functools import partial

NAME = 'from __future__ import ideas'
DISABLED = True


INPUTS = {}
OUTPUTS = {'user/2'}

LANGUAGES = 'python', 'asp'
OPEN_LP_FILE = partial(tk.filedialog.askopenfilename, default_extension='.lp')
DEFAULT_FILE = '~/programs/biseau/contexts/boolean_3var.lp'

def run_on(context:str, *, coucou_les_copaings:bool=False,
           vas_y_ouvre_moi:OPEN_LP_FILE=DEFAULT_FILE):
    yield context
    if vas_y_ouvre_moi:
        with open(vas_y_ouvre_moi) as fd:
            yield fd.read()
    # yield vas_y_ouvre_moi.read()
    if coucou_les_copaings:
        yield 'rel("copaing","human").'
