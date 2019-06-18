import traceback
import sys


# Note: Python 3+ exceptions provide error message
#       thru args attribute instead of message
#       attribute
def get_exception_message(exception):
    if hasattr(exception, "message"):
        return exception.message

    return exception.args


class ModuleLogger(object):
    def __init__(self, module_name, logger):
        self.module_name = module_name
        self.logger = logger

    def log_message(self, level, message):
        self.logger.log_message(level, message, self.module_name)

    def warn(self, message):
        self.log_message("warn", message)

    def error(self, message):
        self.log_message("error", message)

    def info(self, message):
        self.log_message("info", message)

    def debug(self, message):
        self.log_message("debug", message)

    def exception(self, exception):
        exc_type, exc_value, exc_tb = sys.exc_info()
        exception_message = "{}\n".format(get_exception_message(exception))
        stacktrace = traceback.format_exception(exc_type, exc_value, exc_tb)
        message = "".join([exception_message] + stacktrace).rstrip()
        self.debug(message.rstrip())
