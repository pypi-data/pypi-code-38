# -*- coding: utf-8 -*-

import inspect

from django.conf import settings
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured


class SysConfig(object):
    def __init__(self, configs):
        if configs is None:
            return

        for item in configs:
            keys = item.keys()
            if 'config_key' in keys and 'config_value' in keys:
                setattr(self, item['config_key'].upper(), item['config_value'])

    @property
    def configs(self):
        return self.__dict__


def load_backend(path):
    return import_string(path)()


def _get_backend():

    if not hasattr(settings, 'SYS_CONFIG_BACKEND'):
        raise ImproperlyConfigured('SYS_CONFIG_BACKEND')

    path = settings.SYS_CONFIG_BACKEND
    backends = []

    def inn_get_backend():
        if len(backends) == 0:
            backends.append(load_backend(path))
        return backends[0]
    return inn_get_backend


# 使用闭包的目的是延迟加载backend。
get_backend = _get_backend()


def get_config():
    try:
        backend = get_backend()
        try:
            inspect.getcallargs(backend.get_config)
        except TypeError:
            return

        lst = backend.get_config()
        conf = SysConfig(lst)
        return conf
    except Exception as e:
        print e
