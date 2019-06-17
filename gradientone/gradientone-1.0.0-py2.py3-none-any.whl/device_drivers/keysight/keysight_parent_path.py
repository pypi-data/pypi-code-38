from inspect import getsourcefile
import os.path
import sys


# importing 'keysight_parent_path' and calling insert() will
# insert the parent directory of device_drivers to the sys path to make
# the contents available for imports

def insert():
    current_path = os.path.abspath(getsourcefile(lambda: 0))
    current_dir = os.path.dirname(current_path)
    parent_dir = current_dir[:current_dir.rfind(os.path.sep)]
    sys.path.insert(0, parent_dir)
