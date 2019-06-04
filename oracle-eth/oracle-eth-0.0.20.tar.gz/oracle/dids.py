#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 处理和did相关的数据
#

"""


from pycontractsdk import keys
import json


class Did(object):
    def __init__(self):
        pass

    @staticmethod
    def sign_did(did_json_str, first_sign_str, private_key):
        """
        对（did数据+'\n'+第一次签名的数据）进行签名
        :param did_json_str: did的json string
        :param first_sign_str: 第一次签名的数据 （学文提供，从区块链中获得）
        :param private_key: 签名用的私钥, 带有 0x 前缀
        :return: 签名后的结果 hex
        """
        sign_msg = keys.ecdsa_sign('{did_json}\n{first_sign_str}'.format(did_json=did_json_str, first_sign_str=first_sign_str),
                                   private_key_hex=private_key)
        return sign_msg

    @staticmethod
    def verify_did(did_json_str, first_sign_str):
        """
        验证第一次签名真是否正确
        :param did_json: did的json  string
        :param first_sign_str: 第一次签名的字符串 hex
        :return: 正确返回True, 错误返回False
        """
        if not isinstance(did_json_str, str):
            raise ValueError('did_json must be string')
        did_json_obj = json.loads(did_json_str)
        public_key = did_json_obj['publicKey'][0]['publicKeyHex']
        tf = keys.ecdsa_verify(did_json_str, first_sign_str, public_key)
        if tf:
            return True
        else:
            return False

    @staticmethod
    def verify_did_and_firstsign(did_json_str, first_sign_str):
        """
        验证第一次签名真是否正确
        :param did_json: did的json  string
        :param first_sign_str: 第一次签名的字符串 hex
        :return: 正确返回True, 错误返回False
        """
        if not isinstance(did_json_str, str):
            raise ValueError('did_json must be string')
        did_json_obj = json.loads(did_json_str)
        public_key = did_json_obj['publicKey'][0]['publicKeyHex']
        tf = keys.ecdsa_verify(did_json_str, first_sign_str, public_key)
        if tf:
            return True
        else:
            return False

    @staticmethod
    def get_ciphertext(did_json):
        """
        得到did中的加密串
        :param did_json:
        :return:
        """
        id = did_json['id']
        key = id.split('#')[1]
        proof = did_json['proof']
        return ''.join(['0x', proof.lstrip('0x')])
