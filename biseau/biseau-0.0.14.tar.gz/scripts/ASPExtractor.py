# encoding: utf8
"""Allow user to export (some parts of) the ASP program into a file.

"""

import os
import clyngor
from functools import partial


NAME = 'ASP Extractor'
TAGS = {'utils'}
INPUTS = {}
OUTPUTS = {}

DEFAULT_SHOWS = """% Let the #show begin:
#show link/2.


"""
DEFAULT_EXPORT_FILE = 'extraction.lp'
with open(DEFAULT_EXPORT_FILE, 'ab') as fd:
    pass  # make sure that it exists



def run_on(context:str, *, shows:str=DEFAULT_SHOWS, export_file:(open, 'w')=DEFAULT_EXPORT_FILE):
    """
    shows -- ASP lines that will be used to export, but will not be added to the context
    export_file -- name of the file to export to. If it contains an '{}', each model will generate its own file

    """
    try:
        if not export_file: return context
        models = clyngor.solve((), inline=context + '\n' + shows).atoms_as_string.careful_parsing
        istemplate = isinstance(export_file, str) and '{}' in export_file
        if not istemplate:  # empty it before writing it
            with open(export_file, 'w') as fd:
                pass

        for idx, model in enumerate(models):
            fname = export_file.format(idx) if istemplate else export_file
            with open(fname, 'w' if istemplate else 'a') as fd:
                fd.write('\n\n%% MODEL {}:\n'.format(idx))
                fd.write(''.join(atom + '.\n' for atom in model))
    except clyngor.ASPSyntaxError as err:
        raise err
    except clyngor.utils.ASPSyntaxError as err:
        print('This is specifically coming from utils module ; wtf?!')
        raise err
    return context
