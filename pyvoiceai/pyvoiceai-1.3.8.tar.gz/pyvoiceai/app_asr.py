# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
from .app_auth_api import *
from .app_asr_base_api import *

MODEL_ASR_POWER = "model_asr_power"
MODEL_ASR_NUMBER = "model_asr_number"


class ASRClient:
    def __init__(self, app_id, app_secret, host="wss://127.0.0.1:8072", call_back=None):
        self.socket_host = host
        if self.socket_host.endswith("/"):
            self.socket_host = self.socket_host + "api/app/asr/streaming"
        else:
            self.socket_host = self.socket_host + "/api/app/asr/streaming"
        url = ""
        if "wss://" in host:
            url = host.replace("wss://", "https://")
        elif "ws://" in host:
            url = host.replace("ws://", "http://")
        else:
            raise ASRException("host must prefix wss:// or ws://")
        self.auth = AppAuthAPI(app_id=app_id, base_url=url)
        ok, err, data = self.auth.app_auth_get(app_secret)
        if ok is False:
            raise ASRException(data)
        ok1, err, data1 = self.auth.app_auth_token_get()
        if ok1 is False:
            raise ASRException(data1)
        self.auth.app_auth_token_refresh()
        self.token = self.auth.get_access_token()
        self.app_id = app_id
        self.call_back = call_back

    def asr(self, sample_rate, model_type, file_name, delay=800):
        self.auth.app_auth_token_refresh()
        ws = ASRBaseClient(url=self.socket_host, app_id=self.app_id, token=self.token, sample_rate=sample_rate,
                           model_type=model_type, file_name=file_name, delay=delay)
        ws.daemon = True
        try:
            ws.connect()
            logging.debug("wait, please...may be long long.")
            while True:
                ok, result = ws.get_real_time_txt()
                if ok and result is not None:
                    if self.call_back is not None:
                        self.call_back(result)
                        # logging.debug("asr2:%s" % result)
        except ASRCloseException as e:
            # 获取最终结果
            logging.debug("asr err inner %r" % e)
            result = ws.get_final_txt()
            return result

        return ""
