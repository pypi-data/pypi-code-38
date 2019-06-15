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

from .utils import base64_encode, base64_decode
from .message import Message

import dkd  # dkd.InstantMessage, dkd.ReliableMessage


class SecureMessage(Message):
    """
        Secure Message
        ~~~~~~~~~~~~~~
        Instant Message encrypted by a symmetric key

        data format: {
            //-- envelope
            sender   : "moki@xxx",
            receiver : "hulk@yyy",
            time     : 123,
            //-- content data & key/keys
            data     : "...",  // base64_encode(symmetric)
            key      : "...",  // base64_encode(asymmetric)
            keys     : {
                "ID1": "key1", // base64_encode(asymmetric)
            }
        }
    """

    def __init__(self, msg: dict):
        super().__init__(msg)
        # secure(encrypted) data
        self.__data = base64_decode(msg['data'])
        # decrypt key/keys
        key = msg.get('key')
        keys = msg.get('keys')
        if key is not None:
            self.__key = base64_decode(key)
            self.__keys = None
        elif keys is not None:
            self.__key = None
            self.__keys = keys
        else:
            # reuse key/keys
            self.__key = None
            self.__keys = None

    @property
    def data(self) -> bytes:
        return self.__data

    # Group ID
    #    when a group message was split/trimmed to a single message,
    #    the 'receiver' will be changed to a member ID, and
    #    the 'group' will be set with the group ID.
    @property
    def group(self) -> str:
        return self.get('group')

    @group.setter
    def group(self, value):
        if value:
            self['group'] = value
        else:
            self.pop('group')

    @group.deleter
    def group(self):
        self.pop('group')

    """
        Decrypt the Secure Message to Instant Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |  1. PW      = decrypt(key, receiver.SK)
            | data     |      | content  |  2. content = decrypt(data, PW)
            | key/keys |      +----------+
            +----------+
    """

    def decrypt(self, member: str=None):
        """
        Decrypt message data to plaintext content

        :param member: If this is a group message, give the member ID here
        :return: InstantMessage object
        """
        sender = self.envelope.sender
        receiver = self.envelope.receiver
        key = self.__key
        # 1. check receiver and encrypted key
        if member is not None:
            # group message
            group = self.group
            # if 'group' not exists, the 'receiver' must be a group ID, and
            # it is not equal to the member of course
            if group is not None:
                # if 'group' exists and the 'receiver' is a group ID too, they must be equal;
                # or the 'receiver' must equal to member, and the 'group' must not equal to member of course
                receiver = group
            # get key for member from 'keys'
            key_map = self.__keys
            if key_map is not None:
                base64 = key_map.get(member)
                if base64 is not None:
                    key = base64_decode(base64)
        # 2. decrypt 'key' to symmetric key
        password = self.delegate.decrypt_key(key=key, sender=sender, receiver=receiver, msg=self)
        if password is None:
            raise ValueError('failed to decrypt key: %s -> %s' % (sender, receiver))
        # 3. decrypt 'data' to 'content'
        #    (remember to save password for decrypted File/Image/Audio/Video data)
        data = self.data
        content = self.delegate.decrypt_content(data=data, key=password, msg=self)
        if content is None:
            raise ValueError('failed to decrypt content: %s, %s' % (data, password))
        # 4. pack message
        msg = self.copy()
        if 'key' in msg:
            msg.pop('key')
        if 'keys' in msg:
            msg.pop('keys')
        msg.pop('data')
        msg['content'] = content
        return dkd.InstantMessage(msg)

    """
        Sign the Secure Message to Reliable Message
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            +----------+      +----------+
            | sender   |      | sender   |
            | receiver |      | receiver |
            | time     |  ->  | time     |
            |          |      |          |
            | data     |      | data     |
            | key/keys |      | key/keys |
            +----------+      | signature|  1. signature = sign(data, sender.SK)
                              +----------+
    """

    def sign(self):
        """
        Sign the message.data with sender's private key

        :return: ReliableMessage object
        """

        # 1. sign message.data
        sender = self.envelope.sender
        data = self.data
        signature = self.delegate.sign_data(msg=self, data=data, sender=sender)
        if signature is None:
            raise AssertionError('failed to sign message: %s' % self)

        # 2. pack message
        msg = self.copy()
        msg['signature'] = base64_encode(signature)
        return dkd.ReliableMessage(msg)

    """
        Split/Trim group message
        ~~~~~~~~~~~~~~~~~~~~~~~~
    """

    def split(self, members: list) -> list:
        """
        Split the group message to single person messages

        :param members: All group members
        :return:        A list of SecureMessage objects for all group members
        """
        msg = self.copy()
        keys = msg.get('keys')
        if keys:
            msg.pop('keys')
        else:
            keys = {}

        # 1. move the receiver(group ID) to 'group'
        msg['group'] = self.envelope.receiver

        messages = []
        for member in members:
            # 2. change receiver to each member
            msg['receiver'] = member
            # 3. get encrypted key
            key = keys.get(member)
            if key:
                msg['key'] = key
            else:
                msg.pop('key')
            # 4. pack message
            messages.append(SecureMessage(msg))
        # OK
        return messages

    def trim(self, member: str):
        """
        Trim the group message for a member

        :param member: Member ID
        :return:       A SecureMessage object drop all irrelevant keys to the member
        """
        msg = self.copy()

        # trim keys
        keys = msg.get('keys')
        if keys is not None:
            key = keys.get(member)
            if key is not None:
                msg['key'] = key
            msg.pop('keys')

        # msg['group'] = self.envelope.receiver
        # msg['receiver'] = member
        return SecureMessage(msg)
