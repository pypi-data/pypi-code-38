#!/usr/bin/env python
# -------------------------------------------------------
# lutils library
# Author: Tran Duc Loi (loitranduc@gmail.com)
# Git: https://github.com/loitd/lutils
# Documented follow PEP257 
# -------------------------------------------------------
from datetime import date, timedelta, datetime
from deprecated import deprecated


def datetimestr(format="%Y/%m/%d %H:%M:%S"):
    """Return current datetime in specific format."""
    return(datetime.now().strftime(format))

#yesterday
def yesterday():
    """Print yesterday date in datetime value"""
    return (date.today() - timedelta(days=1))

def yesterdaystr(format="%Y/%m/%d"):
    """Print yesterday datetime in string format."""
    return(yesterday().strftime(format))

# @deprecated("This function is deprecated, please use 'printlog()' function in this library instead")
def printx(content, filepath="./log.txt"):
    """Print to screen output AND write to log file. From version 1.0, by default log file path is: ./log.txt
    Will be moved to printlog(). Please use printlog() instead of printx() with the same syntax."""
    try:
        print("{0}".format(content))
        with open(filepath, "a+") as fh:
            fh.write("[{0}]: {1}\r\n".format(datetimestr(), content))
    except Exception as e:
        raise(e)

def printlog(content, filepath="./log.txt"):
    """Print to screen output AND write to log file. Added from version 1.0.
    By default log file path is: ./log.txt"""
    try:
        print("{0}".format(content))
        with open(filepath, "a+") as fh:
            fh.write("[{0}]: {1}\r\n".format(datetimestr(), content))
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    print(datetimestr())
    printx("abc")
    printlog("abc")