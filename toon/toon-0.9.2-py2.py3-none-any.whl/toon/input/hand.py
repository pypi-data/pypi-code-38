import struct
from ctypes import c_double

import hid
import numpy as np
from toon.input.base_input import BaseInput


class Hand(BaseInput):
    """Hand Articulation Neuro-Training Device (HAND)."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 1000)

    @staticmethod
    def data_shapes(**kwargs):
        return [[15]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, nonblocking=False, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self._sqrt2 = np.sqrt(2)
        self.nonblocking = nonblocking
        self._device = None
        self._data_buffer = np.full(15, np.nan)

    def __enter__(self):
        self._device = hid.device()
        dev_path = next((dev for dev in hid.enumerate()
                         if dev['vendor_id'] == 0x16c0 and dev['interface_number'] == 0), None)['path']
        self._device.open_path(dev_path)
        self._device.set_nonblocking(self.nonblocking)
        return self

    def __exit__(self, *args):
        self._device.close()

    def read(self):
        data = self._device.read(46)
        time = self.clock()
        if data:
            # Timestamp, deviation, and 20 unsigned ints
            data = struct.unpack('>Lh' + 'H'*20, bytearray(data))
            data = np.array(data, dtype='d')
            data[0] /= 1000.0
            data[2:] /= 65535.0
            self._data_buffer[0::3] = (data[2::4] - data[3::4])/self._sqrt2  # x
            self._data_buffer[1::3] = (data[2::4] + data[3::4])/self._sqrt2  # y
            self._data_buffer[2::3] = data[4::4] + data[5::4]  # z
            return time, self._data_buffer
