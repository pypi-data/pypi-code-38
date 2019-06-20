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


class Address:
    """
    Class that models an Address.
    """

    def __init__(self, address: str):
        """
        Initializes the entities object
        :param address: The actual entities to which messages can be sent
        """
        self.address = address

    def __str__(self) -> str:
        """
        :return: The actual entities to which messages can be sent
        """
        return self.address
