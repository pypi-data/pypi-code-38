from base.multiprocessing_log_handler import MultiprocessingLogHandler
from base.settings import Settings
import logging
import traceback


# Singleton function.
def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


# This class will fallow Singleton Design Pattern.
@singleton
class MultiprocessingLogger(MultiprocessingLogHandler):
    """
        creates logger object with class name.

        get_logger() creates logger with Class_name  and
            - read level from config file and set level to logger
            - set format
    """

    def __init__(self):
        """
            Constructor for MultiprocessingLogger class.
        """
        self.logger = None
        self.settings = Settings()
        self.get_logger()

    @staticmethod
    def clean_msg(msg):
        """
        This function in used clean message parameter.
        Like remove '\n' etc.
        :param msg: (str) message for log
        :return:
            cleaned_str -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            clean_message = msg.replace("\n", "-")
            return clean_message
        except Exception as e:
            print(traceback.format_exc())
            return False

    def get_logger(self):
        """
        Creates logger with Class_name.
        Sets LogLevel to logger, which specified in {config}.ini file.
        Adds Handler to logger.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            if self.logger is None:
                self.logger = logging.getLogger(__name__)
                # Read level from settings ({config}.ini) file
                level = logging.getLevelName(self.settings.get_logging_level())
                # set level
                self.logger.setLevel(level)
                multiprocessing_log_handler = MultiprocessingLogHandler(self.settings.get_logging_log_file())
                self.logger.addHandler(multiprocessing_log_handler)
            return True
        except Exception as e:
            print("Dist_Logger :Logger Initialization Failed : " + str(e))
            print(traceback.format_exc())
            return False

    def logDebug(self, logcode, codetype, message):
        """
        Logs a message with level CRITICAL on the MultiprocessingLogger.
        :param logcode: logcode for log. (Errorcode or Infocode) Ex., "E-10001067","I-10003421"
        :param codetype: codetype for log. (module name/class_name Ex., "base.webbrowser")
        :param message: log Message.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            message = self.clean_msg(message)
            self.logger.debug(message, extra={'logcode': logcode, 'codetype': codetype})
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False

    def logError(self, logcode, codetype, message):
        """
        Logs a message with level ERROR on the MultiprocessingLogger.
        :param logcode: logcode for log. (Errorcode or Infocode) Ex., "E-10001067","I-10003421"
        :param codetype: codetype for log. (module name/class_name Ex., "base.webbrowser")
        :param message: log Message.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            message = self.clean_msg(message)
            self.logger.error(message, extra={'logcode': logcode, 'codetype': codetype})
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False

    def logInfo(self, logcode, codetype, message):
        """
        Logs a message with level INFO on the MultiprocessingLogger.
        :param logcode: logcode for log. (Errorcode or Infocode) Ex., "E-10001067","I-10003421"
        :param codetype: codetype for log. (module name/class_name Ex., "base.webbrowser")
        :param message: log Message.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            message = self.clean_msg(message)
            self.logger.info(message, extra={'logcode': logcode, 'codetype': codetype})
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False

    def logCritical(self, logcode, codetype, message):
        """
        Logs a message with level CRITICAL on the MultiprocessingLogger.
        :param logcode: logcode for log. (Errorcode or Infocode) Ex., "E-10001067","I-10003421"
        :param codetype: codetype for log. (module name/class_name Ex., "base.webbrowser")
        :param message: log Message.
        :return:
            True -> on successful execution
            OR
            False -> if execution failed
        """
        try:
            message = self.clean_msg(message)
            self.logger.critical(message, extra={'logcode': logcode, 'codetype': codetype})
            return True
        except Exception as e:
            print(traceback.format_exc())
            return False

if __name__ == '__main__':
    pass
