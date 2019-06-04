"""Handling of inbound and outbound messages related to device registraiton."""
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


class RegistrationProtocol(ABC):
    """Parse inbound messages and serialize outbound registration messages."""

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
    def extract_key_from_message(self, message):
        """Return device key from message.

        :param message: Message received
        :type message: Message

        :returns: device_key
        :rtype: str
        """
        pass

    @abstractmethod
    def is_registration_response_message(self, message):
        """Check if message is device registration response.

        :param message: Message received
        :type message: Message

        :returns: is_device_registration_response
        :rtype: bool
        """
        pass

    @abstractmethod
    def make_registration_message(self, request):
        """Make message from device registration request.

        :param request: Device registration request
        :type request: DeviceRegistrationRequest

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def make_registration_response(self, message):
        """Make device registration response from message.

        :param message: Message received
        :rtpe message: Message

        :returns: device_registration_response
        :rtype: DeviceRegistrationResponse
        """
        pass
