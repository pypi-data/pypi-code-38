import datetime
import sys
if sys.platform != 'win32':
    import usbtmc
import usb.core
import usb.util
import usb.control
from gateway_helpers import logger


def get_timestamp():
    return str(datetime.datetime.now())


class UsbController(object):
    """Generic UsbController for talking to instruments"""
    def __init__(self, name):
        super(UsbController, self).__init__()
        self.name = name

    def get_instrument(self, mnf_id, dev_id):
        if sys.platform != 'win32':
            self.instr = usbtmc.Instrument(mnf_id, dev_id)
        return self.instr

    def ask(self, instr=None, command=""):
        logger.info("USB ask: %s" % command)
        if not instr:
            instr = self.instr

        response = instr.ask(command)
        return response


class RawUsbController(object):
    """Generic RawUsbController for sending usb commands"""
    def __init__(self, vendor_id=0x227f, product_id=0x0002):
        super(RawUsbController, self).__init__()
        #  instanatiates the device based off the VID/PIDs.
        self.device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

    def ask(self, instr=None, command=""):
        logger.info("USB ask: %s" % command)
        if not instr:
            instr = self.instr

        response = instr.ask(command)
        return response

    def write(self, ep=0x02, command='\x14\x05'):
        """the write command takes end point and the commands as arguments."""
        logger.info("USB write: %s" % command)
        if not self.device:
            logger.warning("missing device")
            return

        self.device.write(ep, command)
