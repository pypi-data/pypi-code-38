import struct

import crcmod


class VrcT70Response(object):
    def __init__(self, other=None):

        if other:
            self._assign_from_other(other)
            return

        self.address = None
        self.id_event = None
        self.sequence_id = None
        self.processing_result = None
        self.data = None
        self.crc = None

        self._crc_func = None

    def is_crc_valid(self):
        if self._crc_func is None:
            self._crc_func = crcmod.mkCrcFun(poly=0x1D5, initCrc=0, rev=False, xorOut=0)

        data_length = len(self.data) if self.data else 0

        data = bytearray([
            self.address & 0xff,
            self.id_event & 0xff,
            (self.sequence_id & 0xff00) >> 8,
            self.sequence_id & 0xff,
            self.processing_result & 0xff,
            data_length & 0xff
        ]
        )

        if self.data:
            data.extend(self.data)

        data.append(self.crc)

        return self._crc_func(data) == 0x00

    def _assign_from_other(self, other):
        d = other.__dict__

        for k, v in d.items():
            setattr(self, k, v)


class TrunkSensortsCountResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def trunk_number(self):
        return self.data[0]

    def sensors_count(self):
        return self.data[1]


class TemperatureOnSensorResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def trunk_number(self):
        return self.data[0]

    def sensor_index(self):
        return self.data[1]

    def is_connected(self):
        return self.data[2] == 1

    def temperature(self):
        res, = struct.unpack("<f", self.data[3:])
        return res


class SensorUniqueIdResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def trunk_number(self):
        return self.data[0]

    def sensor_index(self):
        return self.data[1]

    def unique_address(self):
        return self.data[2:]


class TemperatureOnTrunkResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def trunk_number(self):
        return self.data[0]

    def temperatures_count(self):
        return (len(self.data) - 1) // 5

    def is_connected(self, sensor_index):
        return self.data[1 + sensor_index * (1 + 4)] == 1

    def temperature(self, sensor_index):
        offset = 1 + sensor_index * (1 + 4) + 1
        res, = struct.unpack("<f", self.data[offset: offset + 4])
        return res


class SensorUniqueAddressOnTrunkResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def trunk_number(self):
        return self.data[0]

    def sensors_count(self):
        return (len(self.data) - 1) // 9

    def is_error_detected(self, sensor_index):
        offset = 1 + sensor_index * (8 + 1) + 8
        return self.data[offset] == 1

    def sensor_unique_address(self, sensor_index):
        offset = 1 + sensor_index * (8 + 1)
        return self.data[offset: offset + 8]


class SessionIdResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def session_id(self):
        return self.data


class ControllerNewAddressResponse(VrcT70Response):
    def __init__(self, data):
        super().__init__(data)

    def new_address(self):
        return self.data[0]
