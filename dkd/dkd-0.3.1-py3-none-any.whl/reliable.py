# -*- coding: utf-8 -*-
#
#   Dao-Ke-Dao: Universal Message Module
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

from .secure import SecureMessage
from .utils import base64_decode


class ReliableMessage(SecureMessage):
    """
        This class is used to sign the SecureMessage
        It contains a 'signature' field which signed with sender's private key
    """

    def __init__(self, msg: dict):
        super().__init__(msg)
        # signature
        self.__signature = base64_decode(msg['signature'])

    @property
    def signature(self) -> bytes:
        return self.__signature

    # Meta info of sender
    #    just for the first contact
    @property
    def meta(self) -> dict:
        return self.get('meta')

    @meta.setter
    def meta(self, value):
        if value:
            self['meta'] = value
        else:
            self.pop('meta')

    @meta.deleter
    def meta(self):
        self.pop('meta')

    """
        Verify the Reliable Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |  1. verify(data, signature, sender.PK)
            | key/keys |      | key/keys |
            | signature|      +----------+
            +----------+
    """

    def verify(self) -> SecureMessage:
        """
        Verify the message.data with signature

        :return: SecureMessage object if signature matched
        """
        data = self.data
        signature = self.signature
        sender = self.envelope.sender
        if self.delegate.verify_data_signature(data=data, signature=signature, sender=sender, msg=self):
            msg = self.copy()
            msg.pop('signature')  # remove 'signature'
            return SecureMessage(msg)
        else:
            raise ValueError('Signature error')
