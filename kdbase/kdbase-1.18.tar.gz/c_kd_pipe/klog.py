# -*- coding:utf-8 -*-
import logging
import os
import shutil
import time
import sys
from proc_pool import WorkerPool

initialized = False
formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)d' '[%(filename)s:%(lineno)d %(funcName)s]: %(message)s')



class Configer():
    def __init__(self):
        self.__log_path = ""
        self.__file_handler = None
        self.__console_handler = None
        self.__pure_path = "./log.txt"
        self.__time_format = "%Y%m%d%H%M"
        self.__time_format = "%Y%m%d"
 
    inst = None

    @staticmethod
    def get():
        if Configer.inst == None:
            Configer.inst = Configer()
        return Configer.inst

    def set_file_handler(self):
        date_str = time.strftime(self.__time_format)
        self.__log_path = self.__pure_path + '.' + date_str+'.'+str(os.getpid())

        fh = logging.FileHandler(self.__log_path)
        fh.setFormatter(formatter)
        self.__file_handler = fh
        logging.getLogger('').addHandler(fh)

    def set_console_handler(self):
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)
        self.__console_handler = console
        logging.getLogger('').addHandler(console)
        logging.getLogger('').setLevel(logging.INFO)

    def del_console_handler(self):
        logging.getLogger('').removeHandler(self.__console_handler)
        del self.__console_handler
        self.__console_handler = None

    def del_file_handler(self):
        logging.getLogger('').removeHandler(self.__file_handler)
        del self.__file_handler
        self.__file_handler = None

    def rotate(self):
        date_str = time.strftime(self.__time_format)
        path = self.__pure_path + '.' + date_str+'.'+str(os.getpid())
        self.__log_path

        if path == self.__log_path:
            return
        sys.stdout.flush()
        sys.stderr.flush()
        self.del_file_handler()
        self.set_file_handler()

    def init(self, level, path="./log.txt", quiet=False):
        self.__pure_path = path
        if quiet:
            self.del_console_handler()

        if not quiet and not self.__console_handler:
            self.set_console_handler()
        self.set_file_handler()

        cmd = str("logging.getLogger("").setLevel(logging.%s)" % (level.upper()))
        exec cmd


class Logger():
    def __init__(self):
        self.info = logging.info
        self.debug = logging.debug
        self.warning = logging.warning
        self.error = logging.error
        self.critical = logging.critical
        self.pid = os.getpid()
        Configer.get().set_console_handler()


def log_init(level, path="./log.txt", quiet=True):
    global initialized
    if initialized: return
    Configer.get().init(level, path, quiet)
    initialized = True


g_logger = Logger()


def logger():
    Configer.get().rotate()
    return g_logger


def main():
     log_init('info', './log.txt', quiet=False)
     l = logger()
     l.info('abc')


def log(log_name):
    def decorator(func):
        def wrapper(*args, **kw):
            quiet = False
            if log_name == 'heart_beat':
                quiet = True
            log_init(GET_CONF('log', 'log_level'),
                        os.path.join(PROJECT_HOME, GET_CONF('log', 'log_dir_' + log_name)),
                        quiet=quiet)
            return func(*args, **kw)
        return wrapper
    return decorator


if __name__ == '__main__':
    pool = WorkerPool(3)
    for i in xrange(5):
         pool.push(main, ())
         time.sleep(1)
    time.sleep(5)
    pool.wait_until_finish()
    print "all process(es) done."
