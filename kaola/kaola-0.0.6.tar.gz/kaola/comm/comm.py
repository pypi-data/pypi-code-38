
import requests
from hashlib import md5
from datetime import datetime
import pytz

class Comm(object):

    def __get__(self, instance, owner):
        self._app_key = instance._app_key
        self._app_secret = instance._app_secret
        self._v = instance._v
        self._host = instance._host
        self._access_token = instance._access_token
        return self

    def sign(self, data):
        """
        验签算法
        """
        data['app_key'] = self._app_key
        data["access_token"] = self._access_token
        qstring = f'{self._app_secret}{"".join(f"{key}{data[key]}" for key in sorted(data.keys()) if data[key] is not None)}{self._app_secret}'
        return md5(qstring.encode("utf-8")).hexdigest().upper()

    def _get_sys_args(self, data=None):
        """
        封装请求的必要参数
        考拉服务器时间使用的是CST时间，UTC的服务器需要加8个小时
        """
        data["app_key"] = self._app_key
        data["timestamp"] = datetime.strftime(
            datetime.now(pytz.timezone("Asia/Shanghai")), '%Y-%m-%d %H:%M:%S')
        data["v"] = self._v
        data["sign"] = self.sign(data)
        return data

    def post(self, data=None, json=None):
        """
        使用post方法提交请求
        如果返回结果正确，则剥去最外一层的封装response
        """
        data = self._get_sys_args(data)
        result = requests.post(self._host, data=data, json=json).json()
        response_name = f'{data["method"].replace(".","_")}_response'
        return result[response_name] if response_name in result else result
