"""Analysis of discrete-event models governed by timers."""

__version__ = '0.0.1'
__title__ = 'oris'
__url__ = 'https://www.oris-tool.org/python'
__author__ = 'Marco Paolieri'
__email__ = 'paolieri@oris-tool.org'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright (C) 2019 Marco Paolieri'
__description__ = __doc__.split('\n')[0]


from .utils import set_logging
# from models import *  # NOQA

set_logging('WARNING')
