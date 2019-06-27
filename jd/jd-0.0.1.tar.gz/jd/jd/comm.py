#!/usr/bin/python3
# @Time    : 2019-06-27
# @Author  : Kevin Kong (kfx2007@163.com)

from hashlib import md5
import json
import requests
from datetime import datetime


class Comm(object):
    """公共工具"""

    def __get__(self, instance, owner):
        self._appkey = instance._appkey
        self._appsecret = instance._appsecret
        self._access_token = instance._access_token
        self._host = instance._host
        return self

    def sign(self, data):
        """
        签名
        """
        # 忍不住要吐槽京东这个签名算法真的是秀，360buy_param_json这个数据必须要字符串化，然后去空格...
        if data.get("360buy_param_json", False):
            data["360buy_param_json"] = str(json.dumps(
                data["360buy_param_json"])).replace(" ", "")
        qstr = f'{self._appsecret}{"".join(f"{key}{data[key]}" for key in sorted(data.keys()) if data[key] is not None)}{self._appsecret}'
        return md5(qstr.encode("utf-8")).hexdigest().upper()

    def _get_data(self, data):
        data["app_key"] = self._appkey
        data["access_token"] = self._access_token
        data["timestamp"] = datetime.strftime(
            datetime.now(), '%Y-%m-%d %H:%M:%S')
        data["sign"] = self.sign(data)
        return data

    def get(self, data):
        """
        get提交
        """
        data = self._get_data(data)
        return requests.get(data=data)
