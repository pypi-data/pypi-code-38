# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, division, print_function
import json, math
import logging, time
import threading

# import copy

from ws4py.client.threadedclient import WebSocketBaseClient
from ws4py.messaging import *
import sys

if sys.version_info[0] == 3:
    import queue
else:
    import Queue

MODEL_ASR_POWER = "model_asr_power"
MODEL_ASR_NUMBER = "model_asr_number"

"""
    ASR结束时会异常，请捕获！！
"""


class ASRException(Exception):
    pass


class ASRCloseException(Exception):
    pass


# 建议不使用该类！！！
class ASRBaseClient(WebSocketBaseClient):
    def __init__(self, url, app_id, token, model_type, sample_rate, file_name=None, long_data=None, client_id="",
                 protocols=['http-only', 'chat'], extensions=None, heartbeat_freq=None,
                 ssl_options=None, headers=None, exclude_headers=None, func=None, delay=800):
        """

        :param url:         WS地址
        :param app_id:      APP应用标志
        :param token:       APP授权Token
        :param model_type:  算法模型类型
        :param sample_rate: 采样率
        :param file_name    验证音频文件，优先级低于下述
        :param long_data:   验证音频数据
        :param client_id:
        :param protocols:
        :param extensions:
        :param heartbeat_freq:
        :param ssl_options:
        :param headers:
        :param exclude_headers:
        :param func:            接收服务器文本辅助回调函数（内部使用)
        """
        WebSocketBaseClient.__init__(self, url, protocols, extensions, heartbeat_freq,
                                     ssl_options, headers=headers, exclude_headers=exclude_headers)
        self._th = threading.Thread(target=self.run, name='WebSocketClientDIY')
        self._th.daemon = True

        if sys.version_info[0] == 3:
            self._buffer = queue.Queue()
        else:
            self._buffer = Queue.Queue()
        self._is_closed = False

        self.app_id = app_id
        self.token = token
        self.client_id = client_id
        self.model_type = model_type
        self.sample_rate = sample_rate

        # 800 ms
        if delay <= 0:
            self.delay = 0
        else:
            self.delay = delay / 1000.0
        if self.sample_rate == 8000:
            self.send_one = 16000
        elif self.sample_rate == 16000:
            self.send_one = 32000
        else:
            raise ASRException("parm sample_rate must 8000 or 16000")
        self._is_done = False
        self.long_data = long_data

        self.save = None
        self.func = func
        self.file_name = file_name
        self._is_open = False

    # 不需要了
    # def __del__(self):
    #     if self._is_closed is False:
    #         self.close()

    @property
    def daemon(self):
        return self._th.daemon

    @daemon.setter
    def daemon(self, flag):
        self._th.daemon = flag

    def run_forever(self):
        while not self.terminated:
            self._th.join(timeout=0.1)

    def handshake_ok(self):
        self._th.start()

    def closed(self, code, reason=None):
        logging.debug("websocket close:%r" % reason)
        self._is_closed = True

    def opened(self):
        self._is_closed = False
        d = {
            "appid": self.app_id,
            "access_token": self.token,
            "clientid": self.client_id,
            "sample_rate": self.sample_rate,
            "model_type": self.model_type

        }

        o = json.dumps(d)
        logging.debug("websocket client open")
        logging.debug("auth: %s" % o)
        self.send(o)
        self._is_open = True

        th1 = threading.Thread(target=ASRBaseClient.handle, args=(self,))
        th1.start()
        # th1.join()

    # 不要直接用
    def handle(self):
        while True:
            if self._is_open is True:
                # 二进制优先
                if self.long_data is not None:
                    temp = self.long_data
                    len_wav_data = len(temp)
                    if len(temp) > self.send_one:
                        times = int(math.ceil(len_wav_data / float(self.send_one)))
                        for i in range(0, times):
                            start = i * self.send_one
                            end = (i + 1) * self.send_one
                            # last
                            if i == times - 1:
                                raw = temp[start:len_wav_data + 1]
                            else:
                                raw = temp[start:end]
                            self.send(self._wrap_head(raw), True)
                            if self.delay > 0:
                                time.sleep(self.delay)
                    else:
                        self.send(self._wrap_head(self.long_data), True)

                    self.send(self._wrap_head(None, True), True)
                elif self.file_name is not None:
                    fd = open(self.file_name, "rb")
                    size = self.send_one
                    times = 1
                    while True:
                        raw = fd.read(size)
                        if len(raw) == 0:
                            self.send(self._wrap_head(None, True), True)
                            break
                        fd.seek(times * size)
                        times = times + 1
                        try:
                            self.send(self._wrap_head(raw), True)
                        except:
                            raise ASRCloseException("server sudden close the connection")
                        # logging.debug("sleep :%f" % self.delay)
                        if self.delay > 0:
                            time.sleep(self.delay)
                return

    def _wrap_head(self, data, final=False):
        if data is not None:
            raw = bytearray(data)
            length = len(raw)
        else:
            length = 0
        header = bytearray(32)
        header[0:4] = b'CRPV'
        header[4] = 1
        header[5] = 0
        header[6] = 0
        header[7] = 0
        header[8] = 1
        header[9] = 0
        header[10] = 1
        if final is True:
            header[11] = 1
            header[24] = 1
        else:
            header[11] = 0
            header[24] = 0

        byte_rate = length + 16
        header[12] = byte_rate & 0xff
        header[13] = (byte_rate >> 8) & 0xff
        header[14] = (byte_rate >> 16) & 0xff
        header[15] = (byte_rate >> 24) & 0xff
        header[16:20] = b'CRPV'
        header[20] = 16
        header[21] = 0
        header[22] = 0
        header[23] = 0
        header[25] = 0
        header[26] = 0
        header[27] = 0
        header[28] = 0
        header[29] = 0
        header[30] = 0
        header[31] = 0

        if data is not None:
            header.extend(data)
        logging.debug("header go: %r" % header)
        return header

    def _reverse(self, hex_raw):
        raw_len = len(hex_raw)
        if raw_len <= 43:
            return None

        re = list()
        i = 0

        # for ii in range(0, raw_len):
        #     print("%d： %#x：%s" % (ii, hex_raw[ii], chr(hex_raw[ii])))
        # exit(1)
        # print("================")
        while True:
            if i >= raw_len:
                break
            if hex_raw[i:i + 4] == b'CRPV':
                star = i
                u8a_number = bytearray(hex_raw[star + 22:star + 26])
                numb = ((u8a_number[0] & 0xFF) | ((u8a_number[1] & 0xFF) << 8) | ((u8a_number[2] & 0xFF) << 16) | (
                        (u8a_number[3] & 0xFF) << 24))
                end = star + 43 + numb
                dest = bytearray(hex_raw[star: end])
                re.append(dest)
                i = end - 1
            i = i + 1

        for i in re:
            u8a_offset = bytearray(i[18:22])

            offset = ((u8a_offset[0] & 0xFF) |
                      ((u8a_offset[1] & 0xFF) << 8) |
                      ((u8a_offset[2] & 0xFF) << 16) |
                      ((u8a_offset[3] & 0xFF) << 24))

            u8a_number = bytearray(i[22:26])
            numb = ((u8a_number[0] & 0xFF) |
                    ((u8a_number[1] & 0xFF) << 8) |
                    ((u8a_number[2] & 0xFF) << 16) |
                    ((u8a_number[3] & 0xFF) << 24))

            isfinal = i[26]

            # 关闭他！！
            if isfinal == 1:
                self._is_done = True
                self.close()

            # print("offset: %d number: %d isfinal: %d" % (offset, numb, isfinal))
            logging.debug("offset: %d number: %d isfinal: %d" % (offset, numb, isfinal))

            sss = bytearray(i[43:])

            if numb > 0:
                if self.save is not None and offset > 0 and offset < len(self.save):
                    self.save[offset:offset + len(sss) + 1] = sss
                else:
                    self.save = bytearray(sss)

        if self.save is not None:
            data = self.save
            return data.decode("utf-8", "ignore")

    def received_message(self, m):
        text = None
        if isinstance(m, BinaryMessage):
            hex_raw = bytearray(m.data)
            logging.debug("receive binary: %r" % hex_raw)

            text = self._reverse(hex_raw)
        elif isinstance(m, TextMessage):
            logging.debug("receive text: %r" % m.data)
            try:
                text = json.loads(str(m))
            except Exception as e:
                raise ASRException(repr(e))

        else:
            return
            # print(m)

        if text is not None:
            logging.debug("put buffer %s" % text)
            self._buffer.put(text)

        if self.save is not None and len(self.save) > 0:
            if self.func is not None:
                self.func(self.save)

                # if len(self.save) > 100:
                #     self.save = bytearray()
                return

    ################## 以下为可用方法，以上方法不要用！！ #################

    # 获取数据
    def get_real_time_txt(self):
        if self._buffer.empty() is False:
            result = self._buffer.get_nowait()

            # logging.debug(result)

            # python2/python3
            if type(result) == type(""):
                return True, result

            # {"flag":true,"error":null,"data":{"type":0}}
            # {"flag":false,"error":{"errorid":"10000","errormsg":"内部错误(算法模型不存在)"},"data":null}
            if result is not None and "error" in result and result["error"] is not None:
                # if self._is_closed is False:
                # self.close()
                raise Exception("%s-%s" % (result["error"]["errormsg"], result["error"]["errorid"]))
            return True, None

        if self._is_closed:
            if self._buffer.empty() is False:
                return False, None
            else:
                raise ASRCloseException("websocket client close")
        return False, None

    # 获取最终结果
    def get_final_txt(self):
        if self.save is not None:
            return self.save.decode("utf-8", "ignore")
        return ASRException("result empty, check the model and rate")

    # 自定发送二进制： 请不要用！！
    def diy_send_binary(self, data):
        if self._is_closed:
            raise ASRCloseException("websocket client close")
        if self.long_data is not None or self.file_name is not None:
            raise ASRException("don't do this action diy_send_binary")
        self.send(self._wrap_head(data), True)

    # 自定发送二进制结束： 请不要用！！
    def diy_send_binary_end(self):
        if self.long_data is not None or self.file_name is not None:
            raise ASRException("don't do this action diy_send_binary_end")
        self.send(self._wrap_head(None, True), True)
