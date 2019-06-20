################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from configparser import ConfigParser
import logging

class LogConfig:
    specific_log_level = logging.WARN
    filename = None

def get_logger(name, specific_log_level=None):
    default_log_level = LogConfig.specific_log_level

    config = ConfigParser()
    config.read("./config.ini")

    try:
        filename = config.get("DEFAULT", 'log-filename')
    except:
        filename = LogConfig.filename

    log_level = default_log_level

    try:
        env_log_level = getattr(logging, config.get("DEFAULT", 'log'), None)
    except:
        env_log_level = None

    if env_log_level is not None:
        log_level = env_log_level

    if specific_log_level is not None:
        log_level = specific_log_level

    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    logger = logging.getLogger(name)
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename=filename)
    logger.setLevel(log_level)
    return logger
