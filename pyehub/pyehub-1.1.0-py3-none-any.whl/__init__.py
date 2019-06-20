"""
The package of everything EHub related.
"""
import os
import sys
import inspect

# import pyehub
# name = "pyehub"

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(CURRENT_DIR)
