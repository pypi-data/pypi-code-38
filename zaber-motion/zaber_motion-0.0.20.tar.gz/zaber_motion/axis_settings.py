# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from .call import call, call_async

from .protobufs import main_pb2
from .units import Units

if TYPE_CHECKING:
    from .axis import Axis


class AxisSettings:
    """
    Class providing access to various axis settings and properties.
    """

    def __init__(self, axis: 'Axis'):
        self._axis = axis

    def get(
            self,
            setting: str,
            unit: Units = Units.Native
    ) -> float:
        """
        Returns any axis setting or property.

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        call("device/get_axis_setting", request, response)
        return response.value

    async def get_async(
            self,
            setting: str,
            unit: Units = Units.Native
    ) -> float:
        """
        Returns any axis setting or property.

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = unit.value
        response = main_pb2.DeviceGetSettingResponse()
        await call_async("device/get_axis_setting", request, response)
        return response.value

    def set(
            self,
            setting: str,
            value: float,
            unit: Units = Units.Native
    ) -> None:
        """
        Sets any axis setting.

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = unit.value
        call("device/set_axis_setting", request)

    async def set_async(
            self,
            setting: str,
            value: float,
            unit: Units = Units.Native
    ) -> None:
        """
        Sets any axis setting.

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = unit.value
        await call_async("device/set_axis_setting", request)
