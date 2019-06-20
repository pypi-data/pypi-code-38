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

import time
import logging
from typing import Callable, List, Type
from bokkichat.entities.Address import Address
from bokkichat.entities.message.Message import Message
from bokkichat.settings.Settings import Settings


class Connection:
    """
    Class that defines methods a Connection must implement.
    A connection is the central class in bokkichat and handles all
    communications with the chat services.
    """

    def __init__(self, settings: Settings):
        """
        Initializes the connection, with credentials provided by a
        Settings object.
        :param settings: The settings for the connection
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.looping = False
        self.loop_break = False

    @property
    def address(self) -> Address:
        """
        A connection must be able to specify its own entities
        :return: The entities of the connection
        """
        raise NotImplementedError()

    @staticmethod
    def settings_cls() -> Type[Settings]:
        """
        The settings class used by this connection
        :return: The settings class
        """
        raise NotImplementedError()

    def send(self, message: Message):
        """
        Sends a message. A message may be either a TextMessage
        or a MediaMessage.
        :param message: The message to send
        :return: None
        """
        raise NotImplementedError()

    def receive(self) -> List[Message]:
        """
        Receives all pending messages.
        :return: A list of pending Message objects
        """
        raise NotImplementedError()

    def loop(self, callback: Callable, sleep_time: int = 1):
        """
        Starts a loop that periodically checks for new messages, calling
        a provided callback function in the process.
        :param callback: The callback function to call for each
                         received message.
                         The callback should have the following format:
                             lambda connection, message: do_stuff()
        :param sleep_time: The time to sleep between loops
        :return: None
        """
        self.looping = True
        while True:
            for message in self.receive():
                callback(self, message)

            if self.loop_break:
                self.loop_break = False
                break

            time.sleep(sleep_time)
        self.looping = False

    def close(self):
        """
        Disconnects the Connection.
        :return: None
        """
        raise NotImplementedError()

    @classmethod
    def from_serialized_settings(cls, serialized: str) -> "Connection":
        """
        Generates a Connection using serialized settings
        :param serialized: The serialized settings
        :return: The generated connection
        """
        settings = cls.settings_cls().deserialize(serialized)
        return cls(settings)
