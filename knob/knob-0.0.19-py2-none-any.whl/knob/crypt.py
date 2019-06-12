# -*- coding:utf-8 -*-

import six
from Crypto.Cipher import AES
import base64


__all__ = ['encrypt', 'decrypt']


def _pad_key(key):
    if len(key) > 32:
        return key[:32]
    elif len(key) > 24:
        return key.ljust(32)
    elif len(key) > 16:
        return key.ljust(24)
    else:
        return key.ljust(16)


def encrypt(msg, key=None):
    if not key:
        return msg.encode('utf-8')
    else:
        key = _pad_key(key)

    msg = (msg + '$').encode('utf-8')
    padded_msg = msg.ljust((len(msg) // 16 + 1) * 16)
    cipher = AES.new(key, AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(padded_msg))
    return encoded


def decrypt(encoded, key=None):
    if not key:
        return encoded.decode('utf-8')
    else:
        key = _pad_key(key)

    cipher = AES.new(key, AES.MODE_ECB)
    decoded = base64.b64decode(encoded)
    padded_msg = cipher.decrypt(decoded)
    msg = padded_msg.rstrip()
    msg = msg.decode('utf-8')
    msg = msg[:-1]
    return msg


