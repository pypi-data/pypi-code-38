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
    Group for assembly
    ~~~~~~~~~~~~~~~~~~

    Group with members
"""

from abc import abstractmethod, ABC

from .identifier import ID
from .entity import Entity, IEntityDataSource


class Group(Entity):

    @property
    def founder(self) -> ID:
        return self.delegate.founder(identifier=self.identifier)

    @property
    def owner(self) -> ID:
        return self.delegate.owner(identifier=self.identifier)

    @property
    def members(self) -> list:
        return self.delegate.members(identifier=self.identifier)


#
#  Delegates
#

class IGroupDataSource(IEntityDataSource, ABC):
    """
        User Data Source
        ~~~~~~~~~~~~~~~~
    """

    @abstractmethod
    def founder(self, identifier: ID) -> ID:
        """ Get founder of the group """
        pass

    @abstractmethod
    def owner(self, identifier: ID) -> ID:
        """ Get current owner of the group """
        pass

    @abstractmethod
    def members(self, identifier: ID) -> list:
        """ Get all members in the group """
        pass
