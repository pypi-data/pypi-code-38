# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, Optional, List
from .call import call, call_async, call_sync

from .protobufs import main_pb2
from .device_settings import DeviceSettings
from .axis import Axis
from .all_axes import AllAxes
from .warnings import Warnings
from .device_identity import DeviceIdentity
from .response import Response

if TYPE_CHECKING:
    from .connection import Connection


class Device:
    """
    Represents the controller part of one device - may be either a standalone controller or an integrated controller.
    """

    @property
    def connection(self) -> 'Connection':
        """
        Connection of this device.
        """
        return self._connection

    @property
    def device_address(self) -> int:
        """
        The device address uniquely identifies the device on the port.
        It can be configured or automatically assigned by the renumber command.
        """
        return self._device_address

    @property
    def settings(self) -> DeviceSettings:
        """
        Settings and properties of this device.
        """
        return self._settings

    @property
    def all_axes(self) -> AllAxes:
        """
        Virtual axis which allows you to target all axes of this device.
        """
        return self._all_axes

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this device and all its axes.
        """
        return self._warnings

    @property
    def identity(self) -> Optional[DeviceIdentity]:
        """
        Identity of the device.
        """
        return self.__retrieve_identity()

    def __init__(self, connection: 'Connection', device_address: int):
        self._connection = connection
        self._device_address = device_address
        self._settings = DeviceSettings(self)
        self._all_axes = AllAxes(self)
        self._warnings = Warnings(self, 0)

    def identify(
            self
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Returns:
            Device identification data.
        """
        request = main_pb2.DeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceIdentity()
        call("device/identify", request, response)
        return DeviceIdentity.from_protobuf(response)

    async def identify_async(
            self
    ) -> DeviceIdentity:
        """
        Queries the device and the database, gathering information about the product.
        Without this information features such as unit conversions will not work.
        Usually, called automatically by detect devices method.

        Returns:
            Device identification data.
        """
        request = main_pb2.DeviceIdentifyRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceIdentity()
        await call_async("device/identify", request, response)
        return DeviceIdentity.from_protobuf(response)

    def generic_command(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_multi_response(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            axis: int = 0,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this device and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    def generic_command_no_response(
            self,
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str,
            axis: int = 0
    ) -> None:
        """
        Sends a generic ASCII command to this device without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            axis: Optional axis number to send the command to.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        request.command = command
        request.axis = axis
        await call_async("interface/generic_command_no_response", request)

    def axis(
            self,
            axis_number: int
    ) -> Axis:
        """
        Gets Axis class instance which allows you to control particular axis on this device.

        Args:
            axis_number: Number of axis intended to control.

        Returns:
            Axis instance.
        """
        if axis_number <= 0:
            raise ValueError('Invalid value, physical axes are numbered from 1.')

        return Axis(self, axis_number)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.ToStringResponse()
        call_sync("device/device_to_string", request, response)
        return response.to_str

    def __retrieve_identity(
            self
    ) -> Optional[DeviceIdentity]:
        """
        Returns identity.

        Returns:
            Device identity.
        """
        request = main_pb2.DeviceGetIdentityRequest()
        request.interface_id = self.connection.interface_id
        request.device = self.device_address
        response = main_pb2.DeviceGetIdentityResponse()
        call_sync("device/get_identity", request, response)
        return DeviceIdentity.from_protobuf(response.identity) if response.identity is not None else None
