"""Store data before publishing."""
#   Copyright 2019 WolkAbout Technology s.r.o.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from collections import deque
from typing import Optional, List

from wolk_gateway_module.persistence.outbound_message_queue import (
    OutboundMessageQueue,
)
from wolk_gateway_module.logger_factory import logger_factory
from wolk_gateway_module.model.message import Message


class OutboundMessageDeque(OutboundMessageQueue):
    """
    Responsible for storing messages before being sent to WolkGateway.

    Messages are sent in the order they were added to the queue.

    Storing readings and alarms without Unix timestamp will result
    in all sent messages being treated as live readings and
    will be assigned a timestamp upon reception, so for a valid
    history add timestamps to readings via `int(round(time.time() * 1000))`
    """

    def __init__(self) -> None:
        """Initialize a double ended queue for storing messages."""
        self.queue = deque()
        self.log = logger_factory.get_logger(str(self.__class__.__name__))

    def __repr__(self) -> str:
        """Make string representation of OutboundMessageDeque.

        :returns: representation
        :rtype: str
        """
        return "OutboundMessageDeque()"

    def put(self, message: Message) -> bool:
        """
        Place a message in storage.

        :param message: Message to be stored
        :type message: Message

        :returns: result
        :rtype: bool
        """
        self.log.debug(f"Placing in storage: {message}")
        self.queue.append(message)
        return True

    def remove(self, message: Message) -> bool:
        """
        Remove specific message from storage.

        :returns: result
        :rtype: bool
        """
        self.log.debug(f"Removing from storage: {message}")
        if message in self.queue:
            self.queue.remove(message)
            return True
        return True

    def get_messages_for_device(self, device_key: str) -> List[Message]:
        """
        Return a list of messages that belong to a certain device.

        Does not remove from storage.

        :param device_key: Device identifier
        :type device_key: str

        :returns: messages
        :rtype: List[Message]
        """
        self.log.debug(f"Getting messages for device: {device_key}")
        if self.queue_size() == 0:
            self.log.debug("No messages in queue")
            return []
        messages = []
        for message in self.queue:
            if device_key in message.topic:
                messages.append(message)
        self.log.debug(f"Found messages: {messages}")
        return messages

    def get(self) -> Optional[Message]:
        """
        Get the first message from storage without removing it.

        :returns: message
        :rtype: Message, None
        """
        try:
            message = self.queue[0]
        except IndexError:
            message = None
        self.log.debug(f"Got message from storage: {message}")
        return message

    def queue_size(self) -> int:
        """
        Return current number of messages in storage.

        :returns: size
        :rtype: int
        """
        size = len(self.queue)
        self.log.debug(f"Queue size: {size}")
        return size
