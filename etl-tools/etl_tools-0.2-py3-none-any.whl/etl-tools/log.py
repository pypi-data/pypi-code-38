from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from datetime import datetime

import logging
import logging.config


def set_logger(logfile_name, log_dir_path):
    log_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'log.conf')
    logfile = os.path.join(log_dir_path, logfile_name + '.txt')
    logging.config.fileConfig(
        log_file_path, defaults={'logfilename': logfile})
    logger = logging.getLogger('etl')
    return logger, logfile
