# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class HexAES(object):

    def __init__(self, key, mode=None):
        """ AES 加密

        @param
            key : byte string
            The secret key to use in the symmetric cipher.
            It must be 16 (*AES-128*), 24 (*AES-192*), or 32 (*AES-256*) bytes long.

            mode : a *MODE_** constant
            The chaining mode to use for encryption or decryption.
            Default is `MODE_ECB`.

        @return: an `AESCipher` object
        """
        if key and len(key) != 16:
            raise ValueError(
                '这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用')

        self.key = key
        self.mode = mode or AES.MODE_ECB

    def encrypt(self, text):
        """ 加密函数

        @param 
            text: text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数.

        @return: 统一把加密后的字符串转化为16进制字符串返回.
        """
        cryptor = AES.new(self.key, self.mode)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        ciphertext = cryptor.encrypt(text)

        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext)

    def decrypt(self, text):
        """解密函数

        @param text: 16进制字符串.

        @return: 解密后的字符串.
        """
        ryptor = AES.new(self.key, self.mode)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')
