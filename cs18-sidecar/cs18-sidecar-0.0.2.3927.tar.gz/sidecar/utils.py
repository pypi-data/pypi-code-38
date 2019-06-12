import datetime
import inspect
import logging
import sys
from logging import Logger

import requests
import time

from sidecar.const import Const


class Utils:

    @staticmethod
    def stop_on_debug():
        while not sys.gettrace():
            time.sleep(0.5)

    @staticmethod
    def read_log(app_name: str) -> str:
        file_path = Const.get_app_log_file(app_name)
        with open(file_path, 'r') as application_log:
            return application_log.read()

    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def wait_for(func, interval_sec: int = 10, max_retries: int = 10, error: str = "", silent: bool = False):
        current_retry = 0
        while current_retry < max_retries:
            try:
                if func():
                    return
                else:
                    if not silent:
                        print('re-try {} out of {}'.format(current_retry, max_retries))
                    time.sleep(interval_sec)
                    current_retry += 1
                    if current_retry >= max_retries:
                        raise Exception('max retries for wait_for is exhausted with message: {}'.format(error))
            except Exception as e:
                raise Exception('wait_for function exited due to an exception: {}'.format(e))

    @staticmethod
    def retry_on_exception(func,
                           logger: Logger = None,
                           logger_msg: str = "",
                           interval: int = 1,
                           timeout_in_sec: int = 10):
        start = datetime.datetime.now()
        attempt_number = 1
        while True:
            try:
                res = func()
                if attempt_number > 1:
                    if logger:
                        elapsed = datetime.datetime.now() - start
                        logger.info(
                            "{} (succeed after {}s with {} attempts)".format(logger_msg, elapsed.total_seconds(),
                                                                             attempt_number))
                return res
            except requests.exceptions.ConnectionError as ce:
                if "Failed to establish a new connection: [Errno -2] Name or service not known'" in str(ce):
                    logger.exception(str(ce))
                    logger.fatal("logger shut down, no access to cloud provider.")
                    Utils._reset_logger()
                    raise ce
                Utils._handle_exception(attempt_number, ce, logger, logger_msg, start, timeout_in_sec)
            except Exception as e:
                Utils._handle_exception(attempt_number, e, logger, logger_msg, start, timeout_in_sec)
            finally:
                time.sleep(interval)
            attempt_number += 1

    @staticmethod
    def _handle_exception(attempt_number, ce, logger, logger_msg, start, timeout_in_sec):
        elapsed = datetime.datetime.now() - start
        in_seconds = elapsed.total_seconds()
        if in_seconds > timeout_in_sec:
            if logger:
                logger.info("Failure while {} (timed out after {}s with {} attempts)"
                            .format(logger_msg, in_seconds, attempt_number))
            raise ce

    @staticmethod
    def _reset_logger():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig()


class CallsLogger:
    logger = None

    @classmethod
    def set_logger(cls, logger):
        cls.logger = logger

    @classmethod
    def wrap(cls, func):
        def decorator(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()

            args_list = ["{}: '{}'".format(k, v) for (k, v) in bound_args.arguments.items()]
            if len(bound_args.arguments) > 0 and bound_args.arguments.get('self'):
                args_list = args_list[1:]
            result_str = ''

            try:
                result = func(**bound_args.arguments)
                result_str = str(result)
                return result
            except Exception as e:
                result_str = str(e)
                raise
            finally:
                if cls.logger:
                    result_str = result_str if len(result_str) < 20 else result_str[:17]+'...'
                    cls.logger.info(func.__qualname__ + "(" + ", ".join(args_list) + ") -> "+result_str)

        return decorator
