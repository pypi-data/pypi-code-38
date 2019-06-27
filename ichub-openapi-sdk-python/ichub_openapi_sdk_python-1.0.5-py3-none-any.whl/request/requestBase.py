import requests
from ichubOpenApi import const
from ..sign.Passport import Identify
import json


class requestBase:

    def __init__(self, host=None, v='1.0.0', app_id='', sign_type='', key='', public_key='', private_key=''):
        self.v = v
        self.verify = Identify(sign_type, key, public_key, private_key)
        self.app_id = app_id
        self.sign_type = sign_type
        self.host = host if host is not None else const.HOST

    def send_request(self, params=None, filter_param=None):
        params['timestamp'] = const.TIMESTAMP
        params['v'] = self.v
        params['app_id'] = self.app_id
        params['sign_type'] = self.sign_type
        build_params = dict.copy(params)

        if filter_param is not None:
            for i in filter_param:
                del build_params[i]

        sign = self.verify.buildRequestMysign(build_params)
        params['sign'] = sign
        try:
            r = requests.post(self.host, data=params)
            r = r.text
            result = json.loads(r)
            return result
        except Exception as e:
            return False
