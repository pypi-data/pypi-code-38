"""Tests for JsonFirmwareUpdateProtocol."""
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


from wolk_gateway_module.json_firmware_update_protocol import (
    JsonFirmwareUpdateProtocol,
)
from wolk_gateway_module.model.firmware_update_status import (
    FirmwareUpdateStatus,
    FirmwareUpdateState,
    FirmwareUpdateErrorCode,
)
from wolk_gateway_module.model.message import Message


class JsonFirmwareUpdateProtocolTests(unittest.TestCase):
    """JsonFirmwareUpdateProtocol Tests."""

    DEVICE_PATH_PREFIX = "d/"
    FIRMWARE_UPDATE_INSTALL_TOPIC_ROOT = "p2d/firmware_update_install/"
    FIRMWARE_UPDATE_ABORT_TOPIC_ROOT = "p2d/firmware_update_abort/"
    FIRMWARE_UPDATE_STATUS_TOPIC_ROOT = "d2p/firmware_update_status/"
    FIRMWARE_VERSION_UPDATE_TOPIC_ROOT = "d2p/firmware_version_update/"

    def test_get_inbound_topics_for_device(self):
        """Test that returned list is correct for given device key."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        device_key = "some_key"

        expected = [
            self.FIRMWARE_UPDATE_INSTALL_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            self.FIRMWARE_UPDATE_ABORT_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
        ]

        self.assertEqual(
            expected,
            json_firmware_update_protocol.get_inbound_topics_for_device(
                device_key
            ),
        )

    def test_make_firmware_update_installation_status_message(self):
        """Test that firmware update status message is created correctly."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        device_key = "some_key"
        status = FirmwareUpdateStatus(FirmwareUpdateState.INSTALLATION)

        expected = Message(
            self.FIRMWARE_UPDATE_STATUS_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps({"status": "INSTALLATION"}),
        )

        self.assertEqual(
            expected,
            json_firmware_update_protocol.make_update_message(
                device_key, status
            ),
        )

    def test_make_firmware_update_error_file_system_status_message(self):
        """Test that firmware update status message is created correctly."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        device_key = "some_key"
        status = FirmwareUpdateStatus(
            FirmwareUpdateState.INSTALLATION,
            FirmwareUpdateErrorCode.FILE_SYSTEM_ERROR,
        )

        expected = Message(
            self.FIRMWARE_UPDATE_STATUS_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            json.dumps(
                {
                    "status": status.status.value,
                    "error": status.error_code.value,
                }
            ),
        )

        self.assertEqual(
            expected,
            json_firmware_update_protocol.make_update_message(
                device_key, status
            ),
        )

    def test_make_version_message(self):
        """Test that firmware version message is created correctly."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        device_key = "some_key"
        firmware_version = "v1.0"

        expected = Message(
            self.FIRMWARE_VERSION_UPDATE_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key,
            firmware_version,
        )

        self.assertEqual(
            expected,
            json_firmware_update_protocol.make_version_message(
                device_key, firmware_version
            ),
        )

    def test_is_firmware_install_command(self):
        """Test that message is firmware install command."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()

        message = Message(self.FIRMWARE_UPDATE_INSTALL_TOPIC_ROOT)

        self.assertTrue(
            json_firmware_update_protocol.is_firmware_install_command(message)
        )

    def test_is_firmware_abort_command(self):
        """Test that message is firmware abort command."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        message = Message(self.FIRMWARE_UPDATE_ABORT_TOPIC_ROOT)

        self.assertTrue(
            json_firmware_update_protocol.is_firmware_abort_command(message)
        )

    def test_make_firmware_file_path(self):
        """Test firmare file path is extracted correctly."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        expected = "some/path/to/file"

        message = Message(
            self.FIRMWARE_UPDATE_INSTALL_TOPIC_ROOT,
            json.dumps({"fileName": expected}),
        )

        self.assertEqual(
            expected,
            json_firmware_update_protocol.make_firmware_file_path(message),
        )

    def test_extract_key_from_message(self):
        """Test that device key is correctly extracted from abort message."""
        json_firmware_update_protocol = JsonFirmwareUpdateProtocol()
        device_key = "some_key"

        message = Message(
            self.FIRMWARE_UPDATE_ABORT_TOPIC_ROOT
            + self.DEVICE_PATH_PREFIX
            + device_key
        )

        self.assertEqual(
            device_key,
            json_firmware_update_protocol.extract_key_from_message(message),
        )


if __name__ == "__main__":
    unittest.main()
