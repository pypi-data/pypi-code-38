# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import sys

from azureml.telemetry import get_telemetry_log_handler


"""Telemetry utils."""

OPENDATASETS_LOGGER_NAMESPACE = "azureml.contrib.opendatasets"
OPENDATASETS_INSTRUMENTATION_KEY = 'f65df220-4460-4269-b954-a11c54f8e611'


def add_appinsights_log_handler(logger):
    handler = get_telemetry_log_handler(
        instrumentation_key=OPENDATASETS_INSTRUMENTATION_KEY,
        component_name=OPENDATASETS_LOGGER_NAMESPACE)
    add_handler(logger, handler)


def add_console_log_handler(logger):
    handler = logging.StreamHandler(sys.stdout)
    add_handler(logger, handler)


def get_opendatasets_logger(name, verbosity=logging.DEBUG):
    logger = logging.getLogger(OPENDATASETS_LOGGER_NAMESPACE).getChild(name)
    logger.propagate = False
    logger.setLevel(verbosity)
    add_appinsights_log_handler(logger)
    add_console_log_handler(logger)
    return logger


def add_handler(logger, handler):
    """
    Add a logger handler and skip if the same type already exists.

    :param logger: Logger
    :param handler: handler instance
    """
    handler_type = type(handler)
    for log_handler in logger.handlers:
        if isinstance(log_handler, handler_type):
            return
    logger.addHandler(handler)
