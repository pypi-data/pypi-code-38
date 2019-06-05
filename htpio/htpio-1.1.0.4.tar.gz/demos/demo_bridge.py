#!/usr/bin/env python

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import time
import platform

# Project imports
from htpio import bridge
from htpio import socketio
from htpio import telnetio
from htpio.exceptions import PinLockedByOtherProcess


"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   Relay 01 : Control by using telnet
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

print("Python version  : " + platform.python_version())
print("Application start...")

# Initialize
board = telnetio.RaspberryPi('192.168.199.31')
gpio = bridge.RemoteAccess(board)

try:
    gpio.lock(pin=14)
    gpio.configure(pin=14, direction=gpio.OUTPUT)

except PinLockedByOtherProcess:
    gpio.logout()
    raise

# Manipulate
gpio.set(14, 1)
time.sleep(1)
gpio.set(14, 0)

# Release
gpio.unlock(14)
gpio.deconfigure(14)
gpio.logout()

"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   Relay 02 : Control by using sockets (pigpio)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

# Configure
board = socketio.RaspberryPi('192.168.199.31')
gpio = bridge.RemoteAccess(board)
gpio.configure(pin=14, direction=gpio.OUTPUT)

# Manipulate
gpio.set(15, 1)
time.sleep(1)
print(gpio.get(15))

gpio.set(15, 0)
time.sleep(1)
print(gpio.get(15))

# Release
gpio.deconfigure(14)
gpio.logout()

print("Application end!")
