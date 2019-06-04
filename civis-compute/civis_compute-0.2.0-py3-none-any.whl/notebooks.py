from __future__ import print_function
from __future__ import division

import nbformat
import nbconvert


def _reformat_notebook(script):
    """convert a notebook to a script and remove jupyter magics

    Parameters
    ----------
    script : str
        The path to the Jupyter notebook

    Returns
    -------
    code : str
        The notebook as a python script.
    """
    nb = nbformat.read(script, nbformat.NO_CONVERT)
    code = nbconvert.export(nbconvert.PythonExporter(), nb)[0]

    new_code = []
    for line in code.split('\n'):
        # Exclude magics - HACK - TODO

        # Matthew R. Becker 2/27/2017
        # So this one is tough. The following magics
        #
        #    %matplotlib inline
        #    %matplotlib notebook
        #
        # are only available in jupyter.
        # When notebooks are converted to scripts currently (2/17/2017 w/
        # version 5.1.1 of nbconvert), these magics are left in the notebook
        # as normal ipython magics. However, they cannot be executed by
        # ipython and cause an error. There is an open issue in nbconvert to
        # exclude these things
        # (see https://github.com/jupyter/nbconvert/pull/507). Until this
        # issue is addressed, we have to parse them out by hand.

        # The block of code here does the following.
        # 1) finds jupyter magics at any indentation level (they CAN be
        #    indented!)
        # 2) replaces them with `pass` in python (which does nothing) at the
        #    same indentation level
        if not (line.strip().startswith("get_ipython().magic("
                                        "'matplotlib") or
                line.strip().startswith("get_ipython().run_line_magic("
                                        "'matplotlib") or
                # python 2 - ugh
                line.strip().startswith("get_ipython().magic("
                                        "u'matplotlib") or
                line.strip().startswith("get_ipython().run_line_magic("
                                        "u'matplotlib")):
            new_code.append(line)
        else:
            new_code.append(line[:-len(line.lstrip())] + 'pass')
    return '\n'.join(new_code)
