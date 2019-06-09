
# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process lobulus analysis.
"""
# import logging
# logger = logging.getLogger(__name__)
from loguru import logger
import sys
import subprocess
import os


def open_path(path):
    """
    Open path (file or dir) in default operation system application.

    :param path:
    :return:
    """
    if sys.platform.startswith('darwin'):
        cmd  = "open"
        # subprocess.call(('open', path))
    elif os.name == 'nt':  # For Windows
        cmd = "start"
        # os.startfile(filepath)
    elif os.name == 'posix':  # For Linux, Mac, etc.
        cmd = "xdg-open"
        # subprocess.call(('xdg-open', filepath))
    else:
        raise EnvironmentError("Unknown OS: " + os.name)

    try:
        retcode = subprocess.call(cmd + " " + str(path), shell=True)
        if retcode < 0:
            logger.error("Child was terminated by signal %i", -retcode)
        else:
            logger.info("Child returned %i", retcode)
    except OSError as e:
        logger.error("Execution failed: %s", e)
        raise e
