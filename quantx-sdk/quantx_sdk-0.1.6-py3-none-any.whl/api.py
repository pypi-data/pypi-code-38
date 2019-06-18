
import requests
import json
import hmac
import hashlib
from logging import getLogger
from quantx_sdk.exception import ApiError
import time
from datetime import datetime


class API:
    """
    QuantX APIオブジェクト
    API呼び出しを管理し、Projectオブジェクトの取得を行います。
    """

    def __init__(self, public_key, secret_key, api_entry_point, websocket_entry_point):
        self.logger = getLogger(__name__)
        self.API_ENTRY_POINT = api_entry_point
        self.WEBSOCKET_ENTRY_POINT = websocket_entry_point
        self.public_key = public_key
        self.secret_key = secret_key
        self.rateLimit = {}

    def _make_headers(self, body):
        signature = hmac.new(
            bytearray(self.secret_key.encode("utf-8")), digestmod=hashlib.sha512
        )
        signature.update(body.encode("utf-8"))
        return {
            "Content-Type": "application/json; charset=utf-8",
            "X-QuantXToken": self.public_key,
            "X-QuantXSignature": signature.hexdigest(),
        }

    def api(self, path, param={}):
        param["timestamp"] = int(time.mktime(datetime.now().timetuple()))
        body = json.dumps(param)
        url = "{}{}".format(self.API_ENTRY_POINT, path)
        self.logger.debug("POST: {}".format(url))
        result = requests.post(url, data=body, headers=self._make_headers(body))
        if "X-RateLimit-Limit" in result.headers:
            self.rateLimit["limit"] = result.headers["X-RateLimit-Limit"]
            self.rateLimit["remaining"] = result.headers["X-RateLimit-Remaining"]
        res = result.json()
        self.logger.debug("RESPONSE: {}".format(res))
        if result.status_code != 200:
            if not res:
                raise ApiError("API ERROR: STATUS {}".format(result.status_code))
            elif "message" in res:
                raise ApiError("API ERROR: {}".format(res["message"]))
            if "error" in res:
                raise ApiError("API ERROR: {}".format(res["error"]))
            elif "code" in res:
                raise ApiError("API ERROR: CODE {}".format(res["code"]))
            else:
                raise ApiError("API ERROR: {}".format(res))
        if "code" in res and res["code"] != 200:
            if "message" in res:
                raise ApiError("API ERROR: {}".format(res["message"]))
            if "error" in res:
                raise ApiError("API ERROR: {}".format(res["error"]))
            elif "code" in res:
                raise ApiError("API ERROR: CODE {}".format(res["code"]))
            else:
                raise ApiError("API ERROR: {}".format(res))
        return res

    def current_rate_limit(self):
        return self.rateLimit
