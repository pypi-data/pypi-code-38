#!/usr/bin/env python
from datetime import date, timedelta, datetime

def todaystr(format="%Y/%m/%d %H:%M:%S"):
    return(datetime.now().strftime(format))

#yesterday
def yesterday():
    return (date.today() - timedelta(days=1))

def yesterdaystr(format="%Y/%m/%d"):
    # print yesterday datetime
    return(yesterday().strftime(format))

def printx(content, filepath):
    try:
        print("{0}".format(content))
        with open(filepath, "a+") as fh:
            fh.write("[{0}]: {1}\r\n".format(todaystr(), content))
    except Exception as e:
        raise(e)

if __name__ == "__main__":
    print(todaystr())