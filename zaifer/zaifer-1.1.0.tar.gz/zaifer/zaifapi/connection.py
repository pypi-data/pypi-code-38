import hashlib
import hmac
import json
import time
from datetime import datetime
from decimal import Decimal
from urllib.parse import urlencode

import requests

from zaifer.zaifapi.exception import *


class HttpConnection():
    '''
    ZaifAPIへの接続を表します。
    '''

    def __init__(self, base_url: str = None, key: str = None, secret: str = None):
        '''
        コンストラクタ
        '''
        self._base_url = base_url
        self._key = key
        self._secret = secret

    def post(self, method: str, params: dict) -> dict:
        '''
        POST要求を送信します。
        '''
        # 引数を検証
        method = '' if method is None else method
        params = {} if params is None else params

        # POST要求を作成
        url = self._base_url + method
        encoded_params = urlencode(params)
        http_headers = self._create_http_headers(encoded_params)

        # POST要求を送信
        response = requests.post(
            url, data=encoded_params, headers=http_headers)

        # レスポンスを取得
        if response.status_code != 200:
            raise Exception(
                'return status code is {}'.format(response.status_code))
        return json.loads(response.text)

    def get(self, method: str, params: dict) -> dict:
        '''
        GET要求を送信します。
        '''
        # 引数を検証
        method = '' if method is None else method
        params = {} if params is None else params

        # GET要求を作成
        url = self._base_url + method

        # GET要求を送信
        response = requests.get(url, params=params)

        # レスポンスを取得
        if response.status_code != 200:
            raise Exception(
                'return status code is {}'.format(response.status_code))
        return json.loads(response.text)

    def _create_http_headers(self, params: str) -> dict:
        '''
        HTTPヘッダーを作成します。
        '''
        return self._create_signature(self._key, self._secret, params)

    def _create_signature(self, key: str, secret: str, params: str) -> dict:
        '''
        デジタル署名を作成します。
        '''
        signature = hmac.new(
            bytearray(secret.encode('utf-8')), digestmod=hashlib.sha512)
        signature.update(params.encode('utf-8'))
        return {
            'key': key,
            'sign': signature.hexdigest()
        }


class UrlConfigs():
    '''
    ZaifAPIの接続情報を表します。
    '''

    def __init__(self):

        self._publicApiUrl = 'https://api.zaif.jp/api/1'
        self._tradeApiUrl = 'https://api.zaif.jp/tapi'
        self._futureTradeApiUrl = 'https://api.zaif.jp/fapi/1'
        self._marginTradeApiUrl = 'https://api.zaif.jp/tlapi'
        self._chartApiUrl = 'https://zaif.jp/zaif_chart_api/v1'

    @property
    def publicApiUrl(self) -> str:
        return self._publicApiUrl

    @publicApiUrl.setter
    def publicApiUrl(self, value: str):
        self._publicApiUrl = value

    @property
    def tradeApiUrl(self) -> str:
        return self._tradeApiUrl

    @tradeApiUrl.setter
    def tradeApiUrl(self, value: str):
        self._tradeApiUrl = value

    @property
    def futureTradeApiUrl(self) -> str:
        return self._futureTradeApiUrl

    @futureTradeApiUrl.setter
    def futureTradeApiUrl(self, value: str):
        self._futureTradeApiUrl = value

    @property
    def marginTradeApiUrl(self) -> str:
        return self._marginTradeApiUrl

    @marginTradeApiUrl.setter
    def marginTradeApiUrl(self, value: str):
        self._marginTradeApiUrl = value

    @property
    def chartApiUrl(self) -> str:
        return self._chartApiUrl

    @chartApiUrl.setter
    def chartApiUrl(self, value: str):
        self._chartApiUrl = value


class NonceGenerator():
    '''
    ノンスを生成します。
    '''

    @staticmethod
    def generate() -> Decimal:
        '''
        ノンスを生成します。
        '''
        now = datetime.now()
        datetime_part = str(int(time.mktime(now.timetuple())))
        second_part = '{0:06d}'.format(now.microsecond)

        return Decimal(datetime_part + '.' + second_part)


class ResponseParser():
    '''
    レスポンスをパースします。
    '''

    @staticmethod
    def parse(response: dict) -> dict:
        '''
        レスポンスをパースします。
        '''
        if response['success'] == 0:
            if response['error'] == 'no data found for the key':
                raise InvalidAPIKeyException(response['error'])
            elif response['error'] == 'signature mismatch':
                raise InvalidAPISecretException(response['error'])
            elif response['error'] == 'order not found':
                raise OrderNotFoundException(response['error'])
            elif response['error'] == 'nonce not incremented':
                raise NonceNotIcreasedException(response['error'])
            elif response['error'] == 'nonce out of range':
                raise NonceOutOfRangeException(response['error'])
            raise Exception(response['error'])

        return response['return']
