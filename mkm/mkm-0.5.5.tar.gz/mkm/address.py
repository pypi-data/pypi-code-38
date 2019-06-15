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
    Address for MKM ID
    ~~~~~~~~~~~~~~~~~~

    properties:
        network - address type
        number  - search number
"""

from enum import IntEnum

from .crypto.utils import sha256, ripemd160, base58_encode, base58_decode


class NetworkID(IntEnum):
    """
        @enum MKMNetworkID

        @abstract A network type to indicate what kind the entity is.

        @discussion An address can identify a person, a group of people,
            a team, even a thing.

            MKMNetwork_Main indicates this entity is a person's account.
            An account should have a public key, which proved by meta data.

            MKMNetwork_Group indicates this entity is a group of people,
            which should have a founder (also the owner), and some members.

            MKMNetwork_Moments indicates a special personal social network,
            where the owner can share information and interact with its friends.
            The owner is the king here, it can do anything and no one can stop it.

            MKMNetwork_Polylogue indicates a virtual (temporary) social network.
            It's created to talk with multi-people (but not too much, e.g. < 100).
            Any member can invite people in, but only the founder can expel member.

            MKMNetwork_Chatroom indicates a massive (persistent) social network.
            It's usually more than 100 people in it, so we need administrators
            to help the owner to manage the group.

            MKMNetwork_SocialEntity indicates this entity is a social entity.

            MKMNetwork_Organization indicates an independent organization.

            MKMNetwork_Company indicates this entity is a company.

            MKMNetwork_School indicates this entity is a school.

            MKMNetwork_Government indicates this entity is a government department.

            MKMNetwork_Department indicates this entity is a department.

            MKMNetwork_Thing this is reserved for IoT (Internet of Things).

        Bits:
            0000 0001 - this entity's branch is independent (clear division).
            0000 0010 - this entity can contains other group (big organization).
            0000 0100 - this entity is top organization.
            0000 1000 - (Main) this entity acts like a human.

            0001 0000 - this entity contains members (Group)
            0010 0000 - this entity needs other administrators (big organization)
            0100 0000 - this is an entity in reality.
            1000 0000 - (IoT) this entity is a 'Thing'.

            (All above are just some advices to help choosing numbers :P)
    """
    ################################
    #  BTC Network
    ################################
    BTCMain = 0x00      # 0000 0000 (BitCoin Address)
    # BTCTest = 0x6f    # 0110 1111 (BitCoin Test)

    ################################
    #  Person Account
    ################################
    Main = 0x08         # 0000 1000 (Person)

    ################################
    #  Virtual Groups
    ################################
    Group = 0x10        # 0001 0000 (Multi-Persons)
    # Moments = 0x18    # 0001 1000 (Twitter)
    Polylogue = 0x10    # 0001 0000 (Multi-Persons Chat, N < 100)
    Chatroom = 0x30     # 0011 0000 (Multi-Persons Chat, N >= 100)

    ################################
    #  Social Entities in Reality
    ################################
    # SocialEntity = 0x50  # 0101 0000
    # Organization = 0x74  # 0111 0100
    # Company = 0x76       # 0111 0110
    # School = 0x77        # 0111 0111
    # Government = 0x73    # 0111 0011
    # Department = 0x52    # 0101 0010

    ################################
    #  Network
    ################################
    Provider = 0x76        # 0111 0110 (Service Provider)
    Station = 0x88         # 1000 1000 (Server Node)

    ################################
    #  Internet of Things
    ################################
    Thing = 0x80           # 1000 0000 (IoT)
    Robot = 0xC8           # 1100 1000

    def is_communicator(self) -> bool:
        return (self.value & self.Main) or (self.value == self.BTCMain)

    def is_person(self) -> bool:
        return (self.value == self.Main) or (self.value == self.BTCMain)

    def is_group(self) -> bool:
        return self.value & self.Group

    def is_station(self) -> bool:
        return self.value == self.Station

    def is_provider(self) -> bool:
        return self.value == self.Provider

    def is_thing(self) -> bool:
        return self.value & self.Thing

    def is_robot(self) -> bool:
        return self.value == self.Robot


class Address(str):
    """
        This class is used to build address for ID
    """

    def __new__(cls, address: str):
        """
        Create address object with string

        :param address: address string
        :return: Address object
        """
        if address is None:
            return None
        elif cls is not Address:
            # subclass
            return super().__new__(cls, address)
        elif isinstance(address, Address):
            # return Address object directly
            return address
        # try to create address object
        for clazz in address_classes:
            try:
                return clazz(address=address)
            except ValueError:
                continue

    @property
    def network(self) -> NetworkID:
        """
        Get network type of address

        :return: NetworkID
        """
        yield None

    @property
    def number(self) -> int:
        """
        Get search number of address

        :return: search number [0, 2^32)
        """
        return 0


"""
    Address like BitCoin
    ~~~~~~~~~~~~~~~~~~~~

    data format: "network+digest+check_code"
        network    --  1 byte
        digest     -- 20 bytes
        check_code --  4 bytes

    algorithm:
        fingerprint = sign(seed, SK);
        digest      = ripemd160(sha256(fingerprint));
        check_code  = sha256(sha256(network + digest)).prefix(4);
        address     = base58_encode(network + digest + check_code);
"""


def check_code(data: bytes) -> bytes:
    # check code in BTC address
    return sha256(sha256(data))[:4]


def user_number(code: bytes) -> int:
    # get user number, which for remembering and searching user
    return int.from_bytes(code, byteorder='little')


class BTCAddress(Address):

    def __new__(cls, address: str):
        # get fields from string
        prefix_digest_code = base58_decode(address)
        if len(prefix_digest_code) != 25:
            raise ValueError('BTC address length error')
        # split them
        prefix = prefix_digest_code[:1]
        digest = prefix_digest_code[1:-4]
        code = prefix_digest_code[-4:]
        # check them
        if check_code(prefix + digest) != code:
            raise ValueError('BTC address check code error')
        network = ord(prefix)
        self = super().__new__(cls, address)
        self.__network = NetworkID(network)
        self.__number = user_number(code)
        return self

    @classmethod
    def new(cls, data: bytes, network: NetworkID=0) -> Address:
        """
        Calculate address string with fingerprint

        :param data:    fingerprint (signature/key.data)
        :param network: address type
        :return:        Address object
        """
        prefix = chr(network).encode('latin1')
        digest = ripemd160(sha256(data))
        code = check_code(prefix + digest)
        address = base58_encode(prefix + digest + code)
        return BTCAddress(address)

    @property
    def network(self) -> NetworkID:
        return self.__network

    @property
    def number(self) -> int:
        return self.__number


address_classes = [
    BTCAddress
]
