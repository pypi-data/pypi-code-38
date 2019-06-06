# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from .call import call, call_async, call_sync

from .protobufs import main_pb2
from .units import Units
from .warnings import Warnings
from .axis_settings import AxisSettings
from .response import Response
from .measurement import Measurement

if TYPE_CHECKING:
    from .device import Device


class Axis:
    """
    Represents an axis of motion associated with a device.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that controls this axis.
        """
        return self._device

    @property
    def axis_number(self) -> int:
        """
        The axis number identifies the axis on the device.
        The first axis has the number one.
        """
        return self._axis_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this axis.
        """
        return self._settings

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this axis.
        """
        return self._warnings

    def __init__(self, device: 'Device', axis_number: int):
        self._device = device
        self._axis_number = axis_number
        self._settings = AxisSettings(self)
        self._warnings = Warnings(device, axis_number)

    def home(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        call("device/home", request)

    async def home_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Homes axis. Axis returns to its homing position.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceHomeRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        await call_async("device/home", request)

    def stop(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        call("device/stop", request)

    async def stop_async(
            self,
            wait_until_idle: bool = True
    ) -> None:
        """
        Stops ongoing axis movement. Decelerates until zero speed.

        Args:
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceStopRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.wait_until_idle = wait_until_idle
        await call_async("device/stop", request)

    def wait_until_idle(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.throw_error_on_fault = throw_error_on_fault
        call("device/wait_until_idle", request)

    async def wait_until_idle_async(
            self,
            throw_error_on_fault: bool = True
    ) -> None:
        """
        Waits until axis stops moving.

        Args:
            throw_error_on_fault: Determines whether to throw error when fault is observed.
        """
        request = main_pb2.DeviceWaitUntilIdleRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.throw_error_on_fault = throw_error_on_fault
        await call_async("device/wait_until_idle", request)

    def is_busy(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = main_pb2.DeviceIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.DeviceIsBusyResponse()
        call("device/is_busy", request, response)
        return response.is_busy

    async def is_busy_async(
            self
    ) -> bool:
        """
        Returns bool indicating whether the axis is executing a motion command.

        Returns:
            True if the axis is currently executing a motion command.
        """
        request = main_pb2.DeviceIsBusyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.DeviceIsBusyResponse()
        await call_async("device/is_busy", request, response)
        return response.is_busy

    def move_absolute(
            self,
            position: float,
            unit: Units = Units.Native,
            wait_until_idle: bool = True
    ) -> None:
        """
        Move axis to absolute position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        call("device/move", request)

    async def move_absolute_async(
            self,
            position: float,
            unit: Units = Units.Native,
            wait_until_idle: bool = True
    ) -> None:
        """
        Move axis to absolute position.

        Args:
            position: Absolute position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.ABS
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        await call_async("device/move", request)

    def move_relative(
            self,
            position: float,
            unit: Units = Units.Native,
            wait_until_idle: bool = True
    ) -> None:
        """
        Move axis to position relative to current position.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        call("device/move", request)

    async def move_relative_async(
            self,
            position: float,
            unit: Units = Units.Native,
            wait_until_idle: bool = True
    ) -> None:
        """
        Move axis to position relative to current position.

        Args:
            position: Relative position.
            unit: Units of position.
            wait_until_idle: Determines whether function should return after the movement is finished or just started.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.REL
        request.arg = position
        request.unit = unit.value
        request.wait_until_idle = wait_until_idle
        await call_async("device/move", request)

    def move_velocity(
            self,
            velocity: float,
            unit: Units = Units.Native
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        call("device/move", request)

    async def move_velocity_async(
            self,
            velocity: float,
            unit: Units = Units.Native
    ) -> None:
        """
        Begins to move axis at specified speed.

        Args:
            velocity: Movement velocity.
            unit: Units of velocity.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.type = main_pb2.DeviceMoveRequest.VEL
        request.arg = velocity
        request.unit = unit.value
        await call_async("device/move", request)

    def get_position(
            self,
            unit: Units = Units.Native
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.setting = "pos"
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        call("device/get_axis_setting", request, response)
        return response.value

    async def get_position_async(
            self,
            unit: Units = Units.Native
    ) -> float:
        """
        Returns current axis position.

        Args:
            unit: Units of position.

        Returns:
            Axis position.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.setting = "pos"
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        await call_async("device/get_axis_setting", request, response)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            check_errors: bool = True
    ) -> Response:
        """
        Sends a generic ASCII command to this axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_multi_response(
            self,
            command: str,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            check_errors: bool = True
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this axis and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
            check_errors: Controls whether to throw exception when device rejects the command.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        request.check_errors = check_errors
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(resp) for resp in response.responses]

    def generic_command_no_response(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this axis without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command to send.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command = command
        await call_async("interface/generic_command_no_response", request)

    def prepare_command(
            self,
            command_template: str,
            *parameters: Measurement
    ) -> str:
        """
        Formats parameters into a command and performs unit conversions.
        Parameters in the command template are denoted by a question mark.
        Command returned is only valid for this axis and this device.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command_template: Template of a command to prepare. Parameters are denoted by question marks.
            parameters: Variable number of command parameters.

        Returns:
            Command with converted parameters.
        """
        request = main_pb2.PrepareCommandRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        request.command_template = command_template
        request.parameters.extend([Measurement.to_protobuf(p) for p in parameters])
        response = main_pb2.PrepareCommandResponse()
        call_sync("device/prepare_command", request, response)
        return response.command

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axis.

        Returns:
            A string that represents the axis.
        """
        request = main_pb2.ToStringRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = self.axis_number
        response = main_pb2.ToStringResponse()
        call_sync("device/axis_to_string", request, response)
        return response.to_str
