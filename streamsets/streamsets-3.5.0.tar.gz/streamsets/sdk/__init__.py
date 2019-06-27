# Copyright 2019 StreamSets Inc.

import logging
import os

from .config import USER_CONFIG_PATH
from .sdc import DataCollector
from .sch import ControlHub

__all__ = ['ControlHub', 'DataCollector']

__version__ = '3.5.0'

logger = logging.getLogger(__name__)

activation_path = os.path.join(USER_CONFIG_PATH, 'activation')

if not os.path.exists(activation_path):
    logger.info('Creating user configuration directory at %s ...', USER_CONFIG_PATH)
    os.makedirs(activation_path)
