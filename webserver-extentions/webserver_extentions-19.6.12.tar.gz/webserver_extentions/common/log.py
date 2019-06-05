#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
Description:
    Packet modification provides log operation.
    It mainly uses dictConfig method of logging module to construct dictionary configuration file.
    Users only need to call init_log structure interface when using it.
    Note: the calling parameter kward corresponds to Handler.
"""

import json
import os
import sys
from logging.config import dictConfig
import logging
import logging.handlers
try:
    import ConfigParser
except:
    import configparser as ConfigParser

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)

outputTypes = ["console", "filebytes", "filetime"]


class Handler(object):
    """Output Handler"""

    def __init__(self):
        """
        init
        format        - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      'INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD'
        """
        self.formatter = "standard"

    def format_dict(self, out):
        """
        Formatted dictionary
        :param out: dict object
        :return:
        """
        for one in out:
            if out[one] == None:
                out[one] = ""
        return out

    def console_handler(self, level):
        """
        Output for console
        :param level: Output level
                msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
        :return:
        """
        out = {}
        out["level"] = level
        out["class"] = "logging.StreamHandler"
        # out["stream"] = sys.stderr
        out["formatter"] = self.formatter
        return self.format_dict(out)

    def filetime_handler(self, level, filename, when='h', interval=1, backupCount=3,
                         encoding="utf-8",
                         delay=False, utc=False):
        """
        Output rollback by time
        :param level: Output level
                msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
        :param filename: Output filename
        :param when: Periodic unit
                - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
        :param interval: Periodic interval
        :param backupCount: Keep the number
        :param encoding: The encoding is UTF-8 by default
        :param delay: Whether or not delay
        :param utc:
        :return: Return to filetime Handler
        """
        out = {}
        out["filename"] = filename
        out["when"] = when
        out["interval"] = interval
        out["backupCount"] = backupCount
        out["encoding"] = encoding
        out["delay"] = delay
        out["utc"] = utc
        out["level"] = level
        out["class"] = "logging.handlers.TimedRotatingFileHandler"
        out["formatter"] = self.formatter
        return self.format_dict(out)

    def filebytes_handler(self, level, filename, mode='a', maxBytes=0, backupCount=0,
                          encoding="utf-8", delay=False):
        """
        Output logs are rolled back by bytes
        :param level: Output level
        :param filename:Output filename
        :param mode: File mode
        :param maxBytes: Maximum number of bytes
        :param backupCount:Keep the number
        :param encoding:The encoding is UTF-8 by default
        :param delay:Whether or not delay
        :return:Return to ffilebytes Handler
        """
        out = {}
        out["filename"] = filename
        out["mode"] = mode
        out["maxBytes"] = maxBytes
        out["backupCount"] = backupCount
        if not encoding:
            out["encoding"] = encoding
        out["delay"] = delay
        out["level"] = level
        out["class"] = "logging.handlers.RotatingFileHandler"
        out["formatter"] = self.formatter
        return self.format_dict(out)


class LoggingData(object):
    """Log parameter class"""

    def __init__(self, logger_name, outputType, **kwargs):
        """
        init
        :param logger_name:  Logger name
        :param outputType: Output type, such as console
        :param kwargs:
            It can be divided into several situations, for example:
                Console: this parameter is console_handler parameter (level).
                Filetime: this parameter is level, filename, when, interval,backupCount,encoding,delay, utc and so on,
                            of course, the default value is ok.
                Note:Similar to other types of Handler.
        """
        self.logger_name = logger_name
        self.outputType = outputType
        self.data = {}
        self.data["version"] = 1
        self.data["disable_existing_logger"] = False
        self.kwargs = kwargs
        if not kwargs.get("format", ""):
            self.format = "%(asctime)s - %(name)s - %(levelname)s -* %(process)d| %(message)s"
        else:
            self.format = kwargs.get("format", "")
        self.loggers()
        self.filters()
        self.handlers()
        self.formatters()

    def loggers(self):
        """logger of logging"""
        if self.outputType not in outputTypes:
            raise ("The output method dont support!")
        self.data["loggers"] = {}
        self.data["loggers"][self.logger_name] = {}
        self.data["loggers"][self.logger_name]["handlers"] = [self.outputType]
        self.data["loggers"][self.logger_name]["propagate"] = False

    def filters(self):
        """filter of logging"""
        self.data["filters"] = {}

    def formatters(self):
        """formatters of logging"""
        self.data["formatters"] = {}
        self.data["formatters"]["standard"] = {"format": self.format}

    def handlers(self):
        """handler of logging"""
        self.data["handlers"] = {}
        self.data["handlers"][self.outputType] = eval("Handler().%s_handler" % self.outputType)(
            **self.kwargs)

    def __str__(self):
        return json.dumps(self.data)


def init_log(logger_name, outputType, **kwargs):
    """
    api of loging
    :param logger_name: Logger name
    :param outputType: Output type, such as console
    :param kwargs:
        It can be divided into several situations, for example:
                Console: this parameter is console_handler parameter (level).
                Filetime: this parameter is level, filename, when, interval,backupCount,encoding,delay, utc and so on,
                            of course, the default value is ok.
                Note:Similar to other types of Handler.
    :return: Returns a logger object.
    """
    if kwargs.get("filename", ""):
        log_dir = os.path.dirname(kwargs.get("filename", ""))
        if log_dir == "":
            log_dir = "./"
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
    data = LoggingData(logger_name, outputType=outputType, **kwargs).data
    dictConfig(data)
    log = logging.getLogger(logger_name)
    return log


def get_conf(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config._sections


def get_log(conffile="../conf/logging.conf"):
    log_conf = get_conf(conffile)
    logger_name = log_conf.get("logging").get("logger_name")
    outputType = log_conf.get("logging").get("outputtype")
    backupCount = int(log_conf.get("logging").get("backupcount", "5"))
    other_params = log_conf.get("logging")
    other_params["__name__"] = ""
    del other_params["logger_name"]
    del other_params["outputtype"]
    del other_params["backupcount"]
    del other_params["__name__"]
    logging = init_log(logger_name, outputType, backupCount=backupCount, **other_params)
    return logging


def test():
    """unittest"""
    # logger = init_log("test", "console", level="DEBUG")
    # logger.warn("dasdas")
    # logger.error("dadasda")
    # logging = init_log("test", "filebytes", level="DEBUG", maxBytes=10000, backupCount=5,
    #                    filename="./log/test_file.log")
    # logging.warn("dasdas")
    # logging.error("dadasda")
    # logging.warn("dasdas")
    # logging.warn("dasdas")
    # logging.error("dadasda")
    # logging.warn("dasdas")
    logging = init_log("test", "filetime", level="DEBUG", when="s", backupCount=5,
                       filename="./log/test_file.log")
    logging.warn("dasdas")
    logging.error("dadasda")
    logging.warn("dasdas")
    logging.warn("dasdas")
    logging.error("dadasda")
    logging.warn("dasdas")
    logging.warn("dasdas")
    logging.error("dadasda")
    logging.warn("dasdas")


if __name__ == '__main__':
    # print LoggingData(outputType="console", level="DEBUG")
    test()
