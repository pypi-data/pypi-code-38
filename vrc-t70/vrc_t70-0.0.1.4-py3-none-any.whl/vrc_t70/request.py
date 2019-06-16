import crcmod


class VrcT70Request(object):
    def __init__(self, controller_address=None, command=None, sequence_id=0x0000, data=None):
        self.controller_address = controller_address
        self.command = command
        self.sequence_id = sequence_id
        self.data = data

        self._crc_func = None

    def to_bytearray(self):
        data_length = len(self.data) if self.data else 0

        res = bytearray(
            [
                self.controller_address & 0xff,
                self.command & 0xff,
                (self.sequence_id & 0xff00) >> 8,
                self.sequence_id & 0xff,
                data_length & 0xff
            ]
        )

        if self.data:
            res.extend(self.data)

        if self._crc_func is None:
            self._crc_func = crcmod.mkCrcFun(poly=0x1D5, initCrc=0, rev=False, xorOut=0)

        crc = self._crc_func(res)
        res.append(crc & 0xff)

        return res

    def __bytes__(self):
        return bytes(self.to_bytearray())

    def __len__(self):
        data_length = len(self.data) if self.data else 0
        # 1 byte - address, 1 byte - command, 2 bytes - sequence id, 1 byte - data length, N bytes data, 1 byte - crc8
        return 1 + 1 + 2 + 1 + data_length + 1
