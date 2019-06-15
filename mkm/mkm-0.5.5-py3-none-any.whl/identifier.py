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

from .address import Address, NetworkID


class ID(str):
    """
        ID for entity (Account/Group)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        data format: "name@address[/terminal]"

        fields:
            name     - entity name, the seed of fingerprint to generate address
            address  - a string to identify an entity
            terminal - entity login resource(device), OPTIONAL
    """

    def __new__(cls, identifier: str='',
                name: str='', address: Address=None, terminal: str=None):
        """
        Create ID object with ID string or name + address

        :param identifier: ID string with format 'name@address/terminal'
        :param name:       A string for ID.name
        :param address:    An Address object for ID.address
        :param terminal:   A string for login point
        :return: ID object
        """
        if identifier:
            # return ID object directly
            if isinstance(identifier, ID):
                return identifier
            # get terminal
            pair = identifier.split('/', 1)
            if len(pair) == 2:
                terminal = pair[1]
            else:
                terminal = None
            # get name & address
            pair = pair[0].split('@', 1)
            if len(pair) == 2:
                name = pair[0]
                address = Address(pair[1])
            else:
                name = ''
                address = Address(pair[0])
        elif address:
            # concatenate ID string
            if name:
                identifier = name + '@' + address
            else:
                identifier = address
            if terminal:
                identifier = identifier + '/' + terminal
        else:
            # raise AssertionError('Parameters error')
            return None
        # verify ID.address, which number must not be ZERO
        if address.number <= 0:
            raise ValueError('Invalid ID (address) string')
        # new ID(str)
        self = super().__new__(cls, identifier)
        self.__name = name
        self.__address = address
        self.__terminal = terminal
        return self

    def __eq__(self, other) -> bool:
        if other:
            other = ID(other)
        else:
            return False
        return self.name == other.name and self.address == other.address

    def __hash__(self) -> int:
        if len(self.name) > 0:
            if self.terminal is not None:
                return hash('%s@%s/%s' % (self.name, self.address, self.terminal))
            else:
                return hash('%s@%s' % (self.name, self.address))
        elif self.terminal is not None:
            return hash('%s/%s' % (self.address, self.terminal))
        else:
            return hash(self.address)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def address(self) -> Address:
        return self.__address

    @property
    def terminal(self) -> str:
        return self.__terminal

    @property
    def type(self) -> NetworkID:
        """ ID type """
        return self.__address.network

    @property
    def number(self) -> int:
        """ Search number of this ID """
        return self.__address.number
