# -*- coding:utf-8 -*-
__author__ = 'Dragon Sun'

import datetime
import dateutil.parser as date_parser  # pip install python-dateutil


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
    将ISO8601字符串转换为datetime.datetime
    :param s: str, ISO8601字符串，例如：'2019-04-13T12:50:00.000Z'
    :return: datetime
    """
    return date_parser.parse(s)


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
