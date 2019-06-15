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


class Envelope(dict):
    """
        This class is used to create a message envelope
        which contains 'sender', 'receiver' and 'time'
    """

    def __new__(cls, envelope: dict):
        """
        Create message envelope

        :param envelope: envelope info
        :return: Envelope object
        """
        if envelope is None:
            return None
        elif isinstance(envelope, Envelope):
            # return Envelope object directly
            return envelope
        # new Envelope(dict)
        return super().__new__(Envelope, envelope)

    def __init__(self, envelope: dict):
        super().__init__(envelope)
        self.__sender = envelope['sender']
        self.__receiver = envelope['receiver']
        time = envelope.get('time')
        if time is None:
            self.__time = 0
        else:
            self.__time = int(time)

    @property
    def sender(self) -> str:
        return self.__sender

    @property
    def receiver(self) -> str:
        return self.__receiver

    @property
    def time(self) -> int:
        return self.__time

    @classmethod
    def new(cls, sender: str, receiver: str, time: int=0):
        env = {
            'sender': sender,
            'receiver': receiver,
            'time': time
        }
        return Envelope(env)
