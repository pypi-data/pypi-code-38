# -*- coding: utf-8 -*-

"""package dmm
author    Benoit Dubois
copyright FEMTO ENGINEERING
license   GPL v3.0+
brief     API dedicated to handle the 34972a datalogger through ethernet.
"""

import logging
import re
import socket
from collections import namedtuple
from time import sleep
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot

from dmm.constants import DAQ34972A_ID, DAQ34972A_PORT, DAQ34972A_TIMEOUT


DEFAULT_PORT = DAQ34972A_PORT
DEFAULT_TIMEOUT = DAQ34972A_TIMEOUT
DEVICE_ID = DAQ34972A_ID


# Define a new type used for storing device configurations
DTuple = namedtuple('DTuple', ['mnemo', 'caption', 'list'])

#==============================================================================
# 34972A device capabilities namespace
#==============================================================================
RESO = [DTuple("0.0001", "0.0001 x range", None), \
        DTuple("0.00001", "0.00001 x range", None), \
        DTuple("0.000003", "0.000003 x range", None), \
        DTuple("0.0000022", "0.0000022 x range", None), \
        DTuple("0.000001", "0.000001 x range", None), \
        DTuple("0.0000008", "0.0000008 x range", None), \
        DTuple("0.0000003", "0.0000003 x range", None), \
        DTuple("0.00000022", "0.00000022 x range", None)]

INTGT = [DTuple("0.02", "0.02 PLC", None), \
         DTuple("0.2", "0.2 PLC", None), \
         DTuple("1", "1 PLC", None), \
         DTuple("2", "2 PLC", None), \
         DTuple("10", "10 PLC", None), \
         DTuple("20", "20 PLC", None), \
         DTuple("100", "100 PLC", None), \
         DTuple("200", "200 PLC", None)]

RES_RANGE = [DTuple("DEF", "Automatique", None), \
             DTuple("100", "100 Ω", None), \
             DTuple("1E+3", "1 kΩ", None), \
             DTuple("10E+3", "10 kΩ", None), \
             DTuple("100E+3", "100 kΩ", None), \
             DTuple("1E+6", "1 MΩ", None), \
             DTuple("10E+6", "10 MΩ", None), \
             DTuple("100E+6", "100 MΩ", None)]

VOLT_RANGE = [DTuple("DEF", "Automatique", None), \
              DTuple("0.1", "100 mV", None), \
              DTuple("1", "1 V", None), \
              DTuple("10", "10 V", None), \
              DTuple("100", "100 V", None), \
              DTuple("300", "300 V", None)]

FREQ_RANGE = [DTuple("DEF", "Automatique", None), \
              DTuple("3", "3 Hz", None), \
              DTuple("20", "20 Hz", None), \
              DTuple("200", "200 Hz", None)]

PER_RANGE = [DTuple("DEF", "Automatique", None), \
             DTuple("1", "1 second", None), \
             DTuple("0.1", "100 ms", None), \
             DTuple("0.01", "10 ms", None)]

CUR_RANGE = [DTuple("DEF", "Automatique", None), \
             DTuple("0.01", "10 mA", None), \
             DTuple("0.1", "100 mA", None), \
             DTuple("1", "1 A", None)]

TCOUPLE_TYPE = [DTuple("B", "Type B", None), \
                DTuple("E", "Type E", None), \
                DTuple("J", "Type J", None), \
                DTuple("K", "Type K", None), \
                DTuple("N", "Type N", None), \
                DTuple("R", "Type R", None), \
                DTuple("S", "Type S", None), \
                DTuple("T", "Type T", None)]

RTD_TYPE = [DTuple("85", "Type 85", None), \
            DTuple("91", "Type 91", None)]

THERM_TYPE = [DTuple("2252", "Type 2252", None), \
              DTuple("5000", "Type 5000", None), \
              DTuple("10000", "Type 10000", None)]

TEMP_TRANS_TYPE = [DTuple("DEF", "Automatique", None), \
                   DTuple("TCouple", "Thermocouple", TCOUPLE_TYPE), \
                   DTuple("RTD", "2-wire RTD", RTD_TYPE), \
                   DTuple("FRTD", "4-wire RTD", RTD_TYPE), \
                   DTuple("THER", "Thermistor", THERM_TYPE)]

FUNCTION = [DTuple("VOLT:DC", "DC Voltage", VOLT_RANGE), \
            DTuple("VOLT:AC", "AC Voltage", VOLT_RANGE), \
            DTuple("FRES", "4-wire Resistance", RES_RANGE), \
            DTuple("RES", "2-wire Resistance", RES_RANGE), \
            DTuple("FREQ", "Frequency", FREQ_RANGE), \
            DTuple("PER", "Period", FREQ_RANGE), \
            DTuple("TEMP", "Temperature", TEMP_TRANS_TYPE)]

FUNCTION_FULL = [DTuple("VOLT:DC", "DC Voltage", VOLT_RANGE), \
                 DTuple("VOLT:AC", "AC Voltage", VOLT_RANGE), \
                 DTuple("FRES", "4-wire Resistance", RES_RANGE), \
                 DTuple("RES", "2-wire Resistance", RES_RANGE), \
                 DTuple("FREQ", "Frequency", FREQ_RANGE), \
                 DTuple("PER", "Period", PER_RANGE), \
                 DTuple("TEMP", "Temperature", TEMP_TRANS_TYPE), \
                 DTuple("CURR:DC", "DC Current", CUR_RANGE), \
                 DTuple("CURR:AC", "AC Current", CUR_RANGE)]


#==============================================================================
class Daq34972aEth(QObject):
    """Class used to handle the ethernet facilities of 34972a device.
    """

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)

    def __init__(self, ip="", \
                 port=DEFAULT_PORT, \
                 timeout=DEFAULT_TIMEOUT):
        """The constructor.
        :param ip: IP address of device (str)
        :param port: Ethernet port of device (int)
        :param timeout: Socket timeout value in second (float)
        :returns: None
        """
        super(Daq34972aEth, self).__init__()
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self._sock = None

    @pyqtSlot()
    def connect(self):
        """Specific ethernet connection process to 34972a.
        :returns: True if connection effective else False (bool)
        """
        try:
            self._sock = socket.socket(socket.AF_INET,
                                       socket.SOCK_STREAM,
                                       socket.IPPROTO_TCP)
            self._sock.settimeout(self.timeout)
            self._sock.connect((self.ip, self.port))
        except ValueError as ex:
            logging.error("Connection parameters out of range: %s", str(ex))
            return False
        except socket.timeout:
            logging.error("Timeout on connection")
            return False
        except Exception as ex:
            logging.critical("Unexpected exception during connection with " + \
                             "34972a: %s", str(ex))
            return False
        else:
            self.reset()
            self.connected.emit()
            logging.debug("Connected to 34972A")
            return True

    @pyqtSlot()
    def close(self):
        """Specific ethernet closing process with 34972A.
        :returns: None
        """
        try:
            self._sock.close()
        except socket.error as ex:
            logging.error("Socket error %s", str(ex))
        except Exception as ex:
            logging.error("Unexpected error %s", str(ex))
        else:
            self._sock = None
            self.closed.emit()
            logging.info("Connection to 34972A closed")

    @pyqtSlot()
    def check_interface(self):
        """Returns True if interface with device is OK.
        :returns: status of interface with device (boolean)
        """
        if self.connect() is False:
            self.id_checked.emit(False)
            return False
        try:
            _id = self.get_id()
        except Exception: # Catch connection and  get_id problem
            _id = "" # To avoid error with 'find()' when '_id' is not defined
        if _id.find(DEVICE_ID) >= 0:
            self.id_checked.emit(True)
            return True
        else:
            self.id_checked.emit(False)
            return False

    @pyqtSlot()
    def reset(self):
        """Resets acquisition process and device.
        :returns: None
        """
        self._sock.send("*RST\n")
        self._sock.send("*CLS\n")
        logging.debug("Reset 34972A device")

    def local_mode(self):
        """Set device in local mode.
        :returns: None
        """
        self.write("SYST:LOC")

    def set_timeout(self, timeout):
        """Set timeout on socket operations.
        :param timeout: timeout value in second (float)
        :returns: None
        """
        self._sock.settimeout(timeout)
        self.timeout = timeout

    def get_timeout(self):
        """Get timeout on socket operations.
        :returns: timeout value in second (float)
        """
        return self._sock.gettimeout()

    def set_ip(self, ip):
        """Set IP address used to speak with device.
        :param ip: IP address (str)
        :return: None
        """
        self.ip = ip

    def get_ip(self):
        """Get IP used to speak with device.
        :returns: IP address (str)
        """
        return self.ip

    def set_port(self, port):
        """Set internet port used to speak with device.
        :param port: port used by dmm4050 (int)
        :returns: None
        """
        self.port = port

    def get_port(self):
        """Get internet port used to speak with device.
        :returns: port used by dmm4050 (int)
        """
        return self.port

    def get_id(self):
        """Get ID of device.
        :returns: ID of device (str)
        """
        self.write("*IDN?")
        return self.read(100)

    def _check_error(self):
        """"Error checking process.
        :returns: list of error (list of str)
        """
        error_list = []
        try:
            self._sock.send("SYST:ERR?\n")
            retval = self._sock.recv(100)
            while not "+0" in retval:
                error_list.append(retval)
                logging.error(retval)
                self._sock.send("SYST:ERR?\n")
                retval = self._sock.recv(100)
        except socket.timeout:
            logging.error("Timeout")
        except Exception as ex:
            logging.error(str(ex))
        return error_list

    def write(self, data):
        """"Ethernet writing process.
        :param data: data writes to device (str)
        :returns: None
        """
        try:
            self._sock.send(data + "\n")
        except socket.timeout:
            logging.error("Timeout")
        except Exception as ex:
            logging.error(str(ex))
        logging.debug("write " + data.strip('\n'))

    def read(self, length):
        """Ethernet reading process.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        try:
            retval = self._sock.recv(length)
        except socket.timeout:
            logging.error("Timeout")
        except Exception as ex:
            logging.error(str(ex))
        else:
            logging.debug("read: " + retval.strip('\n'))
            return retval


#==============================================================================
class Daq34972a(Daq34972aEth):
    """Class used to handle the 34972a device through ethernet connection
    (inherits of 34972aEth class).
    """

    new_data = pyqtSignal((list,), (str,))

    def __init__(self, ip, port, timeout):
        """The constructor.
        :param ip: IP address of device (str)
        :param port: Ethernet port of device (int)
        :param timeout: Socket timeout value in second (float)
        :returns: None
        """
        super(Daq34972a, self).__init__(ip, port, timeout)

    def get_scanlist(self):
        """Gets scan list from real device.
        :returns: a list of scan (list of str)
        """
        self.write("ROUT:SCAN?")
        retval = self.read(1000)
        retval = retval.strip('\n').split('@')[1][:-1].split(',')
        if retval == ['']:
            return retval
        scanlist = []
        for val in retval:
            if 99 < int(val) < 399:
                scanlist.append(val)
            else:
                logging.error("Bad scan value: " + val)
                raise RuntimeError("Bad scan value")
        return scanlist

    def data_read(self):
        """Takes a measurement the next time the trigger condition is met.
        After the measurement is taken, the reading is placed in the output
        buffer. "data_read" will not cause readings to be stored in the Meter’s
        internal memory.
        :returns: data read in buffer (list of float)
        """
        try:
            self.write("READ?")
            retval = self.read(1000)
            if re.match('[\+\-]\d\.\d*E[\+\-]\d\d', retval) is None:
                return None
        except Exception as ex:
            logging.error(str(ex))
        else:
            self.new_data[str].emit(retval)
            float_list = [float(value) for value in retval.split(',')]
            self.new_data[list].emit(float_list)
            logging.debug("Data read measurement: " + retval.strip('\n'))
            return float_list

    def _wait_dataready(self, nbread):
        """Waits until 'nbread' readings are stored in memory.
        :param nbread: number of readings triggering end of wait (int)
        :returns: None
        """
        count = 0
        while count < nbread:
            sleep(0.1)
            self.write("DATA:POIN?")
            count = int(self.read(10))



#==============================================================================
def check_34972a():
    """Checks the 34972a class: connects to the data logger, configures a dc
    voltage measurement on channel 101 to 105 then collects and prints data to
    the standard output.
    """

    # For "Ctrl+C" works
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Specific function imports
    import sys
    from datetime import datetime
    #from mjdutil import datetime_to_mjd
    from PyQt4.QtCore import QCoreApplication#, QThread

    # Handles log
    date_fmt = "%d/%m/%Y %H:%M:%S"
    log_format = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.INFO, \
                        datefmt=date_fmt, \
                        format=log_format)

    def print_data(data):
        """'Virtual slot', used to print data emited by a signal.
        Adds also a timetag.
        :returns: None
        """
        #now = datetime_to_mjd(datetime.utcnow())
        now = datetime.utcnow()
        print(str(now) + "," + data)

    # Creates the application
    app = QCoreApplication(sys.argv)
    sys.exit(app.exec_())


#==============================================================================
if __name__ == '__main__':
    check_34972a()
