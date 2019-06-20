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

import json
from bokkichat.settings.Settings import Settings


class TelegramBotSettings(Settings):
    """
    Class that defines a Settings object for a Telegram bot connection
    """

    def __init__(self, api_key: str):
        """
        Initializes the Telegram Connection.
        :param api_key: The API key used for authentication
        """
        self.api_key = api_key

    # noinspection PyMethodMayBeStatic
    def serialize(self) -> str:
        """
        Serializes the settings to a string
        :return: The serialized Settings object
        """
        return json.dumps({
            "api_key": self.api_key
        })

    @classmethod
    def deserialize(cls, serialized: str) -> "TelegramBotSettings":
        """
        Deserializes a string and generates a Settings object from it
        :param serialized: The serialized string
        :return: The deserialized Settings object
        """
        obj = json.loads(serialized)
        return cls(obj["api_key"])

    @classmethod
    def prompt(cls) -> Settings:
        """
        Prompts the user for input to generate a Settings object
        :return: The generated settings object
        """
        api_key = cls.user_input("API Key")
        return cls(api_key=api_key)
