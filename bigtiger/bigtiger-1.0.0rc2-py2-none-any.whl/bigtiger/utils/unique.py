# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import uuid


def get_uuid():
    """获取一个新的uuid"""
    return uuid.uuid4()


def get_uuid_str():
    """获取uuid字符串"""
    return str(get_uuid())


def to_uuid(str):
    """将字符串转换为uuid对象"""
    return uuid.UUID(str)
