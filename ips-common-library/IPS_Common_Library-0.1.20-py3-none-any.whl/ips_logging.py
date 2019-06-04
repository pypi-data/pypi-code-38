import logging
import logging.config
from os import path


class IPSLogger:
    __logger = logging.getLogger(__name__)

    def __init__(self, file_name):
        logging.config.fileConfig(fname=file_name, disable_existing_loggers=False)

    @staticmethod
    def log():
        log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
        return IPSLogger(log_file_path).__logger


log = IPSLogger.log()

