import logging
import logging.handlers
import os

from tcell_agent.loggers.tcell_log_formatter import TCellLogFormatter
from tcell_agent.utils.tcell_fs import mkdir_p


_PYTHON_LOGGER = None


def get_python_logger(log_directory, logging_options):
    global _PYTHON_LOGGER  # pylint: disable=global-statement

    if _PYTHON_LOGGER:
        return _PYTHON_LOGGER

    mkdir_p(log_directory)

    new_logger = logging.getLogger("tcell")
    formatter = TCellLogFormatter(
        fmt="%(asctime)s [%(tcell_version)s %(process)d] %(name)s %(message)s"
    )
    full_path = os.path.join(log_directory, logging_options["filename"])
    fh = logging.handlers.RotatingFileHandler(full_path, maxBytes=10 * 1024 * 1024, backupCount=5)
    fh.setFormatter(formatter)
    new_logger.setLevel(logging_options["level"])
    new_logger.addHandler(fh)

    _PYTHON_LOGGER = new_logger

    return _PYTHON_LOGGER


# This should only be used for logging needed before
# the native agent has been created.
class PythonLogger(object):
    def __init__(self, logging_options, log_directory):
        self.log_directory = log_directory
        self.logging_options = logging_options

    def log_message(self, level, message, module_name):
        if not self.logging_options["enabled"]:
            return

        logger = get_python_logger(self.log_directory, self.logging_options).getChild(module_name)
        getattr(logger, level)(message)
