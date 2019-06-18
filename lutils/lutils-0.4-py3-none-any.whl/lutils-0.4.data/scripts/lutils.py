#!/usr/bin/env python
from datetime import date, timedelta

#yesterday
def yesterday():
    return (date.today() - timedelta(days=1))

def yesterdaystr(format="%Y/%m/%d"):
    # print yesterday datetime
    return(yesterday().strftime(format))

