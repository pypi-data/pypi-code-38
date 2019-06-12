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
import time
from circuitroomba.series6 import roomba

__repo__ = "https://github.com/AlexanderHagerman/circuitroomba.git"

bot = roomba.Commands(board.TX, board.RX, digitalio.DigitalInOut(board.A1))

c = 0

bot.wake_up()

while True:
    bot.start()
    bot.safe()
    bot.clean()

    time.sleep(2)

    bot.power()
    bot.stop()

    c += 1

    print(c)

    bot.wake_up()

    if c == 2:
        break
