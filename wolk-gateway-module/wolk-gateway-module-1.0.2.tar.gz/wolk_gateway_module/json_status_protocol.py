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

import json

from wolk_gateway_module.logger_factory import logger_factory
from wolk_gateway_module.model.device_status import DeviceStatus
from wolk_gateway_module.model.message import Message
from wolk_gateway_module.protocol.status_protocol import StatusProtocol


class JsonStatusProtocol(StatusProtocol):
    """Parse inbound messages and serialize device status messages."""

    DEVICE_PATH_PREFIX = "d/"
    DEVICE_STATUS_UPDATE_TOPIC_ROOT = "d2p/subdevice_status_update/"
    DEVICE_STATUS_RESPONSE_TOPIC_ROOT = "d2p/subdevice_status_response/"
    DEVICE_STATUS_REQUEST_TOPIC_ROOT = "p2d/subdevice_status_request/"
    LAST_WILL_TOPIC = "lastwill"

    def __init__(self) -> None:
        """Create object."""
        self.log = logger_factory.get_logger(str(self.__class__.__name__))

    def __repr__(self) -> str:
        """Make string representation of JsonStatusProtocol.

        :returns: representation
        :rtype: str
        """
        return "JsonStatusProtocol()"

    def get_inbound_topics_for_device(self, device_key: str) -> list:
        """Return list of inbound topics for given device key.

        :param device_key: Device key for which to create topics
        :type device_key: str

        :returns: inbound_topics
        :rtype: list
        """
        inbound_topics = [
            self.DEVICE_STATUS_REQUEST_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key
        ]
        self.log.debug(f"Inbound topics for {device_key} : {inbound_topics}")

        return inbound_topics

    def is_device_status_request_message(self, message: Message) -> bool:
        """Check if message is device status request.

        :param message: Message received
        :type message: Message

        :returns: is_device_status_request
        :rtype: bool
        """
        is_device_status_request = message.topic.startswith(
            self.DEVICE_STATUS_REQUEST_TOPIC_ROOT
        )
        self.log.debug(
            f"Is {message} device status request "
            f"message: {is_device_status_request}"
        )

        return is_device_status_request

    def make_device_status_response_message(
        self, device_key: str, device_status: DeviceStatus
    ) -> Message:
        """Make message from device status response.

        :param device_status: Device's current status
        :type device_status: DeviceStatus
        :param device_key: Device to which the status belongs to
        :type device_key: str

        :returns: message
        :rtype: Message
        """
        message = Message(
            self.DEVICE_STATUS_RESPONSE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps({"state": device_status.value}),
        )
        self.log.debug(f"Made {message} from {device_status} and {device_key}")

        return message

    def make_device_status_update_message(
        self, device_key: str, device_status: DeviceStatus
    ) -> Message:
        """Make message from device status update.

        :param device_status: Device's current status
        :type device_status: DeviceStatus
        :param device_key: Device to which the status belongs to
        :type device_key: str

        :returns: message
        :rtype: Message
        """
        message = Message(
            self.DEVICE_STATUS_UPDATE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps({"state": device_status.value}),
        )
        self.log.debug(f"Made {message} from {device_status} and {device_key}")

        return message

    def make_last_will_message(self, device_keys: list) -> Message:
        """Make last will message from list of device keys.

        :param device_keys: List of device keys
        :type device_keys: list(str)

        :returns: message
        :rtype: Message
        """
        message = Message(self.LAST_WILL_TOPIC, json.dumps(device_keys))
        self.log.debug(f"Made {message} from {device_keys}")

        return message

    def extract_key_from_message(self, message: Message) -> str:
        """Extract device key from message.

        :param message: Message received
        :type message: Message

        :returns: device_key
        :rtype: str
        """
        device_key = message.topic.split("/")[-1]
        self.log.debug(f"Made {device_key} from {message}")

        return device_key
