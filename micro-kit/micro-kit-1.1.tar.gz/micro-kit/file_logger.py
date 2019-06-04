import logging
import logging.handlers
import os


class Singleton(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FileLogger(object):
    __metaclass__ = Singleton

    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    def __init__(self, api_name, absolute_log_file_path, log_format=None, logging_level=INFO):
        self._api_name = api_name
        self._log_file_name = os.path.basename(absolute_log_file_path)
        self._absolute_log_path = os.path.dirname(absolute_log_file_path)
        self._logging_level = logging_level
        if not log_format:
            self._log_format = '[%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s() - %(lineno)d] - %(message)s'
        else:
            self._log_format = log_format

    def logger(self):
        try:
            logger = logging.getLogger(self._api_name)
            logger.setLevel(self._logging_level)
            if not os.path.exists(self._absolute_log_path):
                os.makedirs(self._absolute_log_path)
            file_handler = logging.FileHandler(os.path.join(self._absolute_log_path, self._log_file_name))
            file_handler.setLevel(self._logging_level)
            log_format = logging.Formatter(self._log_format)
            file_handler.setFormatter(log_format)
            if not logger.handlers:
                logger.addHandler(file_handler)
            return logger
        except Exception as e:
            raise e
