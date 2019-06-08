from __future__ import absolute_import
import os
from .version import __VERSION__ as __version__
from .io import *
from .aliases import *

here = __file__
basedir = os.path.split(here)[0]
example_data = os.path.join(basedir, 'example_data')


# Optional packages
# try:
#     from .visualization import *
# except ImportError as e:
#     print('Some imports failed, which implies some dependencies are missing as described below')
