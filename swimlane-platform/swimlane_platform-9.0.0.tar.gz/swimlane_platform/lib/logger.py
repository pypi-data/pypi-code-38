import logging
import sys


class LessThanFilter(logging.Filter):

    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        return 1 if record.levelno < self.max_level else 0


class SplitStreamLogger(logging.Logger):

    VERBOSE_LVL = 11

    def __init__(self, name, verbose, log_file=None):
        # type: (str, int, str) -> SplitStreamLogger
        super(SplitStreamLogger, self).__init__(name)
        logging.addLevelName(self.VERBOSE_LVL, 'VERBOSE')
        reporting_level = logging.INFO if verbose == 0 else self.VERBOSE_LVL if verbose == 1 else logging.DEBUG
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', '%Y-%m-%dT%H:%M:%S%z')
        log_out = logging.StreamHandler(sys.stdout)
        log_out.setLevel(reporting_level)
        log_out.addFilter(LessThanFilter(logging.WARNING))
        log_out.setFormatter(formatter)
        self.addHandler(log_out)
        log_error = logging.StreamHandler(sys.stderr)
        log_error.setLevel(logging.WARNING)
        log_error.setFormatter(formatter)
        self.addHandler(log_error)
        if log_file:
            self.addHandler(logging.FileHandler(log_file))

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(self.VERBOSE_LVL):
            message = message.replace("\n", "")
            self._log(self.VERBOSE_LVL, message, args, **kws)