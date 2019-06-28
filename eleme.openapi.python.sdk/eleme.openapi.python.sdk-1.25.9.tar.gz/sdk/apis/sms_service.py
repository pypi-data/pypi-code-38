# -*- coding: utf-8 -*-


# 短信服务
class SmsService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def send_message(self, request):
        """
        发送短信
        :param request:短信发送请求
        """
        return self.__client.call("eleme.sms.sendMessage", {"request": request})

