# -*- coding: utf-8 -*-

"""package iopy
author    Benoit Dubois
copyright FEMTO ENGINEERING
licence   GPL v3.0+
brief     Basic interface to Prologix GPIB-Ethernet adapter.
"""

import logging
import socket
from time import sleep


#===============================================================================
class PrologixGpibEth(object):
    """PrologixGpibEth class, Prologix GPIB ethernet adapter device.
    """

    def __init__(self, ip, port, gpib_addr):
        """Constructor.
        :returns: None
        """
        super().__init__()
        self._ip = ip
        self._port = port
        self._gpib_addr = gpib_addr
        self._sock = None

    def __del__(self):
        """Close connection before deleting object.
        :returns: None
        """
        if self._sock:
            self._sock.close()

    def _send(self, string):
        """Low level send method.
        :param string: data string to send (str)
        :returns: None
        """
        try:
            self._sock.send(string.encode('utf-8'))
        except:
            raise

    def _recv(self, bufsize):
        """Low level read/receive method.
        :param bufsize: size of buffer to read (int)
        :returns: read data (str)
        """
        try:
            return self._sock.recv(bufsize).decode('utf-8')
        except:
            raise

    def init(self):
        """Initialization process:
        - open tcp connection with device
        - init device
        :returns: None
        """
        if self._connect() is False:
            return False
        if self._init_prologix() is False:
            return False
        return True

    @property
    def ip(self):
        """Getter of ip.
        """
        return self._ip

    @ip.setter
    def ip(self, value):
        """Setter of ip.
        """
        self._ip = value

    @property
    def port(self):
        """Getter of port.
        """
        return self._port

    @port.setter
    def port(self, value):
        """Setter of port.
        """
        self._port = value

    @property
    def gpib_addr(self):
        """Getter of gpib_addr.
        """
        return self._gpib_addr

    @gpib_addr.setter
    def gpib_addr(self, value):
        """Setter of gpib_addr.
        """
        self._gpib_addr = value

    @property
    def timeout(self):
        """Getter of timeout.
        """
        return self._sock.timeout

    @timeout.setter
    def timeout(self, value):
        """Setter of timeout.
        """
        self._sock.settimeout(value)

    def _connect(self):
        """Makes a socket connection to the GPIB device through the Prologix
        controller and returns the opened socket.
        :returns: None
        """
        logging.info('Connecting to device @%s...', self._ip)
        try:
            self._sock = socket.socket(socket.AF_INET, \
                                       socket.SOCK_STREAM, \
                                       socket.IPPROTO_TCP)
            self._sock.settimeout(2.0)	# Don't hang around forever
            self._sock.connect((self._ip, self._port))
        except socket.timeout:
            logging.warning("Socket timeout error during connection.")
            return False
        except socket.error as er:
            logging.error("Socket error during connection: %r", er)
            return False
        except Exception as er:
            logging.error("Unexpected error during connection: %r", er)
            return False
        logging.info('Connection --> Ok')
        return True
        
    def _init_prologix(self):
        """Inits behavior of Prologix GPIB-ETHERNET controller (see details
        in code).
        :returns: None
        """
        try:
            self._send("++mode 1\n") # Set mode as CONTROLLER
            self._send('++addr ' + str(self._gpib_addr) + '\n') # GPIB addr
            self._send('++eos 3\n') # Set end-of-send character to nothing
            self._send("++eoi 1\n") # Assert EOI with last byte
            self._send("++read_tmo_ms 2750\n") # Set read timeout
            self._send("++auto 0\n") # Turn off read-after-write to avoid
                                     # "Query Unterminated" errors
        except socket.timeout:
            logging.warning("Socket timeout")
            return False
        except socket.error as er:
            logging.error("Socket error: %r", er)
            return False
        except Exception as er:
            logging.error("Unexpected error: %r", er)
            return False
        else:
            return True

    def reset_gpib_ctrlr(self):
        """Performs a power-on reset of the controller. The process takes
        about 5 seconds.
        :returns: None
        """
        logging.warning("Power-on reset of GPIB controller (about 5 seconds)")
        self._send("++rst\n")
        sleep(6)
        logging.info("Power-on reset done")

    def get_status(self):
        """Returns status of device.
        :returns: identification string of device (str)
        """
        self.write("++srq")
        status = self.read(128, 1.0)
        self.write("++status 48")
        return status

    def check_error(self):
        """Checks if error occured in GPIB device.
        :returns: None
        """
        self._send("ERR?\n")
        self._send("++read eoi\n")
        try:
            error = self._recv(128)
        except socket.timeout:
            return
        logging.error("GPIB-Ethernet interface error: %r", error)

    def raw_read(self, length=1024, timeout=1.0):
        """Returns data read on GPIB interface.
        :params length: maximum amount of data to be received at once (int)
        :params timeout: timeout value on socket (float)
        :returns: None
        """
        self._sock.settimeout(timeout)
        data = self._sock.recv(length)
        logging.debug("RawRead: %r", data)
        return data

    def read(self, length=1024, timeout=1.0):
        """Returns data read on GPIB interface.
        :params length: maximum amount of data to be received at once (int)
        :params timeout: timeout value on socket (float)
        :returns: None
        """
        self._sock.settimeout(timeout)
        self._send("++read eoi\n")
        data = None
        try:
            data = self._recv(length)
        except socket.timeout:
            raise
        logging.debug("read: %r", data)
        return data

    def write(self, data):
        """Write data on GPIB interface.
        :params data: data to write (str)
        :returns: None
        """
        self._send(data + "\n")
        logging.debug("write: %r", data)
