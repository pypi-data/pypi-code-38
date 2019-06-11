# Copyright 2017 StreamSets Inc.

import logging
import sys

import colorlog


date_fmt = '%Y-%m-%d %I:%M:%S %p'
formatter = (colorlog.ColoredFormatter(
    (
        '%(asctime)s '
        '[%(log_color)s%(levelname)s%(reset)s] '
        '[%(cyan)s%(name)s%(reset)s] '
        '%(message_log_color)s%(message)s'
    ),
    datefmt=date_fmt,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'bold_yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red,bg_white',
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'bold_yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red,bg_white',
        },
    },
    style='%'
) if sys.stdout.isatty() else logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s', date_fmt))

handler = logging.StreamHandler()
handler.setFormatter(formatter)
# Handler is added to the streamsets logger to propagate to both
# the SDK and the Test Framework's loggers.
logger = logging.getLogger('streamsets')
logger.addHandler(handler)
