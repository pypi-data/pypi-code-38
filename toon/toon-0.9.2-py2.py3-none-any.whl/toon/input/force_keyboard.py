from ctypes import c_double

import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader

from toon.input.base_input import BaseInput


class ForceKeyboard(BaseInput):
    """1-DoF force transducers."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 200)

    @staticmethod
    def data_shapes(**kwargs):
        return [[10]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double]

    def __init__(self, **kwargs):
        super(ForceKeyboard, self).__init__(**kwargs)
        self.sampling_frequency = ForceKeyboard.samp_freq(**kwargs)
        self.period = 1/self.sampling_frequency
        self.t1 = 0
        self._data_buffer = np.full(ForceKeyboard.data_shapes(**kwargs)[0], np.nan)

    def __enter__(self):
        # assume first NI DAQ is the one we want
        self._device_name = nidaqmx.system.System.local().devices[0].name
        self._channels = [self._device_name + '/ai' + str(n) for n in
                          [2, 9, 1, 8, 0, 10, 3, 11, 4, 12]]
        self._device = nidaqmx.Task()
        self._device.ai_channels.add_ai_voltage_chan(
            ','.join(self._channels),
            terminal_config=TerminalConfiguration.RSE
        )
        self._reader = AnalogMultiChannelReader(self._device.in_stream)
        self._device.start()
        return self

    def read(self):
        self._reader.read_one_sample(self._data_buffer)
        time = self.clock()
        while self.clock() < self.t1:
            pass
        self.t1 = self.clock() + self.period
        return time, self._data_buffer

    def __exit__(self, *args):
        self._device.stop()
        self._device.close()
