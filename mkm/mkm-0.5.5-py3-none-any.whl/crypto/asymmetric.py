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

from abc import ABCMeta, abstractmethod

from .cryptography import CryptographyKey, algorithm


class AsymmetricKey(CryptographyKey, metaclass=ABCMeta):

    RSA = 'RSA'
    ECC = 'ECC'


class PublicKey(AsymmetricKey, metaclass=ABCMeta):
    """
        This class is used to en/decrypt symmetric key or sign/verify signature with message data
    """

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='RSA'
        :return: public key
        """
        if key is None:
            return None
        elif cls is not PublicKey:
            # subclass
            return super().__new__(cls, key)
        elif isinstance(key, PublicKey):
            # return PublicKey object directly
            return key
        # get class by algorithm name
        clazz = public_key_classes[algorithm(key)]
        if issubclass(clazz, PublicKey):
            return clazz(key)
        else:
            raise ModuleNotFoundError('Invalid algorithm: %s' % key)

    def match(self, private_key) -> bool:
        if not isinstance(private_key, PrivateKey):
            return False
        # 1. if the SK has the same public key, return true
        public_key = private_key.public_key
        if public_key is not None and public_key.__eq__(self):
            return True
        # 2. try to verify the SK's signature
        promise = 'Moky loves May Lee forever!'.encode('utf-8')
        signature = private_key.sign(promise)
        return self.verify(promise, signature)

    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        """
        ciphertext = encrypt(plaintext, PK)

        :param data: plaintext
        :return:     ciphertext
        """
        pass

    @abstractmethod
    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        OK = verify(data, signature, PK)

        :param data:      message data
        :param signature: signature of message data
        :return:          True on signature matched
        """
        pass


class PrivateKey(AsymmetricKey, metaclass=ABCMeta):
    """
        This class is used to decrypt symmetric key or sign message data
    """

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='RSA'
        :return: private key
        """
        if key is None:
            return None
        elif cls is not PrivateKey:
            # subclass
            return super().__new__(cls, key)
        elif isinstance(key, PrivateKey):
            # return PrivateKey object directly
            return key
        # get class by algorithm name
        clazz = private_key_classes[algorithm(key)]
        if issubclass(clazz, PrivateKey):
            return clazz(key)
        else:
            raise ModuleNotFoundError('Invalid algorithm: %s' % key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, PrivateKey):
            return False
        if super().__eq__(other):
            return True
        pk = self.public_key
        if pk is not None:
            return pk.match(other)

    @property
    def public_key(self) -> PublicKey:
        """
        Get public key from private key

        :return: public key paired to this private key
        """
        yield None

    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        """
        plaintext = decrypt(ciphertext, SK);

        :param data: ciphertext
        :return:     plaintext
        """
        pass

    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        """
        signature = sign(data, SK);

        :param data: message data
        :return:     signature
        """
        pass


public_key_classes = {
}

private_key_classes = {
}
