# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING
from .call import call, call_async

from .protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class DeviceSettings:
    """
    Class providing access to various device settings and properties.
    """

    def __init__(self, device: 'Device'):
        self._device = device

    def get(
            self,
            setting: str
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting
        response = main_pb2.DeviceGetSettingResponse()
        call("device/get_device_setting", request, response)
        return response.value

    async def get_async(
            self,
            setting: str
    ) -> float:
        """
        Returns any device setting or property.

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting
        response = main_pb2.DeviceGetSettingResponse()
        await call_async("device/get_device_setting", request, response)
        return response.value

    def set(
            self,
            setting: str,
            value: float
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting
        request.value = value
        call("device/set_device_setting", request)

    async def set_async(
            self,
            setting: str,
            value: float
    ) -> None:
        """
        Sets any device setting.

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.setting = setting
        request.value = value
        await call_async("device/set_device_setting", request)
