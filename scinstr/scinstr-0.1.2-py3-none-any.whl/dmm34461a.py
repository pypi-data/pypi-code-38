# -*- coding: utf-8 -*-

"""package scinstr
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     API dedicated to handle the Keysight 34461A digital multimeter.
"""

import logging
import time
import re
import socket
import usbtmc
from scinstr.constants import DMM34461A_PORT, DMM34461A_TIMEOUT, DMM34461A_ID, \
DMM34461A_VID, DMM34461A_PID

# Multimeter functions
(CAP, CURR, CURRDC, VOLTAC, VOLTDC, VOLTDCRAT, RES, FRES, FRE, PER,
 TEMPRTD, TEMPFRTD, DIOD, CONT) = ("CAP", "CURR", "CURR:DC", "VOLT:AC",
                                   "VOLT:DC", "VOLT:DC:RAT", "RES",
                                   "FRES", "FRE", "PER", "TEMP:RTD",
                                   "TEMP:FRTD", "DIOD", "CONT")

# Integration time
(PLC002, PLC02, PLC1, PLC10, PLC100) = ("0.02", "0.2", "1", "10", "100")

# Voltage input range
(RANGE10MV, RANGE1V, RANGE10V, RANGE100V, RANGE1000V) = ("0.1", "1", "10",
                                                         "100", "1000")

# Trigger source
(IMM, EXT, BUS) = ("IMM", "EXT", "BUS")

#==============================================================================
class Dmm34461aAbstract(object):
    """Abstract class to handling DMM34461a digital multimeter device. Derived
    classes need to re-implement specific-protocol methods: connect(), close(),
    _write(), _read()...
    """

    def connect(self):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        pass

    def close(self):
        """Abstract protocol closing process. Derived classes must implement
        the closing process dedicated to the specific protocol used.
        :returns: None
        """
        pass

    def _write(self, data):
        """Abstract protocol write process. Derived classes must implement
        the write process dedicated to the specific protocol used.
        :param data: data writes to device (str)
        :returns: None
        """
        pass

    def _read(self, length):
        """Abstract protocol read process. Derived classes must implement
        the read process dedicated to the specific protocol used.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        pass

    def write(self, data):
        """A basic write method: writes "data" to device.
        :param data: data writes to device (str)
        :returns: None
        """
        try:
            nb_bytes = self._write(data)
        except Exception as ex:
            logging.error("Write error: %r", ex)
            return 0
        logging.debug("write: %r", data)
        return nb_bytes

    def read(self, length):
        """A basic read method: read a message from device.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        try:
            retval = self._read(length)
        except Exception as ex:
            logging.error("Read error: %r", ex)
            return ''
        logging.debug("read: %r", retval)
        return retval

    def query(self, data, length=100):
        """Read after write method.
        :param data: data writes to device (str)
        :param length: length of message to read (int)
        :returns: Message returned by device (str)
        """
        self.write(data)
        return self.read(length)

    def reset(self):
        """Resets meter to its power-on state, sets all bits to zero in
        status byte register and all event registers and clear error queue.
        :returns: None
        """
        self.write("*RST")
        time.sleep(2.0)
        self.write("*CLS")
        time.sleep(2.0)
        logging.info("Reset meter")

    def idn(self):
        """Return product id of device.
        :returns: product id of device (str)
        """
        self.write("*IDN?")
        _id = self.read(100)
        return _id

    def check_error(self):
        """Return list of current error.
        :returns: list of current error (list of str)
        """
        errors = [self.query("SYST:ERR?", 100)]
        while errors[-1] != "+0,\"No error\"":
            errors.append(self.query("SYST:ERR?", 100))
        return errors

    def check_interface(self):
        """Basic interface connection test: check id of device.
        Return True if interface with device is OK.
        :returns: status of interface with device (bool)
        """
        retval = self.connect()
        if retval is False:
            return False
        try:
            _id = str(self.idn())
        except Exception:  # Catch connection and get_id problem
            _id = "" # To avoid error with 'find()' if '_id' is not defined
        self.close()
        if _id.find(DMM34461A_ID) >= 0:
            return True
        return False

    def dc_voltage_config(self, intg_time=None, rang=None, res=None,
                          d_fltr=None, a_fltr=None):
        """Configures specific parameters of DC voltage measurement.
        Note that you must specify a range whenever specifying a resolution
        parameter.
        :param intg_time: integration time in PLC (Power Line Cycle) (int)
        :param rang: DC voltage range (str)
        :param res: DC measurement resolution (int)
        :param d_fltr: Set digital averaging filter (bool)
        :param a_fltr: Set analog filter (bool)
        :returns: None
        """
        msg = "CONF:VOLT:DC"
        if rang != None:
            msg += " " + rang
            if res != None:
                msg += ", " + str(res)
        self.write(msg)
        if a_fltr != None:
            self.write("FILT:DC:STAT" + str(a_fltr))
        if intg_time < 1:
            self.write("FILT:DC:DIG:STAT OFF")
        elif d_fltr != None:
            self.write("FILT:DC:DIG:STAT" + str(d_fltr))
        if intg_time != None:
            self.write("VOLT:DC:NPLC " + str(intg_time))
        logging.info("DC voltage measurement config done")

    def trigger_config(self, src=IMM, delay=None, delauto=None, scount=None,
                       tcount=None):
        """Configures trigger.
        :param src: source from which the Meter will expect a measurement
        trigger (str)
        :param delay: delay between receiving a trigger and the beginning of
        measurement cycle (int)
        :param delauto: enables or disables automatic trigger delay.
        The amount of delay is set based on selected function, integration time,
        and filter setting. When automatic delay is enabled, "delay" parameters
        is ignored (int)
        :param scount: number of measurements the Meter takes per trigger
        (int or str)
        :param tcount: number of triggers the Meter will take before switching
        to an idle state. If you use "INF", continously accepts triggers,
        in this case use a device clear to stop the process (int or str)
        :returns: None
        """
        self.write("TRIG:SOUR " + src)
        if delauto == 1:
            self.write("TRIG:DEL:AUTO ON")
        elif delauto == 0:
            self.write("TRIG:DEL:AUTO OFF")
        elif delay != None:
            self.write("TRIG:DEL " + str(delay))
        if tcount != None:
            self.write("TRIG:COUN " + str(tcount))
        if scount != None:
            self.write("SAMP:COUN " + str(scount))
        logging.info("Trigger configuration done")

    def init_trig(self):
        """Once the Meter has been configured for a measurement, ini_meas()
        causes the Meter to take a measurement when the trigger conditions have
        been met. The measurement reading(s) are placed in the Meter’s internal
        memory (up to 5,000 to be read at a later time using the FETCh? command.
        :returns: None
        """
        self.write("INIT")
        logging.info("Initiate triggering")

    def data_read_fetch(self):
        """To process readings from the Meter’s internal memory to the output
        buffer.
        :returns: data read in internal memory buffer (float)
        """
        self.write("FETC?")
        retval = self.read(100)
        if re.match(r"[\+\-]\d\.\d*E[\+\-]\d\d", retval) is None:
            return None
        logging.debug("Data read (fetch) measurement: %r", retval)
        return float(retval)

    def data_read(self):
        """Takes a measurement the next time the trigger condition is met.
        After the measurement is taken, the reading is placed in the output
        buffer. "data_read" will not cause readings to be stored in the Meter’s
        internal memory.
        Read method convenient for slow measurement.
        :returns: data read in buffer and list of errors (tupple (float, list))
        """
        self.write("READ?")
        retval = self.read(100) # Note '100' not used in serial com mode
        errors = self.check_error()
        logging.debug("Error during reading?: %r", errors)
        if re.match(r"[\+\-]\d\.\d*E[\+\-]\d\d", retval) is None:
            return None
        logging.debug("Data read measurement: %r", retval)
        return float(retval), errors


#==============================================================================
class Dmm34461aEth(Dmm34461aAbstract):
    """Handle DMM device through ethernet connection.
    """

    DEFAULT_PORT = DMM34461A_PORT
    DEFAULT_TIMEOUT = DMM34461A_TIMEOUT

    def __init__(self, ip=None, port=DMM34461A_PORT,
                 timeout=DMM34461A_TIMEOUT):
        """The constructor.
        :param ip: IP address of device (str)
        :param port: Ethernet port of device (int)
        :param timeout: Socket timeout value in s (float)
        :returns: None
        """
        self._sock = None
        self.ip = ip
        self.port = port
        self._timeout = timeout

    def connect(self):
        """Specific ethernet connection process to DMM.
        :returns: True if connection success other False (Bool)
        """
        self._sock = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM,
                                   socket.IPPROTO_TCP)
        self._sock.settimeout(self._timeout)
        try:
            self._sock.connect((self.ip, self.port))
        except ValueError as ex:
            logging.error("Connection parameters out of range: %r", ex)
            return False
        except socket.timeout:
            logging.error("Timeout on connection")
            return False
        except Exception as ex:
            logging.critical("Connection with DMM problem: %r", ex)
            return False
        logging.info("Connected to DMM")
        return True

    def close(self):
        """Specific ethernet closing process with DMM.
        :returns: None
        """
        if self._sock is not None:
            self._sock.close()
            self._sock = None
        logging.info("Connection to DMM closed")

    def _write(self, data):
        """Specific ethernet writing process.
        :param data: data writes to device (str)
        :returns: number of byte sent (int)
        """
        return self._sock.send(data + '\n').encode('utf-8')

    def _read(self, length):
        """Specific ethernet reading process.
        :param length: length of message to read (int)
        :returns: message reads from device (str)
        """
        return self._sock.recv(length).decode('utf-8').strip('\n')

    @property
    def timeout(self):
        """Gets timeout on socket operations.
        :returns: timeout value in second (float)
        """
        return self._sock.gettimeout()

    @timeout.setter
    def timeout(self, timeout):
        """Sets timeout on socket operations.
        :param timeout: timeout value in second (float)
        :returns: None
        """
        self._sock.settimeout(timeout)


# =============================================================================
class Dmm34461aUsb(Dmm34461aAbstract):
    """Handle DMM device through USB connection.
    """

    def __init__(self, vendor_id=DMM34461A_VID,
                 product_id=DMM34461A_PID,
                 timeout=DMM34461A_TIMEOUT):
        self._dev = None
        self.vid = vendor_id
        self.pid = product_id
        self._timeout = timeout

    def connect(self):
        """Connect to the remote host.
        :returns: True if connection succeeded, False otherwise
        """
        logging.info('Connecting to DMM')
        try:
            self._dev = usbtmc.Instrument(self.vid, self.pid)
        except usbtmc.usbtmc.UsbtmcException as ex:
            logging.error("Connection problem: %r", ex)
            return False
        self._dev.timeout = self._timeout
        logging.info('Connection --> Ok')
        return True

    def close(self):
        """Closes the underlying serial connection
        """
        if self._dev is not None:
            try:
                self._dev.close()
            except Exception as ex:
                logging.error("Error when closing USB connection: %r", ex)
        self._dev = None
        logging.info("Connection to DMM closed")

    def _write(self, data):
        """Specific USB writing process.
        :param data: data writes to device (str)
        :returns: number of bytes sent (int)
        """
        try: 
            nb_byte = self._dev.write(data)
        except AttributeError as ex: # Exception raised after first write
            logging.debug(ex)        # No explication found
            nb_byte = self._dev.write(data)
        return nb_byte

    def _read(self, length):
        """Specific USB reading process.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        return self._dev.read(length)

    @property
    def timeout(self):
        """Gets timeout on socket operations.
        :returns: timeout value in second (float)
        """
        if self._dev is None:
            logging.debug("Can't get timeout value, device not connected")
            return None
        return self._dev.timeout

    @timeout.setter
    def timeout(self, timeout):
        """Sets timeout on socket operations.
        :param timeout: timeout value in second (float)
        :returns: None
        """
        if self._dev is None:
            logging.debug("Can't set timeout valule, device not connected")
            return
        self._dev.timeout = timeout
        self._timeout = timeout


#==============================================================================
def check_dmm():
    """Checks the Dmm34461axx class: connects to the multimeter, configures a dc
    voltage measurement then collects and prints data to standard output.
    """
    from datetime import datetime

    date_fmt = "%d/%m/%Y %H:%M:%S"
    log_format = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.INFO,
                        datefmt=date_fmt,
                        format=log_format)


    dmm = Dmm34461aUsb(0x2a8d, 0x1601, timeout=4.8)
    #dmm = DmmEth(ip="192.168.0.61", port=5025, timeout=2.8)
    if dmm.connect() is not True:
        print("Connection failed")
        return
    dmm.reset()

    print("IDN:", dmm.query("*IDN?"))
    dmm.write("CONF:VOLT:DC AUTO") # Autorange
    dmm.write("VOLT:DC:NPLC 100")
    dmm.write("VOLT:DC:ZERO:AUTO ON") # Autozero off
    print("Error config?:", dmm.check_error())

    try:
        while True:
            value, errors = dmm.data_read()
            now = datetime.utcnow()
            if value is None or value == "":
                print("# No data @", now)
            else:
                print(now, value)
    except KeyboardInterrupt:
        dmm.write("ABORT")
    except Exception as er:
        logging.error("# Exception during acquisition: %r", er)

    print("Final error?:", dmm.check_error())

    dmm.close()


#==============================================================================
if __name__ == '__main__':
    check_dmm()
