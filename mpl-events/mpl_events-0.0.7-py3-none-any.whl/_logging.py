# -*- coding: utf-8 -*-

import logging

LOGGER_NAME = 'mpl_events'

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.NullHandler())
