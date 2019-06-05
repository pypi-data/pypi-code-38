#!/usr/bin/env python

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# System imports
import time
import platform

# Project imports
from htpio import telnetio


"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   Basic i/o example
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
"""

print("Python version  : " + platform.python_version())
print("Application start...")

relay1 = telnetio.RaspberryPi(host='192.168.199.31')

try:
    relay1.lock(pin=14)
    relay1.configure(pin=14, direction=telnetio.RaspberryPi.OUTPUT)

except telnetio.PinLockedByOtherProcess:
    relay1.logout()
    raise
  
v1 = relay1.set(14, 1)
v2 = relay1.get(14)

time.sleep(1)

relay1.set(14, 0)
 
relay1.unlock(14)
relay1.deconfigure(14)
 
relay1.logout()

print("Application end!")
