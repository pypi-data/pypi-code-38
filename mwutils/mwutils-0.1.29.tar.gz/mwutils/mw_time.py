from datetime import datetime,timezone,timedelta
try:
    # 性能 10000次转换耗时：0.00976705551147461
    from ciso8601 import parse_datetime
except ImportError as e:
    # 性能 10000次转换耗时：2.91825270652771
    from dateutil.parser import parse as parse_datetime

import time
DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M:%S'
WEB_DATETIME_FMT='%Y-%m-%dT%H:%M:%SZ'
LOCALE_TIMEZONE = None
TIME_FMT = '%H:%M:%S'

# 取最小时间
min_time = lambda t1,t2: t1 if t1<t2 else t2
# 取最大时间
max_time = lambda t1,t2: t1 if t1>t2 else t2

def str2date(datestr):
    '''
    把日期型的str转换成日期
    :param datestr: 格式为 YYYY-MM-DD
    :return:
    '''
    return str2datetime(datestr).date()

# 兼容旧的格式
mw_str_to_date = str2date

def str2time(timestr):
    '''
    把时间格式换成时间
    :param timestr: 格式：HH:MM::SS
    :return:
    '''
    return datetime.strptime(timestr, TIME_FMT).time()

def datetime2timestamp(dt):
    '''
    把日期时间变成时间戳
    :param datetime: 日期时间
    :return:
    '''
    return int(dt.timestamp())
toUTCtime = mw_time_to_timestamp=datetime2timestamp

def date2str(d):
    '''
    把日期输出 YYYY-MM-DD 格式
    :param d:  date
    :return:
    '''
    return datetime.strftime(d, DATE_FMT)
mw_date_to_str = date2str

def datetime2str(dt):
    '''
    把日期时间变成 YYYY-MM-DD HH:MM:SS 格式
    :param dt: datetime
    :return:
    '''
    return datetime.strftime(dt,DATETIME_FMT)

mw_datetime_to_str=datetime2str

def timestamp2datetimestr(ts):
    '''
    timestamp转换成本地日期时间格式
    :param ts: 时间戳timestamp
    :return:
    '''
    t =datetime.fromtimestamp(ts)
    return mw_datetime_to_str(t)
mw_timestamp_to_str=timestamp2datetimestr

def get_locale_timezone():
    # 台北 -28800
    # 美国 +14400
    global LOCALE_TIMEZONE
    if LOCALE_TIMEZONE is None:
        LOCALE_TIMEZONE = timezone(timedelta(seconds=-time.timezone))
    return LOCALE_TIMEZONE

def str2datetime(iso8601str):
    '''
    支持 iso8601格式的字符串转为本地的datetime
    使用第三方类库,
    :param iso8601str:
       本地时间格式：2018-01-10 12:33:00 ,2018-01-10T12:33:00
       UTC 时间格式：2018-01-10T12:33:00Z
     不同时区的格式：2018-01-10T12:33:00+01:00，2018-01-10T12:33:00+08:00
    :return:
    '''
    dt = parse_datetime(iso8601str)
    if dt.tzinfo is None:
        return dt
    # 10000笔耗时0.025秒
    return dt.fromtimestamp(dt.timestamp())

def datetime2isostr(dt):
    '''
    转换成iso8601标准的格式
    :param dt: datetime
    :return:
    '''
    if dt.tzinfo is None:
        dt = dt.astimezone(get_locale_timezone())
    return dt.isoformat()
mw_str_to_datetime = str2datetime

if __name__ == '__main__':
    print(str2datetime('2018-01-01'))
    print(str2datetime('2018-01-01T12:00:00'))
    print(str2datetime('2018-01-01T12:00:00Z'))
    print(str2datetime('2018-01-01T12:00:00+02:00'))
    print(str2date('2018-01-01'))
    print(str2time('11:11:11'))
    print(datetime2isostr(datetime.now()))
    print(datetime2str(datetime.now()))
    print(datetime2timestamp(datetime.now()))
    print(timestamp2datetimestr(1515579120.0))



