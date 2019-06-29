import matplotlib
import os
if 'DISPLAY' in os.environ and os.environ['DISPLAY'] == ":0":
    try:
        import PyQt5
        matplotlib.use('Qt5Agg', warn=False)
    except ImportError:
        matplotlib.use('Qt4Agg', warn=False)
else:
    matplotlib.use('Agg', warn=False)

from . import files
from . import parser
from . import algorithms
from . import plot
from . import utils
#import gui
