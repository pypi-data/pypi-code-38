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
# noinspection PyPackageRequirements
import telegram
import requests
from typing import List, Dict, Any, Optional, Type, Callable
from bokkichat.entities.Address import Address
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.message.MediaType import MediaType
from bokkichat.entities.message.MediaMessage import MediaMessage
from bokkichat.connection.Connection import Connection
from bokkichat.settings.impl.TelegramBotSettings import TelegramBotSettings
from bokkichat.exceptions import InvalidMessageData, InvalidSettings


class TelegramBotConnection(Connection):
    """
    Class that implements a Telegram bot connection
    """

    def __init__(self, settings: TelegramBotSettings):
        """
        Initializes the connection, with credentials provided by a
        Settings object.
        :param settings: The settings for the connection
        """
        super().__init__(settings)
        try:
            self.bot = telegram.Bot(settings.api_key)
        except telegram.error.InvalidToken:
            raise InvalidSettings()

        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = 0

    @property
    def address(self) -> Address:
        """
        A connection must be able to specify its own entities
        :return: The entities of the connection
        """
        return Address(str(self.bot.name))

    @staticmethod
    def settings_cls() -> Type[TelegramBotSettings]:
        """
        The settings class used by this connection
        :return: The settings class
        """
        return TelegramBotSettings

    def send(self, message: Message):
        """
        Sends a message. A message may be either a TextMessage
        or a MediaMessage.
        :param message: The message to send
        :return: None
        """

        self.logger.info("Sending message to {}".format(message.receiver))

        try:
            if isinstance(message, TextMessage):
                self.bot.send_message(
                    chat_id=message.receiver.address,
                    text=message.body
                )
            elif isinstance(message, MediaMessage):

                media_map = {
                    MediaType.AUDIO: ("audio", self.bot.send_audio),
                    MediaType.VIDEO: ("video", self.bot.send_video),
                    MediaType.IMAGE: ("photo", self.bot.send_photo)
                }

                send_func = media_map[message.media_type][1]

                # Write to file TODO: Check if this can be done with bytes
                with open("/tmp/bokkichat-telegram-temp", "wb") as f:
                    f.write(message.data)

                tempfile = open("/tmp/bokkichat-telegram-temp", "rb")
                params = {
                    "chat_id": message.receiver.address,
                    "caption": message.caption,
                    media_map[message.media_type][0]: tempfile
                }
                send_func(**params)
                tempfile.close()

        except (telegram.error.Unauthorized, telegram.error.BadRequest):
            self.logger.warning(
                "Failed to send message to {}".format(message.receiver)
            )

    def receive(self) -> List[Message]:
        """
        Receives all pending messages.
        :return: A list of pending Message objects
        """
        messages = []

        try:
            for update in self.bot.get_updates(
                    offset=self.update_id, timeout=10
            ):
                self.update_id = update.update_id + 1

                if update.message is None:
                    continue

                telegram_message = update.message.to_dict()

                try:
                    generated = self._parse_message(telegram_message)
                    self.logger.info(
                        "Received message from {}".format(generated.sender)
                    )
                    self.logger.debug(str(generated))
                    messages.append(generated)
                except InvalidMessageData as e:
                    self.logger.error(str(e))

        except telegram.error.Unauthorized:
            # The self.bot.get_update method may cause an
            # Unauthorized Error if the bot is blocked by the user
            self.update_id += 1

        except telegram.error.TimedOut:
            pass

        return messages

    def _parse_message(self, message_data: Dict[str, Any]) -> \
            Optional[Message]:
        """
        Parses the message data of a Telegram message and generates a
        corresponding Message object.
        :param message_data: The telegram message data
        :return: The generated Message object.
        :raises: InvalidMessageData if the parsing failed
        """
        address = Address(str(message_data["chat"]["id"]))

        if "text" in message_data:
            body = message_data["text"]
            self.logger.debug("Message Body: {}".format(body))
            return TextMessage(address, self.address, body)

        else:

            for media_key, media_type in {
                "photo": MediaType.IMAGE,
                "audio": MediaType.AUDIO,
                "video": MediaType.VIDEO,
                "voice": MediaType.AUDIO
            }.items():

                if media_key in message_data:

                    self.logger.debug("Media Type: {}".format(media_key))
                    media_info = message_data[media_key]

                    if len(media_info) == 0:
                        continue

                    if isinstance(media_info, list):
                        largest = media_info[len(media_info) - 1]
                        file_id = largest["file_id"]
                    elif isinstance(media_info, dict):
                        file_id = media_info["file_id"]
                    else:
                        continue

                    file_info = self.bot.get_file(file_id)
                    resp = requests.get(file_info["file_path"])
                    data = resp.content

                    return MediaMessage(
                        address,
                        self.address,
                        media_type,
                        data,
                        message_data.get("caption", "")
                    )

        raise InvalidMessageData(message_data)

    def close(self):
        """
        Disconnects the Connection.
        :return: None
        """
        pass

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
        try:
            super().loop(callback, sleep_time)
        except telegram.error.NetworkError:
            time.sleep(10)
            self.loop(callback, sleep_time)
