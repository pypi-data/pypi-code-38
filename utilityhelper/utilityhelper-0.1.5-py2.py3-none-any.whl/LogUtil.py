#coding:utf-8
from __future__ import (print_function, unicode_literals)
from utilityhelper.compatible import *
import logging
import logging.handlers
import os

class EncodingFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None, encoding=None):
        super(EncodingFormatter, self).__init__(fmt, datefmt)
        self.encoding = encoding

    def format(self, record):
        result = logging.Formatter.format(self, record)
        if not PY3:
            if isinstance(result, unicode):
                result = result.encode(self.encoding or 'utf-8')
        return result

class Log(object):
    
    currScriptPath = os.path.split(os.path.realpath(__file__))[0]
    lifile = os.listdir(currScriptPath)
    os.chdir(currScriptPath)
    logfile = r"testLog.log"
    logger=logging.getLogger("testLog")
    logger.setLevel(logging.DEBUG)
    # 创建一个handler，用于写入日志文件
    # handler=logging.FileHandler(logfile)
    handler=logging.StreamHandler()

    # 定义handler的输出格式
    fmtstr = '[%(asctime)s] [%(levelname)s] [%(name)s] [PID:%(process)d-TID:%(thread)d(%(threadName)s)] -- %(message)s'
    formatter = EncodingFormatter(fmtstr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    @staticmethod
    def SetLevel(level):
        Log.logger.setLevel(level)
    
    @staticmethod
    def GetLogLevel():
        return Log.logger.level
        
    @staticmethod
    def Info(msg):
        Log.logger.info(msg)
        
    @staticmethod        
    def Debug(msg):
        Log.logger.debug(msg)
         
    @staticmethod
    def Warn(msg):
        Log.logger.warning(msg)
            
    @staticmethod       
    def Error(msg):
        Log.logger.error(msg)
    

class MailLog(Log):
    logger=logging.getLogger("mailFactory")
    logger.setLevel(logging.DEBUG)
    #创建一个SMTP handler，用于输出日志到邮件
    mailHandler = logging.handlers.SMTPHandler(mailhost="",
                                     fromaddr='',
                                     toaddrs='',
                                     subject='Logged Event',
                                     credentials = ('', ''))

    mailHandler.setFormatter(EncodingFormatter(Log.fmtstr, encoding='utf-8'))
    logger.addHandler(mailHandler)

    @staticmethod
    def SetLevel(level):
        MailLog.logger.setLevel(level)
    
    @staticmethod
    def GetLogLevel():
        return MailLog.logger.level
        
    @staticmethod
    def Info(msg):
        MailLog.logger.info(msg)
        
    @staticmethod        
    def Debug(msg):
        MailLog.logger.debug(msg)
         
    @staticmethod
    def Warn(msg):
        MailLog.logger.warning(msg)
            
    @staticmethod       
    def Error(msg):
        MailLog.logger.error(msg)

if __name__ == "__main__":
    Log.Info("11111111111222222222222222")
    Log.Info("UNICODE中文")