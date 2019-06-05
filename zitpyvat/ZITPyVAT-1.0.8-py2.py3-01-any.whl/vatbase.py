# -*- coding: utf-8 -*-
# @Time    : 2017/1/24 8:25
# @Author  : Liu Gang
# @Site    : 
# @File    : Vatbase.py
# @Software: PyCharm Community Edition

import csv
import time

# import socket
try:
    import ConfigParser as cp
    from ConfigParser import NoSectionError, NoOptionError
except ImportError:
    import configparser as cp
    from configparser import NoSectionError, NoOptionError

__all__ = ["Vatbase", "CfgSet", "LOGGER_PATH", "VAT_BASE_VER", "gettime", "NoSectionError", "NoOptionError"]

_CFG_FILE = "Config\\config.ini"
LOGGER_PATH = 'Config\\logging.ini'

"""
modification history
--------------------
V1.00.00, 18May2018, Liu Gang written
V1.00.01, 19Jun2018, Liu Gang Add Config Set functions
V1.00.02, 03Aug2018, Liu Gang Vatbase.file_open, add model name.
V1.00.03, 21May2019, Liu Gang Add Python 3.
V1.00.04, 24May2019, Liu Gang Add Read file ,before set...
--------------------
"""
VAT_BASE_VER = "V1.00.04"


def gettime(time_format=0):
    """
    get system current time
    :param time_format: the format for return value
    :return:
    """
    if time_format == 0:
        return time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    elif time_format == 1:
        return time.strftime("%Y%m%d", time.localtime(time.time()))
    elif time_format == 2:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


class Vatbase:
    def __init__(self):
        self.fn = None
        self.writer = None
        self.isopen = False
        self.headprinted = False
        # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # def __del__(self):
    #     # self.s.close()
    #     # if self.fn is not None:
    #     #     # tmplist = []
    #     #     # wstr = "---TestEnd---"
    #     #     # tmplist.append(wstr)
    #     #     # self.writer.writerow(tmplist)
    #     #     # tmplist.remove(wstr)
    #     #     # tmplist.append("")
    #     #     # self.writer.writerow(tmplist)
    #     #     self.fn.close()
    #     #     self.isopen = False

    def log_tail(self):
        tmplist = []
        wstr = "---TestEnd---"
        tmplist.append(wstr)
        self.writer.writerow(tmplist)
        tmplist.remove(wstr)
        tmplist.append("")
        self.writer.writerow(tmplist)
        self.fn.close()
        self.isopen = False

    def faillog_head(self):
        if self.headprinted is True:
            return True

        if self.isopen is False:
            try:
                self.fn = open('Log\\FailLog' + gettime(1) + '.csv', 'ab+')
            except IOError:
                print("File Open Error")
                return False
            self.isopen = True

        self.writer = csv.writer(self.fn)
        tmplist = []

        wstr = '---TestStart---'
        tmplist.append(wstr)
        self.writer.writerow(tmplist)
        tmplist.remove(wstr)
        tmplist.append(gettime(2))
        self.writer.writerow(tmplist)
        del tmplist
        self.headprinted = True
        return True

    def file_open(self, sel=1, model_name=""):
        """
        file open and print the default head content for log
        :param sel:1 for test log, 0 for platform fail log
        :param model_name:model name ,in file name .
        :return:bool

        180803, add model name.  Liugang

        """
        # if os.getcwd()

        try:
            if sel == 1:
                self.fn = open('Log\\TestLog' + "_%s_" % model_name + gettime(1) + '.csv', 'ab+')
            else:
                self.fn = open('Log\\FailLog' + "_%s_" % model_name + gettime(1) + '.csv', 'ab+')

        except IOError:
            print("File Open Error")
            return False
        self.isopen = True
        self.writer = csv.writer(self.fn)
        if sel == 1:
            tmplist = []
            wstr = '---TestStart---'
            tmplist.append(wstr)
            self.writer.writerow(tmplist)
            tmplist.remove(wstr)
            tmplist.append(gettime(2))
            self.writer.writerow(tmplist)
            tmplist = ["Item", "Low", "High", "Value", "Result", "Time"]
            self.writer.writerow(tmplist)
            self.headprinted = True
            del tmplist

        return True

    def faillog_close(self):
        if self.fn is not None:
            self.fn.close()
            self.isopen = False
        self.isopen = False

    def d_print(self, *str_data):
        """
        print to csv file
        :param str_data:data to print
        :return:
        """
        if self.isopen is False:
            self.file_open(0)

        if self.headprinted is False:
            self.faillog_head()

        str_list = list()
        for s in str_data:
            str_list.append(s)
        self.writer.writerow(str_list)
        # print str_list

        # def udpsend(self, txstr):
        #     """
        #     Udp send , communicate with QT VAT platform
        #     :param txstr:
        #     :return:
        #     """
        #     global _HOST_IP
        #     txstr = txstr.decode("utf-8")
        #     txstr = txstr.encode("gb2312")
        #     c = self.s.sendto(txstr, _HOST_IP)
        #     if c > 0:
        #         return True
        #     else:
        #         return False


class CfgSet:
    def __init__(self, fn=_CFG_FILE):
        self.conf = cp.ConfigParser()
        self.fn = fn

    def readfile(self):
        if len(self.conf.read(self.fn)) == 0:
            return False
        else:
            return True

    def getsections(self):
        return self.conf.sections()

    def getoptions(self, sec):
        return self.conf.options(sec)

    def getvalue(self, sec, opt, dtype='s'):
        if dtype == 's':  # get for string
            return self.conf.get(sec, opt)
        elif dtype == 'f':  # get for float
            return self.conf.getfloat(sec, opt)
        elif dtype == 'i':  # get for int
            return self.conf.getint(sec, opt)

    def getlist(self, sec, dtype='s'):
        optionlen = len(self.getoptions(sec))
        lists = [0] * optionlen
        for i in range(0, optionlen):
            lists[i] = self.getvalue(sec, self.getoptions(sec)[i], dtype)

        return lists

    def setvalue(self, sec, opt, set_value):
        # Add readfile before change. 190524 liugang
        self.readfile()
        try:
            self.conf.set(sec, opt, set_value)
        except NoSectionError:
            self.conf.add_section(sec)
            self.conf.set(sec, opt, set_value)
        finally:
            with open(self.fn, "w") as configfile:
                self.conf.write(configfile)
            return True


if __name__ == "__main__":
    v = Vatbase()
    x = "中国"
