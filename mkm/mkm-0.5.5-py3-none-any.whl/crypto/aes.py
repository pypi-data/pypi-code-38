# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

import numpy
from Crypto.Cipher import AES

from .symmetric import SymmetricKey, symmetric_key_classes
from .utils import base64_encode, base64_decode


class AESKey(SymmetricKey):
    """ AES Key """

    def __init__(self, key: dict):
        super().__init__(key=key)
        # key data
        data = self.get('data')
        if data is None:
            # generate data and iv
            data = bytes(numpy.random.bytes(self.size))
            self['data'] = base64_encode(data)
            iv = bytes(numpy.random.bytes(AES.block_size))
            self['iv'] = base64_encode(iv)
        else:
            data = base64_decode(data)
        # initialization vector
        iv = self.get('iv')
        if iv is None:
            # iv = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
            iv = AES.block_size * chr(0).encode('utf-8')
            self['iv'] = base64_encode(iv)
        else:
            iv = base64_decode(iv)
        self.data = data
        self.iv = iv

    @property
    def size(self) -> int:
        size = self.get('size')
        if size is None:
            return 32
        else:
            return int(size)

    def encrypt(self, data: bytes) -> bytes:
        key = AES.new(self.data, AES.MODE_CBC, self.iv)
        size = key.block_size
        pad = (size - len(data) % size) * chr(0).encode('utf-8')
        return key.encrypt(data + pad)

    def decrypt(self, data: bytes) -> bytes:
        key = AES.new(self.data, AES.MODE_CBC, self.iv)
        plaintext = key.decrypt(data)
        pad = plaintext[-1:]  # chr(0).encode('utf-8')
        return plaintext.rstrip(pad)


"""
    Key Classes Maps
"""

# AES Key
symmetric_key_classes[SymmetricKey.AES] = AESKey        # default
symmetric_key_classes['AES/CBC/PKCS5Padding'] = AESKey
