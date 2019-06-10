# -*- coding: utf-8 -*-
import re
import json
from ..lib.CommonLogger import debug, info, warn, error


class ApiInfo:
    """
    用于生成需要的对接数据结构
    """

    def __init__(self, cfg_dict):
        self.cfg = cfg_dict

    def __getitem__(self, item):
        return self.cfg.get(item)

    def __setitem__(self, key, value):
        return self.cfg.__setitem__(key, value)

    def get(self, item, default=None):
        return self.cfg.get(item, default)

    def is_cli(self):
        if self.cfg.get('is_cli'):
            return True
        else:
            return False

    def call_api(self, *args, **kwargs):
        api_func = self.cfg.get('api')
        debug("api 调用: url=> [{}],api:{}".format(self.cfg.get('url'), api_func))
        return api_func(*args, **kwargs)

    @property
    def uniq_url(self):
        method = self.cfg.get('method')
        url = self.cfg.get('url')
        if method is None:
            return url
        else:
            return "{}/{}".format(url, method)
