# -*-coding:utf-8-*-
import time
from . import Md5
from . import Rsa
import os

SIGN_TYPE_MD5 = 'MD5'
SIGN_TYPE_RSA = 'RSA'


class Identify:
    def __init__(self, sign_type=SIGN_TYPE_MD5, key='', public_key='', private_key=''):
        self.sign_type = sign_type
        self.key = key
        self.public_key = public_key
        self.private_key = private_key
        if sign_type != SIGN_TYPE_MD5 and sign_type != SIGN_TYPE_RSA:
            print('sign_type invalid')
            exit(0)
        if sign_type == SIGN_TYPE_RSA:
            if public_key == '' or private_key == '':
                print('public_key and private_key not empty')
                exit(0)
            if os.path.exists(public_key) is False:
                print('public_key file not exists')
                exit(0)
            if os.path.exists(private_key) is False:
                print('private_key file not exists')
                exit(0)

    # 过滤一些不需要参与签名的数据
    def paraFilter(self, para_temp):
        para_filter = {}

        for key in para_temp:
            if key == "sign" or key == "sign_type" or para_temp[key] == "":
                continue
            else:
                para_filter[key] = para_temp[key]
        return para_filter

    # 参数排序并组合
    def argSort(self, para_filter):
        res = ''
        keys = para_filter.keys()
        keys = sorted(keys)
        for i in range(0, len(keys)):
            res += str(str(keys[i]) + '=' + str(para_filter[keys[i]]) + '&')

        return res[:-1]

    # 生成签名
    def buildRequestMysign(self, para_temp):
        para_filter = self.paraFilter(para_temp)
        prestr = self.argSort(para_filter)
        prestr = str(prestr + "&" + self.key)
        if self.sign_type == SIGN_TYPE_MD5:
            md5Verify = Md5.Verify()
            mysign = md5Verify.md5Sign(prestr)
        else:
            rsaVerify = Rsa.Verify(self.public_key, self.private_key)
            mysign = rsaVerify.publicSign(prestr)

        return mysign

    # 签名验证
    def getSignVeryfy(self, para_temp, sign):
        para_filter = self.paraFilter(para_temp)
        prestr = self.argSort(para_filter)
        prestr = prestr + "&" + self.key
        # if sign_type == 'MD5':
        sign_result = False
        if self.sign_type == SIGN_TYPE_MD5:
            md5Verify = Md5.Verify()
            sign_result = md5Verify.md5Verify(prestr, sign)
        else:
            prestr = str(prestr)
            rsaVerify = Rsa.Verify(self.public_key, self.private_key)
            sign_result = rsaVerify.privateRsaVerify(prestr, sign)

        return sign_result
