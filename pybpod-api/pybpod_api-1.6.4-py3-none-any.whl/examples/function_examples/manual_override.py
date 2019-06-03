# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Manually set values on Bpod channels via serial instructions.

Example adapted from Josh Sanders' original version on Sanworks Bpod repository
"""

import time

from pybpodapi.protocol import Bpod

import examples.settings as settings



my_bpod = Bpod()

wait_active_time_ms = 2

### INPUTS - BNC (1, 2) ###
print("Set BNC1 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, Bpod.ChannelNames.BNC, channel_number=1, value=12)
time.sleep(wait_active_time_ms)

print("Set BNC2 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, Bpod.ChannelNames.BNC, channel_number=2, value=15)
time.sleep(wait_active_time_ms)

### INPUTS - PWM (1..4) ###
print("Set PWM1 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, 'Port', channel_number=1, value=12)
time.sleep(wait_active_time_ms)

print("Set PWM2 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, 'Port', channel_number=2, value=13)
time.sleep(wait_active_time_ms)

print("Set PWM3 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, 'Port', channel_number=3, value=14)
time.sleep(wait_active_time_ms)

print("Set PWM3 (Input) to a value")
my_bpod.manual_override(Bpod.ChannelTypes.INPUT, 'Port', channel_number=4, value=15)
time.sleep(wait_active_time_ms)


### PORT 1 LED ###

print("Set LED of port 1 to max intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=1, value=255)
time.sleep(wait_active_time_ms)

print("Set LED of port 1 to lower intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=1, value=8)
time.sleep(wait_active_time_ms)

print("Set LED of port 1 to zero intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=1, value=0)
time.sleep(1)

### PORT 2 LED ###

print("Set LED of port 2 to max intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=255)
time.sleep(wait_active_time_ms)

print("Set LED of port 2 to lower intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=8)
time.sleep(wait_active_time_ms)

print("Set LED of port 2 to zero intensity")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.PWM, channel_number=2, value=0)
time.sleep(1)  # Wait 1s

### PORT 1 VALVE ###

print("Set valve of port 1 to open")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, 1, value=1)
time.sleep(wait_active_time_ms)

print("Set valve of port 1 to close")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, 1, value=0)
time.sleep(1)  # Wait 1s

### PORT 3 VALVE ###

print("Set valve of port 3 to open")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=3, value=1)
time.sleep(wait_active_time_ms)  # Wait 250ms

print("Set valve of port 3 to close")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.VALVE, channel_number=3, value=0)
time.sleep(1)  # Wait 1s

### PORT 2 BNC ###

print("Set BNC output ch2 to high")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.BNC, channel_number=2, value=1)
time.sleep(0.01)  # Wait 10ms

print("Set BNC output ch2 to low")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.BNC, channel_number=2, value=0)
time.sleep(1)  # Wait 1s

### PORT 3 Wire ###

print("Set Wire output ch3 to high")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.WIRE, channel_number=3, value=1)
time.sleep(0.01)  # Wait 10ms

print("Set Wire output ch3 to low")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.WIRE, channel_number=3, value=0)
time.sleep(1)  # Wait 1s

### PORT 2 Serial ###

print("Send byte 65 on UART port 2")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=2, value=65)
time.sleep(0.01)  # Wait 10ms

print("Send byte 66 on UART port 1")
my_bpod.manual_override(Bpod.ChannelTypes.OUTPUT, Bpod.ChannelNames.SERIAL, channel_number=1, value=66)

# Stop Bpod
my_bpod.close()  # Sends a termination byte and closes the serial port. PulsePal stores current params to its EEPROM.