# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List, Any, Callable
from rx.subjects import ReplaySubject  # type: ignore
from rx.core import ObservableBase  # type: ignore

from .call import call, call_async, call_sync
from .motion_lib_exception import MotionLibException
from .events import events

from .device import Device
from .response import Response
from .unknown_response_event import UnknownResponseEvent
from .alert_event import AlertEvent
from .protobufs import main_pb2


class Connection:
    """
    Class representing access to particular connection (serial port, TCP connection).
    """

    @property
    def unknown_response(self) -> ObservableBase:
        """
        Event invoked when a response from a device cannot be matched to any known request.
        """
        return self._unknown_response

    @property
    def alert(self) -> ObservableBase:
        """
        Event invoked when an alert is received from a device.
        """
        return self._alert

    @property
    def disconnected(self) -> ObservableBase:
        """
        Event invoked when connection is interrupted or closed.
        """
        return self._disconnected

    @property
    def interface_id(self) -> int:
        """
        The interface ID identifies this Connection instance with the underlying library.
        """
        return self._interface_id

    def __init__(self, interface_id: int):
        self._interface_id = interface_id
        self.__setup_events()

    @staticmethod
    def open_serial_port(
            port_name: str,
            baud_rate: int = 0
    ) -> 'Connection':
        """
        Opens a serial port.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 115200).

        Returns:
            An object representing the port.
        """
        request = main_pb2.OpenInterfaceRequest()
        request.interface_type = main_pb2.OpenInterfaceRequest.SERIAL_PORT
        request.port_name = port_name
        request.baud_rate = baud_rate
        response = main_pb2.OpenInterfaceResponse()
        call("interface/open", request, response)
        return Connection(response.interface_id)

    @staticmethod
    async def open_serial_port_async(
            port_name: str,
            baud_rate: int = 0
    ) -> 'Connection':
        """
        Opens a serial port.

        Args:
            port_name: Name of the port to open.
            baud_rate: Optional baud rate (defaults to 115200).

        Returns:
            An object representing the port.
        """
        request = main_pb2.OpenInterfaceRequest()
        request.interface_type = main_pb2.OpenInterfaceRequest.SERIAL_PORT
        request.port_name = port_name
        request.baud_rate = baud_rate
        response = main_pb2.OpenInterfaceResponse()
        await call_async("interface/open", request, response)
        return Connection(response.interface_id)

    @staticmethod
    def open_tcp(
            host_name: str,
            port: int = 0
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 8657).

        Returns:
            An object representing the connection.
        """
        request = main_pb2.OpenInterfaceRequest()
        request.interface_type = main_pb2.OpenInterfaceRequest.TCP
        request.host_name = host_name
        request.port = port
        response = main_pb2.OpenInterfaceResponse()
        call("interface/open", request, response)
        return Connection(response.interface_id)

    @staticmethod
    async def open_tcp_async(
            host_name: str,
            port: int = 0
    ) -> 'Connection':
        """
        Opens a TCP connection.

        Args:
            host_name: Hostname or IP address.
            port: Optional port number (defaults to 8657).

        Returns:
            An object representing the connection.
        """
        request = main_pb2.OpenInterfaceRequest()
        request.interface_type = main_pb2.OpenInterfaceRequest.TCP
        request.host_name = host_name
        request.port = port
        response = main_pb2.OpenInterfaceResponse()
        await call_async("interface/open", request, response)
        return Connection(response.interface_id)

    def generic_command(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this port.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this port.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_no_response(
            self,
            command: str,
            device: int = 0,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this port without expecting a response and without adding a message ID.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str,
            device: int = 0,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this port without expecting a response and without adding a message ID.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        await call_async("interface/generic_command_no_response", request)

    def generic_command_multi_response(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this port and expect multiple responses,
        either from one device or from many devices.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            device: int = 0,
            axis: int = 0,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this port and expect multiple responses,
        either from one device or from many devices.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            device: Optional device address to send the command to.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.interface_id
        request.command = command
        request.device = device
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    def reset_ids(
            self
    ) -> None:
        """
        Resets ASCII protocol message IDs. Only for testing purposes.
        """
        request = main_pb2.ResetIdsRequest()
        request.interface_id = self.interface_id
        call_sync("interface/reset_ids", request)

    def close(
            self
    ) -> None:
        """
        Close the serial port.
        """
        request = main_pb2.CloseInterfaceRequest()
        request.interface_id = self.interface_id
        call("interface/close", request)

    async def close_async(
            self
    ) -> None:
        """
        Close the serial port.
        """
        request = main_pb2.CloseInterfaceRequest()
        request.interface_id = self.interface_id
        await call_async("interface/close", request)

    def device(
            self,
            device_address: int
    ) -> Device:
        """
        Gets Device class instance which allows you to control particular device on this connection.

        Args:
            device_address: Address of device intended to control. Address is configured for each device.

        Returns:
            Device instance.
        """
        if device_address <= 0:
            raise ValueError('Invalid value, physical devices are numbered from 1.')

        return Device(self, device_address)

    def renumber_devices(
            self,
            first_address: int = 1
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, devices need to be identified again.

        Args:
            first_address: This is the address that the device closest to the computer is given.
                Remaining devices are numbered consecutively.

        Returns:
            Total number of devices that responded to the renumber.
        """
        if first_address <= 0:
            raise ValueError('Invalid value, device addresses are numbered from 1.')

        request = main_pb2.DeviceRenumberRequest()
        request.interface_id = self.interface_id
        request.first_address = first_address
        response = main_pb2.DeviceRenumberResponse()
        call("device/renumber", request, response)
        return response.number_devices

    async def renumber_devices_async(
            self,
            first_address: int = 1
    ) -> int:
        """
        Renumbers devices present on this connection. After renumbering, devices need to be identified again.

        Args:
            first_address: This is the address that the device closest to the computer is given.
                Remaining devices are numbered consecutively.

        Returns:
            Total number of devices that responded to the renumber.
        """
        if first_address <= 0:
            raise ValueError('Invalid value, device addresses are numbered from 1.')

        request = main_pb2.DeviceRenumberRequest()
        request.interface_id = self.interface_id
        request.first_address = first_address
        response = main_pb2.DeviceRenumberResponse()
        await call_async("device/renumber", request, response)
        return response.number_devices

    def detect_devices(
            self,
            identify_devices: bool = True
    ) -> List[Device]:
        """
        Attempts to detect any devices present on this connection.

        Args:
            identify_devices: Determines whether device identification should be performed as well.

        Returns:
            Array of detected devices.
        """
        request = main_pb2.DeviceDetectRequest()
        request.interface_id = self.interface_id
        request.identify_devices = identify_devices
        response = main_pb2.DeviceDetectResponse()
        call("device/detect", request, response)
        return list(map(self.device, response.devices))

    async def detect_devices_async(
            self,
            identify_devices: bool = True
    ) -> List[Device]:
        """
        Attempts to detect any devices present on this connection.

        Args:
            identify_devices: Determines whether device identification should be performed as well.

        Returns:
            Array of detected devices.
        """
        request = main_pb2.DeviceDetectRequest()
        request.interface_id = self.interface_id
        request.identify_devices = identify_devices
        response = main_pb2.DeviceDetectResponse()
        await call_async("device/detect", request, response)
        return list(map(self.device, response.devices))

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the connection.

        Returns:
            A string that represents the connection.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.interface_id
        response = main_pb2.ToStringResponse()
        call_sync("interface/to_string", request, response)
        return response.to_str

    def __enter__(self) -> 'Connection':
        """ __enter__ """
        return self

    def __exit__(self, _type: Any, _value: Any, _traceback: Any) -> None:
        """ __exit__ """
        self.close()

    def __filter_event(self, event_name: str) -> Callable[[Any], bool]:
        def filter_event(event: Any) -> bool:
            return event[0] == event_name and event[1].interface_id == self._interface_id  # type: ignore
        return filter_event

    def __setup_events(self) -> None:
        self._disconnected = ReplaySubject()  # terminates all the events

        self._unknown_response = events.take_until(self.disconnected)\
            .filter(self.__filter_event('interface/unknown_response'))\
            .map(lambda ev: UnknownResponseEvent.from_protobuf(ev[1]))\

        self._alert = events.take_until(self.disconnected)\
            .filter(self.__filter_event('interface/alert'))\
            .map(lambda ev: AlertEvent.from_protobuf(ev[1]))\

        events.filter(self.__filter_event('interface/disconnected'))\
            .take(1)\
            .map(lambda ev: MotionLibException(ev[1].error_type, ev[1].error_message))\
            .subscribe(self.disconnected)
