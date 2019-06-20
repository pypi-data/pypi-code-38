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

from typing import Dict, Any


class InvalidMessageData(Exception):
    """
    Exception that indicates message data that's invalid or otherwise could
    not be correctly parsed.
    """

    def __init__(self, message_data: Dict[str, Any]):
        """
        Initializes the Exception
        :param message_data: The message data that caused the
                             exception to be raised
        """
        self.message_data = message_data

    def __str__(self) -> str:
        """
        :return: A string representation of the exception
        """
        return "InvalidMessageData: {}".format(self.message_data)


class InvalidSettings(Exception):
    """
    Exception that gets raised whenever there's a problem with the settings.
    Example: Invalid API key, connection can't be established
    """
    pass
