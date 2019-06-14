import logging
import logging.config

# Set up custom log levels for plugins
logging.PLUGIN = 21


class ArgusCLILog(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        logging.addLevelName(logging.PLUGIN, "PLUGIN")

    def plugin(self, msg, *args, **kwargs):
        """Custom log level for plugins"""
        if self.isEnabledFor(logging.PLUGIN):
            self._log(logging.PLUGIN, msg, args, **kwargs)


def setup_logger(settings: dict):
    logging.setLoggerClass(ArgusCLILog)
    logging.config.dictConfig(settings)


# The logger!
log = logging.getLogger("argus_cli")
log.propagate = False
