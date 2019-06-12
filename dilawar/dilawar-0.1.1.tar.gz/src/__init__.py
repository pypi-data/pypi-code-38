"""ajgar.py: Main module.

"""
from __future__ import print_function, division, absolute_import
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__license__          = "GNU GPL"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"

try:
    # This depends on scipy
    from .data_analysis import *
except ImportError as e:
    pass

from .text_processing import *
from .file_utils import *
from .plot_utils import *
from .statistics import *
from .information_theory import *
from .io_utils import *
from .logger import *
