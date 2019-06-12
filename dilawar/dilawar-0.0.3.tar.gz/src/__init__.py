"""ajgar.py: Main module.

"""
from __future__ import print_function, division
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

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

# random module.
from .random import Random
random = Random( )
