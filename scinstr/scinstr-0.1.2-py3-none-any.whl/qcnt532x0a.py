# -*- coding: utf-8 -*-

"""package scinstr
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     API dedicated to handle the Keysight 532X0A counter serie with
          PyQt signal/slot capabilities.
"""

import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from scinstr.cnt532x0a import Cnt532x0aEth, Cnt532x0aUsb
import scinstr.constants as scst


# =============================================================================
class QObjectAdapter(QObject):
    """cf https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
    "How to Incorporate a Non-cooperative Class"
    """
    def __init__(self, **kwargs):
        self._object = QObject(*kwargs)
        super().__init__(**kwargs)


#==============================================================================
class QCnt532x0aUsb(QObjectAdapter, Cnt532x0aUsb):
    """Class derived from Cnt532x0aEth class to add PyQt facilities.
    """

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)
    outUpdated = pyqtSignal((float,), (str,))

    def __init__(self, vendor_id=scst.CNT532X0A_VID,
                 product_id=scst.CNT532X0A_PID,
                 timeout=scst.CNT532X0A_TIMEOUT):
        QObject.__init__(self)
        Cnt532x0aUsb.__init__(self, vendor_id, product_id, timeout)

    @pyqtSlot(object)
    def connect(self, **kwargs):
        """Connection process.
        :returns: True if connection is ok else False (bool)
        """
        retval = Cnt532x0aUsb.connect(self, **kwargs)
        if retval is True:
            self.connected.emit()
        return retval

    @pyqtSlot()
    def close(self):
        """Closing process.
        :returns: None
        """
        Cnt532x0aUsb.close(self)
        self.closed.emit()

    @pyqtSlot()
    def check_interface(self):
        retval = Cnt532x0aUsb.check_interface(self)
        self.id_checked.emit(retval)
        return retval

    @pyqtSlot()
    def data_read(self):
        retval, errors = Cnt532x0aUsb.data_read(self)
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


#==============================================================================
class QCnt532x0aEth(QObjectAdapter, Cnt532x0aEth):
    """Class derived from Cnt532x0aEth class to add PyQt facilities.
    """

    connected = pyqtSignal()
    closed = pyqtSignal()
    id_checked = pyqtSignal(bool)
    outUpdated = pyqtSignal((float,), (str,))

    def __init__(self, ip=None,
                 port=scst.CNT532X0A_PORT,
                 timeout=scst.CNT532X0A_TIMEOUT):
        QObject.__init__(self)
        Cnt532x0aEth.__init__(self, ip, port, timeout)

    @pyqtSlot(object)
    def connect(self, **kwargs):
        """Abstract protocol connect process. Derived classes must implement
        the connect process dedicated to the specific protocol used.
        :returns: None
        """
        retval = Cnt532x0aEth.connect(self, **kwargs)
        if retval is True:
            self.connected.emit()
        return retval

    @pyqtSlot()
    def close(self):
        """Abstract protocol closing process. Derived classes must implement
        the closing process dedicated to the specific protocol used.
        :returns: None
        """
        Cnt532x0aEth.close(self)
        self.closed.emit()

    @pyqtSlot()
    def check_interface(self):
        retval = Cnt532x0aEth.check_interface(self)
        self.id_checked.emit(retval)
        return retval

    @pyqtSlot()
    def data_read(self):
        retval, errors = Cnt532x0aEth.data_read(self)
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


#==============================================================================
def check_counter532x0a():
    """Checks the Counter532x0axx class: connects to the multimeter, configures a dc
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

    counter = QCnt532x0aUsb(0x0957, 0x1707, timeout=2.8)
    #counter = Counter532x0aEth(ip="192.168.0.20", port=5025, timeout=1.5)
    if counter.connect() is not True:
        print("Connection failed")
        return
    counter.reset()
    print("IDN:", counter.idn())
    counter.write("CONF:FREQ 100.0E6")
    counter.write("TRIG:SLOP POS")
    counter.write("SENS:FREQ:GATE:TIME 1.0")
    counter.write("SENS:FREQ:GATE:SOUR TIME")
    print("Error config?:", counter.check_error())

    try:
        while True:
            value = counter.data_read()
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
    counter.reset()
    counter.close()


#==============================================================================
if __name__ == '__main__':
    check_counter532x0a()
