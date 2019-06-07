# coding=utf-8
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------
from ibm_ai_openscale_cli.api_environment import ApiEnvironment
from datetime import datetime
import json
import logging
import os
import sys
import time
import threading
import traceback

class FastpathLogger():
    """
    Usage:
    # import the class:
        from utils.fastpath_logger import FastpathLogger

    # Get the instance of logger
        logger = FastpathLogger(__name__)

    # Log the message
        logger.log_log_info("Processing Heartbeat request")
    """

    api_env = ApiEnvironment()
    json_enabled = api_env.is_cli_json_logging_enabled()
    details_enabled = api_env.is_cli_logging_from_api_enabled()

    def __init__(self, name):
        self.logger = self.get_logger(name)
        self.log_source = None

    def get_logger(self, logger_name=None):
        # logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        logger_name = logger_name if logger_name else '__Watson_OpenScale_Fastpath_CLI__'
        logger = logging.getLogger(logger_name)
        return logger

    def msg_to_log(self, attributes, msg):
        # import threading
        # msg = '{} - {}'.format(threading.current_thread(), msg)
        if FastpathLogger.json_enabled:
            return json.dumps(attributes)
        else:
            if self.log_source:
                return "[" + self.log_source + "]" + msg
            else:
                return msg

    def log_info(self, msg, **kwargs):
        attributes = self.get_logging_attributes("INFO", **kwargs)
        attributes["message_details"] = msg
        self.logger.info(self.msg_to_log(attributes, msg))

    def log_error(self, err_msg, **kwargs):
        attributes = self.get_logging_attributes("ERROR", **kwargs)
        attributes["message_details"] = err_msg
        self.logger.error(self.msg_to_log(attributes, err_msg))

    def log_exception(self, exc_msg, **kwargs):
        attributes = self.get_logging_attributes("ERROR", **kwargs)
        attributes["message_details"] = exc_msg
        exc_info = kwargs.get("exc_info", False)
        if exc_info is True:
            type_, value_, traceback_ = sys.exc_info()
            attributes["exception"] = "".join(traceback.format_exception(
                type_, value_, traceback_))
        self.logger.error(self.msg_to_log(attributes, exc_msg))

    def log_warning(self, msg, **kwargs):
        attributes = self.get_logging_attributes("WARNING", **kwargs)
        attributes["message_details"] = msg
        exc_info = kwargs.get("exc_info", False)
        if exc_info is True:
            type_, value_, traceback_ = sys.exc_info()
            attributes["exception"] = "".join(traceback.format_exception(
                type_, value_, traceback_))
        self.logger.warning(self.msg_to_log(attributes, msg))

    def log_debug(self, msg, **kwargs):
        attributes = self.get_logging_attributes("DEBUG", **kwargs)
        attributes["message_details"] = msg
        self.logger.debug(self.msg_to_log(attributes, msg))

    def log_critical(self, msg, **kwargs):
        attributes = self.get_logging_attributes("CRITICAL", **kwargs)
        attributes["message_details"] = msg
        self.logger.critical(self.msg_to_log(attributes, msg))

    def get_logging_attributes(self, level, **kwargs):
        attributes = {}
        attributes["component_id"] = "fastpath-service"
        attributes["log_level"] = level
        attributes["timestamp"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        attributes["worker_id"] = os.getpid()
        attributes["thread_name"] = threading.current_thread().getName()

        if FastpathLogger.details_enabled:
            fn, lno, func = self.logger.findCaller(False)[0:3]
            self.log_source = fn + ":" + str(lno) + " - " + func
            attributes["filename"] = fn
            attributes["method"] = func
            attributes["line_number"] = str(lno)

        start_time = kwargs.get("start_time", None)
        if start_time:
            elapsed_time = round(time.time() * 1000) - start_time
            attributes["response_time"] = elapsed_time
            attributes["perf"] = True

        additional_info = kwargs.get("additional_info", None)
        if additional_info:
            attributes["additional_info"] = additional_info

        return attributes