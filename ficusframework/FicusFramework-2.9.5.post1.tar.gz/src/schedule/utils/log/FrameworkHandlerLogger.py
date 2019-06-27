import json
import logging

from api.model import LogMessage, ClassInfo
from client import HandlerLogClient
from config.annotation import Value

localLogger = logging.getLogger('Ficus')

@Value("${log.type:local}")        # 默认是本地日志
def log_type():
    pass

@Value("${actor.name:unknown}")        # 找到actorName
def actor_name():
    pass


def log_debug(message:str):
    """
    记录debug日志
    :param message:
    :return:
    """
    log_message = __generateLogMessage__(message)

    if "remote" == log_type():
        try:
            HandlerLogClient.log_debug(log_message)
        except:
            localLogger.error("记录远程日志失败,改为本地日志记录")
            localLogger.debug(json.dumps(log_message))
    else:
        localLogger.debug(message)

def log_info(message:str):
    """
    记录info日志
    :param message:
    :return:
    """
    log_message = __generateLogMessage__(message)

    if "remote" == log_type():
        try:
            HandlerLogClient.log_info(log_message)
        except:
            localLogger.error("记录远程日志失败,改为本地日志记录")
            localLogger.info(json.dumps(log_message))
    else:
        localLogger.info(message)

def log_warn(message:str,exception:Exception=None):
    """
    记录warn日志
    :param message:
    :return:
    """
    log_message = __generateLogMessage__(message,exception)

    if "remote" == log_type():
        try:
            HandlerLogClient.log_warn(log_message)
        except:
            localLogger.error("记录远程日志失败,改为本地日志记录")
            localLogger.warning(json.dumps(log_message))
    else:
        localLogger.warning(message if exception is None else f"{message},{str(exception)}")

def log_error(message:str,exception:Exception=None):
    """
    记录error日志
    :param message:
    :param exception:
    :return:
    """
    log_message = __generateLogMessage__(message,exception)

    if "remote" == log_type():
        try:
            HandlerLogClient.log_error(log_message)
        except:
            localLogger.error("记录远程日志失败,改为本地日志记录")
            localLogger.error(json.dumps(log_message))
    else:
        localLogger.error(message if exception is None else f"{message},{str(exception)}")


def __findClassInfo__(limit=1):
    import traceback
    stackTuple = traceback.extract_stack(limit=limit + 1)[0]
    class_info = ClassInfo()

    class_info.className = stackTuple[0]
    class_info.methodName = stackTuple[2]
    class_info.lineNumber = stackTuple[1]

    return class_info

def __generateLogMessage__(message:str,exception:Exception=None):
    log_message = LogMessage()
    log_message.actorName = actor_name()
    log_message.exception = exception
    log_message.message = message
    import threading
    log_message.threadName = threading.currentThread().getName()
    log_message.classInfo = __findClassInfo__(2)
