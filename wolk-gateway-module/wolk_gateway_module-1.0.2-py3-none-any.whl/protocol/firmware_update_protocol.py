"""Handling of messages related to device firmware update."""
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


class FirmwareUpdateProtocol(ABC):
    """Parse inbound messages and serialize outbound firmware messages."""

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
    def make_update_message(self, device_key, status):
        """Make message from device firmware update status.

        :param device_key: Device key to which the firmware update belongs to
        :type device_key: str
        :param status: Device firmware update status
        :type status: FirmwareUpdateStatus

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def make_version_message(self, device_key, firmware_verison):
        """Make message from device firmware update version.

        :param device_key: Device key to which the firmware update belongs to
        :type device_key: str
        :param firmware_verison: Current firmware version
        :type firmware_verison: str

        :returns: message
        :rtype: Message
        """
        pass

    @abstractmethod
    def is_firmware_install_command(self, message):
        """Check if received message is firmware install command.

        :param message: Message received
        :type message: Message

        :returns: is_firmware_install_command
        :rtype: bool
        """
        pass

    @abstractmethod
    def is_firmware_abort_command(self, message):
        """Check if received message is firmware abort command.

        :param message: Message received
        :type message: Message

        :returns: is_firmware_abort_command
        :rtype: bool
        """
        pass

    @abstractmethod
    def make_firmware_file_path(self, message):
        """Extract file path from firmware install message.

        :param message: Message received
        :type message: Message

        :returns: firmware_file_path
        :rtype: str
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
