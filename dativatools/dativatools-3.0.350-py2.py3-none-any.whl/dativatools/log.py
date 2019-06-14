import logging
import logging.config
import logging.handlers
import os


class Logger(object):
    def __init__(self):
        self.file_handler = None
        self.root_logger = None
        self.formatter = None

    # -------------------------------------------------------------------------
    #    Args: path, filename, logger_name, log_level
    # Returns: logger
    #    Desc: This function creates a log file if not present and returns logger
    # -------------------------------------------------------------------------
    def __get_logger__(self, path, filename, logger_name="logger", log_level=logging.INFO):
        self.logfile(path, filename)
        logger = logging.getLogger('inrlogger.%s'.format(logger_name))
        logger.setLevel(log_level)
        return logger

    # -------------------------------------------------------------------------
    #    Name: set_format
    #    Desc: Sets format of the message being logged in file
    # -------------------------------------------------------------------------
    def set_format(self):
        message_format = "%(asctime)s.%(msecs)03d [%(levelname)s] " \
                         "(%(process)d:%(thread)d:%(filename)s:%(lineno)s) %(message)s"
        date_format = "%Y-%m-%dT%H:%M:%S"
        self.formatter = logging.Formatter(fmt=message_format, datefmt=date_format)

    # -------------------------------------------------------------------------
    #    Name: logfile
    #    Args: path, log_filename
    #    Desc: Creates file to which log messages are output and set a handler
    # -------------------------------------------------------------------------
    def logfile(self, path, log_filename, when='midnight', interval=1, backupCount=0,
                encoding=None, delay=False, utc=False):
        self.set_format()
        if self.root_logger is None:
            self.root_logger = logging.getLogger('inrlogger')
            self.root_logger.setLevel(logging.INFO)
        log_file = os.path.join(path, log_filename)

        if not os.path.exists(os.path.join(path)):
            os.makedirs(os.path.join(path))
        if not os.path.isfile(log_file):
            open(log_file, 'w').close()
        with open(log_file, 'a') as f:
            # verify file is writeable or exception will be thrown
            pass
        if when is None:
            fh = logging.handlers.WatchedFileHandler(log_file, delay=delay)
        else:
            fh = logging.handlers.TimedRotatingFileHandler(log_file, when, interval, backupCount, encoding, delay, utc)
        fh.setLevel(logging.INFO)
        fh.setFormatter(self.formatter)

        if not self.root_logger.handlers:
            logging.getLogger('').addHandler(fh)

        if self.file_handler is not None:
            self.root_logger.removeHandler(self.file_handler)
        self.file_handler = fh
