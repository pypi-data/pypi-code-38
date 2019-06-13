#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-09-21 15:46:17
'''
import collections
import datetime
import json
import socket


class Dict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            self.__setitem__(key, value)

    def to_dict(self):
        return DictUnwrapper(self)

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        try:
            return self[key]
        except Exception:
            return None

    def __setitem__(self, key, value):
        super().__setitem__(key, DictWrapper(value))

    __setattr__ = __setitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    # def __repr__(self):
    #     return 'Dict<%s>' % dict.__repr__(self)

    # def __str__(self):
    #     return json.dumps(self, cls=JSONEncoder, ensure_ascii=False)


class DefaultDict(collections.defaultdict):

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        return self[key]


def DictWrapper(*args, **kwargs):
    if args and len(args) == 1:
        if isinstance(args[0], collections.defaultdict):
            return DefaultDict(args[0].default_factory, args[0])
        elif isinstance(args[0], dict):
            return Dict(args[0])
        elif isinstance(args[0], (tuple, list)):
            return type(args[0])(map(DictWrapper, args[0]))
        else:
            return args[0]
    elif args:
        return type(args)(map(DictWrapper, args))
    else:
        return Dict(**kwargs)


def DictUnwrapper(doc):
    if isinstance(doc, DefaultDict):
        return collections.defaultdict(doc.default_factory, doc)
    if isinstance(doc, Dict):
        return dict(map(lambda x: (x[0], DictUnwrapper(x[1])), doc.items()))
    if isinstance(doc, (tuple, list)):
        return type(doc)(map(DictUnwrapper, doc))
    return doc


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def connect(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


class JSONEncoder(json.encoder.JSONEncoder):
    '''针对某些不能序列化的类型如datetime，使用json.dumps(data, cls=JSONEncoder)
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        try:
            return super().default(obj)
        except Exception:
            return str(obj)
