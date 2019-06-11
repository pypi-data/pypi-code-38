"""
Handles logging setup

Set the DSDK_LOG_CFG environment variable to set a custom path to a JSON
logging config file

Set the DSDK_LOG_STDOUT environment variable to a level (eg: debug, info) to
also send logging to STDOUT at the specified logging level

Logs are rotated after reaching 50 MB (default, configurable in
debug_logging.json) and compressed (gz) after rotation
"""
import gzip
import io
import json
import logging
import logging.config
import logging.handlers
import os
import sys
import shutil


from .constants import PYTHON_2_7_0_HEXVERSION

LOGDIR = 'log_cfg'
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOGDIR)
DEBUG_LOG = os.path.join(DIR, 'debug_logging.json')
INFO_LOG = os.path.join(DIR, 'info_logging.json')
ERROR_LOG = os.path.join(DIR, 'error_logging.json')
DISABLE = 'disable'


LOGS = {'debug': DEBUG_LOG,
        'info': INFO_LOG,
        'error': ERROR_LOG}


def get_log(name):
    log = logging.getLogger(name)
    if sys.hexversion >= PYTHON_2_7_0_HEXVERSION:
        if not log.handlers:
            log.addHandler(logging.NullHandler())
    return log


def setup_logging(disable=False):
    path = os.getenv('DSDK_LOG_CFG', DEBUG_LOG)
    # Allows for disabling all logging config by the library
    # This is meant to prevent messing with any top-level logging configs
    # Using the library
    if disable or path.lower() == DISABLE:
        return
    if path in LOGS:
        path = LOGS[path]
    if not os.path.exists(path):
        io.open(path, 'w+').close()
    with io.open(path) as f:
        j = json.load(f)
        logging.config.dictConfig(j)
    stdout = os.getenv('DSDK_LOG_STDOUT', None)
    if stdout:
        add_stdout(stdout)


def add_stdout(level):
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, level.upper()))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


class CompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, **kwargs):
        self.delay = kwargs.get('delay', None)
        backupCount = kwargs.get('backupCount', 0)
        self.backup_count = backupCount
        logging.handlers.RotatingFileHandler.__init__(self, filename, **kwargs)

    def doArchive(self, old_log):
        with io.open(old_log, 'rb') as log, \
                gzip.open(old_log + '.gz', 'wb') as comp_log:
            shutil.copyfileobj(log, comp_log)
        os.remove(old_log)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backup_count > 0:
            for index in range(self.backup_count - 1, 0, -1):
                sfn = "{}.{}.gz".format(self.baseFilename, index)
                dfn = "{}.{}.gz".format(self.baseFilename, index + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
        dfn = ".".join((self.baseFilename, "1"))
        if os.path.exists(dfn):
            os.remove(dfn)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doArchive(dfn)
        if not self.delay:
            self.stream = self._open()


# Adding this to the main logging module so we can specify
# class: 'logging.CompressedRotatingFileHandler' in our dictConfigs
logging.CompressedRotatingFileHandler = CompressedRotatingFileHandler
