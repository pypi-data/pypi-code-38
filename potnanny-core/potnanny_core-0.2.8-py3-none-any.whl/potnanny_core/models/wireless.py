import os
import logging
import time
from potnanny_core.utils import subprocess_cmd
from potnanny_core.models.setting import PrimitiveWirelessSetting

logger = logging.getLogger(__name__)


class WirelessInterface(object):
    """Class for scanning and transmitting 433Mhz RF codes."""

    def __init__(self, *args, **kwargs):
        self.settings = PrimitiveWirelessSetting.get()
        if not self.settings:
            raise RuntimeError("Wireless not configured")


    def send_code(self, code):
        """
        Transmit code to wireless outlets.

        args:
            - code (str, like "code protocol bits", "12345678 2 24")
        returns:
            bool
        raises:
            RuntimeError if no RF interfaces are found
        """

        # we pause here, to prevent consecutive rf_send commands from being
        # too close, corrupted and being received incorrectly.
        time.sleep(0.2)

        code, protocol, bits = code.split()
        if 'rf_send' in self.settings:
            cmd = [
                self.settings['rf_send'],
                code,
                protocol,
                self.settings['pulse_width'],
                self.settings['transmit_pin']
            ]
            rval, output, errors = subprocess_cmd(cmd)
            if rval:
                logger.warning("rf_send command ({}) failed. {}".format(" ".join(cmd), errors))
                return False

            return True
        else:
            raise RuntimeError("No RF Interfaces defined")


    def scan_code(self):
        """
        Scan a remote code from wireless receiver.

        args:
            none
        returns:
            str
        raises:
            RuntimeError if no RF interfaces are found
        """

        if 'rf_scan' in self.settings:
            cmd = [
                self.settings['rf_scan'],
                self.settings['receive_pin'],
                self.settings['pulse_width']
            ]
            rval, output, errors = subprocess_cmd(cmd)

            if rval:
                logger.warning("rf_scan command failed. {}".format(errors))
                return None

            return output.strip()

        else:
            raise RuntimeError("No RF Interfaces defined")
