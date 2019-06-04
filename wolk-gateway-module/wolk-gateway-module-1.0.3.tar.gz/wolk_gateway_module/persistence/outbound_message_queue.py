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


from abc import ABC, abstractmethod


class OutboundMessageQueue(ABC):
    """Responsible for storing messages before being sent to WolkGateway."""

    @abstractmethod
    def put(self, message):
        """
        Place a message in storage.

        :param message: Message to be stored
        :type message: Message

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def get(self):
        """
        Get the first message from storage without removing it.

        :returns: message
        :rtype: Message, None
        """
        pass

    @abstractmethod
    def remove(self, message):
        """
        Remove specific message from storage.

        :returns: result
        :rtype: bool
        """
        pass

    @abstractmethod
    def get_messages_for_device(self, device_key):
        """
        Return a list of messages that belong to a certain device.

        Does not remove from storage.

        :param device_key: Device identifier
        :type device_key: str

        :returns: messages
        :rtype: List[Message]
        """
        pass

    @abstractmethod
    def queue_size(self):
        """
        Return current number of messages in storage.

        :returns: size
        :rtype: int
        """
        pass
