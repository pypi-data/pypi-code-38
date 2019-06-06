# talk to honeywell temperature monitor
from __future__ import absolute_import, unicode_literals, print_function, division
from hcam_widgets import DriverError
import six
if not six.PY3:
    from pymodbus.constants import Endian
    from pymodbus.payload import BinaryPayloadDecoder
    from pymodbus.client.sync import ModbusTcpClient as ModbusClient
else:
    from pymodbus3.constants import Endian
    from pymodbus3.payload import BinaryPayloadDecoder
    from pymodbus3.client.sync import ModbusTcpClient as ModbusClient


class Honeywell:
    def __init__(self, address, port):
        self.address = address
        self.client = ModbusClient(address, port=port)
        # list mapping pen ID number to address
        self.pen_addresses = dict(
            ccd1=0x18C0,  # pen 1
            ccd2=0x18C2,  # pen 2
            ccd3=0x18C4,  # pen 3
            ccd4=0x18C6,  # pen 4
            ccd5=0x18D0,  # pen 9
            ngc=0x18D2    # pen 10
            )
        self.unit_id = 0x01  # allows us to address different units on the same network

    def connect(self):
        success = self.client.connect()
        if not success:
            raise Exception('cannot connect to honeywell at {}'.format(self.address))

    def read_pen(self, pen_name):
        """
        Read a pen value from the client

        Raises
        ------
        DriverError
            When reading fails
        """
        try:
            self.connect()
            address = self.pen_addresses[pen_name]
            value = self.get_pen(address)
        except Exception as err:
            raise DriverError(str(err))
        finally:
            self.client.close()
        return value

    def get_pen(self, address):
        result = self.client.read_input_registers(address, 2, unit=self.unit_id)
        if not six.PY3:
            decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                         endian=Endian.Big)
        else:
            decoder = BinaryPayloadDecoder.from_registers(result.registers,
                                                          endian=Endian.Big)
        return decoder.decode_32bit_float()

    def __iter__(self):
        """
        Iterator so that CCD temps can be looped over
        """
        try:
            self.connect()
            for address in self.pen_addresses:
                yield address, self.read_pen(address)
        except StopIteration:
            raise
        except Exception as err:
            raise DriverError(str(err))
        finally:
            self.client.close()
