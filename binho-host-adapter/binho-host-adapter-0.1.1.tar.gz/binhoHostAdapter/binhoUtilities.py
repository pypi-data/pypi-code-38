## binhoUtilities Python Library
## Version 1.0
##
## Jonathan Georgino <jonathan@binho.io>
## Binho LLC
## www.binho.io

import sys
import glob
import serial
from . import binhoHostAdapter

# Source: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
# Claims that it is successfully tested on Windows 8.1 x64, Windows 10 x64, Mac OS X 10.9.x / 10.10.x / 10.11.x and Ubuntu 14.04 / 14.10 / 15.04 / 15.10 with both Python 2 and Python 3.

class binhoUtilities:

    def __init__(self):
        self.stuff = "test"

    def _checkForDeviceID(self, serialPort):

        comport = serial.Serial(serialPort, baudrate=1000000, timeout=0.025, write_timeout=0.05)

        command = '+ID ?\n'
        comport.write(command.encode("utf-8"))

        receivedData = comport.readline().strip().decode("utf-8")

        if len(receivedData) > 0:
            if receivedData[0] != '-':
                receivedData = comport.readline().strip().decode("utf-8")

        comport.close()

        return receivedData
                    
    def listAvailablePorts(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port, timeout=500)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def listAvailableDevices(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:               
                resp = self._checkForDeviceID(port)

                if "-ID" in resp:
                    result.append(port)

            except (OSError, serial.SerialException):
                pass
        return result

    def getPortByDeviceID(self, deviceID):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                resp = self._checkForDeviceID(port)

                if resp == '-ID ' + deviceID:
                    result.append(port)
                elif resp == '-ID 0x' + deviceID:
                    result.append(port)

            except (OSError, serial.SerialException):
                pass
        return result

    if __name__ == '__main__':
        print(listAvailableDevices())