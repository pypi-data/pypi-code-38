# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Example adapted from Josh Sanders' original version on Sanworks Bpod repository
"""

import time

from pybpodapi.protocol import Bpod


my_bpod = Bpod()

print("Send byte 65 on UART port 1 - by default, this is ASCII 'A'")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, 1, 65)
time.sleep(1)  # Wait 1s

print("Set byte 65 ('A') on UART port 1 to trigger a 3-byte message: 'BCD'")
my_bpod.load_serial_message(1, 65, [66, 67, 68])
# Now, the same command has a different result
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=65)
time.sleep(1)  # Wait 1s

print("Reset the serial message library. Bytes will now pass through again.")
my_bpod.reset_serial_messages()
# Back to 'A'
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=65)

# Stop Bpod
my_bpod.close()  # Sends a termination byte and closes the serial port. PulsePal stores current params to its EEPROM.
