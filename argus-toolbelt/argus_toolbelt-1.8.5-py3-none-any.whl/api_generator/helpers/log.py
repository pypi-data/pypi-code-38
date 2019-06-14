import logging

# Set up custom log levels for plugins
PLUGIN_LOG_LEVEL_NUM = 9 
logging.addLevelName(PLUGIN_LOG_LEVEL_NUM, "PLUGIN")


def plugin(self, message, *args, **kws):
    """
    Custom log level for plugins
    """
    if self.isEnabledFor(logging.INFO):
        self._log(PLUGIN_LOG_LEVEL_NUM, message, args, **kws)


logging.Logger.plugin = plugin
# Package wide logger
log = logging.getLogger("api_generator")
log.propagate = False
