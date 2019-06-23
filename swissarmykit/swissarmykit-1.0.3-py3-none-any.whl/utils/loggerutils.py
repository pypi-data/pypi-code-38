import logging
import time

class LoggerUtils:

    def __init__(self, file_name='log_', gui=None):
        rootLogger = logging.getLogger()
        self.logger = rootLogger
        self.gui = gui

        if not rootLogger.hasHandlers():
            time.strftime("%Y-%m-%d")
            log_file = file_name + time.strftime("%Y-%m-%d") + '.log'

            logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            rootLogger.setLevel(level=logging.INFO)

            fileHandler = logging.FileHandler(log_file, encoding='UTF-8')
            fileHandler.setFormatter(logFormatter)
            rootLogger.addHandler(fileHandler)

            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)

    def info(self, text):
        self.logger.info(text)
        if self.gui:
            self.gui.send_info_text(text)

    def debug(self, text):
        self.logger.debug(text)
        if self.gui:
            self.gui.send_debug_text(text)

    def error(self, text):
        self.logger.error(text)
        if self.gui:
            self.gui.send_error_text(text)

    def warn(self, text):
        self.warning(text)

    def warning(self, text):
        self.logger.warning(text)
        if self.gui:
            self.gui.send_warning_text(text)

if __name__ == '__main__':
    log = LoggerUtils()
    log.info('test')