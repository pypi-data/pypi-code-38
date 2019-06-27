"""package iopy
author  Benoit Dubois
copyright FEMTO ENGINEERING
brief   Basic API for SMDP protocol v2 and v3 over RS232.
details SMDP (Sycon Multi Drop Protocol) is basicaly used over RS485 "network".
        Nevertheless, some Sycon products may implement this protocol over
        a RS232 interface. This allows the same protocol stack software to be
        used for 232 or 485 networks. Note that the module is only tested with
        the RS232 interface of a compressor, model CP2800 from Cryomech.

        SMDP packet structure:
            <STX><ADDR><CMD_RSP>[<DATA>...]<CKSUM1><CKSUM2><CR>
        with
        STX 		\x02
        ADDR		address of the slave to be spoken to
        CMD_RSP	send \x80
        DATA 		must be escaped:
        			\x02 -> \x07\x30
        			\x0D -> \x07\x31
        			\x07 -> \x07\x32
        CKSUM1		compute mod-256 checksum of ADDR, CMD_RSP, and DATA
                CKSUM1 is upper 4 bits 'read as a nibble' + \x30, w/ result
                    \x30 to \x3F
        CKSUM2		is lower 4 bits + \x30 w/ result \x30 to \3F
        CR: 		\x13 or '\r'
"""

import logging
import binascii
import serial


STX = '\x02'   # Start of text character
CR = '\x0D'    # End of text character
ESCAPES = {'\x02': '\x07\x30', \
           '\x0D': '\x07\x31', \
           '\x07': '\x07\x32'}  # Protocol escape characters


#==============================================================================
# CLASS Smdp
#==============================================================================
class Smdp(object):
    """Core class for SMDP API, implements SDMP protocol.
    """

    def __init__(self, port=None, baudrate=None, timeout=None):
        """Constructor.
        :param port: device name or port number value (str or int)
        :param baudrate: baudrate (9600 or 115200) (int)
        :param timeout: timeout on serial interface (int)
        :returns: None
        """
        self._ser = serial.Serial(port=port,
                                  baudrate=baudrate,
                                  timeout=timeout)
        if self._ser.isOpen() is True:
            self._ser.flush()

    @property
    def port(self):
        """Getter of port.
        """
        return self._ser.port

    @port.setter
    def port(self, value):
        """Setter of port.
        """
        self._ser.port = value

    @property
    def baudrate(self):
        """Setter of baudrate.
        """
        return self._ser.baudrate

    @baudrate.setter
    def baudrate(self, value):
        """Setter of baudrate.
        """
        self._ser.baudrate = value

    @property
    def timeout(self):
        """Setter of timeout.
        """
        return self._ser.timeout

    @timeout.setter
    def timeout(self, value):
        """Setter of timeout.
        """
        self._ser.timeout = value

    def open(self):
        """Open port.
        :returns: None
        """
        self._ser.open()
        self._ser.flush()

    def is_open(self):
        """Open port.
        :returns: None
        """
        return self._ser.isOpen()

    def close(self):
        """Close port immediately.
        :returns: None
        """
        self._ser.close()

    def write(self, addr, cmd_rsp, data):
        """Write message to device with address 'addr'.
        :param addr: address of device (str)
        :param cmd_rsp: command/response  to device (str)
        :param data: data to send (str)
        :returns: None
        """
        cmd = self._gen_command(addr, cmd_rsp, data)
        self._ser.write(cmd)

    def read(self, size=128):
        """Read message from device.
        :param size: max number of bytes to read, None -> no limit (int)
        :returns: data received (str)
        """
        result = self._ser.read(size)
        data = self._extract_data(result)
        data = int(binascii.hexlify(data), 16)
        return data

    @staticmethod
    def _checksum(addr, cmd_rsp, data):
        """Process cheksums of message (see doc).
        :param addr: address of device (str)
        :param cmd_rsp: command/response  to device (str)
        :param data: command to write to device (str)
        :returns: checksums for the message (str, str)
        """
        result = 0
        for ch in addr + cmd_rsp + data:
            result += int(binascii.hexlify(ch), 16)
        result = binascii.hexlify(chr(result % 256))
        chk1 = binascii.unhexlify('3' + result[0])
        chk2 = binascii.unhexlify('3' + result[1])
        return chk1, chk2

    @staticmethod
    def _escape_data(data):
        """Handles protocol escape characters which can be present in the data
        field of the message.
        :param data: the data field of the message (str)
        :returns: a valid data field (str)
        """
        result = ''
        for ch in data:
            if ch in ESCAPES:
                result += ESCAPES[ch]
            else:
                result += ch
        return result

    def _extract_data(self, result):
        """Does the reverse of _escape_data(): recombines it.
        :param data: the data field of the message (str)
        :returns: a valid data field (str)
        """
        stx = result[0]
        if stx != STX:
            logging.error("Start character is not valid")
            raise IOError("Start character is not valid")
        addr = result[1]
        cmd_rsp = result[2]
        scksum1 = result[-3]
        scksum2 = result[-2]
        data = result[3:-3]
        for key in ESCAPES.keys():
            data = data.replace(ESCAPES[key], key)
        chk1, chk2 = self._checksum(addr, cmd_rsp, data)
        if scksum1 != chk1 or scksum2 != chk2:
            logging.error("Checksum failure")
            raise IOError("Checksum failure")
        return data[4:]

    def _gen_command(self, addr, cmd_rsp, data):
        """Generate command to send to device.
        :param addr: address of device (int)
        :param cmd_rsp: command/response  to device (str)
        :param data: command to write to device (str)
        :returns: A valid command (str)
        """
        escdata = self._escape_data(data)
        chk1, chk2 = self._checksum(addr, cmd_rsp, data)
        return STX + addr + cmd_rsp + escdata + chk1 + chk2 + CR

