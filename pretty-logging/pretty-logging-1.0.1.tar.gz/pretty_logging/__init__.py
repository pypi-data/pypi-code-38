# -*- coding:utf-8 -*-

from .log import enable_pretty_logging
import logging

pretty_logger = logging.getLogger('pretty_logger')

enable_pretty_logging(logger=pretty_logger)

pretty_logger.setLevel(logging.DEBUG)
