# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__description__ = '''
use hot-redis(ORM) operate on redis
'''

import os
import sys

import hot_redis as hr

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from importlib import reload

reload(sys)

List = hr.List
Set = hr.Set
Dict = hr.Dict
String = hr.String
ImmutableString = hr.ImmutableString
Int = hr.Int
Float = hr.Float
Queue = hr.Queue
LifoQueue = hr.LifoQueue
SetQueue = hr.SetQueue
LifoSetQueue = hr.LifoSetQueue
DefaultDict = hr.DefaultDict
MultiSet = hr.MultiSet


class Rds(object):
    def __init__(self, conf=None):
        conf = conf if conf else {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 3,
            'socket_connect_timeout': 3,
        }
        hr.configure(conf)


class RdsClient(Rds):
    """
        wrapper of hot-redis, exported all properties
        in case we may use other ORM lib to operate on redis
    """
    List = hr.List
    Set = hr.Set
    Dict = hr.Dict
    String = hr.String
    ImmutableString = hr.ImmutableString
    Int = hr.Int
    Float = hr.Float
    Queue = hr.Queue
    LifoQueue = hr.LifoQueue
    SetQueue = hr.SetQueue
    LifoSetQueue = hr.LifoSetQueue
    DefaultDict = hr.DefaultDict
    MultiSet = hr.MultiSet

    def __init__(self, conf):
        super(RdsClient, self).__init__(conf)

    def ok(self):
        l = self.List(key='foo')

    @classmethod
    def transaction(cls):
        """
        """
        return hr.transaction()


def transaction():
    """
    """
    return hr.transaction()


def client(*args, **kwargs):
    return hr.HotClient(*args, **kwargs)


def config(*args, **kwargs):
    return hr.configure(*args, **kwargs)
