import logging
from inspect import getframeinfo, stack
def log_message_level(level,message):
    if level==0:
        r_message='* '+message+' *'
    else:

        pre = ''.join(['.....' for x in range(level)])
        r_message=pre+message


    return r_message


class BleroLogger():


    def __init__(self,path,source):

        self.set_user_log(path,source)
        self.logger_level_print=0
    def increase_logger_level(self):
        self.logger_level_print=self.logger_level_print+1
        self.pre_text=' '.join(["..."] * self.logger_level_print)


    def decrease_logger_level(self):
        self.logger_level_print=self.logger_level_print-1
        self.pre_text = ' '.join(["..."] * self.logger_level_print)

    def info(self,message):
        caller = getframeinfo(stack()[1][0])
        lineno="-" + str(caller.lineno) +"- "

        self.logger.info(lineno+self.pre_text+str(message))

    def debug(self,message):
        caller = getframeinfo(stack()[1][0])
        lineno="-" + str(caller.lineno) +"- "
        self.logger.debug(lineno+self.pre_text+str(message))

    def exception(self,message):
        caller = getframeinfo(stack()[1][0])
        lineno="-" + str(caller.lineno) +"- "
        self.logger.exception(lineno+self.pre_text + str(message))


    def set_user_log(self,path,source):
        logger = logging.getLogger(source)
        logger.setLevel(logging.DEBUG)
        # create a file handler
        handler = logging.FileHandler(path+"/"+source+".log")
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  %(message)s')
        handler.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(handler)
        self.pre_text = ''
        self.logger=logger
