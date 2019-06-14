import base64
import json
import urllib
from dataclasses import dataclass, asdict
from .message import Message
import requests
from requests.auth import HTTPBasicAuth


class Xinge(object):
    def __init__(self, appId, secretKey):
        """

        :param appId: str, APP的唯一标识
        :param secretKey: str, 信鸽网站分配的通信密钥
        """
        self.appId = appId
        self.secretKey = secretKey

    def push_account(self, platform: str, account: str, message: Message):
        if platform != "ios" and platform != "android":
            raise ValueError("Invalid platform")
        body = {
            "audience_type": "account",
            "account_list": [account],
            "platform": platform,
            "message": asdict(message),
        }
        if platform == "ios":
            body["message"]["ios"] = {
                "aps": {
                    "alert": {
                        "title": message.title,
                        "subtitle": message.subtitle,
                        "body": message.content,
                    }
                }
            }
        return Xinge3Helper.push(self.appId, self.secretKey, body)


class Xinge3Helper(object):
    URL = "https://openapi.xg.qq.com/v3/push/app"
    STR_RET_CODE = "ret_code"
    STR_ERR_MSG = "err_msg"
    STR_RESULT = "result"

    @classmethod
    def push(cls, app_id, secret_key, body):
        auth = HTTPBasicAuth(app_id, secret_key)
        headers = {"Content-Type": "application/json"}
        body = requests.post(cls.URL, auth=auth, json=body, headers=headers).json()
        return body["ret_code"], body["err_msg"]

