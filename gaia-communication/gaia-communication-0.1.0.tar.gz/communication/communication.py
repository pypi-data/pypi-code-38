#!/usr/bin/env/python
# -*- coding: utf-8 -*-


def serial_communication():
    import serial
    port = "/dev/ttyUSB0"
    rate = 9600
    s1 = serial.Serial(port, rate)
    s1.flushInput()
    return


def interrupt_to_esp():
    serial_communication()
    comp_list = ["Interrupt\r\n"]
    while True:
        if s1.inWaiting() > 0:
            inputValue = s1.readline()
            print(inputValue)
            if inputValue in comp_list:
                s1.write('0')
                return
