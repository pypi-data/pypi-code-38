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

"""
    Extends Crypto Keys
    ~~~~~~~~~~~~~~~~~~~

    AESKey        -> SymmetricKey
    RSAPublicKey  -> PublicKey
    RSAPrivateKey -> PrivateKey
"""

import numpy
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

from .utils import base64_encode, base64_decode
from .crypto import SymmetricKey, symmetric_key_classes
from .crypto import PublicKey, public_key_classes
from .crypto import PrivateKey, private_key_classes


class AESKey(SymmetricKey):
    """ AES Key """

    def __new__(cls, key: dict):
        # data
        data = base64_decode(key['data'])
        # iv
        iv = key.get('iv')
        if iv is None:
            # iv = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
            iv = AES.block_size * chr(0).encode('utf-8')
            key['iv'] = base64_encode(iv)
        else:
            iv = base64_decode(iv)
        # create key
        self = super().__new__(cls, key)
        self.data = data
        self.iv = iv
        return self

    @classmethod
    def generate(cls, key: dict) -> SymmetricKey:
        # key size
        size = key.get('size')
        if size is None:
            size = 32
        else:
            size = int(size)
        # key data
        data = bytes(numpy.random.bytes(size))
        key['data'] = base64_encode(data)
        # initialization vector
        iv = bytes(numpy.random.bytes(AES.block_size))
        key['iv'] = base64_encode(iv)
        return AESKey(key)

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


class RSAPublicKey(PublicKey):
    """ RSA Public Key """

    def __new__(cls, key: dict):
        # data in 'PEM' format
        data = key['data']
        # create key
        self = super().__new__(cls, key)
        self.key = RSA.importKey(data)
        return self

    @property
    def data(self) -> bytes:
        return self.key.exportKey(format='DER')

    def encrypt(self, data: bytes) -> bytes:
        cipher = Cipher_PKCS1_v1_5.new(self.key)
        return cipher.encrypt(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        hash_obj = SHA256.new(data)
        verifier = Signature_PKCS1_v1_5.new(self.key)
        try:
            return verifier.verify(hash_obj, signature)
        except ValueError:
            # raise ValueError("Invalid signature")
            return False


class RSAPrivateKey(PrivateKey):
    """ RSA Private Key """

    def __new__(cls, key: dict):
        # data in 'PEM' format
        data = key['data']
        # create key
        self = super().__new__(cls, key)
        self.key = RSA.importKey(data)
        return self

    @classmethod
    def generate(cls, key: dict) -> PrivateKey:
        # key size
        bits = key.get('keySizeInBits')
        if bits is None:
            bits = 1024
        else:
            bits = int(bits)
        # generate with key size
        private_key = RSA.generate(bits)
        data = private_key.exportKey()
        key['data'] = data.decode('utf-8')
        return RSAPrivateKey(key)

    def decrypt(self, data: bytes) -> bytes:
        cipher = Cipher_PKCS1_v1_5.new(self.key)
        sentinel = ''
        plaintext = cipher.decrypt(data, sentinel)
        if sentinel:
            print('error: ' + sentinel)
        return plaintext

    def sign(self, data: bytes) -> bytes:
        hash_obj = SHA256.new(data)
        signer = Signature_PKCS1_v1_5.new(self.key)
        return signer.sign(hash_obj)

    @property
    def publicKey(self) -> PublicKey:
        pk = self.key.publickey()
        data = pk.exportKey()
        info = {
            'algorithm': 'RSA',
            'data': data.decode('utf-8'),
        }
        return RSAPublicKey(info)


"""
    Key Classes Maps
"""

# AES
symmetric_key_classes['AES'] = AESKey       # default
symmetric_key_classes['AES/CBC/PKCS5Padding'] = AESKey

# RSA
public_key_classes['RSA'] = RSAPublicKey    # default
private_key_classes['RSA'] = RSAPrivateKey  # default
public_key_classes['SHA256withRSA'] = RSAPublicKey
private_key_classes['SHA256withRSA'] = RSAPrivateKey
public_key_classes['RSA/ECB/PKCS1Padding'] = RSAPublicKey
private_key_classes['RSA/ECB/PKCS1Padding'] = RSAPrivateKey
