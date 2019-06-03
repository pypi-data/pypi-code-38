"""Tests for Wolk."""
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

import sys
import unittest

sys.path.append("..")  # noqa

from wolk_gateway_module.connectivity.connectivity_service import (
    ConnectivityService,
)
from wolk_gateway_module.wolk import Wolk
from wolk_gateway_module.model.actuator_state import ActuatorState
from wolk_gateway_module.model.device import Device
from wolk_gateway_module.model.device_template import DeviceTemplate
from wolk_gateway_module.model.message import Message
from wolk_gateway_module.model.device_status import DeviceStatus
from wolk_gateway_module.interface.firmware_handler import FirmwareHandler
from wolk_gateway_module.model.firmware_update_status import (
    FirmwareUpdateStatus,
    FirmwareUpdateState,
)
from wolk_gateway_module.model.sensor_template import SensorTemplate
from wolk_gateway_module.model.data_type import DataType

from wolk_gateway_module.logger_factory import logging_config

logging_config("notset")


class MockConnectivityService(ConnectivityService):

    _connected = False
    _topics = []

    def set_inbound_message_listener(self, on_inbound_message):
        pass

    def set_lastwill_message(self, message):
        self._lastwill = message

    def add_subscription_topics(self, topics):
        self._topics.extend(topics)

    def remove_topics_for_device(self, device_key):
        pass

    def connected(self):
        return self._connected

    def connect(self):
        return self._connected

    def reconnect(self):
        return self._connected

    def disconnect(self):
        pass

    def publish(self, message):
        return self._connected


actuator_1 = False
actuator_2 = 0
actuator_3 = "default"


def mock_actuator_handler(device_key, reference, value):
    if device_key == "key1":
        if reference == "REF1":
            global actuator_1
            actuator_1 = value
        elif reference == "REF2":
            global actuator_2
            actuator_2 = value
    elif device_key == "key2":
        if reference == "REF3":
            global actuator_3
            actuator_3 = value


def mock_actuator_status_provider(device_key, reference):
    if device_key == "key1":
        if reference == "REF1":
            global actuator_1
            return ActuatorState.READY, actuator_1
        elif reference == "REF2":
            global actuator_2
            return ActuatorState.READY, actuator_2
    elif device_key == "key2":
        if reference == "REF3":
            global actuator_3
            return ActuatorState.READY, actuator_3


configuration_1 = False
configuration_2 = 3.14
configuration_3 = ("string1", "string2")


def mock_configuration_provider(device_key):
    if device_key == "key1":
        global configuration_1
        global configuration_2
        return {
            "configuration_1": configuration_1,
            "configuration_2": configuration_2,
        }
    elif device_key == "key2":
        global configuration_3
        return {"configuration_3": configuration_3}


def mock_configuration_handler(device_key, configuration):
    if device_key == "key1":
        global configuration_1
        global configuration_2
        for key, value in configuration.items():
            if key == "configuration_1":
                configuration_1 = value
            elif key == "configuration_2":
                configuration_2 = value
    elif device_key == "key2":
        global configuration_3
        for key, value in configuration.items():
            if key == "configuration_3":
                configuration_3 = value


class MockFirmwareHandler(FirmwareHandler):
    def install_firmware(
        self, device_key: str, firmware_file_path: str
    ) -> None:
        """
        Handle the installation of the firmware file.

        Call `self.on_install_success(device_key)` to report success.
        Reporting success will also get new firmware version.

        If installation fails, call `self.on_install_fail(device_key, status)`
        where:
        `status = FirmwareUpdateStatus(
            FirmwareUpdateState.ERROR,
            FirmwareUpdateErrorCode.INSTALLATION_FAILED
        )`
        or use other values from `FirmwareUpdateErrorCode` if they fit better.

        :param device_key: Device for which the firmware command is intended
        :type device_key: str
        :param firmware_file_path: Path where the firmware file is located
        :type firmware_file_path: str
        """
        if device_key == "key1":
            self.on_install_success(device_key)

    def abort_installation(self, device_key: str) -> None:
        """
        Attempt to abort the firmware installation process for device.

        Call `self.on_install_fail(device_key, status)` to report if
        the installation process was able to be aborted with
        `status = FirmwareUpdateStatus(FirmwareUpdateState.ABORTED)`
        If unable to stop the installation process, no action is required.

        :param device_key: Device for which to abort installation
        :type device_key: str
        """
        if device_key == "key1":
            status = FirmwareUpdateStatus(FirmwareUpdateState.ABORTED)
            self.on_install_fail(device_key, status)

    def get_firmware_version(self, device_key: str) -> str:
        """
        Return device's current firmware version.

        :param device_key: Device identifier
        :type device_key: str
        :returns: version
        :rtype: str
        """
        if device_key == "key1":
            return "v1.0"
        elif device_key == "key2":
            return "v0.1"


class WolkTests(unittest.TestCase):
    """Wolk Tests."""

    def test_bad_status_provider(self):
        """Test that exception is raised for bad device status provider."""
        with self.assertRaises(RuntimeError):
            wolk = Wolk(  # noqa
                "host", 1883, "module_name", lambda a, b: a * b
            )

    def test_add_sensor_reading(self):
        """Test adding a sensor reading to storage and then publish."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: a,
            connectivity_service=MockConnectivityService(),
        )
        wolk.add_sensor_reading("device_key", "REF", 13)
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_add_alarm(self):
        """Test adding a alarm event to storage and then publish."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: a,
            connectivity_service=MockConnectivityService(),
        )
        wolk.add_alarm("device_key", "REF", False)
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_publish_actuator(self):
        """Test publishing actuator status."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: a,
            connectivity_service=MockConnectivityService(),
            actuation_handler=mock_actuator_handler,
            acutator_status_provider=mock_actuator_status_provider,
        )
        wolk.publish_acutator_status("key1", "REF1")
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_receive_actuation(self):
        """Test receiving actuator set command."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
            actuation_handler=mock_actuator_handler,
            acutator_status_provider=mock_actuator_status_provider,
        )
        wolk.connectivity_service._connected = True
        message = Message("p2d/actuator_set/d/key1/r/REF2", '{"value": "3"}')
        wolk._on_inbound_message(message)

        global actuator_2
        self.assertEqual(3, actuator_2)

    def test_publish_configuration(self):
        """Test publishing configuration."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: a,
            connectivity_service=MockConnectivityService(),
            configuration_handler=mock_configuration_handler,
            configuration_provider=mock_configuration_provider,
        )
        wolk.publish_configuration("key1")
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_receive_configuration(self):
        """Test receiving configuration set command."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda a: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
            configuration_handler=mock_configuration_handler,
            configuration_provider=mock_configuration_provider,
        )
        wolk.connectivity_service._connected = True
        message = Message(
            "p2d/configuration_set/d/key1",
            '{"configuration_1": "true", "configuration_2": "4.2"}',
        )
        wolk._on_inbound_message(message)

        self.assertEqual(True, configuration_1)
        self.assertEqual(4.2, configuration_2)

        message = Message(
            "p2d/configuration_set/d/key2",
            '{"configuration_3": "newstring1,newstring2"}',
        )
        wolk._on_inbound_message(message)

        self.assertEqual(("newstring1", "newstring2"), configuration_3)

    def test_publish_device_status(self):
        """Test sending device status."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
        )
        wolk.publish_device_status("key1")
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_publish_device_status_explicit(self):
        """Test sending explicit device status."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
        )
        wolk.publish_device_status("key1", DeviceStatus.OFFLINE)
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())
        wolk.connectivity_service._connected = True
        wolk.publish()
        self.assertEqual(0, wolk.outbound_message_queue.queue_size())

    def test_on_status_request(self):
        """Test receiving device status request."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
        )
        message = Message("p2d/subdevice_status_request/d/key1")
        wolk._on_inbound_message(message)

        self.assertEqual(1, wolk.outbound_message_queue.queue_size())

    def test_firmware_update(self):
        """Test receiving firmware installation command."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
            firmware_handler=MockFirmwareHandler(),
        )

        message = Message(
            "p2d/firmware_update_install/d/key1", '{ "fileName": "some_path"}'
        )

        wolk._on_inbound_message(message)
        self.assertEqual(3, wolk.outbound_message_queue.queue_size())

    def test_firmware_abort(self):
        """Test receiving firmware abort command."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
            firmware_handler=MockFirmwareHandler(),
        )

        message = Message("p2d/firmware_update_abort/d/key1")

        wolk._on_inbound_message(message)
        self.assertEqual(1, wolk.outbound_message_queue.queue_size())

    def test_add_simple_device(self):
        """Test adding a simple device."""
        wolk = Wolk(
            "host",
            1883,
            "module_name",
            lambda device_key: DeviceStatus.CONNECTED,
            connectivity_service=MockConnectivityService(),
        )

        sensor1 = SensorTemplate("sensor1", "s1", DataType.NUMERIC)

        device_template = DeviceTemplate(sensors=[sensor1])

        device = Device("device1", "key1", device_template)

        wolk.add_device(device)

        self.assertEqual(1, wolk.outbound_message_queue.queue_size())


if __name__ == "__main__":
    unittest.main()
