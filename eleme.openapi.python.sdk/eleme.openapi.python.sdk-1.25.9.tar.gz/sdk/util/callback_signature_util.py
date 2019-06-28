# -*- coding: utf-8 -*-

import hashlib
from sdk.config import Config
import json


class CallbackValidationUtil:
    @staticmethod
    def is_valid_message(message):
        message = json.loads(message.decode("utf-8"))
        signature = message['signature']
        data = []
        for k, v in message.items():
            data.append(u"{}={}".format(k, v))
        sorted_msg = sorted(data)
        string = "".join(sorted_msg)
        string = u"{}{}".format(string, Config.get_secret())
        hash_value = hashlib.md5(string.encode("utf-8")).hexdigest().upper()
        return hash_value == signature
