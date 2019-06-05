#!/usr/bin/env python

# Compatibility imports
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

# Project imports
from htpio import bridge
from htpio import socketio


HOST = '192.168.199.31'

board = socketio.RaspberryPi(HOST)
gpio = bridge.RemoteAccess(board)
gpio.lock(14)
