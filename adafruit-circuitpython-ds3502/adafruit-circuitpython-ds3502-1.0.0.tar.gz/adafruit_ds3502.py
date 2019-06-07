# The MIT License (MIT)
#
# Copyright (c) 2019 Bryan Siepert for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_ds3502`
================================================================================

CircuitPython library for the Maxim DS3502 I2C Potentionmeter


* Author(s): Bryan Siepert

Implementation Notes
--------------------

**Hardware:**

* `Adafruit DS3502 <https://www.adafruit.com/products>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases



 * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
 * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_DS3502.git"



from time import sleep
from micropython import const
from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_bit import RWBit
import adafruit_bus_device.i2c_device as i2cdevice
# pylint: disable=bad-whitespace
_REG_WIPER        = const(0x00) # Wiper value register (R/W)
_REG_CONTROL      = const(0x02) # Configuration Register (R/W)

class DS3502:
    """Driver for the DS3502 I2C Potentiometer.

        :param ~busio.I2C i2c_bus: The I2C bus the INA260 is connected to.
        :param address: The I2C device address for the sensor. Default is ``0x40``.
    """

    def __init__(self, i2c_bus, address=0x28):
        self.i2c_device = i2cdevice.I2CDevice(i2c_bus, address)


        # set to mode 1 on init to not write to the IVR every time you set
        self._write_only_to_wiper = True

    _wiper = UnaryStruct(_REG_WIPER, ">B")
    _write_only_to_wiper =  RWBit(_REG_CONTROL, 7)

    @property
    def wiper(self):
        """The value of the potentionmeter's wiper.

            :param wiper_value: The value from 0-127 to set the wiper to.
        """
        return self._wiper

    @wiper.setter
    def wiper(self, value):
        if value < 0 or value >127:
            raise ValueError("wiper must be from 0-127")
        self._wiper = value

    def set_default(self, default):
        """Sets the wiper's default value and current value to the given value

            :param new_default: The value from 0-127 to set as the wiper's default.
        """
        self._write_only_to_wiper = False
        self.wiper = default
        sleep(0.1) # wait for write to eeprom to finish
        self._write_only_to_wiper = True
