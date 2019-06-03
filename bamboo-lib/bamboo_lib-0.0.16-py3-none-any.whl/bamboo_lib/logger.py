import logging
import logging.config
import os

logger_conf_path = os.environ.get("BAMBOO_LOGGER_CONF", None)

# logging.basicConfig(level=logging.DEBUG)
mode = "Default logger"

if logger_conf_path and os.path.isfile(logger_conf_path):
    logging.config.fileConfig(logger_conf_path)
    mode = "Using logger config from BAMBOO_LOGGER_CONF..."
elif os.path.isfile('logging.conf'):
    logging.config.fileConfig('logging.conf')
    mode = "Using logger config from logging.conf file..."
else:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

if mode != "Default logger":
    logger.info(mode)
