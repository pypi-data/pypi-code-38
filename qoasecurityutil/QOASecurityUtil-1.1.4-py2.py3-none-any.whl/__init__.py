# -*- coding:utf-8 -*-
import time
import binascii
from pyDes import des, CBC, PAD_PKCS5


def des_encrypt(content, password):
    return binascii.b2a_hex(
        des(password, CBC, password, pad=None, padmode=PAD_PKCS5)
        .encrypt(content, padmode=PAD_PKCS5)).upper()


def make_token(appcode, password):
    return 'token__' + des_encrypt('%s__%s' % (appcode, str(
            int(time.time() * 1000))), password)
