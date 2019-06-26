#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from urllib import request
from urllib.request import urlopen
from urllib import parse

class Giftcard:

    __x_token = None

    def __init__(self, config, token):
        self.url = config.get_request_url()
        self.__x_token = token

    def detail(self, code):
        """
        礼品卡查询接口
        :param code: 礼品卡卡号
        :return:
        """
        params = {
            'code': code,
        }
        data = parse.urlencode(params).encode("utf-8")
        return self.post('card/detail', data)

    def payment(self, code, amount):
        """
        礼品卡支付接口
        :param code: 礼品卡卡号
        :param amount: 消费金额 单位分
        :return:
        """
        params = {
            'code': code,
            'amount': amount
        }
        data = parse.urlencode(params).encode("utf-8")
        return self.post('card/payment', data)

    def post(self, api_suffix, data):
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                'X-TOKEN': self.__x_token
            }
            req_url = self.url + api_suffix
            req = request.Request(req_url, data, headers)
            res = urlopen(req)
            return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            raise Exception('sagabuy api response:{}'.format(e))