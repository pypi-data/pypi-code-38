from .base_communicator import VrcT70CommunicatorBase
from .commands import VrcT70Commands
from .request import VrcT70Request
from .response import (ControllerNewAddressResponse, SensorUniqueAddressOnTrunkResponse, SensorUniqueIdResponse,
                       SessionIdResponse, TemperatureOnSensorResponse, TemperatureOnTrunkResponse,
                       TrunkSensortsCountResponse)


class VrcT70Communicator(VrcT70CommunicatorBase):
    def __init__(self, serial, controller_address=0x01):
        super().__init__(serial, controller_address)

    def ping(self, sequence_id=0x0000):
        return self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.PING,
                sequence_id
            )
        )

    def rescan_sensors_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.RESCAN_SENSORS_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return TrunkSensortsCountResponse(res)

    def get_temperature_on_sensor_on_trunk(self, trunk_number, sensor_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_TEMPERATURE_OF_SENSOR_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff, sensor_index & 0xff])
            )
        )

        return TemperatureOnSensorResponse(res)

    def get_sensor_unique_address_on_trunk(self, trunk_number, sensor_index, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SENSOR_UNIQUE_ADDRESS_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff, sensor_index & 0xff])
            )
        )

        return SensorUniqueIdResponse(res)

    def get_temperature_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_TEMPERATURES_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return TemperatureOnTrunkResponse(res)

    def get_sensors_unique_addresses_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SENSORS_UNIQUE_ADDRESSES_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number & 0xff])
            )
        )

        return SensorUniqueAddressOnTrunkResponse(res)

    def get_session_id(self, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SESSION_ID,
                sequence_id
            )
        )

        return SessionIdResponse(res)

    def set_session_id(self, session_id, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.SET_SESSION_ID,
                sequence_id,
                session_id[0: 4]
            )
        )

        return SessionIdResponse(res)

    def get_sensors_count_on_trunk(self, trunk_number, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.GET_SENSORS_COUNT_ON_TRUNK,
                sequence_id,
                bytearray([trunk_number])
            )
        )

        return TrunkSensortsCountResponse(res)

    def set_new_controller_address(self, new_address, sequence_id=0x0000):
        res = self.send_command(
            VrcT70Request(
                self.controller_address,
                VrcT70Commands.SET_CONTROLLER_NEW_ADDRESS,
                sequence_id,
                bytearray([new_address])
            )
        )

        return ControllerNewAddressResponse(res)
