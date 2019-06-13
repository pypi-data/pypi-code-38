# -*- coding: utf-8 -*-
"""
    pyvoiceai public
"""

from .app_voiceprint_api import AppVoicePrintAPI
from .app_client_api import AppClientAPI
from .app_group_api import AppGroupAPI
from .app_auth_api import AppAuthAPI
from .baseapi import BaseAPI
from .log import mylog
from .app_asr_base_api import *
from .app_asr import *

# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
