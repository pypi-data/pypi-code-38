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

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5

from .asymmetric import PublicKey, PrivateKey, public_key_classes, private_key_classes


class RSAPublicKey(PublicKey):
    """ RSA Public Key """

    def __init__(self, key: dict):
        super().__init__(key=key)
        # data in 'PEM' format
        data = key['data']
        self.key = RSA.importKey(data)
        self.data = self.key.exportKey(format='DER')

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

    def __init__(self, key: dict):
        super().__init__(key=key)
        # data in 'PEM' format
        data = key.get('data')
        if data is None:
            # generate private key data
            private_key = RSA.generate(self.size)
            data = private_key.exportKey()
            self['data'] = data.decode('utf-8')
        # create key
        self.key = RSA.importKey(data)

    @property
    def size(self):
        bits = self.get('keySizeInBits')
        if bits is None:
            return 1024
        else:
            return int(bits)

    @property
    def public_key(self) -> PublicKey:
        pk = self.key.publickey()
        data = pk.exportKey()
        info = {
            'algorithm': PublicKey.RSA,
            'data': data.decode('utf-8'),
        }
        return RSAPublicKey(info)

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


"""
    Key Classes Maps
"""

# RSA Public Key
public_key_classes[PublicKey.RSA] = RSAPublicKey             # default
public_key_classes['SHA256withRSA'] = RSAPublicKey
public_key_classes['RSA/ECB/PKCS1Padding'] = RSAPublicKey

# RSA Private Key
private_key_classes[PrivateKey.RSA] = RSAPrivateKey          # default
private_key_classes['SHA256withRSA'] = RSAPrivateKey
private_key_classes['RSA/ECB/PKCS1Padding'] = RSAPrivateKey
