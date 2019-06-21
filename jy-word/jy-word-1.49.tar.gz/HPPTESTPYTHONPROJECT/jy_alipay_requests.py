# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/2/13 0013
__author__ = 'huohuo'

import json
import time
import requests
from jy_word.web_tool import format_time
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import decodestring, encodestring
from urllib import quote_plus

ALIPAY_APPID = '2016092300580658'
ALIPAY_APPID = '2019012963189101'
ALIPAY_URL = 'https://openapi.alipay.com/gateway.do'
app_private_key = ''''''
sign = 'fwx6t6UZl2Th5Q1c+rkdatplNkJ68LnIf1Ipv9MgAQHRutLTLoz/mYBQOotBYy5fAC94A1RPGvV2QJHD15VKVhDcOnIm0xjF7HiR7evlDzH/Rg9xUSSYhTq/u9lnibWn2gdXqwmhsiJ6F9j4FNmRE9LseOowLqAlJTHzKRVjC7Tp31hetEO3uKpl0YCBXHYyzcU0Ac8oaoKbkjFnvSxPKdsWcsxj7gYMszxOiUZDzgInxns9ke5MnWRFLC1v3Hs96/+POCT2vMbOtdhPTCYUz6Hvsy73IZp5FbcluzxCiEiYT8UnYXKSrqQMnobhXBAOZ0MMw/gENGL/XqwKygHzvw=='


def init_sign(timestamp):
    method = 'alipay.user.info.auth'
    method = 'alipay.mobile.public.menu.add'
    params = 'app_id=%s&biz_content={"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}&charset=GBK&method=%s&sign_type=RSA2&timestamp=%s&version=1.0'% (ALIPAY_APPID, method, timestamp)
    biz_content = {"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}

    url1 = '%s?app_id=%s&biz_content=%s&charset=GBK&method=alipay.mobile.public.menu.add&sign_type=RSA2&timestamp=%s&version=1.0' % (ALIPAY_URL, ALIPAY_APPID, biz_content, timestamp)
    url1 = '%s?%s' % (ALIPAY_URL, params)
    print url1

    response = requests.request('post', url1)
    print response.status_code
    if response.status_code == 200:
        print response.text
    else:
        print response.text


def init_sign1(timestamp):
    method = 'alipay.mobile.public.menu.add'
    charset = 'utf-8'
    params = 'app_id=%s&biz_content={"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}&charset=%s&method=%s&timestamp=%s&version=1.0'% (ALIPAY_APPID, charset, method, timestamp)
    url1 = '%s?%s' % (ALIPAY_URL, params)
    print url1
    response = requests.request('post', url1)
    print response.status_code
    if response.status_code == 200:
        print response.json()
    else:
        print response.text


if __name__ == '__main__':
    out_trade_no = int(time.time())
    timestamp = format_time(out_trade_no)
    total_amount = 0.01
    init_sign1(timestamp)
