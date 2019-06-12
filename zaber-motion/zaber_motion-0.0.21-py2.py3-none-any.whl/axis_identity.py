# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from .protobufs import main_pb2
from .axis_type import AxisType


class AxisIdentity:
    """
    Representation of data gathered during axis identification.
    """

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """

        return self._peripheral_id

    @peripheral_id.setter
    def peripheral_id(self, value: int) -> None:
        self._peripheral_id = value

    @property
    def name(self) -> str:
        """
        Name of the peripheral.
        """

        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def is_peripheral(self) -> bool:
        """
        Determines whether the axis is a peripheral or part of an integrated device.
        """

        return self._is_peripheral

    @is_peripheral.setter
    def is_peripheral(self, value: bool) -> None:
        self._is_peripheral = value

    @property
    def axis_type(self) -> AxisType:
        """
        Determines the type of an axis and units it accepts.
        """

        return self._axis_type

    @axis_type.setter
    def axis_type(self, value: AxisType) -> None:
        self._axis_type = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(pb_data: main_pb2.AxisIdentity) -> 'AxisIdentity':
        instance = AxisIdentity()
        instance.peripheral_id = pb_data.peripheral_id
        instance.name = pb_data.name
        instance.is_peripheral = pb_data.is_peripheral
        instance.axis_type = AxisType(pb_data.axis_type)
        return instance
