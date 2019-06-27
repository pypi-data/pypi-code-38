# -*- coding: utf-8 -*-

"""package scinstr
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     API dedicated to handle the Keysight 34461A digital multimeter
          with PyQt signal/slot capabilities.
"""

import logging
import re
import socket

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from scinstr.dmm34461a import Dmm34461aUsb, Dmm34461aEth
import scinstr.constants as scst


# =============================================================================
class QObjectAdapter(QObject):
    """cf https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
    "How to Incorporate a Non-cooperative Class"
    """
    def __init__(self, **kwargs):
        self._object = QObject(*kwargs)
        super().__init__(**kwargs)


# =============================================================================
class QDmm34461aUsb(QObjectAdapter, Dmm34461aUsb):
    """Class derived from Dmm34461aEth class to add PyQt facilities.
    """

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)
    outUpdated = pyqtSignal((float,), (str,))

    def __init__(self, vendor_id=scst.DMM34461A_VID,
                 product_id=scst.DMM34461A_PID,
                 timeout=scst.DMM34461A_TIMEOUT):
        QObject.__init__(self)
        Dmm34461aUsb.__init__(self, vendor_id, product_id, timeout)

    @pyqtSlot(object)
    def connect(self, **kwargs):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        retval = Dmm34461aUsb.connect(self, **kwargs)
        if retval is True:
            self.connected.emit()
        return retval

    @pyqtSlot()
    def close(self):
        """Abstract protocol closing process. Derived classes must implement
        the closing process dedicated to the specific protocol used.
        :returns: None
        """
        Dmm34461aUsb.connect(self)
        self.closed.emit()

    @pyqtSlot()
    def check_interface(self):
        retval = Dmm34461aUsb.check_interface(self)
        self.id_checked.emit(retval)
        return retval

    @pyqtSlot()
    def data_read(self):
        retval, errors = Dmm34461aUsb.data_read(self)
        if retval is not None:
            self.outUpdated[str].emit(str(retval))
            self.outUpdated[float].emit(retval)
            return retval, errors

    @pyqtSlot(float)
    def set_timeout(self, timeout):
        """Sets timeout on operations.
        :param timeout: timeout value in second (float)
        :returns: None
        """
        self.timeout = timeout

    @pyqtSlot()
    def get_timeout(self):
        """Gets timeout on socket operations.
        :returns: timeout value in second (float)
        """
        return self.timeout

    @pyqtSlot(str)
    def set_pid(self, pid):
        """
        :param pid:
        :returns: None
        """
        self.pid = pid

    @pyqtSlot()
    def get_pid(self):
        """
        :returns: pid
        """
        return self.pid

    @pyqtSlot(str)
    def set_vid(self, vid):
        """
        :param vid:
        :returns: None
        """
        self.vid = vid

    @pyqtSlot()
    def get_vid(self):
        """
        :returns: vid
        """
        return self.vid


# =============================================================================
class QDmm34461aEth(QObjectAdapter, Dmm34461aEth):
    """Class derived from Dmm34461aEth class to add PyQt facilities.
    """

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)
    outUpdated = pyqtSignal((float,), (str,))

    def __init__(self, ip=None, port=scst.DMM34461A_PORT,
                 timeout=scst.DMM34461A_TIMEOUT):
        QObject.__init__(self)
        Dmm34461aEth.__init__(self, ip, port, timeout)

    @pyqtSlot(object)
    def connect(self, **kwargs):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        retval = Dmm34461aEth.connect(self, **kwargs)
        if retval is True:
            self.connected.emit()
        return retval

    @pyqtSlot()
    def close(self):
        """Abstract protocol closing process. Derived classes must implement
        the closing process dedicated to the specific protocol used.
        :returns: None
        """
        Dmm34461aEth.connect(self)
        self.closed.emit()

    @pyqtSlot()
    def check_interface(self):
        retval = Dmm34461aEth.check_interface(self)
        self.id_checked.emit(retval)
        return retval

    @pyqtSlot()
    def data_read(self):
        retval, errors = Dmm34461aEth.data_read(self)
        if retval is not None:
            self.outUpdated[str].emit(str(retval))
            self.outUpdated[float].emit(retval)
            return retval, errors

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
        :param port: port used by counter532x0a (int)
        :returns: None
        """
        self._port = port

    @pyqtSlot()
    def get_port(self):
        """Gets internet port used to speak with device.
        :returns: port used by counter532x0a (int)
        """
        return self._port


# =============================================================================
def check_qdmm34461a():
    """Checks the Dmm34461axx class: connects to the multimeter, configures a dc
    voltage measurement then collects and prints data to standard output.
    Values that work:
    - 1PLC with 0.5 de rtimeout
    - 10PLC with 0.8 de rtimeout
    """
    from datetime import datetime
    #from mjdutil import datetime_to_mjd

    date_fmt = "%d/%m/%Y %H:%M:%S"
    log_format = "%(asctime)s %(levelname) -8s %(filename)s " + \
                 " %(funcName)s (%(lineno)d): %(message)s"
    logging.basicConfig(level=logging.INFO,
                        datefmt=date_fmt,
                        format=log_format)

    #dmm34461a = Dmm34461aSerial(serport="/dev/ttyUSB0", timeout=0.8)
    dmm34461a = QDmm34461aUsb(0x2a8d, 0x1601, timeout=4.8)
    #dmm34461a = Dmm34461aEth(ip="192.168.0.61", port=5025, timeout=2.8)
    if dmm34461a.connect() is not True:
        print("Connection failed")
        return
    dmm34461a.reset()
    dmm34461a.write("CONF:VOLT:DC AUTO") # Autorange
    dmm34461a.write("VOLT:ZERO:AUTO ON") # Autozero off
    dmm34461a.write("VOLT:DC:NPLC 100")
    #dmm34461a.write("TRIG:SOUR IMM") # Immediate trigger source
    #dmm34461a.write("TRIG:DEL 0")   # No trigger delay
    #dmm34461a.write("TRIG:COUN 1")  # 1 measurement per trigger
    #dmm34461a.write("SAMP:COUN 1")  # 1 sample per trigger
    try:
        while True:
            value = dmm34461a.data_read()
            now = datetime.utcnow()
            if value is None or  value == "":
                print("# No data @", now)
            else:
                #print(now, '{:0.14f}'.format(value.strip('\n')))
                print(now, value)
    except KeyboardInterrupt:
        pass
    except Exception as er:
        print("# Exception during acquisition: " + str(er))
    dmm34461a.reset()
    dmm34461a.write("SYST:LOC\n")
    dmm34461a.close()


# =============================================================================
if __name__ == '__main__':
    check_qdmm34461a()
