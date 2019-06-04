"""Tests for JsonStatusProtocol."""
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
import sys
import unittest

sys.path.append("..")  # noqa

from wolk_gateway_module.json_status_protocol import JsonStatusProtocol
from wolk_gateway_module.model.device_status import DeviceStatus
from wolk_gateway_module.model.message import Message


class JsonStatusProtocolTests(unittest.TestCase):
    """JsonStatusProtocol Tests."""

    DEVICE_PATH_PREFIX = "d/"
    DEVICE_STATUS_UPDATE_TOPIC_ROOT = "d2p/subdevice_status_update/"
    DEVICE_STATUS_RESPONSE_TOPIC_ROOT = "d2p/subdevice_status_response/"
    DEVICE_STATUS_REQUEST_TOPIC_ROOT = "p2d/subdevice_status_request/"
    LAST_WILL_TOPIC = "lastwill"

    def test_get_inbound_topics_for_device(self):
        """Test that returned list is correctfor given device key."""
        json_status_protocol = JsonStatusProtocol()
        device_key = "some_key"

        self.assertEqual(
            [
                self.DEVICE_STATUS_REQUEST_TOPIC_ROOT
                + self.DEVICE_PATH_PREFIX
                + device_key
            ],
            json_status_protocol.get_inbound_topics_for_device(device_key),
        )

    def test_is_device_status_request_message(self):
        """Test that message is device status request."""
        json_status_protocol = JsonStatusProtocol()
        message = Message(self.DEVICE_STATUS_REQUEST_TOPIC_ROOT)
        self.assertTrue(
            json_status_protocol.is_device_status_request_message(message)
        )

    def test_make_device_status_response_message(self):
        """Test that message is made correctly."""
        json_status_protocol = JsonStatusProtocol()
        device_key = "some_key"
        status = DeviceStatus.CONNECTED

        expected = Message(
            self.DEVICE_STATUS_RESPONSE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps({"state": status.value}),
        )

        serialized = json_status_protocol.make_device_status_response_message(
            device_key, status
        )

        self.assertEqual(expected, serialized)

    def test_make_device_status_update_message(self):
        """Test that message is made correctly."""
        json_status_protocol = JsonStatusProtocol()
        device_key = "some_key"
        status = DeviceStatus.OFFLINE

        expected = Message(
            self.DEVICE_STATUS_UPDATE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps({"state": status.value}),
        )

        serialized = json_status_protocol.make_device_status_update_message(
            device_key, status
        )

        self.assertEqual(expected, serialized)

    def test_make_last_will_message(self):
        """Test that message is made correctly from device keys."""
        json_status_protocol = JsonStatusProtocol()
        keys = ["device1", "device2", "device3"]

        expected = Message(self.LAST_WILL_TOPIC, json.dumps(keys))

        serialized = json_status_protocol.make_last_will_message(keys)

        self.assertEqual(expected, serialized)


if __name__ == "__main__":
    unittest.main()
