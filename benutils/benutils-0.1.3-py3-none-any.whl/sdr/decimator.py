# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO Engineeering, 2019
license   GPL v3.0+
brief     Class Decimator.
details   Implements a decimator by D associates with an averager.
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import numpy as np


#==============================================================================
class Decimator(QObject):
    """Class Decimator, implements a decimator by D associates with an averager.
    """

    outUpdated = pyqtSignal((float,), (str,))
    inUpdated = pyqtSignal((float,), (str,))

    def __init__(self, d_factor=1, ini_value=0.0):
        """The constructor.
        :param d_factor: factor of decimation (int)
        :returns: None
        """
        super().__init__()
        self._ini_value = ini_value
        self.set_d(d_factor)
        self.reset()

    def reset(self):
        """Reset decimator.
        """
        self._csamp = 0 # Current SAMPling number
        self._data = np.full([self._d], self._ini_value, np.float64)
        self._idx = 0
        self._out = 0.0

    def set_ini(self, value):
        self._ini_value = value

    def get_ini(self):
        return self._ini_value

    def set_d(self, d_factor):
        """Sets decimation factor.
        :param d_factor: decimation factor (int)
        :returns: None
        """
        if d_factor < 1:
            raise AttributeError("decimation factor must be >= 1")
        self._data = np.full([d_factor], self._ini_value, np.float64)
        self._d = d_factor

    def get_d(self):
        """Gets decimation factor.
        :returns: decimation factor (int)
        """
        return self._d

    def _add_data(self, inp):
        """Add new data like an circular buffer do: 
        Use a fixed size array with an index pointing to current top.
        :param inp: new data input value (float)
        :returns: None
        """
        self._data[self._idx] = inp
        self._idx = (self._idx + 1) % self._d

    def _filtering(self):
        """Computes filtered response of data.
        :param data_array: array of data value (array of float)
        :returns: filtered data (float)
        """
        # Currently computes a simple mean
        return np.mean(self._data, dtype=np.float64)

    @pyqtSlot(float)
    @pyqtSlot(str)
    def process(self, inp):
        """Decimation process. Emits 'outUpdated' signal when data is ready
        for output.
        :param inp: data value (str, float)
        :returns: None
        """
        inp = float(inp)
        # Notify new computation
        self.inUpdated[float].emit(inp)
        self.inUpdated[str].emit('{:0.10E}'.format(inp))
        # Add new data
        self._add_data(inp)
        # Decimates data: emits signal every 'D' samples
        if self._csamp == (self._d - 1):
            self._out = self._filtering()
            self.outUpdated.emit(self._out)
            self.outUpdated[str].emit('{:0.10E}'.format(self._out))
        # Computes new index
        self._csamp = (self._csamp + 1) % self._d


#==============================================================================
if __name__ == '__main__':

    def print_dec_out(value):
        """Just print value to stdout.
        """
        print(value)

    DEC = Decimator(2)
    DEC.outUpdated[str].connect(print_dec_out)
    for val in range(1, 30):
        DEC.process(val)
