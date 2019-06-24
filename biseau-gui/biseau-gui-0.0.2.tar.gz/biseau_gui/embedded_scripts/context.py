# encoding: utf8
"""Widget helping user picking a formal context to use.

If the choosen file is in ASP format, the data will be output as-is.

"""

import os
import glob
import tempfile

import rofetta


NAME = 'Context Picker'
TAGS = {'FCA', 'ASP', 'initial example'}
INPUTS = {}
OUTPUTS = {'rel/2'}

CONTEXTS_GLOB = 'contexts/*.[ctxsvlp]*'


def compute_context(fname:str) -> str:
    """Return the Context object describing the context in given file"""
    if not fname.endswith('.lp'):
        with tempfile.NamedTemporaryFile('w', suffix='.lp', delete=False) as fd:
            rofetta.convert(fname, fd.name)
            fname = fd.name
    with open(fname) as fd:
        return fd.read()


def run_on(context:str, *, context_file:open=''):
    """Return the ASP source code describing the context"""
    if not os.path.exists(context_file):  return ''
    new_context = compute_context(context_file)
    if new_context:
        return '\n\n% Context encoding\n' + new_context
    else:
        return '\n\n% Context was not choosen by user.'
