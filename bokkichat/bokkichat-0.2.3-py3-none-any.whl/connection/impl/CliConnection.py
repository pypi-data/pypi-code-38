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

from typing import List, Type
from bokkichat.entities.Address import Address
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.connection.Connection import Connection
from bokkichat.settings.impl.CliSettings import CliSettings


class CliConnection(Connection):
    """
    Class that implements a CLI connection which can be used in testing
    """

    @property
    def address(self) -> Address:
        """
        A CLI connection has no real entities,
        so a dummy entities is generated.
        :return: The entities of the connection
        """
        return Address("CLI")

    @staticmethod
    def settings_cls() -> Type[CliSettings]:
        """
        The settings class used by this connection
        :return: The settings class
        """
        return CliSettings

    # noinspection PyMethodMayBeStatic
    def send(self, message: Message):
        """
        Prints a "sent" message
        :param message: The message to "send"
        :return: None
        """
        print(message)

    def receive(self) -> List[Message]:
        """
        A CLI Connection receives messages by listening to the input
        :return: A list of pending Message objects
        """
        return [TextMessage(self.address, self.address, input())]

    def close(self):
        """
        Disconnects the Connection.
        :return: None
        """
        pass
