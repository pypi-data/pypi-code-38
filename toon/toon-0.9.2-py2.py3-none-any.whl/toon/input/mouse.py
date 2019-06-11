from ctypes import c_int32
from toon.input.base_input import BaseInput
from pynput import mouse
import numpy as np


class Mouse(BaseInput):
    """Mouse interface."""
    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 100)

    @staticmethod
    def data_shapes(**kwargs):
        return [[2]]

    @staticmethod
    def data_types(**kwargs):
        return [c_int32]

    def __init__(self, **kwargs):
        super(Mouse, self).__init__(**kwargs)

    def __enter__(self):
        self.dev = mouse.Listener(on_move=self.on_move)
        self.dev.start()
        self.dev.wait()
        self.times = []
        self.readings = []
        self.x_prev = 0
        self.y_prev = 0
        return self

    def __exit__(self, *args):
        self.dev.stop()
        self.dev.join()

    def on_move(self, x, y):
        self.times.append(self.clock())
        self.readings.append(np.array([x - self.x_prev, y - self.y_prev]))
        self.x_prev = x
        self.y_prev = y

    def read(self):
        """Returns the *change* in mouse position, not the absolute position."""
        if not self.readings:
            return None, None
        time2 = []
        read2 = []
        time2[:] = self.times
        read2[:] = self.readings
        self.readings = []
        return time2[-1], read2[-1]  # hack until multi-datapoint
