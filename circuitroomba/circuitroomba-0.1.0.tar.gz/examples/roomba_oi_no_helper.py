# The MIT License (MIT)
#
# Copyright (c) 2019 Alexander Hagerman for Alexander Hagerman
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
`circuitroomba`
================================================================================

CircuitPython helper library for interfacing with Roomba Open Interface devices.


* Author(s): Alexander Hagerman

**Hardware:**

* Adafruit Circuit Playground Express

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

import board
import digitalio
import busio
import time

__repo__ = "https://github.com/AlexanderHagerman/circuitroomba.git"

start = b"\x80"
clean = b"\x87"
stop = b"\xAD"
power = b"\x85"
safe_mode = b"\x83"
full_mode = b"\x84"

start_codes = [start, safe_mode, clean]
stop_codes = [power, stop]

brc = digitalio.DigitalInOut(board.A1)
brc.direction = digitalio.Direction.OUTPUT
uart = busio.UART(board.TX, board.RX, baudrate=115200)

c = 0


def wake_up(brc):
    brc.value = False
    time.sleep(0.5)
    brc.value = True
    time.sleep(0.5)
    brc.value = False
    time.sleep(0.5)


for i in range(3):
    wake_up(brc)

while True:
    for code in start_codes:
        uart.write(code)
        print(code)

    time.sleep(2)

    for code in stop_codes:
        uart.write(code)
        print(code)

    c += 1

    print(brc)
    print(c)

    wake_up(brc)

    if c == 2:
        break
