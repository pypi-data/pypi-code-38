"""Tests for JsonDataProtocol."""
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

from wolk_gateway_module.json_data_protocol import JsonDataProtocol
from wolk_gateway_module.model.actuator_command import (
    ActuatorCommand,
    ActuatorCommandType,
)
from wolk_gateway_module.model.actuator_state import ActuatorState
from wolk_gateway_module.model.actuator_status import ActuatorStatus
from wolk_gateway_module.model.alarm import Alarm
from wolk_gateway_module.model.configuration_command import (
    ConfigurationCommand,
    ConfigurationCommandType,
)
from wolk_gateway_module.model.message import Message
from wolk_gateway_module.model.sensor_reading import SensorReading


class JsonDataProtocolTests(unittest.TestCase):
    """JsonDataProtocol Tests."""

    DEVICE_PATH_PREFIX = "d/"
    REFERENCE_PATH_PREFIX = "r/"
    CHANNEL_WILDCARD = "#"
    CHANNEL_DELIMITER = "/"
    SENSOR_READING = "d2p/sensor_reading/"
    ALARM = "d2p/events/"
    ACTUATOR_SET = "p2d/actuator_set/"
    ACTUATOR_GET = "p2d/actuator_get/"
    ACTUATOR_STATUS = "d2p/actuator_status/"
    CONFIGURATION_SET = "p2d/configuration_set/"
    CONFIGURATION_GET = "p2d/configuration_get/"
    CONFIGURATION_STATUS = "d2p/configuration_get/"

    def test_get_inbound_topics_for_device(self):
        """Test that returned list is correct."""
        json_data_protocol = JsonDataProtocol()
        device_key = "some_key"

        self.assertEqual(
            json_data_protocol.get_inbound_topics_for_device(device_key),
            [
                self.ACTUATOR_SET
                + self.DEVICE_PATH_PREFIX
                + device_key
                + self.CHANNEL_DELIMITER
                + self.REFERENCE_PATH_PREFIX
                + self.CHANNEL_WILDCARD,
                self.ACTUATOR_GET
                + self.DEVICE_PATH_PREFIX
                + device_key
                + self.CHANNEL_DELIMITER
                + self.REFERENCE_PATH_PREFIX
                + self.CHANNEL_WILDCARD,
                self.CONFIGURATION_SET + self.DEVICE_PATH_PREFIX + device_key,
                self.CONFIGURATION_GET + self.DEVICE_PATH_PREFIX + device_key,
            ],
        )

    def test_is_actuator_get_message(self):
        """Test that message is actuator_get message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(self.ACTUATOR_GET)

        self.assertTrue(json_data_protocol.is_actuator_get_message(message))

    def test_is_actuator_set_message(self):
        """Test that message is actuator_set message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(self.ACTUATOR_SET)

        self.assertTrue(json_data_protocol.is_actuator_set_message(message))

    def test_is_configuration_set_message(self):
        """Test that message is configuration_set message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(self.CONFIGURATION_SET)

        self.assertTrue(
            json_data_protocol.is_configuration_set_message(message)
        )

    def test_is_configuration_get_message(self):
        """Test that message is configuration_get message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(self.CONFIGURATION_GET)

        self.assertTrue(
            json_data_protocol.is_configuration_get_message(message)
        )

    def test_make_actuator_set_command(self):
        """Test deserializing of actuator_set message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(
            self.ACTUATOR_SET
            + self.DEVICE_PATH_PREFIX
            + "some_key"
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + "REF",
            '{"value": "test"}',
        )

        expected = ActuatorCommand("REF", ActuatorCommandType.SET, "test")

        deserialized = json_data_protocol.make_actuator_command(message)

        self.assertEqual(expected, deserialized)

    def test_make_actuator_get_command(self):
        """Test deserializing of actuator_get message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(
            self.ACTUATOR_GET
            + self.DEVICE_PATH_PREFIX
            + "some_key"
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + "REF"
        )

        expected = ActuatorCommand("REF", ActuatorCommandType.GET)

        deserialized = json_data_protocol.make_actuator_command(message)

        self.assertEqual(expected, deserialized)

    def test_make_configuration_set_message(self):
        """Test deserializing of configuration_set message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(
            self.CONFIGURATION_SET + self.DEVICE_PATH_PREFIX + "some_key",
            '{"config_1": "false"}',
        )

        expected = ConfigurationCommand(
            ConfigurationCommandType.SET, {"config_1": False}
        )

        deserialized = json_data_protocol.make_configuration_command(message)

        self.assertEqual(expected, deserialized)

    def test_make_configuration_large_data_size_set_message(self):
        """Test deserializing of configuration message with data size > 1."""
        json_data_protocol = JsonDataProtocol()

        message = Message(
            self.CONFIGURATION_SET + self.DEVICE_PATH_PREFIX + "some_key",
            '{"config_1": "2.3,3.4,4.4"}',
        )

        expected = ConfigurationCommand(
            ConfigurationCommandType.SET, {"config_1": (2.3, 3.4, 4.4)}
        )

        deserialized = json_data_protocol.make_configuration_command(message)

        self.assertEqual(expected, deserialized)

    def test_make_configuration_get_message(self):
        """Test deserializing of configuration_get message."""
        json_data_protocol = JsonDataProtocol()

        message = Message(
            self.CONFIGURATION_GET + self.DEVICE_PATH_PREFIX + "some_key"
        )

        expected = ConfigurationCommand(ConfigurationCommandType.GET)

        deserialized = json_data_protocol.make_configuration_command(message)

        self.assertEqual(expected, deserialized)

    def test_make_sensor_reading_message(self):
        """Test serializing of sensor reading for device key."""
        json_data_protocol = JsonDataProtocol()

        reading = SensorReading("REF", "value")

        expected = Message(
            self.SENSOR_READING
            + self.DEVICE_PATH_PREFIX
            + "some_key"
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + "REF",
            '{"data": "value"}',
        )

        serialized = json_data_protocol.make_sensor_reading_message(
            "some_key", reading
        )

        self.assertEqual(expected, serialized)

    def test_make_multi_sensor_reading_message(self):
        """Test serializing of tuple sensor reading for device key."""
        json_data_protocol = JsonDataProtocol()

        reading = SensorReading("REF", (1, 2, 3))

        expected = Message(
            self.SENSOR_READING
            + self.DEVICE_PATH_PREFIX
            + "some_key"
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + "REF",
            '{"data": "1,2,3"}',
        )

        serialized = json_data_protocol.make_sensor_reading_message(
            "some_key", reading
        )

        self.assertEqual(expected, serialized)

    def test_make_alarm_message(self):
        """Test serializing of alarm event for device key."""
        json_data_protocol = JsonDataProtocol()

        reading = Alarm("REF", True, 1557150524022)

        expected = Message(
            self.ALARM
            + self.DEVICE_PATH_PREFIX
            + "some_key"
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + "REF",
            '{"data": "true", "utc": 1557150524022}',
        )

        serialized = json_data_protocol.make_alarm_message("some_key", reading)

        self.assertEqual(expected, serialized)

    def test_make_actuator_status_message(self):
        """Test serializing of actuator status for device key."""
        json_data_protocol = JsonDataProtocol()

        device_key = "some_key"
        reference = "REF"
        actuator_status = ActuatorStatus(reference, ActuatorState.READY, 15)

        expected = Message(
            self.ACTUATOR_STATUS
            + self.DEVICE_PATH_PREFIX
            + device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + reference,
            json.dumps({"status": "READY", "value": "15"}),
        )

        serialized = json_data_protocol.make_actuator_status_message(
            device_key, actuator_status
        )

        self.assertEqual(expected, serialized)

    def test_make_multi_data_actuator_status_message(self):
        """Test serializing of tuple actuator status for device key."""
        json_data_protocol = JsonDataProtocol()

        device_key = "some_key"
        reference = "REF"
        actuator_status = ActuatorStatus(
            reference, ActuatorState.READY, (15, 12)
        )

        expected = Message(
            self.ACTUATOR_STATUS
            + self.DEVICE_PATH_PREFIX
            + device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + reference,
            json.dumps({"status": "READY", "value": "15,12"}),
        )

        serialized = json_data_protocol.make_actuator_status_message(
            device_key, actuator_status
        )

        self.assertEqual(expected, serialized)

    def test_make_configuration_message(self):
        """Test serializing of configuration message for device key."""
        json_data_protocol = JsonDataProtocol()

        device_key = "some_key"
        configuration = {
            "ref1": False,
            "ref2": 2,
            "ref3": 4.4,
            "ref4": ("a", "b"),
        }

        expected = Message(
            self.CONFIGURATION_STATUS + self.DEVICE_PATH_PREFIX + device_key,
            '{"values": {"ref1": "false", "ref2": "2",'
            + ' "ref3": "4.4", "ref4": "a,b"}}',
        )

        serialized = json_data_protocol.make_configuration_message(
            device_key, configuration
        )

        self.assertEqual(expected, serialized)


if __name__ == "__main__":
    unittest.main()
