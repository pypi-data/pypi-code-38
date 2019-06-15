# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
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

from abc import abstractmethod, ABC

from .crypto import PublicKey, PrivateKey
from .identifier import ID
from .entity import Entity, IEntityDataSource


class Account(Entity):
    """
        Account for communication
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        Account with ID and Public Key
    """

    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify data with signature, use meta.key

        :param data:
        :param signature:
        :return:
        """
        # 1. get key for signature from meta
        key = self.__meta_key()
        if key is not None:
            # 2. verify with meta.key
            return key.verify(data=data, signature=signature)

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data, try profile.key first, if not found, use meta.key

        :param data: message data
        :return: encrypted data
        """
        # 1. get key for encryption from profile
        key = self.__profile_key()
        if key is None:
            # 2. get key for encryption from meta instead
            # NOTICE: meta.key will never changed, so use profile.key to encrypt is the better way
            key = self.__meta_key()
        if key is not None:
            # 3. encrypt with profile.key
            return key.encrypt(data=data)

    def __meta_key(self) -> PublicKey:
        meta = self.meta
        if meta is not None:
            return meta.key
        raise AssertionError('failed to get meta.key for:' + self.identifier)

    def __profile_key(self) -> PublicKey:
        profile = self.profile
        if profile is not None:
            return profile.key


class User(Account):
    """
        User account
        ~~~~~~~~~~~~
    """

    @property
    def contacts(self) -> list:
        """
        Get all contacts of the user

        :return: contacts list
        """
        return self.delegate.contacts(identifier=self.identifier)

    def sign(self, data: bytes) -> bytes:
        """
        Sign data with user's private key

        :param data: message data
        :return: signature
        """
        key = self.delegate.private_key_for_signature(identifier=self.identifier)
        if key is not None:
            return key.sign(data=data)

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data with user's private key(s)

        :param data: encrypted data
        :return: plaintext
        """
        keys = self.delegate.private_keys_for_decryption(identifier=self.identifier)
        plaintext = None
        for key in keys:
            try:
                plaintext = key.decrypt(data=data)
            except ValueError:
                # If the dat length is incorrect
                continue
            if plaintext is not None:
                # decryption success
                break
        return plaintext


#
#  Delegate
#

class IUserDataSource(IEntityDataSource, ABC):
    """
        User Data Source
        ~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    def private_key_for_signature(self, identifier: ID) -> PrivateKey:
        """
        Get user's private key for signature

        :param identifier: user ID
        :return: private key
        """
        pass

    @abstractmethod
    def private_keys_for_decryption(self, identifier: ID) -> list:
        """
        Get user's private keys for decryption

        :param identifier: user ID
        :return: private keys
        """
        pass

    @abstractmethod
    def contacts(self, identifier: ID) -> list:
        """
        Get contacts list

        :param identifier: user ID
        :return: contacts list (ID)
        """
        pass
