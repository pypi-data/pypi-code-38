"""
MIT License

Copyright (c) 2019 truedl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations
from .exceptions import *

colors = [
    'Blue', 'BlueViolet', 'CadetBlue', 'Chocolate',
    'Coral', 'DodgerBlue', 'Firebrick',
    'GoldenRod', 'Green', 'HotPink', 'OrangeRed',
    'Red', 'SeaGreen', 'SpringGreen', 'YellowGreen'
]


def set_bot(bot):
    """ Set the gbot variable for the struct.py file. """

    globals().update(gbot=bot)


class Auth:
    def __init__(self, **kwargs) -> None:
        try:
            self.bot_username = kwargs['bot_username']
            self.oauth_token = kwargs['oauth_token']
        except Exception as e:
            print(e)
            oft = '"bot_username", "oauth_token"'
            raise OneOfTheseKwargsNotProvidedError(oft)
        if 'channel_name' not in kwargs:
            self.channel_name = kwargs['bot_username']
        else:
            self.channel_name = kwargs['channel_name']

    def __repr__(self) -> str:
        """ The class repr. """

        return f'< Auth({self.bot_username}, {self.oauth_token}) >'


class Message:
    def __init__(self, **kwargs) -> None:
        self.content = kwargs['message_content']
        self.sender = kwargs['message_sender']
        self.command = kwargs['message_command']
        self.channel = Chat(kwargs['message_channel'])
        self.args = kwargs['message_args']

    def __repr__(self) -> str:
        """ The class repr. """

        return f'<Message({self.channel}, @{self.sender})>'


class Chat:
    def __init__(self, channel_name) -> None:
        self.name = channel_name

    async def send(self, message: str) -> bool:
        """ Send message (string) to the Channel.name (object attr) chat and
            returning boolean (On success is True and on fail is False). """

        return await gbot.send(message, self.name)

    def __repr__(self) -> str:
        """ The class repr. """

        return f'#{self.name}'


class Events:
    def __repr__(self) -> str:
        """ The class repr. """

        return '<Events Class>'
