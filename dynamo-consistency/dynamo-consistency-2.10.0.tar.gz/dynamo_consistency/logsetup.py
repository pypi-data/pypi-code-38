"""
The module that sets up logging for us
"""

import os
import logging

from .parser import OPTS as opts

LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'


if opts.DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
elif opts.INFO:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
else:
    logging.basicConfig(format=LOG_FORMAT)


def change_logfile(*filenames):
    """
    Changes the output file of all of the loggers.
    Creates any directories that are needed to hold the logs.

    :param filenames: The files to write new logs to
    """

    new_hldrs = []

    for name in filenames:
        logdir = os.path.dirname(name)

        if not os.path.exists(logdir):
            os.makedirs(logdir)

        fhdl = logging.FileHandler(name, 'a')
        fhdl.setFormatter(logging.Formatter(LOG_FORMAT))

        new_hldrs.append(fhdl)

    parents = []

    # Sort the loggers so that we come to the parents first
    for logger in \
            sorted([logger for logger in
                    logging.Logger.manager.loggerDict.values()
                    if isinstance(logger, logging.Logger)],
                   key=lambda logger: logger.name):

        # Don't reconfigure a logger with a parent
        if True in [logger.name.startswith(parent) for parent in parents]:
            continue

        parents.append(logger.name)

        hdlr_copy = list(logger.handlers)
        for hdlr in hdlr_copy:
            logger.removeHandler(hdlr)

        for fhdl in new_hldrs:
            logger.addHandler(fhdl)


def match_logs(source, targets):
    """
    :param logging.Logger source: Logger that has handlers to use
    :param list targets: List of loggers that need handlers updated
    """

    for logger in targets:
        for hdlr in list(logger.handlers):
            logger.removeHandler(hdlr)

        for hdlr in source.handlers:
            logger.addHandler(hdlr)
