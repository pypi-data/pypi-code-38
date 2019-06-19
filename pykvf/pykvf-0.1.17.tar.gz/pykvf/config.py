#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

@author: banixc

@contact: banixc@gmail.com

@time: 2017/12/11 16:26

@desc: config

    读取配置文件

"""
import json

try:
    import toml
except ImportError:
    toml = None

config_dict = {}


def init_conf(filename, name='__default'):
    with open(filename, encoding='utf8') as fp:
        data = fp.read()
        decode_data = __try_decode(data, json.loads)

        if decode_data:
            config_dict[name] = decode_data
            return decode_data

        if toml:
            decode_data = __try_decode(data, toml.loads)
            if decode_data:
                config_dict[name] = decode_data
                return decode_data
    return None


def get_conf(name='__default'):
    return config_dict[name]


def __try_decode(data, call):
    try:
        return call(data)
    except ValueError:
        return None
