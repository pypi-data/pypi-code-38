"""Service for exchanging data with WolkGateway."""
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


class ConnectivityService(ABC):
    """Responsible for exchanging data with WolkGateway."""

    @abstractmethod
    def set_inbound_message_listener(self, on_inbound_message):
        """Set the callback function to handle inbound messages.

        :param on_inbound_message: Callable that handles inbound messages
        :type on_inbound_message: Callable[[str], None]
        """
        pass

    @abstractmethod
    def set_lastwill_message(self, message):
        """Send offline state for module devices on disconnect.

        :param message: Message to be published
        :type message: Message
        """
        pass

    @abstractmethod
    def add_subscription_topics(self, topics):
        """Add subscription topics.

        :param topics: List of topics
        :type topics: List[str]
        """
        pass

    @abstractmethod
    def remove_topics_for_device(self, device_key):
        """Remove topics for device from subscription topics.

        :param device_key: Device identifier
        :type device_key: str
        """
        pass

    @abstractmethod
    def connected(self):
        """Return if currently connected.

        :returns: connected
        :rtype: bool
        """
        pass

    @abstractmethod
    def connect(self):
        """Establish connection with WolkGateway."""
        pass

    @abstractmethod
    def reconnect(self):
        """Reestablish connection with WolkGateway."""
        pass

    @abstractmethod
    def disconnect(self):
        """Terminate connection with WolkGateway."""
        pass

    @abstractmethod
    def publish(self, message):
        """Publish serialized data to WolkGateway.

        :param message: Message to be published
        :type message: Message
        :returns: result
        :rtype: bool
        """
