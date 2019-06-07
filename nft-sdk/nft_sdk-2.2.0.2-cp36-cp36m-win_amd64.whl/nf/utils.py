# coding=utf-8
from __future__ import unicode_literals, print_function, absolute_import
import time
import six
from typing import Dict, Text, Any, List, Union
from datetime import date, datetime, timedelta, timezone
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from nf.constant import DATA_TYPE_TICK

GmDate = Union[Text, datetime, date]  # 自定义gm里可表示时间的类型
TextNone = Union[Text, None]  # 可表示str或者None类型


def str_lowerstrip(s):
    # type: (Text) -> Text
    """把字符串进行lower跟strip操作"""
    return s.lower().strip() if s else ''


def date2datetime(d):
    # type: (Union[date,str]) -> datetime
    """
    把date类型转换为datetime类型
    """
    if isinstance(d, six.string_types):
        if len(d) == 8:
            return datetime.strptime(d, '%Y%m%d')
        if len(d) == 10:
            return datetime.strptime(d, '%Y-%m-%d')
        raise Exception('字符串{}不能转为datetime'.format(d))
    return datetime.combine(d, datetime.min.time())


def protobuf_timestamp2datetime(timestamp):
    # type: (Timestamp) -> Union[datetime, None]
    """
    把 protobuf 的 timestamp 转为 datetime类型
    :return:
    """
    if timestamp is None:
        return None
    deltasec = timestamp.seconds + timestamp.nanos / float(_NANOS_PER_SECOND)
    return datetime(1970, 1, 1) + timedelta(seconds=deltasec)


# 来自于 google.protobuf.internal.well_nkown_types.py 里定义的变量
_NANOS_PER_SECOND = 1000000000


def protomessage2dict(protomessageobj, dictobj, *keys):
    # type: (Message, Dict[Text, Any], List[Text]) -> None
    """
    把 proto的message 上的指定的property,附值到dictobj上.其中timestamp会转换为 datetime类型
    """
    for k in keys:
        pv = getattr(protomessageobj, k, None)
        if pv is not None:
            if isinstance(pv, Timestamp):
                if pv.ListFields():
                    # pv.ToDatetime()  不要使用这个方法, 这个方法在python32位时, 最小只能转到 1969-12-31 12:00:00, 因为受限于
                    # ValueError: timestamp out of range for platform localtime()/gmtime() function
                    deltasec = pv.seconds + pv.nanos / float(_NANOS_PER_SECOND)
                    dictobj[k] = datetime(1970, 1, 1) + timedelta(seconds=deltasec)
                else:
                    dictobj[k] = None
            else:
                dictobj[k] = pv


def to_datestr(d):
    # type: (GmDate) -> TextNone
    """
    把datetime.date或datetime.datetime, 或者 yyyy-mm-dd, yyyymmdd 表示日期的字符串统一转换为 yyyy-mm-dd的字符串
    如果不能转换返回None
    """
    date_str = ''
    if isinstance(d, (date, datetime)):
        date_str = d.strftime('%Y-%m-%d')
    if isinstance(d, six.string_types):
        if len(d) == 8:
            try:
                dt = datetime.strptime(d, '%Y%m%d')
                date_str = dt.strftime('%Y-%m-%d')
            except ValueError as e:
                pass
        if len(d) == 10:
            try:
                datetime.strptime(d, '%Y-%m-%d')
                date_str = d
            except ValueError as e:
                pass

    return date_str if date_str else d


def to_exchange(exchange):
    # type: (Text) -> TextNone
    """转换成正确的交易市场. 如果不存在, 则返回None"""
    exchange_set = {'SHSE', 'SZSE', 'CFFEX', 'SHFE', 'DCE', 'CZCE'}
    if not exchange:
        return None
    s = str(exchange).upper().strip()
    return s if s in exchange_set else None


def load_to_list(value):
    """
    无论输入的是啥类型， 都转成list
    """
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        return [value]

    if isinstance(value, six.string_types):
        return [item.strip() for item in value.split(',')]
    return value


def load_to_datetime_str(value):
    if isinstance(value, (date, datetime)):
        value = value.astimezone(tz=timezone.utc)
        return value.strftime('%Y-%m-%d %H:%M:%S')

    return value


def load_to_second(value):
    # type: (str) -> int
    value = value.lower()

    if value.endswith('h'):
        return int(value[0:-1]) * 60 * 60

    if value.endswith('d'):
        return int(value[0:-1]) * 60 * 60 * 24

    if value.endswith('s'):
        return int(value[0:-1])

    raise ValueError('仅支持s(秒), h(小时), d(天) 结尾')


class DictLikeObject(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, item, value):
        self[item] = value

    def __str__(self):
        return super(DictLikeObject, self).__str__()

    def __repr__(self):
        return super(DictLikeObject, self).__repr__()


class ObjectLikeDict(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, item):
        return self.data.get(item)

    # 如果前面没有定义过的属性， 就会调用这个函数
    def __getattr__(self, item):
        return self.data.get(item)

    def __setitem__(self, item, value):
        self.data[item] = value

    def __setattr__(self, item, value):
        if item != 'data':
            self.data[item] = value
        else:
            super(ObjectLikeDict, self).__setattr__(item, value)

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.data.__repr__()


def timestamp2datetime(stamp):
    if stamp is None:
        return None
    if stamp/1000000000>1000:
        stamp=int(stamp/1000)
    return datetime(1970, 1, 1, 0, 0, 0) + timedelta(seconds=stamp)


# this method doesn't work correctly
def datetime2timestamp(dt, convert_to_utc=False):
    ''' Converts a datetime object to UNIX timestamp in seconds. '''

    if isinstance(dt, datetime):
        if convert_to_utc:  # 是否转化为UTC时间
            dt = dt + timedelta(hours=-8) # 中国默认时区
        timestamp = time.mktime(dt.timetuple())
        return int(timestamp)
    return dt
    '''
    #Note: It is necessary to supply timezone.utc explicitly otherwise.timestamp()
    #assume that your naive datetime object is in local timezone.
    if isinstance(dt, datetime):
        dt = dt.replace(tzinfo=timezone.utc)
        timestamp = dt.timestamp()
        return int(timestamp)
    return dt
    '''


def standard_fields(fields, letter_upper=False):
    if not fields:
        return None, None

    if letter_upper:
        fields_list = [field.strip().upper() for field in fields.split(',')]

    else:
        fields_list = [field.strip().lower() for field in fields.split(',')]

    fields_str = ','.join(fields_list)
    return fields_str, fields_list


def dict_fields_filter(dic, fields):
    if not dict or not fields:
        return {}

    if not isinstance(dic, dict):
        return {}

    if not isinstance(fields, list):
        fields = load_to_list(fields)

    ret_dict = {}
    for field in fields:
        if field in dic:
            ret_dict[field] = dic[field]

    return ret_dict


def takePriceFromDepth(depth):
    return depth['price']


def check_frequency(frequency):
    frequency = frequency.lower()
    if frequency == DATA_TYPE_TICK:
        return frequency
    elif frequency.endswith('s'):
        return frequency
    elif frequency.endswith('m'):
        return '{}s'.format(int(frequency[0:-1]) * 60)
    elif frequency.endswith('h'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60)
    elif frequency.endswith('d'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24)
    elif frequency.endswith('w'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24 * 7)
    elif frequency.endswith('y'):
        return '{}s'.format(int(frequency[0:-1]) * 60 * 60 * 24 * 365)
    else:
        return None
