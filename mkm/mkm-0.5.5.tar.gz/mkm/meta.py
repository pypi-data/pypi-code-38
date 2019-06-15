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

"""
    Account/Group Meta data
    ~~~~~~~~~~~~~~~~~~~~~~~

    data format: {
        version: 1,          // meta version
        seed: "moKy",        // user/group name
        key: "{public key}", // PK = secp256k1(SK);
        fingerprint: "..."   // CT = sign(seed, SK);
    }

    algorithm:
        fingerprint = sign(seed, SK);
"""

from abc import ABCMeta, abstractmethod

from .crypto.utils import base64_encode, base64_decode
from .crypto import PublicKey, PrivateKey

from .address import NetworkID, Address, BTCAddress
from .identifier import ID


class Meta(dict, metaclass=ABCMeta):
    """
        Meta for Identifier
        ~~~~~~~~~~~~~~~~~~~

        @enum MKMMetaVersion

        @abstract Defined for meta data structure to generate identifier.

        @discussion Generate & check ID/Address

            MKMMetaVersion_MKM give a seed string first, and sign this seed to get
            fingerprint; after that, use the fingerprint to generate address.
            This will get a firmly relationship between (username, address & key).

            MKMMetaVersion_BTC use the key data to generate address directly.
            This can build a BTC address for the entity ID without username.

            MKMMetaVersion_ExBTC use the key data to generate address directly, and
            sign the seed to get fingerprint (just for binding username & key).
            This can build an entity ID with username and BTC address.
    """
    Version_MKM = 0x01    # 0000 0001
    Version_BTC = 0x02    # 0000 0010
    Version_ExBTC = 0x03  # 0000 0011
    Version_ETH = 0x04    # 0000 0100
    Version_ExETH = 0x05  # 0000 0101
    DefaultVersion = Version_MKM

    def __new__(cls, meta: dict):
        """
        Create meta for entity

        :param meta: meta info
        :return: Meta object
        """
        if meta is None:
            return None
        elif cls is not Meta:
            # subclass
            return super().__new__(cls, meta)
        elif isinstance(meta, Meta):
            # return Meta object directly
            return meta
        # get class by meta version
        version = int(meta['version'])
        clazz = meta_classes.get(version)
        if issubclass(clazz, Meta):
            return clazz(meta)
        else:
            raise ModuleNotFoundError('Invalid meta version')

    def __init__(self, meta: dict):
        super().__init__(meta)
        # meta version
        version = int(meta['version'])
        self.__version = version
        # public key
        key = PublicKey(meta['key'])
        self.__key = key
        # seed & fingerprint
        if version & Meta.Version_MKM:  # MKM, ExBTC, ExETH, ...
            seed = meta['seed']
            fingerprint = base64_decode(meta['fingerprint'])
            if key.verify(seed.encode('utf-8'), fingerprint):
                self.__seed = seed
                self.__fingerprint = fingerprint
            else:
                raise ValueError('Meta key not match: %s' % meta)
        else:
            self.__seed = None
            self.__fingerprint = None

    def __eq__(self, other) -> bool:
        """ Check whether they can generate same IDs """
        if other:
            other = Meta(other)
        else:
            return False
        id1 = self.generate_identifier(network=NetworkID.Main)
        id2 = other.generate_identifier(network=NetworkID.Main)
        return id1 == id2

    @property
    def version(self) -> chr:
        return self.__version

    @property
    def key(self) -> PublicKey:
        return self.__key

    @property
    def seed(self) -> str:
        return self.__seed

    @property
    def fingerprint(self) -> bytes:
        return self.__fingerprint

    @classmethod
    def new(cls, key: PublicKey, seed: str=None, fingerprint: bytes=None, version: chr=DefaultVersion):
        """
        Create new meta info

        :param version:     - meta version
        :param key:         - public key
        :param seed:        - user/group name
        :param fingerprint: - signature
        :return: Meta object
        """
        if version & Meta.Version_MKM:  # MKM, ExBTC, ExETH, ...
            meta = {
                'version': version,
                'seed': seed,
                'key': key,
                'fingerprint': base64_encode(fingerprint),
            }
        else:  # BTC, ETH, ...
            meta = {
                'version': version,
                'key': key,
            }
        # new Meta(dict)
        return Meta(meta)

    @classmethod
    def generate(cls, private_key: PrivateKey, seed: str='', version: chr=DefaultVersion):
        """
        Generate meta info with seed and private key

        :param private_key: - user/founder private key
        :param seed:        - user/group name
        :param version:     - meta version
        :return:
        """
        if version & Meta.Version_MKM:  # MKM, ExBTC, ExETH, ...
            # generate fingerprint with private key
            fingerprint = private_key.sign(seed.encode('utf-8'))
            dictionary = {
                'version': version,
                'seed': seed,
                'key': private_key.public_key,
                'fingerprint': base64_encode(fingerprint),
            }
        else:  # BTC, ETH, ...
            dictionary = {
                'version': version,
                'key': private_key.public_key,
            }
        # new Meta(dict)
        return Meta(dictionary)

    def match_public_key(self, public_key: PublicKey) -> bool:
        """ Check whether match public key """
        if self.key == public_key:
            return True
        if self.version & Meta.Version_MKM:  # MKM, ExBTC, ExETH, ...
            # check whether keys equal by verifying signature
            return public_key.verify(data=self.seed.encode('utf-8'), signature=self.fingerprint)
        else:  # BTC, ETH, ...
            # ID with BTC/ETH address has no username
            # so we can just compare the key.data to check matching
            return False

    def match_identifier(self, identifier: ID) -> bool:
        """ Check ID(name+address) with meta info """
        if self.seed is None:
            if identifier.name is not None:
                return False
        elif self.seed != identifier.name:
            return False
        return self.match_address(address=identifier.address)

    def match_address(self, address: Address) -> bool:
        """ Check address with meta info """
        return self.generate_address(network=address.network) == address

    def generate_identifier(self, network: NetworkID) -> ID:
        """ Generate ID with meta info and network ID """
        address = self.generate_address(network=network)
        return ID(name=self.seed, address=address)

    @abstractmethod
    def generate_address(self, network: NetworkID) -> Address:
        """ Generate address with meta info and network ID """
        pass


"""
    Meta for generate ID with address
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    algorithm:
        CT      = fingerprint;
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
        number  = u_int(code);
"""


class MKMMeta(Meta):

    def generate_address(self, network: NetworkID):
        assert self.version == Meta.Version_MKM
        return BTCAddress.new(data=self.fingerprint, network=network)


"""
    Meta for generate ID with BTC address
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    algorithm:
        CT      = key.data;
        hash    = ripemd160(sha256(CT));
        code    = sha256(sha256(network + hash)).prefix(4);
        address = base58_encode(network + hash + code);
        number  = u_int(code);
"""


class BTCMeta(Meta):

    def generate_address(self, network: NetworkID):
        assert self.version & Meta.Version_BTC
        return BTCAddress.new(data=self.key.data, network=network)


meta_classes = {
    # MKM (default)
    Meta.Version_MKM: MKMMeta,
    # BTC
    Meta.Version_BTC: BTCMeta,
    Meta.Version_ExBTC: BTCMeta,
    # ETH
    # ...
}
