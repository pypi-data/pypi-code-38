"""LICENSE
Copyright 2018 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bokkichat.

bokkichat is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

bokkichat is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with bokkichat.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from bokkichat.entities.Address import Address


class Message:
    """
    Class that defines common attributes for a Message object.
    """

    def __init__(self, sender: Address, receiver: Address):
        """
        Initializes a Message object.
        :param sender: The sender of the message
        :param receiver: The receiver of the message
        """
        self.sender = sender
        self.receiver = receiver

    def __str__(self) -> str:
        """
        :return: A string representation of the Message object
        """
        raise NotImplementedError()

    def make_reply(self) -> "Message":
        """
        Swaps the sender and receiver of the message
        :return: The generated reply
        """
        raise NotImplementedError()

    @staticmethod
    def is_text() -> bool:
        """
        :return: Whether or not the message is a text message
        """
        return False

    @staticmethod
    def is_media() -> bool:
        """
        :return: Whether or not the message is a media message
        """
        return False
