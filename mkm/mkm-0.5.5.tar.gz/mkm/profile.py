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

import json

from .crypto.utils import base64_decode, base64_encode
from .crypto import PublicKey, PrivateKey
from .identifier import ID


class TAO(dict):
    """
        The Additional Object
        ~~~~~~~~~~~~~~~~~~~~~

        'Meta' is the information for entity which never changed, which contains the key for verify signature;
        'TAO' is the variable part, which contains the key for asymmetric encryption.
    """

    def __new__(cls, profile: dict):
        if profile is None:
            return None
        elif isinstance(profile, TAO):
            # return Meta object directly
            return profile
        # new Profile(dict)
        return super().__new__(cls, profile)

    def __init__(self, profile: dict):
        super().__init__(profile)
        # entity ID
        identifier = profile['ID']
        self.__identifier = ID(identifier)
        # properties data
        data = profile.get('data')
        self.__data = data
        # properties signature
        signature = profile.get('signature')
        if signature is None:
            self.__signature = None
        else:
            self.__signature = base64_decode(signature)
        # properties
        self.__properties = {}
        # valid flag
        self.__valid = False
        # public key
        self.__key = None

    @property
    def identifier(self) -> ID:
        return self.__identifier

    @property
    def valid(self) -> bool:
        return self.__valid

    """
        Public Key for encryption
        ~~~~~~~~~~~~~~~~~~~~~~~~~
        For safety considerations, the profile.key which used to encrypt message data should be different with meta.key
    """

    @property
    def key(self) -> PublicKey:
        if self.__valid:
            return self.__key

    @key.setter
    def key(self, value: PublicKey):
        self.__key = value
        self.set_property('key', value)

    """
        Profile Properties
        ~~~~~~~~~~~~~~~~~~
        Inner dictionary
    """

    def get_property(self, key):
        if self.__valid:
            return self.__properties.get(key)

    def set_property(self, key, value):
        if value is None:
            self.__properties.pop(key, None)
        else:
            self.__properties[key] = value
        self.__reset()

    def __reset(self):
        """ Reset data signature after properties changed """
        self.pop('data', None)
        self.pop('signature', None)
        self.__data = None
        self.__signature = None
        self.__valid = False
        self.__key = None

    """
        Sign/Verify profile data
        ~~~~~~~~~~~~~~~~~~~~~~~~
    """

    def verify(self, public_key: PublicKey) -> bool:
        """
        Verify 'data' and 'signature', if OK, refresh properties from 'data'

        :param public_key: public key in meta.key
        :return: True on signature matched
        """
        if self.__valid:
            # already verify
            return True
        if self.__data is None or self.__signature is None:
            # data error
            return False
        if public_key.verify(self.__data.encode('utf-8'), self.__signature):
            # signature matched
            self.__valid = True
            # refresh properties
            self.__properties = json.loads(self.__data)
            # get public key
            self.__key = PublicKey(self.__properties.get('key'))
        return self.__valid

    def sign(self, private_key: PrivateKey) -> bytes:
        """
        Encode properties to 'data' and sign it to 'signature'

        :param private_key: private key match meta.key
        :return: signature
        """
        if self.__valid:
            # already signed
            return self.__signature
        data = json.dumps(self.__properties)
        signature = private_key.sign(data.encode('utf-8'))
        self['data'] = data
        self['signature'] = base64_encode(signature)
        self.__data = data
        self.__signature = signature
        self.__valid = True
        return signature


class Profile(TAO):

    @property
    def name(self) -> str:
        return self.get_property(key='name')

    @name.setter
    def name(self, value: str):
        self.set_property(key='name', value=value)

    @classmethod
    def new(cls, identifier: ID):
        """ Create new empty profile object with entity ID """
        profile = {
            'ID': identifier,
        }
        return cls(profile)
