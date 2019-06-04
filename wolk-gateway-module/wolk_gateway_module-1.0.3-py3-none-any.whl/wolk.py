"""This module contains the Wolk class that ties together the whole package."""
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

from inspect import signature
from reprlib import recursive_repr
from typing import Callable, Dict, Optional, Tuple, Union


from wolk_gateway_module.json_data_protocol import JsonDataProtocol
from wolk_gateway_module.json_firmware_update_protocol import (
    JsonFirmwareUpdateProtocol,
)
from wolk_gateway_module.json_registration_protocol import (
    JsonRegistrationProtocol,
)
from wolk_gateway_module.json_status_protocol import JsonStatusProtocol
from wolk_gateway_module.mqtt_connectivity_service import (
    MQTTConnectivityService,
)
from wolk_gateway_module.logger_factory import logger_factory
from wolk_gateway_module.outbound_message_deque import OutboundMessageDeque
from wolk_gateway_module.model.device import Device
from wolk_gateway_module.model.device_registration_request import (
    DeviceRegistrationRequest,
)
from wolk_gateway_module.model.device_status import DeviceStatus
from wolk_gateway_module.model.actuator_state import ActuatorState
from wolk_gateway_module.model.actuator_status import ActuatorStatus
from wolk_gateway_module.model.alarm import Alarm
from wolk_gateway_module.model.sensor_reading import SensorReading
from wolk_gateway_module.model.device_registration_response_result import (
    DeviceRegistrationResponseResult,
)
from wolk_gateway_module.model.firmware_update_status import (
    FirmwareUpdateStatus,
    FirmwareUpdateState,
    FirmwareUpdateErrorCode,
)

from wolk_gateway_module.protocol.data_protocol import DataProtocol
from wolk_gateway_module.protocol.firmware_update_protocol import (
    FirmwareUpdateProtocol,
)
from wolk_gateway_module.protocol.registration_protocol import (
    RegistrationProtocol,
)
from wolk_gateway_module.protocol.status_protocol import StatusProtocol
from wolk_gateway_module.persistence.outbound_message_queue import (
    OutboundMessageQueue,
)
from wolk_gateway_module.connectivity.connectivity_service import (
    ConnectivityService,
)
from wolk_gateway_module.model.message import Message
from wolk_gateway_module.interface.firmware_handler import FirmwareHandler


class Wolk:
    """This class is the core of this package, tying together all features.

    :ivar actuation_handler: Set new actuator values for your devices
    :vartype actuation_handler: Optional[Callable[[str, str,str], None]]
    :ivar acutator_status_provider: Get device's current actuator state
    :vartype acutator_status_provider: Optional[Callable[[str, str], Tuple[ActuatorState, Union[bool, int, float, str]]]]
    :ivar configuration_handler: Set new configuration values for your devices
    :vartype configuration_handler: Optional[Callable[[str, Dict[str, str]], None]]
    :ivar configuration_provider: Get device's current configuration options
    :vartype configuration_provider: Optional[Callable[[str],Dict[]]
    :ivar connectivity_service: Service that enables connection to WolkGateway
    :vartype connectivity_service: ConnectivityService
    :ivar data_protocol: Parse messages related to device data
    :vartype data_protocol: DataProtocol
    :ivar device_status_provider: Get device's current status
    :vartype device_status_provider: Callable[[str], DeviceStatus]
    :ivar devices: List of devices added to module
    :vartype devices: List[Device]
    :ivar firmware_handler: Handle commands related to firmware update
    :vartype firmware_handler: Optional[FirmwareHandler]
    :ivar firmware_update_protocol: Parse messages related to firmware update
    :vartype firmware_update_protocol: FirmwareUpdateProtocol
    :ivar host: WolkGateway's host address
    :vartype host: str
    :ivar log: Logger instance
    :vartype log: logging.Logger
    :ivar module_name: Name of module used for identification on WolkGateway
    :vartype module_name: str
    :ivar outbound_message_queue: Means of storing messages
    :vartype outbound_message_queue: OutboundMessageQueue
    :ivar port: WolkGateway's connectivity port
    :vartype port: int
    :ivar registration_protocol: Parse messages related to device registration
    :vartype registration_protocol: RegistrationProtocol
    :ivar status_protocol: Parse messages related to device status
    :vartype status_protocol: StatusProtocol
    """

    def __init__(
        self,
        host: str,
        port: int,
        module_name: str,
        device_status_provider: Callable[[str], DeviceStatus],
        actuation_handler: Optional[Callable[[str, str, str], None]] = None,
        acutator_status_provider: Optional[
            Callable[
                [str, str], Tuple[ActuatorState, Union[bool, int, float, str]]
            ]
        ] = None,
        configuration_handler: Optional[
            Callable[[str, Dict[str, str]], None]
        ] = None,
        configuration_provider: Optional[
            Callable[
                [str],
                Dict[
                    str,
                    Union[
                        int,
                        float,
                        bool,
                        str,
                        Tuple[int, int],
                        Tuple[int, int, int],
                        Tuple[float, float],
                        Tuple[float, float, float],
                        Tuple[str, str],
                        Tuple[str, str, str],
                    ],
                ],
            ]
        ] = None,
        firmware_handler: Optional[FirmwareHandler] = None,
        connectivity_service: Optional[ConnectivityService] = None,
        data_protocol: Optional[DataProtocol] = None,
        firmware_update_protocol: Optional[FirmwareUpdateProtocol] = None,
        registration_protocol: Optional[RegistrationProtocol] = None,
        status_protocol: Optional[StatusProtocol] = None,
        outbound_message_queue: Optional[OutboundMessageQueue] = None,
    ):
        """Construct an instance ready to communicate with WolkGateway.

        :param host: Host address of WolkGateway
        :type host: str
        :param port: TCP/IP port of WolkGateway
        :type port: int
        :param module_name: Module identifier used when connecting to gateway
        :type module_name: str
        :param device_status_provider: Provider of device's current status
        :type device_status_provider: Callable[[str], DeviceStatus]
        :param actuation_handler: Setter of new device actuator values
        :type actuation_handler: Optional[Callable[[str, str, str], None]]
        :param acutator_status_provider: Provider of device's current actuator status
        :type acutator_status_provider: Optional[Callable[[str, str], Tuple[ActuatorState, Union[bool, int, float, str]]]]
        :param configuration_handler: Setter of new device configuration values
        :type configuration_handler: Optional[Callable[[str, Dict[str, str]], None]]
        :param configuration_provider: Provider of device's configuration options
        :type configuration_provider: Optional[Callable[[str], Dict[str, Union[int, float, bool, str, Tuple[int, int], Tuple[int, int, int], Tuple[float, float], Tuple[float, float, float], Tuple[str, str], Tuple[str, str, str]]]]]
        :param install_firmware: Handling of firmware installation
        :type install_firmware: Optional[Callable[[str, str], None]]
        :param connectivity_service: Custom connectivity service implementation
        :type connectivity_service: Optional[ConnectivityService]
        :param data_protocol: Custom data protocol implementation
        :type data_protocol: Optional[DataProtocol]
        :param firmware_update_protocol: Custom firmware update protocol implementation
        :type firmware_update_protocol: Optional[FirmwareUpdateProtocol]
        :param registration_protocol: Custom registration protocol implementation
        :type registration_protocol: Optional[RegistrationProtocol]
        :param status_protocol: Custom device status protocol implementation
        :type status_protocol: Optional[StatusProtocol]
        :param outbound_message_queue: Custom persistent storage implementation
        :type outbound_message_queue: Optional[OutboundMessageQueue]
        """
        self.log = logger_factory.get_logger(str(self.__class__.__name__))

        self.host = host
        self.port = port
        self.module_name = module_name

        if not callable(device_status_provider):
            raise RuntimeError(f"{device_status_provider} is not a callable!")
        if len(signature(device_status_provider).parameters) != 1:
            raise RuntimeError(f"{device_status_provider} invalid signature!")
        self.device_status_provider = device_status_provider

        if actuation_handler is not None:
            if not callable(actuation_handler):
                raise RuntimeError(f"{actuation_handler} is not a callable!")
            if len(signature(actuation_handler).parameters) != 3:
                raise RuntimeError(f"{actuation_handler} invalid signature!")
            self.actuation_handler = actuation_handler
        else:
            self.actuation_handler = None

        if acutator_status_provider is not None:
            if not callable(acutator_status_provider):
                raise RuntimeError(
                    f"{acutator_status_provider} is not a callable!"
                )
            if len(signature(acutator_status_provider).parameters) != 2:
                raise RuntimeError(
                    f"{acutator_status_provider} invalid signature!"
                )
            self.acutator_status_provider = acutator_status_provider
        else:
            self.acutator_status_provider = None

        if (
            self.actuation_handler is None
            and self.acutator_status_provider is not None
        ) or (
            self.actuation_handler is not None
            and self.acutator_status_provider is None
        ):
            raise RuntimeError(
                "Provide actuation_handler and acutator_status_provider"
                " to enable actuators on your devices!"
            )

        if configuration_handler is not None:
            if not callable(configuration_handler):
                raise RuntimeError(
                    f"{configuration_handler} is not a callable!"
                )
            if len(signature(configuration_handler).parameters) != 2:
                raise RuntimeError(
                    f"{configuration_handler} invalid signature!"
                )
            self.configuration_handler = configuration_handler
        else:
            self.configuration_handler = None

        if configuration_provider is not None:
            if not callable(configuration_provider):
                raise RuntimeError(
                    f"{configuration_provider} is not a callable!"
                )
            if len(signature(configuration_provider).parameters) != 1:
                raise RuntimeError(
                    f"{configuration_provider} invalid signature!"
                )
            self.configuration_provider = configuration_provider
        else:
            self.configuration_provider = None

        if (
            self.configuration_handler is None
            and self.configuration_provider is not None
        ) or (
            self.configuration_handler is not None
            and self.configuration_provider is None
        ):
            raise RuntimeError(
                "Provide configuration_handler and configuration_provider"
                " to enable configuration options on your devices!"
            )

        if firmware_handler is not None:
            if not isinstance(firmware_handler, FirmwareHandler):
                raise RuntimeError(
                    f"{firmware_handler} isn't an instance of FirmwareHandler!"
                )
            self.firmware_handler = firmware_handler
            self.firmware_handler.on_install_success = self._on_install_success
            self.firmware_handler.on_install_fail = self._on_install_fail
        else:
            self.firmware_handler = None

        if data_protocol is not None:
            if not isinstance(data_protocol, DataProtocol):
                raise RuntimeError(
                    f"{data_protocol} is not a valid instance of DataProtocol!"
                )
            self.data_protocol = data_protocol
        else:
            self.data_protocol = JsonDataProtocol()

        if firmware_update_protocol is not None:
            if not isinstance(
                firmware_update_protocol, FirmwareUpdateProtocol
            ):
                raise RuntimeError(
                    f"{firmware_update_protocol} is not a valid instance of"
                    " FirmwareUpdateProtocol!"
                )
            self.firmware_update_protocol = firmware_update_protocol
        else:
            self.firmware_update_protocol = JsonFirmwareUpdateProtocol()

        if status_protocol is not None:
            if not isinstance(status_protocol, StatusProtocol):
                raise RuntimeError(
                    f"{status_protocol} is not a valid instance of "
                    "StatusProtocol!"
                )
            self.status_protocol = status_protocol
        else:
            self.status_protocol = JsonStatusProtocol()

        if registration_protocol is not None:
            if not isinstance(registration_protocol, RegistrationProtocol):
                raise RuntimeError(
                    f"{registration_protocol} is not a valid instance of "
                    "RegistrationProtocol!"
                )
            self.registration_protocol = registration_protocol
        else:
            self.registration_protocol = JsonRegistrationProtocol()

        if outbound_message_queue is not None:
            if not isinstance(outbound_message_queue, OutboundMessageQueue):
                raise RuntimeError(
                    f"{outbound_message_queue} is not a valid instance of "
                    "OutboundMessageQueue!"
                )
            self.outbound_message_queue = outbound_message_queue
        else:
            self.outbound_message_queue = OutboundMessageDeque()

        self.devices = []

        last_will_message = self.status_protocol.make_last_will_message(
            [device.key for device in self.devices]
        )

        if connectivity_service is not None:
            if not isinstance(connectivity_service, ConnectivityService):
                raise RuntimeError(
                    f"{connectivity_service} is not a valid instance of "
                    "ConnectivityService!"
                )
            self.connectivity_service = connectivity_service
        else:
            self.connectivity_service = MQTTConnectivityService(
                host, port, module_name, 0, last_will_message, []
            )

        self.connectivity_service.set_inbound_message_listener(
            self._on_inbound_message
        )

        self.log.debug(self.__repr__())

    @recursive_repr()
    def __repr__(self) -> str:
        """Make string representation or Wolk.

        :returns: representation
        :rtype: str
        """
        return (
            f"Wolk(host='{self.host}', "
            f"port='{self.port}', "
            f"module_name='{self.module_name}', "
            f"device_status_provider='{self.device_status_provider}', "
            f"actuation_handler='{self.actuation_handler}', "
            f"acutator_status_provider='{self.acutator_status_provider}', "
            f"configuration_handler='{self.configuration_handler}', "
            f"configuration_provider='{self.configuration_provider}', "
            f"firmware_handler='{self.firmware_handler}', "
            f"data_protocol='{self.data_protocol}', "
            f"firmware_update_protocol='{self.firmware_update_protocol}', "
            f"status_protocol='{self.status_protocol}', "
            f"registration_protocol='{self.registration_protocol}', "
            f"outbound_message_queue='{self.outbound_message_queue}', "
            f"connectivity_service='{self.connectivity_service}', "
            f"devices='{self.devices}')"
        )

    def _on_install_success(self, device_key: str) -> None:
        """Handle firmware installation message from firmware_handler.

        :param device_key: Device that completed firmware update
        :type device_key: str
        """
        self.log.info(
            f"Received firmware installation success for device '{device_key}'"
        )
        status = FirmwareUpdateStatus(FirmwareUpdateState.COMPLETED)
        message = self.firmware_update_protocol.make_update_message(
            device_key, status
        )
        if not self.connectivity_service.publish(message):
            if not self.outbound_message_queue.put(message):
                self.log.error(
                    "Failed to publish or store "
                    f"firmware version message {message}"
                )
                return
        version = self.firmware_handler.get_firmware_version(device_key)
        if not version:
            self.log.error(
                "Did not get firmware version for " f"device '{device_key}'"
            )
            return
        message = self.firmware_update_protocol.make_version_message(
            device_key, version
        )
        if not self.connectivity_service.publish(message):
            if not self.outbound_message_queue.put(message):
                self.log.error(
                    "Failed to publish or store "
                    f"firmware version message {message}"
                )

    def _on_install_fail(
        self, device_key: str, status: FirmwareUpdateStatus
    ) -> None:
        """Handle firmware installation failiure from firmware_handler.

        :param device_key: Device that reported firmware installation error
        :type device_key: str
        :param status: Firware update status information
        :type status: FirmwareUpdateStatus
        """
        self.log.info(
            "Received firmware installation status "
            f"message '{status}' for device '{device_key}'"
        )
        if not isinstance(status, FirmwareUpdateStatus):
            self.log.error(
                f"Received status {status} is not "
                "an instance of FirmwareUpdateStatus!"
            )
            return

        message = self.firmware_update_protocol.make_update_message(
            device_key, status
        )
        if not self.connectivity_service.publish(message):
            if not self.outbound_message_queue.put(message):
                self.log.error(
                    "Failed to publish or store "
                    f"firmware version message {message}"
                )

    def _on_inbound_message(self, message: Message) -> None:
        """Handle messages received from WolkGateway.

        :param message: Message received
        :type message: Message
        """
        self.log.debug(f"Received message: {message}")

        if self.data_protocol.is_actuator_set_message(message):

            if not (self.actuation_handler and self.acutator_status_provider):
                self.log.warning(
                    f"Received actuation message {message} , but no "
                    "actuation handler and actuator status provider present"
                )
                return

            self.log.info(f"Received actuator set command: {message}")
            device_key = self.data_protocol.extract_key_from_message(message)
            device_status = self.device_status_provider(device_key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{device_key}' returned '{device_status.value}' "
                    "status, not forwarding command"
                )
                self.publish_device_status(device_key)
                return

            command = self.data_protocol.make_actuator_command(message)
            self.actuation_handler(
                device_key, command.reference, command.value
            )
            try:
                self.publish_acutator_status(device_key, command.reference)
            except RuntimeError as e:
                self.log.error(
                    "Error occurred during handing"
                    f" inbound actuation message {message} : {e}"
                )

        elif self.data_protocol.is_actuator_get_message(message):

            if not (self.actuation_handler and self.acutator_status_provider):
                self.log.warning(
                    f"Received actuation message {message} , but no "
                    "actuation handler and actuator status provider present"
                )
                return

            self.log.info(f"Received actuator get command: {message}")
            device_key = self.data_protocol.extract_key_from_message(message)
            device_status = self.device_status_provider(device_key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{device_key}' returned '{device_status.value}' "
                    "status, not forwarding command"
                )
                self.publish_device_status(device_key)
                return

            command = self.data_protocol.make_actuator_command(message)
            try:
                self.publish_acutator_status(device_key, command.reference)
            except RuntimeError as e:
                self.log.error(
                    "Error occurred during handing "
                    f"inbound actuation message {message} : {e}"
                )

        elif self.data_protocol.is_configuration_set_message(message):

            if not (
                self.configuration_handler and self.configuration_provider
            ):
                self.log.warning(
                    f"Received configuration message {message} , but no "
                    "configuration handler and configuration provider present"
                )
                return

            self.log.info(f"Received configuration set command: {message}")
            device_key = self.data_protocol.extract_key_from_message(message)
            device_status = self.device_status_provider(device_key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{device_key}' returned '{device_status.value}' "
                    "status, not forwarding command"
                )
                self.publish_device_status(device_key)
                return

            command = self.data_protocol.make_configuration_command(message)
            self.configuration_handler(device_key, command.value)
            try:
                self.publish_configuration(device_key)
            except RuntimeError as e:
                self.log.error(
                    "Error occurred during handling "
                    f"inbound configuration message {message} : {e}"
                )
                return

        elif self.data_protocol.is_configuration_get_message(message):

            if not (
                self.configuration_handler and self.configuration_provider
            ):
                self.log.warning(
                    f"Received configuration message {message} , but no "
                    "configuration handler and configuration provider present"
                )
                return

            self.log.info(f"Received configuration get command: {message}")
            device_key = self.data_protocol.extract_key_from_message(message)
            device_status = self.device_status_provider(device_key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{device_key}' returned '{device_status.value}' "
                    "status, not forwarding command"
                )
                self.publish_device_status(device_key)
                return

            try:
                self.publish_configuration(device_key)
            except RuntimeError as e:
                self.log.error(
                    "Error occurred during handling "
                    f"inbound configuration message {message} : {e}"
                )
                return

        elif self.registration_protocol.is_registration_response_message(
            message
        ):

            response = self.registration_protocol.make_registration_response(
                message
            )
            if response.key not in [device.key for device in self.devices]:
                self.log.warning(
                    f"Received unexpected registration response: {message}"
                )
                return

            self.log.info(f"Received registration response: {response}")

            for device in self.devices:
                if device.key == response.key:
                    registered_device = device
                    break

            device_status = self.device_status_provider(registered_device.key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{registered_device.key}' returned "
                    f"'{device_status.value}' "
                    "status, not getting device data"
                )
                self.publish_device_status(device_key)
                return

            if registered_device.get_actuator_references():
                for actuator in registered_device.get_actuator_references():
                    try:
                        self.publish_acutator_status(
                            registered_device.key, actuator.reference
                        )
                    except RuntimeError as e:
                        self.log.error(
                            "Error occurred when sending actuator status "
                            f"for device {registered_device.key} with "
                            f"reference {actuator.reference} : {e}"
                        )

            if registered_device.has_configurations():
                try:
                    self.publish_configuration(registered_device.key)
                except RuntimeError as e:
                    self.log.error(
                        "Error occurred when sending configuration "
                        f"for device {registered_device.key} : {e}"
                    )

            if registered_device.supports_firmware_update():
                firmware_version = self.firmware_handler.get_firmware_version(
                    registered_device.key
                )
                if not firmware_version:
                    self.log.error(
                        "Did not get firmware version for "
                        f"device '{registered_device.key}'"
                    )
                    return

                message = self.firmware_update_protocol.make_version_message(
                    registered_device.key, firmware_version
                )
                if not self.connectivity_service.publish(message):
                    if not self.outbound_message_queue.put(message):
                        self.log.error(
                            "Failed to publish or store "
                            f"firmware version message {message}"
                        )

        elif self.status_protocol.is_device_status_request_message(message):

            self.log.info(f"Received device status request: {message}")
            device_key = self.status_protocol.extract_key_from_message(message)
            status = self.device_status_provider(device_key)
            if not status:
                self.log.error(
                    "Device status provider didn't return a "
                    f"status for device '{device_key}'"
                )
                return
            message = self.status_protocol.make_device_status_response_message(
                device_key, status
            )
            if not self.connectivity_service.publish(message):
                if not self.outbound_message_queue.put(message):
                    self.log.error(
                        "Failed to publish or store "
                        f"device status message {message}"
                    )

        elif self.firmware_update_protocol.is_firmware_install_command(
            message
        ):

            key = self.firmware_update_protocol.extract_key_from_message(
                message
            )
            device_status = self.device_status_provider(key)
            if device_status not in [
                DeviceStatus.CONNECTED,
                DeviceStatus.SLEEP,
            ]:
                self.log.warning(
                    f"Device '{key}' returned '{device_status.value}' "
                    "status, not forwarding command"
                )
                self.publish_device_status(key)
                return

            path = self.firmware_update_protocol.make_firmware_file_path(
                message
            )
            self.log.info(
                "Received firmware installation command "
                f"for device '{key}' with file path: {path}"
            )
            firmware_status = FirmwareUpdateStatus(
                FirmwareUpdateState.INSTALLATION
            )
            update_message = self.firmware_update_protocol.make_update_message(
                key, firmware_status
            )
            if not self.connectivity_service.publish(update_message):
                if not self.outbound_message_queue.put(update_message):
                    self.log.error(
                        "Failed to publish or store "
                        f"firmware update status message {update_message}"
                    )

            self.firmware_handler.install_firmware(key, path)

        elif self.firmware_update_protocol.is_firmware_abort_command(message):

            key = self.firmware_update_protocol.extract_key_from_message(
                message
            )
            self.log.info(
                "Received firmware installation abort command for device {key}"
            )
            self.firmware_handler.abort_installation(key)

    def add_sensor_reading(
        self,
        device_key: str,
        reference: str,
        value: Union[
            bool,
            int,
            float,
            str,
            Tuple[int, int],
            Tuple[int, int, int],
            Tuple[float, float],
            Tuple[float, float, float],
            Tuple[str, str],
            Tuple[str, str, str],
        ],
        timestamp: Optional[int] = None,
    ) -> None:
        """Serialize sensor reading and put into storage.

        Storing readings without Unix timestamp will result
        in all sent messages being treated as live readings and
        will be assigned a timestamp upon reception, so for a valid
        history add timestamps to readings via ``int(round(time.time() * 1000))``

        :param device_key: Device on which the sensor reading occurred
        :type device_key: str
        :param reference: Sensor reference (unique per device)
        :type reference: str
        :param value: Value(s) that the reading yielded
        :type value: Union[bool,int,float,str,Tuple[int, int],Tuple[int, int, int],Tuple[float, float],Tuple[float, float, float],Tuple[str, str],Tuple[str, str, str],]
        :param timestamp: Unix time
        :type timestamp: Optional[int]

        :raises RuntimeError: Unable to place in storage
        """
        self.log.debug(
            f"Add sensor reading: {device_key} , "
            f"{reference} , {value} , {timestamp}"
        )
        reading = SensorReading(reference, value, timestamp)
        message = self.data_protocol.make_sensor_reading_message(
            device_key, reading
        )
        if not self.outbound_message_queue.put(message):
            raise RuntimeError(f"Unable to store message: {message}")

    def add_alarm(
        self,
        device_key: str,
        reference: str,
        active: bool,
        timestamp: Optional[int] = None,
    ) -> None:
        """Serialize alarm event and put into storage.

        Storing alarms without Unix timestamp will result
        in all sent messages being treated as live and
        will be assigned a timestamp upon reception, so for a valid
        history add timestamps to alarms via ``int(round(time.time() * 1000))``

        :param device_key: Device on which the sensor reading occurred
        :type device_key: str
        :param reference: Alarm reference (unique per device)
        :type reference: str
        :param value: Current state of alarm
        :type active: bool
        :param timestamp: Unix time
        :type timestamp: Optional[int]

        :raises RuntimeError: Unable to place in storage
        """
        self.log.debug(
            f"Add alarm: {device_key} , {reference} , {active} , {timestamp}"
        )
        alarm = Alarm(reference, active, timestamp)
        message = self.data_protocol.make_alarm_message(device_key, alarm)
        if not self.outbound_message_queue.put(message):
            raise RuntimeError(f"Unable to store message: {message}")

    def publish_acutator_status(
        self,
        device_key: str,
        reference: str,
        state: Optional[ActuatorState] = None,
        value: Optional[Union[bool, int, float, str]] = None,
    ) -> None:
        """Publish device actuator status to WolkGateway.

        Getting the actuator status is achieved by calling the user's
        implementation of ``acutator_status_provider`` or optionally an
        actuator status can be published explicitly
        by providing ``ActuatorState`` as ``state`` parameter and the
        current actuator value via ``value`` parameter

        If message is unable to be sent, it will be placed in storage.

        If no ``acutator_status_provider`` is present, will raise exception.

        :param device_key: Device on which the sensor reading occurred
        :type device_key: str
        :param reference: Alarm reference (unique per device)
        :type reference: str
        :param state: Current actuator state for explicitly publishing status
        :type state: Optional[ActuatorState]
        :param value: Current actuator value for explicitly publishing status
        :type value: Optional[Union[bool, int, float, str]]

        :raises ValueError: Provided state is not an instance of ActuatorState
        :raises RuntimeError: Unable to place in storage or no status provider
        """
        self.log.debug(f"Publish actuator status: {device_key} , {reference}")
        if not (self.acutator_status_provider and self.actuation_handler):
            raise RuntimeError(
                "Unable to publish actuator status because "
                "acutator_status_provider and actuation_handler "
                "were not provided!"
            )
        if state is not None:
            if not isinstance(state, ActuatorState):
                raise ValueError(
                    f"{state} is not an instance of ActuatorState"
                )
            if state != ActuatorState.ERROR and value is None:
                raise ValueError(
                    f"Value must be provided for actuator state"
                    f" '{state.value}' !"
                )
        else:
            state, value = self.acutator_status_provider(device_key, reference)
            self.log.debug(
                f"Actuator status provider returned: {state} {value}"
            )

            if state is None:
                raise RuntimeError(
                    f"{self.acutator_status_provider} did not return anything"
                    f" for device '{device_key}' with reference '{reference}'"
                )

            if not isinstance(state, ActuatorState):
                raise RuntimeError(
                    f"{state} is not a member of ActuatorState!"
                )

        status = ActuatorStatus(reference, state, value)
        message = self.data_protocol.make_actuator_status_message(
            device_key, status
        )
        if self.connectivity_service.connected():
            if not self.connectivity_service.publish(message):
                if not self.outbound_message_queue.put(message):
                    raise RuntimeError(
                        f"Unable to publish and failed "
                        f"to store message: {message}"
                    )
        else:
            self.log.warning(
                "Not connected, unable to publish "
                f"actuator status message {message}"
            )
            if not self.outbound_message_queue.put(message):
                raise RuntimeError(f"Unable to store message: {message}")

    def publish_device_status(
        self, device_key: str, status: Optional[DeviceStatus] = None
    ) -> None:
        """Publish current device status to WolkGateway.

        Getting the current device status is achieved by calling the user's
        provided ``device_status_provider`` or a device status can be published
        explicitly by passing a ``DeviceStatus`` as the ``status`` parameter.

        :param device_key: Device to which the status belongs to
        :type device_key: str
        :param status: Current device status
        :type status: Optional[DeviceStatus]

        :raises ValueError: status is not of ``DeviceStatus``
        :raises RuntimeError: Failed to publish and store message
        """
        self.log.debug(f"Publish device status for {device_key}")

        if status is not None:
            if not isinstance(status, DeviceStatus):
                raise ValueError(
                    f"{status} is not an instance of DeviceStatus"
                )

        else:
            status = self.device_status_provider(device_key)
            if not isinstance(status, DeviceStatus):
                raise ValueError(
                    f"{status} is not an instance of DeviceStatus"
                )

        message = self.status_protocol.make_device_status_update_message(
            device_key, status
        )

        if self.connectivity_service.connected():
            if not self.connectivity_service.publish(message):
                if not self.outbound_message_queue.put(message):
                    raise RuntimeError(
                        f"Unable to publish and failed "
                        f"to store message: {message}"
                    )
        else:
            self.log.warning(
                "Not connected, unable to publish "
                f"device status message {message}"
            )
            if not self.outbound_message_queue.put(message):
                raise RuntimeError(f"Unable to store message: {message}")

    def publish_configuration(self, device_key: str) -> None:
        """Publish device configuration options to WolkGateway.

        If message is unable to be sent, it will be placed in storage.

        Getting the current configuration is achieved by calling the user's
        implementation of ``configuration_provider``.

        If no ``configuration_provider`` is present, will raise exception.

        :param device_key: Device to which the configuration belongs to
        :type device_key: str

        :raises RuntimeError: No configuration provider present or no data returned
        """
        self.log.debug(f"Publish configuration: {device_key}")
        if not (self.configuration_handler and self.configuration_provider):
            raise RuntimeError(
                "Unable to publish configuration because "
                "configuration_provider and configuration_handler "
                "were not provided!"
            )

        configuration = self.configuration_provider(device_key)

        self.log.debug(f"Configuration provider returned: {configuration}")

        if configuration is None:
            raise RuntimeError(
                f"{self.configuration_provider} did not return"
                f"anything for device '{device_key}'"
            )

        message = self.data_protocol.make_configuration_message(
            device_key, configuration
        )
        if self.connectivity_service.connected():
            if not self.connectivity_service.publish(message):
                if not self.outbound_message_queue.put(message):
                    raise RuntimeError(
                        f"Unable to publish and failed "
                        f"to store message: {message}"
                    )
        else:
            self.log.warning(
                "Not connected, unable to publish "
                f"configuration status message {message}"
            )
            if not self.outbound_message_queue.put(message):
                raise RuntimeError(f"Unable to store message: {message}")

    def add_device(self, device: Device) -> None:
        """
        Add device to module.

        Will attempt to send a registration request and
        update list of subscribed topics.

        :param device: Device to be added to module
        :type device: Device

        :raises RuntimeError: Unable to store message
        :raises ValueError: Invalid device given
        """
        self.log.debug(f"Add device: {device}")
        if not isinstance(device, Device):
            raise ValueError(
                "Given device is not an instance of Device class!"
            )
        if device.key in [device.key for device in self.devices]:
            self.log.error(f"Device with key '{device.key}' was already added")
            return

        if device.get_actuator_references():
            if not (self.actuation_handler and self.acutator_status_provider):
                self.log.error(
                    f"Can not add device '{device.key}' with actuators "
                    "without having an actuation handler and "
                    "actuator status provider"
                )
                return

        if device.has_configurations():
            if not (
                self.configuration_handler and self.configuration_provider
            ):
                self.log.error(
                    f"Can not add device '{device.key}' with "
                    "configuration options without having a "
                    "configuration handler and configuration provider"
                )
                return

        if device.supports_firmware_update():
            if not self.firmware_handler:
                self.log.error(
                    f"Can not add device '{device.key}' with "
                    "firmware update support without having a "
                    "firmware handler"
                )
                return

        self.devices.append(device)

        device_topics = []
        device_topics.extend(
            self.data_protocol.get_inbound_topics_for_device(device.key)
        )
        device_topics.extend(
            self.registration_protocol.get_inbound_topics_for_device(
                device.key
            )
        )
        device_topics.extend(
            self.firmware_update_protocol.get_inbound_topics_for_device(
                device.key
            )
        )
        device_topics.extend(
            self.status_protocol.get_inbound_topics_for_device(device.key)
        )

        self.connectivity_service.add_subscription_topics(device_topics)

        self.connectivity_service.set_lastwill_message(
            self.status_protocol.make_last_will_message(
                [device.key for device in self.devices]
            )
        )

        registration_request = DeviceRegistrationRequest(
            device.name, device.key, device.template
        )

        message = self.registration_protocol.make_registration_message(
            registration_request
        )

        if not self.connectivity_service.connected():
            if not self.outbound_message_queue.put(message):
                raise RuntimeError(f"Unable to store message: {message}")
        else:
            try:
                if not self.connectivity_service.reconnect():
                    self.log.error("Failed to reconnect")
            except RuntimeError as e:
                self.log.error(f"Failed to reconnect: {e}")
                if not self.outbound_message_queue.put(message):
                    raise RuntimeError(f"Unable to store message: {message}")
            if not self.connectivity_service.publish(message):
                if not self.outbound_message_queue.put(message):
                    raise RuntimeError(f"Unable to store message: {message}")

    def remove_device(self, device_key: str) -> None:
        """
        Remove device from module.

        Removes device for subscription topics and lastwill message.

        :param device_key: Device identifier
        :type device_key: str
        """
        self.log.debug(f"Removing device: {device_key}")
        if device_key not in [device.key for device in self.devices]:
            self.log.info(f"Device with key '{device_key}' was not stored")
            return

        for device in self.devices:
            if device_key == device.key:
                self.devices.remove(device)
                break

        self.connectivity_service.remove_topics_for_device(device_key)

        self.connectivity_service.set_lastwill_message(
            self.status_protocol.make_last_will_message(
                [device.key for device in self.devices]
            )
        )

        if self.connectivity_service.connected():
            try:
                self.connectivity_service.reconnect()
            except RuntimeError as e:
                self.log.error(f"Failed to reconnect: {e}")

    def publish(self, device_key: Optional[str] = None) -> None:
        """
        Publish stored messages to WolkGateway.

        If device_key parameter is provided, will publish messages only
        for that specific device.

        :param device_key: Device for which to publish stored messages
        :type device_key: Optional[str]
        """
        if device_key:
            self.log.debug(f"Publishing messages for {device_key}")
        else:
            self.log.debug("Publishing all stored messages")

        if self.outbound_message_queue.queue_size() == 0:
            self.log.info("No messages to publish")
            return

        if not self.connectivity_service.connected():
            self.log.warning("Not connected, unable to publish")
            return

        if device_key is None:
            while self.outbound_message_queue.queue_size() > 0:
                message = self.outbound_message_queue.get()
                if not self.connectivity_service.publish(message):
                    self.log.info.error(f"Failed to publish {message}")
                    return
                self.outbound_message_queue.remove(message)
        else:
            messages = self.outbound_message_queue.get_messages_for_device(
                device_key
            )
            if messages is None:
                self.log.warning(f"No messages stored for {device_key}")
                return
            for message in messages:
                if not self.connectivity_service.publish(message):
                    self.log.info.error(f"Failed to publish {message}")
                    return
                self.outbound_message_queue.remove(message)

    def connect(self):
        """Establish connection with WolkGateway.

        Will attempt to publish actuator statuses, configuration options,
        and current firmware version for all added devices.

        :raises RuntimeError: Error publishing actuator status or configuration
        """
        self.log.debug("Connecting to WolkGateway")
        if self.connectivity_service.connected():
            self.log.info("Already connected")
        else:
            try:
                if not self.connectivity_service.connect():
                    self.log.error("Failed to connect")
            except RuntimeError as e:
                self.log.error(f"Failed to connect: {e}")
                return

        if self.connectivity_service.connected():
            self.log.info("Connection to gateway established")
            for device in self.devices:
                try:
                    device_status = self.device_status_provider(device.key)
                    if device_status not in [
                        DeviceStatus.CONNECTED,
                        DeviceStatus.SLEEP,
                    ]:
                        self.log.warning(
                            f"Device '{device.key}' returned "
                            f"'{device_status.value}' "
                            "status, not getting device data"
                        )
                        self.publish_device_status(device.key)
                        continue

                    self.publish_device_status(device.key)

                except (ValueError, RuntimeError) as e:
                    raise e

                for reference in device.get_actuator_references():
                    try:
                        self.publish_acutator_status(device.key, reference)
                    except RuntimeError as e:
                        raise e

                if device.has_configurations():
                    try:
                        self.publish_configuration(device.key)
                    except RuntimeError as e:
                        raise e

                if device.supports_firmware_update():
                    version = self.firmware_handler.get_firmware_version(
                        device.key
                    )
                    if not version:
                        self.log.error(
                            "Did not get firmware version for "
                            f"device '{device.key}'"
                        )
                        continue
                    msg = self.firmware_update_protocol.make_version_message(
                        device.key, version
                    )
                    if not self.connectivity_service.publish(msg):
                        if not self.outbound_message_queue.put(msg):
                            raise RuntimeError(
                                "Failed to publish or store "
                                f"firmware version message {msg}"
                            )

    def disconnect(self):
        """Terminate connection with WolkGateway."""
        self.log.debug("Disconnecting from WolkGateway")
        if not self.connectivity_service.connected():
            self.log.debug("Not connected")
            return
        else:
            self.connectivity_service.disconnect()
