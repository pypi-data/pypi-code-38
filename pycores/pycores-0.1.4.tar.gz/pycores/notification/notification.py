#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, unique

@unique
class NOTIFICATION(Enum):
    '''
    :brief 预定义事件类型
    '''
    EXAMPLE = 'example'

# NOTIFICATION.EEEE = 'DDDD';
setattr(NOTIFICATION, 'EEEE', 'DDDD')

class AA_NOTIFICATION(NOTIFICATION):
    XXX = 'ddddddd'

def parse_notification(notification_str):
    return NOTIFICATION.__members__.get(notification_str.upper(), None)

'''
@brief 通知，在当前线程执行
'''
class Notification(object):
    _notification_type = None
    _notification_payload = None

    _before = None
    _after = None

    def __init__(self, notification_type, notification_payload=None):
        self._notification_type = notification_type
        self._notification_payload = notification_payload

    def __repr__(self):
        return ' '.join('{}:{}'.format(k, v) for k, v in self.__dict__.items())

    def before(self, notification):
        '''
        添加后置事件
        :param event:
        :return:
        '''
        self._after = notification

    def after(self, notification):
        '''
        添加前置事件
        :param event:
        :return:
        '''
        self._before = notification

    def type(self):
        '''
        获取事件类型
        :return:
        '''
        return self._notification_type

    def data(self):
        '''
        获取事件负载
        :return:
        '''
        return self._notification_payload

    def pre(self):
        '''
        获取前置事件

        :return:
        '''
        return self._before

    def post(self):
        '''
        获取后置事件
        :return:
        '''
        return self._after


d = parse_notification('ddddddd')
print(str(d))