import datetime
from calendar import EPOCH
from numpy import long
from sklearn.utils.bench import total_seconds
import time

def datetime2timestamp(dt, convert_to_utc=False):
    if isinstance(dt, datetime.datetime):
        if convert_to_utc: # 是否转化为UTC时间
            dt = dt + datetime.timedelta(hours=-8) # 中国默认时区
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp)
    return dt

def ConvertCSharpTicksToLinuxTicks(value):
    csharpTicks1970 = 621355968000000000
    linuxTicks = (value - csharpTicks1970) / 10000000
    timeZone = 28800
    linuxTicks = linuxTicks- timeZone
    return linuxTicks

# 636793920000000000
# 1553754008
# 1543795200

#621355968000000000
linuxTicks = ConvertCSharpTicksToLinuxTicks(636909351085100108)
print(linuxTicks)

dt = datetime.datetime.fromtimestamp(0)
print(dt)
# online_dt = datetime.datetime(1970,1,1,0,0,0)
# online_seconds = int(time.mktime(online_dt.timetuple()))
# print(online_seconds)


