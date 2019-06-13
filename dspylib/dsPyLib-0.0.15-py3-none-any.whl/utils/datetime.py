# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'

import time
import datetime
import calendar
import math
from enum import Enum
import dateutil.parser as date_parser

"""
"%Y-%m-%d %H:%M:%S.%f"
"""


class CycleUnit(Enum):
    second = 1
    minute = 2
    hour = 3
    day = 4
    week = 5
    month = 6
    quarter = 7
    year = 8


def whole_point(dt, unit):
    """
    获取最靠近指定时间之前的整点时间
        '2016-01-02 12:34:56', second , '2016-01-02 12:34:56'
        '2016-01-02 12:34:56', minute , '2016-01-02 12:34:00'
        '2016-01-02 12:34:56', hour   , '2016-01-02 12:00:00'
        '2016-01-02 12:34:56', day    , '2016-01-02 00:00:00'
        '2016-01-02 12:34:56', week   , '2015-12-28 00:00:00'
        '2016-01-02 12:34:56', month  , '2016-01-01 00:00:00'
        '2016-01-02 12:34:56', quarter, '2016-01-01 00:00:00'
        '2016-01-02 12:34:56', year   , '2016-01-01 00:00:00'

    示例：
        s = '2016-01-02 12:34:56'
        dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        dt = whole_point(dt, CycleUnit.week)
        print(dt.strftime("%Y-%m-%d %H:%M:%S.%f"))

    :param dt: datetime, 指定的时间
    :param unit: CycleUnit, 单位
    :return: datetime, 整点时间
    """
    if unit == CycleUnit.week:
        week_day = datetime.datetime.isoweekday(dt)
        dt = dt + datetime.timedelta(days=-(week_day - 1))

    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    if unit.value >= CycleUnit.minute.value:
        second = 0
    if unit.value >= CycleUnit.hour.value:
        minute = 0
    if unit.value >= CycleUnit.day.value:
        hour = 0
    if unit.value >= CycleUnit.month.value:
        day = 1
    if unit.value >= CycleUnit.year.value:
        month = 1
    if unit == CycleUnit.quarter:
        month = max(1, int(month / 3) * 3)

    return datetime.datetime(year, month, day, hour, minute, second)


def month_delta(dt, interval):
    """
    获取差异月份时间
        '2016-03-31 12:34:56', -1, 2016-02-29 12:34:56  前一个月(注意日期)
        '2016-03-31 12:34:56', 1 , 2016-04-30 12:34:56  后一个月(注意日期)
    示例
        s = '2016-03-31 12:34:56'
        dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        dt = month_delta(dt, 1)
        print(dt.strftime("%Y-%m-%d %H:%M:%S.%f"))

    :param dt: datetime, 指定时间
    :param interval: int, 月份差异数(可为负数)
    :return: datetime，新的时间
    """
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    month += interval
    if month > 0:
        year += int(month / 12)
        month = month % 12
    else:
        delta = abs(math.floor(month / 12))
        year -= delta
        month += delta * 12

    month_range = calendar.monthrange(year, month)
    day = min(day, month_range[1])

    return datetime.datetime(year, month, day, hour, minute, second)


def next_time(dt, interval, unit):
    """
    获取从指定时间开始的下一次时间
    例如：
        '2018-08-17 14:01:32', 2, minute => '2018-08-17 14:03:32'

    :param dt: datetime, 开始时间
    :param interval: int, 周期次数
    :param unit: CycleUnit, 周期单位
    :return: datetime 下一次时间
    """
    if unit == CycleUnit.second:
        dt = dt + datetime.timedelta(seconds=interval)
    if unit == CycleUnit.minute:
        dt = dt + datetime.timedelta(minutes=interval)
    if unit == CycleUnit.hour:
        dt = dt + datetime.timedelta(hours=interval)
    if unit == CycleUnit.day:
        dt = dt + datetime.timedelta(days=interval)
    if unit == CycleUnit.week:
        dt = dt + datetime.timedelta(weeks=interval)
    if unit == CycleUnit.month:
        dt = month_delta(dt, interval)
    if unit == CycleUnit.quarter:
        dt = month_delta(dt, interval * 3)
    if unit == CycleUnit.year:
        dt = month_delta(dt, interval * 12)
    return dt


def timestamp_to_iso(ts):
    """
    将timestamp转换为ISO8601字符串
    例如：
        timestamp_to_iso(time.time()) => 2019-04-07T12:51:30.000Z
    :param ts: timestamp
    :return: str
    """
    date = datetime.datetime.utcfromtimestamp(ts)
    iso = date.isoformat('T', 'milliseconds') + 'Z'
    return iso


def iso_to_datetime(s: str) -> datetime.datetime:
    """
    将ISO8601字符串转换为datetime.datetime(本地时区)
    :param s: str, ISO8601字符串，例如：'2019-04-13T12:50:00.000Z'
    :return: datetime
    """
    d = date_parser.parse(s)
    d = d.astimezone(datetime.datetime.now().tzinfo)
    return d


def datetime_to_iso(d: datetime.datetime) -> str:
    """
    将datetime转换为ISO8601字符串
    :param d: datetime.datetime
    :return: str, ISO8601字符串，例如：'2019-04-13T12:50:00.000Z'
    """
    if d:
        d1 = datetime.datetime.utcfromtimestamp(d.timestamp())
        return d1.isoformat(timespec='milliseconds') + 'Z'
    else:
        return ''


def datetime_compare(d1: datetime.datetime, d2: datetime.datetime) -> int:
    """
    比较两个日期的大小
    :param d1: 日期1
    :param d2: 日期2
    :return: d1 < d2 => -1; d1 = d2 => 0; d1 > d2 => 1
    """
    t1 = time.mktime(d1.timetuple())
    t2 = time.mktime(d2.timetuple())
    if t1 < t2:
        return -1
    if t1 > t2:
        return 1
    return 0
