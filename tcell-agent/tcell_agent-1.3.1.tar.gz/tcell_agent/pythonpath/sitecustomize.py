"""
tCell Agent

This agent communicates with the tCell service and instruments your
application.
"""

from __future__ import unicode_literals

import imp
import os
import sys


def find_dotted_module(name, path=None):
    """
    Example: find_dotted_module("mypackage.myfile")

    Background: imp.find_module() does not handle hierarchical module names (names containing dots).

    Important: No code of the module gets executed. The module does not get loaded (on purpose)
    ImportError gets raised if the module can't be found.

    Use case: Test discovery without loading (otherwise coverage does not see the lines which are executed
              at import time)
    """

    for x in name.split("."):
        if path is not None:
            path = [path]
        file, path, descr = imp.find_module(x, path)
    return file, path, descr


tcell_pythonpath = os.path.dirname(__file__)
path = list(sys.path)
if tcell_pythonpath in path:
    del path[path.index(tcell_pythonpath)]

for p in path:
    try:
        if "newrelic" not in p:
            (file, pathname, description) = find_dotted_module("sitecustomize", p)

            imp.load_module("sitecustomize", file, pathname, description)
            break
    except Exception:
        pass


"""
Entrypoint for the TCellAgent when it gets called from the
command line utility: `tcell_agent run`.

Example command for a django app:

    $ tcell_agent run python manage.py run 0.0.0.0:8000
"""
from tcell_agent.instrumentation.startup import instrument
instrument()
