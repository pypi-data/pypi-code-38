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
    Crypto
    ~~~~~~

    Crypto Keys: SymmetricKey, PrivateKey, PublicKey
"""


class SymmetricKey(dict):
    """
        This class is used to encrypt or decrypt message data
    """

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='AES'
        :return: symmetric key
        """
        if cls is not SymmetricKey:
            # subclass
            if issubclass(cls, SymmetricKey):
                return super().__new__(cls, key)
            else:
                raise TypeError('Not subclass of SymmetricKey')
        elif isinstance(key, SymmetricKey):
            # return SymmetricKey object directly
            return key
        elif isinstance(key, dict):
            # get class by algorithm name
            algorithm = key['algorithm']
            clazz = symmetric_key_classes[algorithm]
            if issubclass(clazz, SymmetricKey):
                return clazz(key)
            else:
                raise ModuleNotFoundError('Invalid algorithm: ' + algorithm)
        else:
            raise AssertionError('Invalid symmetric key')

    def encrypt(self, data: bytes) -> bytes:
        pass

    def decrypt(self, data: bytes) -> bytes:
        pass

    @classmethod
    def generate(cls, key: dict):
        # get class by algorithm name
        algorithm = key['algorithm']
        clazz = symmetric_key_classes[algorithm]
        if issubclass(clazz, SymmetricKey):
            return clazz.generate(key)
        else:
            raise ModuleNotFoundError('Invalid algorithm: ' + algorithm)

    def __eq__(self, other) -> bool:
        if not isinstance(other, SymmetricKey):
            return False
        if super().__eq__(other):
            return True
        promise = 'Moky loves May Lee forever!'.encode('utf-8')
        return self.decrypt(other.encrypt(promise)) == promise


class PublicKey(dict):
    """
        This class is used to encrypt symmetric key or verify signature with message data
    """

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='RSA'
        :return: public key
        """
        if cls is not PublicKey:
            # subclass
            if issubclass(cls, PublicKey):
                return super().__new__(cls, key)
            else:
                raise TypeError('Not subclass of PublicKey')
        elif isinstance(key, PublicKey):
            # return PublicKey object directly
            return key
        elif isinstance(key, dict):
            # get class by algorithm name
            algorithm = key['algorithm']
            clazz = public_key_classes[algorithm]
            if issubclass(clazz, PublicKey):
                return clazz(key)
            else:
                raise ModuleNotFoundError('Invalid algorithm: ' + algorithm)
        else:
            raise AssertionError('Invalid public key')

    def encrypt(self, data: bytes) -> bytes:
        pass

    def verify(self, data: bytes, signature: bytes) -> bool:
        pass

    def match(self, private_key) -> bool:
        if not isinstance(private_key, PrivateKey):
            return False
        # 1. if the SK has the same public key, return true
        public_key = private_key.publicKey
        if public_key is not None and public_key.__eq__(self):
            return True
        # 2. try to verify the SK's signature
        promise = 'Moky loves May Lee forever!'.encode('utf-8')
        signature = private_key.sign(promise)
        return self.verify(promise, signature)


class PrivateKey(dict):
    """
        This class is used to decrypt symmetric key or sign message data
    """

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='RSA'
        :return: private key
        """
        if cls is not PrivateKey:
            # subclass
            if issubclass(cls, PrivateKey):
                return super().__new__(cls, key)
            else:
                raise TypeError('Not subclass of PrivateKey')
        elif isinstance(key, PrivateKey):
            # return PrivateKey object directly
            return key
        elif isinstance(key, dict):
            # get class by algorithm name
            algorithm = key['algorithm']
            clazz = private_key_classes[algorithm]
            if issubclass(clazz, PrivateKey):
                return clazz(key)
            else:
                raise ModuleNotFoundError('Invalid algorithm: ' + algorithm)
        else:
            raise AssertionError('Invalid private key')

    def decrypt(self, data: bytes) -> bytes:
        pass

    def sign(self, data: bytes) -> bytes:
        pass

    @property
    def publicKey(self) -> PublicKey:
        yield None

    @classmethod
    def generate(cls, key: dict):
        # get algorithm name
        algorithm = key['algorithm']
        clazz = private_key_classes[algorithm]
        if issubclass(clazz, PrivateKey):
            return clazz.generate(key)
        else:
            raise ModuleNotFoundError('Invalid algorithm: ' + algorithm)

    def __eq__(self, other) -> bool:
        if not isinstance(other, PrivateKey):
            return False
        if super().__eq__(other):
            return True
        return self.publicKey.match(other)


"""
    Key Classes Maps
"""

symmetric_key_classes = {
}

public_key_classes = {
}

private_key_classes = {
}
