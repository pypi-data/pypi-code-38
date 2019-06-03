import logging

from ips_common.config.configuration import Configuration


class IPSLogger:
    __logger = logging.getLogger(__name__)

    def __init__(self):
        config = Configuration().get_logging_config()
        file_name = config['file']['file_name']
        file_level = config['file']['file_level']
        console_level = config['console']['console_level']
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if file_name is not None:
            f_handler = logging.FileHandler(file_name)

            f_handler.setFormatter(log_format)

            if file_level is not None:
                level = logging.getLevelName(file_level)
                f_handler.setLevel(level)
            else:
                f_handler.setLevel(logging.INFO)

            self.__logger.addHandler(f_handler)

        c_handler = logging.StreamHandler()
        c_handler.setFormatter(log_format)

        if console_level is not None:

            level = logging.getLevelName(console_level)
            c_handler.setLevel(level)
        else:
            c_handler.setLevel(logging.INFO)
        self.__logger.addHandler(c_handler)

    @staticmethod
    def log():
        return IPSLogger().__logger


log = IPSLogger.log()


