# -*- coding: utf-8 -*-

"""package dmm4050
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2018
license   GPL v3.0+
brief     Dedicated to handle the Tektronix DMM4050 digital multimeter.
"""

import logging
import re
#import serial
import socket
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from dmm.constants import DMM4050_ID


class Dmm4050Abstract(QObject):
    """Abstract class to handling DMM4050 digital multimeter device. Derived
    classes need to re-implement specific-protocol methods: connect(), close(),
    _write(), _read()...
    """

    # Multimeter functions
    (CAP, CURR, CURRDC, VOLTAC, VOLTDC, VOLTDCRAT, RES, FRES, FRE, PER,
    TEMPRTD, TEMPFRTD, DIOD, CONT) = ("CAP", "CURR", "CURR:DC",
                                      "VOLT:AC", "VOLT:DC", "VOLT:DC:RAT",
                                      "RES", "FRES", "FRE", "PER",
                                      "TEMP:RTD", "TEMP:FRTD",
                                      "DIOD", "CONT")
    # Integration time
    (PLC002, PLC02, PLC1, PLC10, PLC100) = ("0.02", "0.2", "1", "10", "100")
    # Voltage input range
    (RANGE10MV, RANGE1V, RANGE10V, RANGE100V, RANGE1000V) = ("0.1", "1", "10",
                                                            "100", "1000")
    # Trigger source
    IMM, EXT, BUS = "IMM", "EXT", "BUS"

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)
    outUpdated = pyqtSignal((float,), (str,))

    def __init__(self):
        """The constructor.
        """
        super().__init__()

    @pyqtSlot()
    def connect(self):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        pass

    @pyqtSlot()
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
            self._write(data)
        except Exception:
            pass # Handled in _write() subclass

    def read(self, length):
        """A basic read method: read a message from device.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        try:
            retval = self._read(length)
        except Exception:
            pass # Handled in _read() subclass
        else:
            return retval

    def reset(self):
        """Resets meter to its power-on state, sets all bits to zero in
        status byte register and all event registers and clear error queue.
        :returns: None
        """
        try:
            self._write("*RST\n")
            self._write("*CLS\n")
        except Exception as ex:
            logging.error(str(ex))
        else:
            logging.info("Reset meter")

    def dc_voltage_config(self, intg_time=None, rang=None, res=None, \
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
        try:
            msg = "CONF:VOLT:DC"
            if rang != None:
                msg += " " + rang
                if res != None:
                    msg += ", " + str(res)
            self._write(msg + "\n")
            if a_fltr != None:
                self._write("FILT:DC:STAT" + str(a_fltr) + "\n")
            if intg_time < 1:
                self._write("FILT:DC:DIG:STAT OFF\n")
            elif d_fltr != None:
                self._write("FILT:DC:DIG:STAT" + str(d_fltr) + "\n")
            if intg_time != None:
                self._write("VOLT:DC:NPLC " + str(intg_time) + "\n")
        except Exception as ex:
            logging.error("%s", str(ex))
        else:
            logging.info("DC voltage measurement config done")

    def trigger_config(self, src=IMM, delay=None, delauto=None, scount=None, \
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
        try:
            self._write("TRIG:SOUR " + src + "\n")
            if delauto == 1:
                self._write("TRIG:DEL:AUTO ON\n")
            elif delauto == 0:
                self._write("TRIG:DEL:AUTO OFF\n")
            elif delay != None:
                self._write("TRIG:DEL " + str(delay) + "\n")
            if tcount != None:
                self._write("TRIG:COUN " + str(tcount) + "\n")
            if scount != None:
                self._write("SAMP:COUN " + str(scount) + "\n")
        except Exception as ex:
            logging.error("%s", str(ex))
        else:
            logging.info("Trigger configuration done")

    def init_trig(self):
        """Once the Meter has been configured for a measurement, ini_meas()
        causes the Meter to take a measurement when the trigger conditions have
        been met. The measurement reading(s) are placed in the Meter’s internal
        memory (up to 5,000 to be read at a later time using the FETCh? command.
        :returns: None
        """
        try:
            self._write("INIT\n")
        except Exception as ex:
            logging.error("%s", str(ex))
        else:
            logging.info("Initiate triggering")

    def data_read_fetch(self):
        """To process readings from the Meter’s internal memory to the output
        buffer.
        :returns: data read in internal memory buffer (float)
        """
        try:
            self._write("FETC?\n")
            retval = self._read(100) # Note '100' not used in serial com mode
        except Exception as ex:
            logging.error(str(ex))
        else:
            logging.debug("Data read (fetch) measurement: " + retval)
        return float(retval)

    def data_read(self):
        """Takes a measurement the next time the trigger condition is met.
        After the measurement is taken, the reading is placed in the output
        buffer. "data_read" will not cause readings to be stored in the Meter’s
        internal memory.
        :returns: data read in buffer (float)
        """
        try:
            self._write("READ?\n")
            retval = self._read(100) # Note '100' not used in serial com mode
            if re.match("[\+\-]\d\.\d*E[\+\-]\d\d", retval) is None:
                return None
        except Exception as ex:
            logging.error(str(ex))
            return 0.0  # Default value
        self.outUpdated[str].emit(retval)
        self.outUpdated[float].emit(float(retval))
        logging.debug("Data read measurement: " + retval)
        return float(retval)


class Dmm4050Eth(Dmm4050Abstract):
    """Class using to handle the DMM4050 device through ethernet protocol.
    """

    DEFAULT_IP = "192.168.0.32"
    DEFAULT_PORT = 3490
    DEFAULT_TIMEOUT = 0.5

    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT, \
                 timeout=DEFAULT_TIMEOUT):
        """The constructor.
        :param ip: IP address of device (str)
        :param port: Ethernet port of device (int)
        :param timeout: Socket timeout value in s (float)
        :returns: None
        """
        super().__init__()
        self._sock = None
        self._ip = ip
        self._port = port
        self._timeout = timeout

    @pyqtSlot()
    def connect(self):
        """Specific ethernet connection process to DMM4050.
        :returns: True if connection success other False (Bool)
        """
        self._sock = socket.socket(socket.AF_INET,
                                   socket.SOCK_STREAM,
                                   socket.IPPROTO_TCP)
        self._sock.settimeout(self._timeout)
        try:
            self._sock.connect((self._ip, self._port))
        except ValueError as ex:
            logging.error("Connection parameters out of range: %s", str(ex))
            return False
        except socket.timeout:
            logging.error("Timeout on connection")
            return False
        except Exception as ex:
            logging.critical("Unexpected exception during connection with " + \
                             "DMM4050: %s", str(ex))
            return False
        self.connected.emit()
        logging.info("Connected to DMM4050")
        return True

    @pyqtSlot()
    def close(self):
        """Specific ethernet closing process with DMM4050.
        :returns: True if connection success other False (Bool)
        """
        try:
            self._sock.close()
        except Exception as ex:
            print("dmm.close.exception")
            logging.error("%s", str(ex))
            return False
        self._sock = None
        self.closed.emit()
        logging.info("Connection to DMM4050 closed")
        return True    

    @pyqtSlot()
    def check_interface(self):
        """Basic interface connection test: check id of device.
        Return True if interface with device is OK.
        :returns: status of interface with device (bool)
        """
        try:
            self.connect()
            _id = str(self.get_id())
        except Exception:  # Catch connection and get_id problem
            _id = ""  # To avoid error with 'find()' if '_id' is not defined
        else:
            self.close()
        if _id.find(DMM4050_ID) >= 0:
            self.id_checked.emit(True)
            return True
        else:
            self.id_checked.emit(False)
            return False

    def _write(self, data):
        """Specific ethernet writing process.
        :param data: data writes to device (str)
        :returns: None
        """
        try:
            self._sock.send(data.encode('utf8'))
        except socket.timeout:
            logging.error("DMM timeout")
        except Exception as ex:
            logging.error(str(ex))
            raise Exception(ex)
        else:
            logging.debug("_write " + data.strip('\n'))

    def _read(self, length):
        """Specific ethernet reading process.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        try:
            retval = (self._sock.recv(length)).decode('utf-8')
        except socket.timeout:
            logging.error("DMM timeout")
        except Exception as ex:
            logging.error(str(ex))
        else:
            logging.debug("_read %r", retval)
            return retval

    @pyqtSlot()
    def get_id(self):
        """Return product id of device.
        :returns: product id of device (str)
        """
        self._write("*IDN?\n")
        _id = self._read(100)
        return _id

    @pyqtSlot(float)
    def set_timeout(self, timeout):
        """Sets timeout on socket operations.
        :param timeout: timeout value in second (float)
        :returns: None
        """
        self._sock.settimeout(timeout)

    @pyqtSlot()
    def get_timeout(self):
        """Gets timeout on socket operations.
        :returns: timeout value in second (float)
        """
        return self._sock.gettimeout()

    @pyqtSlot(str)
    def set_ip(self, ip):
        """Sets IP address used to speak with device.
        :param ip: IP address (str)
        :return: None
        """
        self._ip = ip

    @pyqtSlot()
    def get_ip(self):
        """Gets IP used to speak with device.
        :returns: IP address (str)
        """
        return self._ip

    @pyqtSlot(int)
    def set_port(self, port):
        """Sets internet port used to speak with device.
        :param port: port used by dmm4050 (int)
        :returns: None
        """
        self._port = port

    @pyqtSlot()
    def get_port(self):
        """Gets internet port used to speak with device.
        :returns: port used by dmm4050 (int)
        """
        return self._port


class Dmm4050Emul(Dmm4050Abstract):
    """Class using to emulate the DMM4050 device.
    """

    def __init__(self, *args):
        super().__init__()
        import random
        self._datas = [random.uniform(-1,1) for _ in range(100)]
        # Add 'spikes'
        self._datas[43], self._datas[74], self._datas[75] = -35, 44, 45
        self._did = 0 # self._datas index
        logging.info("Dmm4050Emul initialized with args :" + str(args))

    @pyqtSlot()
    def check_interface(self):
        """Basic interface connection test: check id of device.
        Return True if interface with device is OK.
        :returns: status of interface with device (bool)
        """
        self.id_checked.emit(True)
        return True
    
    @pyqtSlot()
    def get_id(self):
        super().get_id()

    @pyqtSlot(float)
    def set_timeout(self, timeout):
        logging.debug("Set timeout to " + str(timeout))

    @pyqtSlot()
    def get_timeout(self):
        logging.debug("Get timeout")
        return 0.1

    @pyqtSlot(str)
    def set_ip(self, ip):
        logging.debug("Set ip to " + str(ip))

    @pyqtSlot()
    def get_ip(self):
        logging.debug("Get IP")
        return "192.168.0.2"

    @pyqtSlot(int)
    def set_port(self, port):
        """Sets internet port used to speak with device.
        :param port: port used by dmm4050 (int)
        :returns: None
        """
        logging.debug("Set port to " + str(port))

    @pyqtSlot()
    def get_port(self):
        logging.debug("Get port")
        return 1
                
    @pyqtSlot()
    def connect(self):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        logging.info("Connected to DMM")
        self.connected.emit()
        return True

    @pyqtSlot()
    def close(self):
        """Abstract protocol closing process. Derived classes must implement
        the closing process dedicated to the specific protocol used.
        :returns: None
        """
        logging.info("Connection to DMM closed")
        self.closed.emit()
        return True

    def _write(self, data):
        """Abstract protocol write process. Derived classes must implement
        the write process dedicated to the specific protocol used.
        :param data: data writes to device (str)
        :returns: None
        """
        logging.debug("Write: " + data)

    def _read(self, length):
        """Abstract protocol read process. Derived classes must implement
        the read process dedicated to the specific protocol used.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        retval = self._datas[self._did]
        if self._did < len(self._datas) - 1 :
            self._did += 1
        else:
            self._did = 0
        logging.info("Read: %E", retval)
        return "{:+E}".format(retval)

    def write(self, data):
        """A basic write method: writes "data" to device.
        :param data: data writes to device (str)
        :returns: None
        """
        super().write(data)

    def read(self, length):
        """A basic read method: read a message from device.
        :param length: length of message to read (int)
        :returns: Message reads from device (str)
        """
        super().read(length)

    def reset(self):
        """Resets meter to its power-on state, sets all bits to zero in
        status byte register and all event registers and clear error queue.
        :returns: None
        """
        super().reset()

    def dc_voltage_config(self, intg_time=None, rang=None, res=None, \
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
        super().dc_voltage_config(intg_time, rang, res, d_fltr, a_fltr)

    def trigger_config(self, src=None, delay=None, delauto=None, scount=None, \
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
        super().trigger_config(src, delay, delauto, scount, tcount)

    def init_trig(self):
        """Once the Meter has been configured for a measurement, ini_meas()
        causes the Meter to take a measurement when the trigger conditions have
        been met. The measurement reading(s) are placed in the Meter’s internal
        memory (up to 5,000 to be read at a later time using the FETCh? command.
        :returns: None
        """
        super().init_trig()

    def data_read_fetch(self):
        """To process readings from the Meter’s internal memory to the output
        buffer.
        :returns: data read in internal memory buffer (float)
        """
        super().data_read_fetch()

    def data_read(self):
        """Takes a measurement the next time the trigger condition is met.
        After the measurement is taken, the reading is placed in the output
        buffer. "data_read" will not cause readings to be stored in the Meter’s
        internal memory.
        :returns: data read in buffer (float)
        """
        super().data_read()
    

def check_dmm4050():
    """Checks the Dmm4050xx class: connects to the multimeter, configures a dc
    voltage measurement then collects and prints data to standard output.
    Values that work:
    - 1PLC with 0.5 de rtimeout
    - 10PLC with 0.8 de rtimeout
    """
    from datetime import datetime

    date_fmt = "%d/%m/%Y %H:%M:%S"
    log_format = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.INFO, \
                        datefmt=date_fmt, \
                        format=log_format)

    # dmm4050 = Dmm4050Serial(serport="/dev/ttyUSB0", timeout=0.8)
    dmm4050 = Dmm4050Eth(ip="192.168.0.32", port=3490, timeout=0.8)
    dmm4050.connect()
    dmm4050.reset()
    dmm4050.write("ZERO:AUTO OFF\n")
    dmm4050.write("CONF:VOLT:DC DEF\n") # Autorange
    dmm4050.write("ZERO:AUTO OFF\n") # Autozero off
    dmm4050.write("VOLT:DC:NPLC 10\n")
    dmm4050.write("TRIG:SOUR IMM\n") # Immediate trigger source
    dmm4050.write("TRIG:DEL 0\n")   # No trigger delay
    dmm4050.write("TRIG:COUN 1\n")  # 1 measurement per trigger
    dmm4050.write("SAMP:COUN 1\n")  # 1 sample per trigger
    dmm4050.write("SYST:REM\n") # DMM in remote mode
    try:
        while True:
            value = dmm4050.data_read()
            now = datetime.utcnow()
            if value is None or  value == "":
                print("# No data @", now)
            else:
                print(now, value)
    except KeyboardInterrupt:
        pass
    except Exception as er:
        print("# Exception during acquisition: " + str(er))
    dmm4050.reset()
    dmm4050.write("SYST:LOC\n")
    dmm4050.close()


if __name__ == '__main__':
    check_dmm4050()
