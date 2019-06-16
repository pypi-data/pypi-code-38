#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Extra logging bells and whistles
#
import logging
import os


__all__ = ['logger']


# Deprecation level
def deprecated(self, message, *args, **kws):
    if not hasattr(self, 'deprecated_msgs'):
        self.deprecated_msgs = []

    if self.isEnabledFor(35) and message not in self.deprecated_msgs:
        self.deprecated_msgs.append(message)
        self._log(35, message, args, **kws)


logging.addLevelName(35, "DEPRECATED")
logging.Logger.deprecated = deprecated

# Console Handler
ch = logging.StreamHandler()
if 'BB_LOGLVL' in os.environ:
    ch.setLevel(os.environ['BB_LOGLVL'].upper())
else:
    ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('{levelname:10} [{name}] {message}', style='{'))

# Logger
logger = logging.getLogger('brambox')
logger.setConsoleLevel = ch.setLevel
logger.setLevel(logging.DEBUG)
logger.addHandler(ch)
