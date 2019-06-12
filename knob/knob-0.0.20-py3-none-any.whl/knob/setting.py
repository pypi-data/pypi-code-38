# -*- coding:utf-8 -*-

import six
from django.conf import settings

__all__ = ['get_setting', 'set_setting']


setting_pool = []
dynamic_setting = None

if 'constance' in settings.INSTALLED_APPS:
    try:
        from constance import config as constance_config
        setting_pool.append(constance_config)
        dynamic_setting = 'Constance'
    except ImportError:
        constance_config = None

setting_pool.append(settings)


def get_setting(key, default=None):
    res = default
    for setting in setting_pool:
        if hasattr(setting, key):
            res = getattr(setting, key)
    return res


def set_setting(key, value):
    if dynamic_setting == 'Constance':
        setattr(constance_config, key, value)
    else:
        raise RuntimeError("No dynamic setting module installed.")
