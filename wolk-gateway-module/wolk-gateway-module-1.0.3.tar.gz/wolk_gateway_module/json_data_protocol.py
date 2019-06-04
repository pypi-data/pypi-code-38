"""Handling of outbound and inbound messages related to device data."""
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
from wolk_gateway_module.protocol.data_protocol import DataProtocol


class JsonDataProtocol(DataProtocol):
    """Parse inbound messages and serialize outbound messages."""

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

    def __init__(self) -> None:
        """Create object."""
        self.log = logger_factory.get_logger(str(self.__class__.__name__))

    def __repr__(self) -> str:
        """Make string representation of JsonDataProtocol.

        :returns: representation
        :rtype: str
        """
        return "JsonDataProtocol()"

    def get_inbound_topics_for_device(self, device_key: str) -> list:
        """Return list of inbound topics for given device key.

        :param device_key: Device key for which to create topics
        :type device_key: str

        :returns: inbound_topics
        :rtype: list
        """
        inbound_topics = [
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
        ]
        self.log.debug(f"Inbound topics for {device_key} : {inbound_topics}")

        return inbound_topics

    def is_actuator_get_message(self, message: Message) -> bool:
        """Check if message is actuator get command.

        :param message: Message received
        :type message: Message

        :returns: is_actuator_get_message
        :rtype: bool
        """
        is_actuator_get_message = message.topic.startswith(self.ACTUATOR_GET)
        self.log.debug(
            f"Is {message} actuator get message: {is_actuator_get_message}"
        )

        return is_actuator_get_message

    def is_actuator_set_message(self, message: Message) -> bool:
        """Check if message is actuator set command.

        :param message: Message received
        :type message: Message

        :returns: is_actuator_set_message
        :rtype: bool
        """
        is_actuator_set_message = message.topic.startswith(self.ACTUATOR_SET)
        self.log.debug(
            f"Is {message} actuator set message: {is_actuator_set_message}"
        )

        return is_actuator_set_message

    def is_configuration_get_message(self, message: Message) -> bool:
        """Check if message is configuration get command.

        :param message: Message received
        :type message: Message

        :returns: is_configuration_get_message
        :rtype: bool
        """
        is_configuration_get_message = message.topic.startswith(
            self.CONFIGURATION_GET
        )
        self.log.debug(
            f"Is {message} configuration get "
            f"message: {is_configuration_get_message}"
        )

        return is_configuration_get_message

    def is_configuration_set_message(self, message: Message) -> bool:
        """Check if message is configuration set command.

        :param message: Message received
        :type message: Message

        :returns: is_configuration_set_message
        :rtype: bool
        """
        is_configuration_set_message = message.topic.startswith(
            self.CONFIGURATION_SET
        )
        self.log.debug(
            f"Is {message} configuration set "
            f"message: {is_configuration_set_message}"
        )

        return is_configuration_set_message

    def extract_key_from_message(self, message: Message) -> str:
        """Extract device key from message.

        :param message: Message received
        :type message: Message

        :returns: device_key
        :rtype: str
        """
        if self.REFERENCE_PATH_PREFIX in message.topic:
            device_key = message.topic.split("/")[-3]
        else:
            device_key = message.topic.split("/")[-1]
        self.log.debug(f"Made {device_key} from {message}")

        return device_key

    def make_actuator_command(self, message: Message) -> ActuatorCommand:
        """Make actuator command from message.

        :param message: Message received
        :type message: Message

        :returns: actuator_command
        :rtype: ActuatorCommand
        """
        reference = message.topic.split("/")[-1]
        if self.is_actuator_set_message(message):
            command = ActuatorCommandType.SET
            payload = json.loads(message.payload)
            value = payload["value"]
            if "\n" in str(value):
                value = value.replace("\n", "\\n")
                value = value.replace("\r", "")

            if "true" == str(value):
                value = True
            elif "false" == str(value):
                value = False

            else:
                try:
                    if any("." in char for char in value):
                        value = float(value)
                    else:
                        value = int(value)
                except (ValueError, TypeError):
                    pass
        elif self.is_actuator_get_message(message):
            command = ActuatorCommandType.GET
            value = None

        actuator_command = ActuatorCommand(reference, command, value)
        self.log.debug(f"Made {actuator_command} from {message}")

        return actuator_command

    def make_configuration_command(
        self, message: Message
    ) -> ConfigurationCommand:
        """Make configuration command from message.

        :param message: Message received
        :type message: Message

        :returns: configuration_command
        :rtype: ConfigurationCommand
        """
        if self.is_configuration_set_message(message):
            command = ConfigurationCommandType.SET
            payload = json.loads(message.payload)
            for reference, value in payload.items():
                if "\n" in str(value):
                    value = value.replace("\n", "\\n")
                    value = value.replace("\r", "")

                if "true" == str(value):
                    payload[reference] = True
                elif "false" == str(value):
                    payload[reference] = False

                else:
                    try:
                        if any("." in char for char in value):
                            payload[reference] = float(value)
                        else:
                            payload[reference] = int(value)
                    except (ValueError, TypeError):
                        pass

                if isinstance(payload[reference], (int, float, bool)):
                    pass
                else:
                    if "," in value:
                        values_list = value.split(",")
                        try:
                            if any("." in value for value in values_list):
                                values_list = [
                                    float(value) for value in values_list
                                ]
                            else:
                                values_list = [
                                    int(value) for value in values_list
                                ]
                        except ValueError:
                            pass
                        payload[reference] = tuple(values_list)
                values = payload

        elif self.is_configuration_get_message(message):
            command = ConfigurationCommandType.GET
            values = None

        configuration_command = ConfigurationCommand(command, values)
        self.log.debug(f"Made {configuration_command} from {message}")

        return configuration_command

    def make_sensor_reading_message(
        self, device_key: str, sensor_reading: SensorReading
    ) -> Message:
        """Make message from sensor reading for device key.

        :param device_key: Device on which the sensor reading occurred
        :type device_key: str
        :param sensor_reading: Sensor reading data
        :type sensor_reading: SensorReading

        :returns: message
        :rtype: Message
        """
        topic = (
            self.SENSOR_READING
            + self.DEVICE_PATH_PREFIX
            + device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + sensor_reading.reference
        )

        if isinstance(sensor_reading.value, tuple):
            sensor_reading.value = ",".join(map(str, sensor_reading.value))
        elif isinstance(sensor_reading.value, bool):
            sensor_reading.value = str(sensor_reading.value).lower()

        if sensor_reading.timestamp is not None:
            payload = json.dumps(
                {
                    "data": str(sensor_reading.value),
                    "utc": int(sensor_reading.timestamp),
                }
            )
        else:
            payload = json.dumps({"data": str(sensor_reading.value)})

        message = Message(topic, payload)
        self.log.debug(
            f"Made {message} from {sensor_reading} and {device_key}"
        )

        return message

    def make_alarm_message(self, device_key: str, alarm: Alarm) -> Message:
        """Make message from alarm for device key.

        :param device_key: Device on which the alarm occurred
        :type device_key: str
        :param alarm: Alarm data
        :type alarm: Alarm

        :returns: message
        :rtype: Message
        """
        topic = (
            self.ALARM
            + self.DEVICE_PATH_PREFIX
            + device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + alarm.reference
        )

        if alarm.timestamp is not None:
            payload = json.dumps(
                {
                    "data": str(alarm.active).lower(),
                    "utc": int(alarm.timestamp),
                }
            )
        else:
            payload = json.dumps({"data": str(alarm.active).lower()})

        message = Message(topic, payload)
        self.log.debug(f"Made {message} from {alarm} and {device_key}")

        return message

    def make_actuator_status_message(
        self, device_key: str, actuator_status: ActuatorStatus
    ) -> Message:
        """Make message from actuator status for device key.

        :param device_key: Device on which the actuator status occurred
        :type device_key: str
        :param actuator_status: Actuator status data
        :type actuator_status: ActuatorStatus

        :returns: message
        :rtype: Message
        """
        topic = (
            self.ACTUATOR_STATUS
            + self.DEVICE_PATH_PREFIX
            + device_key
            + self.CHANNEL_DELIMITER
            + self.REFERENCE_PATH_PREFIX
            + actuator_status.reference
        )

        if isinstance(actuator_status.value, tuple):
            actuator_status.value = ",".join(map(str, actuator_status.value))
        elif isinstance(actuator_status.value, bool):
            actuator_status.value = str(actuator_status.value).lower()

        payload = json.dumps(
            {
                "status": actuator_status.state.value,
                "value": str(actuator_status.value),
            }
        )

        message = Message(topic, payload)
        self.log.debug(
            f"Made {message} from {actuator_status} and {device_key}"
        )

        return message

    def make_configuration_message(
        self, device_key: str, configuration: dict
    ) -> Message:
        """Make message from configuration for device key.

        :param device_key: Device to which the configuration belongs to.
        :type device_key: str
        :param configuration: Current configuration data
        :type configuration: dict

        :returns: message
        :rtype: Message
        """
        topic = (
            self.CONFIGURATION_STATUS + self.DEVICE_PATH_PREFIX + device_key
        )

        for reference, config_value in configuration.items():
            if isinstance(config_value, tuple):
                values_list = []
                for value in config_value:
                    if "\n" in str(value):
                        value = value.replace("\n", "\\n")
                        value = value.replace("\r", "")

                    if '"' in str(value):
                        value = value.replace('"', '\\"')

                    values_list.append(value)

                configuration[reference] = ",".join(map(str, values_list))
            else:
                if isinstance(config_value, bool):
                    config_value = str(config_value).lower()

                configuration[reference] = str(config_value)

        payload = json.dumps({"values": configuration})

        message = Message(topic, payload)
        self.log.debug(f"Made {message} from {configuration} and {device_key}")

        return message
