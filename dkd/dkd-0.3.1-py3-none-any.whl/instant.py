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

from .utils import base64_encode
from .envelope import Envelope
from .content import Content
from .message import Message
from .secure import SecureMessage


class InstantMessage(Message):
    """
        Instant Message
        ~~~~~~~~~~~~~~~

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content
            content  : {...}
        }
    """

    def __init__(self, msg: dict):
        super().__init__(msg)
        # message content
        self.__content = Content(msg['content'])

    @property
    def content(self) -> Content:
        return self.__content

    @classmethod
    def new(cls, content: Content, envelope: Envelope=None,
            sender: str=None, receiver: str=None, time: int=0):
        if envelope:
            sender = envelope.sender
            receiver = envelope.receiver
            time = envelope.time
        # build instant message info
        msg = {
            'sender': sender,
            'receiver': receiver,
            'time': time,

            'content': content,
        }
        return InstantMessage(msg)

    """
        Encrypt the Instant Message to Secure Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | content  |      | data     |  1. data = encrypt(content, PW)
            +----------+      | key/keys |  2. key  = encrypt(PW, receiver.PK)
                              +----------+
    """

    def encrypt(self, password: dict, members: list=None) -> SecureMessage:
        """
        Encrypt message content with password(symmetric key)

        :param password: A symmetric key for encrypting message content
        :param members:  If this is a group message, get all members here
        :return: SecureMessage object
        """
        msg = self.copy()

        # 1. encrypt 'content' to 'data'
        content = self.content
        data = self.delegate.encrypt_content(content=content, key=password, msg=self)
        if data is None:
            raise AssertionError('failed to encrypt content with key: %s' % password)

        # 2. encrypt password to 'key'/'keys'
        if members is None:
            # personal message
            receiver = self.envelope.receiver
            key = self.delegate.encrypt_key(key=password, receiver=receiver, msg=self)
            if key:
                msg['key'] = base64_encode(key)
            else:
                print('reused key for contact: %s' % self.envelope.sender)
        else:
            # group message
            keys = {}
            for member in members:
                key = self.delegate.encrypt_key(key=password, receiver=member, msg=self)
                if key:
                    keys[member] = base64_encode(key)
                else:
                    print('reused key for member: %s' % member)
            msg['keys'] = keys

        # 3. pack message
        msg['data'] = base64_encode(data)
        msg.pop('content')  # remove 'content'
        return SecureMessage(msg)
