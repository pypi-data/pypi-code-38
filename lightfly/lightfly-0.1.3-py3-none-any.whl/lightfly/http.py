import json
import hmac
import requests
import hashlib
from datetime import datetime
from .exception import AuthException
from .exception import BadRequestException


class Client(object):

    def __init__(self, app_id='', app_secret_key=''):
        self.app_id = app_id
        self.app_secret_key = app_secret_key
        self.base_url = 'http://129.211.11.159'

    def get(self, path_info, params={}):

        query_params = params.copy()
        params["path_info"] = path_info
        params["sign_date"] = datetime.now().strftime("%Y-%m-%d")
        params['app_id'] = self.app_id

        data_str = json.dumps(params, sort_keys=True, separators=(',', ':'))
        token = hmac.new(self.app_secret_key.encode(), data_str.encode(), digestmod=hashlib.sha256).hexdigest()

        r = requests.get(self.base_url + path_info, query_params, headers={
            "X-App-Id": self.app_id,
            "X-Token": token,
        })

        if r.status_code == 400:
            raise BadRequestException(r.text)

        if r.status_code != 200:
            raise AuthException(r.text)

        return r.text

    def set_app_id(self, app_id):
        self.app_id = app_id

    def set_app_secret_key(self, key):
        self.app_secret_key = key
