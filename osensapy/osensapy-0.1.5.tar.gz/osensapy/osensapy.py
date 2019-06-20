import sys
import glob
import serial
from .minimalmodbusosensa import Instrument, SecurityError, _SERIALPORTS


"""
DEFAULT SETTINGS:
    baudrate            = 9600
    # of databits       = 8
    parity              = NONE
    stop bits           = 1
"""
BAUDRATE = 9600
NUMBITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP = serial.STOPBITS_ONE

def serial_get_portlist():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
        ports += glob.glob('/dev/serial[0-9]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    portlist = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            portlist.append(port)
            print(port)
        except (OSError, serial.SerialException):
            pass
    return portlist

class Transmitter():
    """
    Transmitter class for talking to OSENSA temperature transmitters

    Args:
        * param1: 
        * param2:

    """

    def __init__(self, port, slaveaddress, baudrate=BAUDRATE, timeout=0.05, close_port_after_each_call=False):
        self.modbus = Instrument(port, slaveaddress, close_port_after_each_call=close_port_after_each_call)
        self.modbus.serial.parity = PARITY
        self.modbus.serial.baudrate = baudrate
        self.modbus.serial.timeout = timeout
        # self.modbus.close_port_after_each_call = False

    def read_serial_number(self):
        return self.modbus.read_long(2)

    def read_device_id(self):
        return self.modbus.read_register(10)

    def fast_single(self, channel='A'):
        if (channel == 'A'):
            startaddress = 1024
        elif (channel == 'B'):
            startaddress = 1025
        elif (channel == 'C'):
            startaddress = 1026
        elif (channel == 'D'):
            startaddress = 1027
        elif (channel == 'E'):
            startaddress = 1028
        elif (channel == 'F'):
            startaddress = 1029
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        fwval = self.modbus.read_register(startaddress)
        return (channel, float(int(fwval / 10)/10.0), fwval % 10)

    def fast_batch(self, num_channels=3):
        startaddress = 1024
        data = []
        values = self.modbus.read_registers(startaddress, num_channels)
        for i in range(len(values)):
            channel = chr(ord('A') + i)
            fwval = values[i]
            data.append((channel, float(int(fwval / 10)/10.0), fwval % 10))
        return data

    def read_channel_data(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4096
        elif (channel == 'B'):
            startaddress = 4112
        elif (channel == 'C'):
            startaddress = 4128
        elif (channel == 'D'):
            startaddress = 4104
        elif (channel == 'E'):
            startaddress = 4120
        elif (channel == 'F'):
            startaddress = 4136
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        data = []
        values = self.modbus.read_registers(startaddress, 8)
        # Add temperature
        v = float(values[0] << 16 | values[1]) / 65536.0 - 273.0
        data.extend([ v ])
        # Add decay
        v = float(values[2] << 16 | values[3]) / 65536.0
        data.extend([ v ])
        # Add light level
        data.extend([ values[4] ])
        # Add LED current
        data.extend([ values[5] ])
        # Add status 
        data.extend([ values[7] ])
        return data

    def read_channel_temp(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4096
        elif (channel == 'B'):
            startaddress = 4112
        elif (channel == 'C'):
            startaddress = 4128
        elif (channel == 'D'):
            startaddress = 4104
        elif (channel == 'E'):
            startaddress = 4120
        elif (channel == 'F'):
            startaddress = 4136
        else:
            raise ValueError('Unsupported channel received: ' + channel)            
        firmwarevalue = self.modbus.read_long(startaddress)
        return float(firmwarevalue) / 65536.0 - 273.0

    def read_channel_decay(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4098
        elif (channel == 'B'):
            startaddress = 4114
        elif (channel == 'C'):
            startaddress = 4130
        elif (channel == 'D'):
            startaddress = 4106
        elif (channel == 'E'):
            startaddress = 4122
        elif (channel == 'F'):
            startaddress = 4138
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        firmwarevalue = self.modbus.read_long(startaddress)
        return float(firmwarevalue) / 65536.0

    def read_channel_light_level(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4100
        elif (channel == 'B'):
            startaddress = 4116
        elif (channel == 'C'):
            startaddress = 4132
        elif (channel == 'D'):
            startaddress = 4108
        elif (channel == 'E'):
            startaddress = 4124
        elif (channel == 'F'):
            startaddress = 4140
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        return self.modbus.read_register(startaddress)

    def read_channel_led_curr(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4101
        elif (channel == 'B'):
            startaddress = 4117
        elif (channel == 'C'):
            startaddress = 4133
        elif (channel == 'D'):
            startaddress = 4109
        elif (channel == 'E'):
            startaddress = 4125
        elif (channel == 'F'):
            startaddress = 4141
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        return self.modbus.read_register(startaddress)

    def read_channel_status(self, channel='A'):
        if (channel == 'A'):
            startaddress = 4103
        elif (channel == 'B'):
            startaddress = 4119
        elif (channel == 'C'):
            startaddress = 4135
        elif (channel == 'D'):
            startaddress = 4111
        elif (channel == 'E'):
            startaddress = 4127
        elif (channel == 'F'):
            startaddress = 4143
        else:
            raise ValueError('Unsupported channel received: ' + channel)
        return self.modbus.read_register(startaddress)

    def read_pcb_temp(self):
        firmwarevalue = self.modbus.read_register(4144)
        return float(firmwarevalue)/10.0 - 273.0

    def write_device_id(self, deviceid, password, subfunc=1):
        try:
            self.modbus.write_register(10, deviceid)
        except IOError:
            print('IOError occurred while writing...')
        except ValueError:
            print('ValueError occurred while writing...')
        except SecurityError as e:
            print(e.args)
            self.unlock(password, subfunc)
            self.modbus.write_register(10, deviceid)

    def write_serial_number(self, serialnumber, password, subfunc=2):
        try:
            self.modbus.write_long(2, serialnumber)
        except IOError:
            print('IOError occurred while writing...')
        except ValueError:
            print('ValueError occurred while writing...')
        except SecurityError as e:
            print(e.args)
            self.unlock(password, subfunc)
            self.modbus.write_long(2, serialnumber)

    def unlock(self, password, subfunc=1):
        self.modbus.security_unlock(password,subfunc)

    def close(self):
        port = self.modbus.serial.port
        self.modbus.serial.close()
        _SERIALPORTS.pop(port, None)

    def isOpen(self):
        try:
            return self.modbus.serial.isOpen()
        except TypeError:
            return False
                
        