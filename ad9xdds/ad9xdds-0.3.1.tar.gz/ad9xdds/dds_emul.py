# -*- coding: utf-8 -*-

"""package ad9xdds
author  Benoit Dubois
version 0.2
date    2014-01-12
brief   API to control various DDS.
details -Ad9912Dev: AD9912 DDS development card class.
        -Ad9854Dev: AD9852/4 DDS development card class.
        Note need importlib module for all class, parallel for Ad9854Dev class
        and usb.(core|util|control) for class Ad9912Dev.
"""

import logging
from dds.dds_core import AbstractDds, bound_value, split_len

AD_VENDOR_ID = 0x0456
AD9912DEV_PRODUCT_ID = 0xee09
AD9549DEV_PRODUCT_ID = 0xee08
DDS_DEVICE_LIST = {'AD9912': 'Ad9912Dev'}


#==============================================================================
class TestUsbDds(AbstractDds):
    """Class 'emulating' a DDS development card.
    Used for test when no real device is available.
    """

    FTW_SIZE = 48               # Frequency Tuning Word register size (bit)
    PHASE_SIZE = 14             # Phase register size (bit)
    DAC_OUT_SIZE = 10           # Output DAC resolution (bit)
    IFMAX = 1000000000          # Input maximum frequency (Hz)
    OFMAX = 400000000           # Output maximum frequency (Hz)
    AMAX = (1<<DAC_OUT_SIZE)-1


    def __init__(self):
        super(TestUsbDds, self).__init__()
        self._ifreq = None
        self._ofreq = None
        self._phy = None
        self._amp = None
        logging.info("Init DDS test device:")

    def connect(self):
        logging.info("Connect to DDS test device")
        return True

    def get_ifreq(self):
        logging.debug("DdsTestDev.get_ifreq() = " + str(self._ifreq))
        return self._ifreq

    def set_ifreq(self, ifreq):
        logging.debug("DdsTestDev.set_ifreq(" + str(ifreq) + ")")
        self._ifreq = float(ifreq)

    def get_ifreq(self):
        logging.debug("DdsTestDev.get_ifreq() = " + str(self._ifreq))
        return self._ifreq

    def set_ofreq(self, ofreq):
        logging.info("DdsTestDev.set_ofreq(" + str(ofreq) + ")")
        self._ofreq = float(ofreq)
        return ofreq

    def get_ofreq(self):
        logging.debug("DdsTestDev.get_ofreq() = " + str(self._ofreq))
        return self._ofreq

    def set_phy(self, phy):
        logging.debug("DdsTestDev.set_phy(" + str(phy) + ")")
        self._phy = phy
        return phy

    def get_phy(self):
        logging.debug("DdsTestDev.get_phy() = " + str(self._phy))
        return self._phy

    def set_amp(self, fsc):
        logging.debug("DdsTestDev.set_amp(" + str(fsc) + ")")
        self._amp = fsc
        return fsc

    def get_amp(self):
        logging.debug("DdsTestDev.get_amp() = " + str(self._amp))
        return self._amp

    def set_hstl_output_state(self, state=False):
        logging.debug("Set HSTL output state to: " + str(state))

    def get_hstl_output_state(self):
        pass

    def set_cmos_output_state(self, state=False):
        logging.debug("Set CMOS output state to: " + str(state))

    def get_cmos_output_state(self):
        pass

    def set_pll_state(self, state=False):
        logging.debug("Set PLL state to: %s", str(state))

    def get_pll_state(self):
        pass

    def set_cp_current(self, value=0):
        logging.debug("Set charge pump current to: " + str(value))

    def get_cp_current(self):
        pass

    def set_vco_range(self, value=None):
        logging.debug("Set VCO range to: " + str(value))

    def get_vco_range(self):
        pass

    def set_hstl_doubler_state(self, flag=False):
        logging.debug("Set HSTL doubler state to: " + str(flag))

    def get_hstl_doubler_state(self):
        pass

    def set_pll_doubler_state(self, flag=False):
        logging.debug("Set PLL doubler state to: " + str(flag))

    def get_pll_doubler_state(self):
        pass

    def set_pll_multiplier_factor(self, factor):
        logging.debug("Set PLL multiplier factor to: " + str(factor))

    def get_pll_multiplier_factor(self):
        pass

    def set_led(self, flag=False):
        logging.debug("Set LED blink: " + str(flag))

    def set_reg(self, address, value):
        logging.debug("Set " + str(value) + " @adress "  + str(adress))

    def get_reg(self, address):
        pass


#==============================================================================
if __name__ == '__main__':
    IFREQ = 10000000.0
    OFREQ = 1000000.0
    DDS = TestUsbDds()
    DDS.set_ifreq(IFREQ)
    DDS.set_ofreq(OFREQ)
