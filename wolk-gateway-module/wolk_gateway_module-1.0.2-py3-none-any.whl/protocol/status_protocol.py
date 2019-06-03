"""Handling of inbound and outbound messages related to device status."""
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


class StatusProtocol(ABC):
    """Parse inbound messages and serialize device status messages."""

    @abstractmethod
    def get_inbound_topics_for_device(self, device_key):
        """Return list of inbound topics for given device key.

        :param device_key: Device key for which to create topics
        :type device_key: str

        :returns: inbound_topics
        :rtype: list
        """
        pass

    @abstractmethod
    def is_device_status_request_message(self, message):
        """Check if message is device status request.

        :param message: Message received
        :type message: Message

        :returns: is_device_status_request
        :rtype: bool
        """
        pass

    @abstractmethod
    def make_device_status_response_message(self, device_status, device_key):
        """Make message from device status response.

        :param device_status: Device's current status
        :type device_status: DeviceStatus
        :param device_key: Device to which the status belongs to
        :type device_key: str

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def make_device_status_update_message(self, device_status, device_key):
        """Make message from device status update.

        :param device_status: Device's current status
        :type device_status: DeviceStatus
        :param device_key: Device to which the status belongs to
        :type device_key: str

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def make_last_will_message(self, device_keys):
        """Make last will message from list of device keys.

        :param device_keys: List of device keys
        :type device_keys: list(str)

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def extract_key_from_message(self, message):
        """Extract device key from message.

        :param message: Message received
        :type message: Message

        :returns: device_key
        :rtype: str
        """
        pass
