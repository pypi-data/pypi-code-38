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


class SymmetricKey(CryptographyKey, metaclass=ABCMeta):
    """
        This class is used to encrypt or decrypt message data
    """

    AES = 'AES'
    DES = 'DES'

    def __new__(cls, key: dict):
        """

        :param key: key info with algorithm='AES'
        :return: symmetric key
        """
        if key is None:
            return None
        elif cls is not SymmetricKey:
            # subclass
            return super().__new__(cls, key)
        elif isinstance(key, SymmetricKey):
            # return SymmetricKey object directly
            return key
        # get class by algorithm name
        clazz = symmetric_key_classes[algorithm(key)]
        if issubclass(clazz, SymmetricKey):
            return clazz(key)
        else:
            raise ModuleNotFoundError('Invalid algorithm: %s' % key)

    def __init__(self, key: dict):
        super().__init__(key=key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, SymmetricKey):
            return False
        if super().__eq__(other):
            return True
        promise = 'Moky loves May Lee forever!'.encode('utf-8')
        return self.decrypt(other.encrypt(promise)) == promise

    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        """
        ciphertext = encrypt(plaintext, PW)

        :param data: plaintext
        :return:     ciphertext
        """
        pass

    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        """
        plaintext = decrypt(ciphertext, PW);

        :param data: ciphertext
        :return:     plaintext
        """
        pass


"""
    Key Classes Map
"""

symmetric_key_classes = {
}
