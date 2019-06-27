# -*- coding: utf-8 -*-

"""package ad9xdds
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     API to control AD9912 DDS development board.
details   AD9912 development board is configurable by USB through an USB
          to serial transceiver from Cypress (FX2 device). Class allows
          configuration of principle DDS parameters (frequency, phase,
          amplitude, PLL handling, output handling...).
"""

import logging
from array import array
import usb.core
from iopy.fx2 import Fx2Core

AD_VENDOR_ID = 0x0456
AD9912DEV_PRODUCT_ID = 0xee09

VENDOR_ID = AD_VENDOR_ID
PRODUCT_ID = AD9912DEV_PRODUCT_ID

FTW_SIZE = 48               # Frequency Tuning Word register size (bit)
PHASE_SIZE = 14             # Phase register size (bit)
DAC_OUT_SIZE = 12           # Output DAC resolution (bit)

IFMAX = 1000000000          # Input maximum frequency (Hz)
OFMAX = 400000000           # Output maximum frequency (Hz)
AMAX = (1<<DAC_OUT_SIZE)-1  # Output maximum amplitude (a.u.)


# =============================================================================
def split_len(seq, length):
    """Take data of sequence type and return a list containing the n-sized
    pieces of the string.
    For example: split_len('aabbccdd', 2) => ['aa', 'bb', 'cc', 'dd']
    arg    seq     Any sequences that support slicing and len().
    arg    length  Size of slice (int).
    return         Splited sequence (list of str).
    """
    return [seq[i:i+length] for i in range(0, len(seq), length)]


# =============================================================================
def bound_value(value, vmin, vmax, val_name=""):
    """Check that a value is included in the range [min, max], if not the value
    is bounded to the range, ie:
    - if value < min  ->  min = value
    - if value > max  ->  max = value
    :param value: Value that is checked
    :param vmin: Minimum valid value.
    :param vmax: Maximum valid value.
    :returns: Bounded value.
    """
    if value < vmin:
        logging.warning("Parameter %s out of range (%f). Set to: %f",
                        val_name, value, vmin)
        return vmin
    elif value > vmax:
        logging.warning("Parameter %s out of range (%f). Set to: %f",
                        val_name, value, vmax)
        return vmax
    else:
        return value


# =============================================================================
class Ad9912Dev(object):
    """Class representing AD9912 development card.
    Board integrates an USB port for transmission with PC and a Cypress FX2
    device is used as USB transceiver.
    """
    
    _CONFIG_ID     = 1
    _INTERFACE_ID  = 0       # The interface we use to talk to the device
    _ALT_INTF_ID   = 0       # The alternate interface use to talk to the device
    _IN_EP_ID      = 1       # EP1_IN @0x81 = 129 -> small endpoint
    _OUT_EP_ID     = 0       # EP1_OUT @0x01 = 1  -> small endpoint
    _IN_DAT_EP_ID  = 5       # EP8 @0x88 = 136    -> large endpoint
    _OUT_DAT_EP_ID = 3       # EP4 @0x04 = 4      -> large endpoint

    _regName2addr = {'SerPortCfg': 0x0, 'PartIdLsb': 0x2, 'PartIdMsb': 0x3,
                     'SerOpt': 0x4, 'SerOptClr': 0x5, 'PDEn': 0x10,
                     'ResetAuto': 0x12, 'ResetNAuto': 0x13, 'Ndivider': 0x20,
                     'PllParam': 0x22, 'SdivLsb': 0x104, 'SdivMsb': 0x105,
                     'SdivCfg': 0x106, 'Ftw0_0': 0x1a6, 'Ftw0_1': 0x1a7,
                     'Ftw0_2': 0x1a8, 'Ftw0_3': 0x1a9, 'Ftw0_4': 0x1aa,
                     'Ftw0_5': 0x1ab, 'ACphase': 0x1ac, 'ADphase': 0x1ad,
                     'HstlDrv': 0x200, 'CmosDrv': 0x201, 'DacFsLsb': 0x40b,
                     'DacFsMsb': 0x40c, 'SpurA': 0x500, 'SpurAmag': 0x501,
                     'SpurAphLsb': 0x503, 'SpurAphMsb': 0x504,
                     'SpurB': 0x505, 'SpurBmag': 0x506,
                     'SpurBphLsb': 0x508, 'SpurBphMsb': 0x509}

    def __init__(self, ifreq=IFMAX):
        """The constructor.
        :param ifreq: Current input frequency in Hz (float))
        :returns: None
        """
        super().__init__()
        self._fx2 = Fx2Core()  # USB interface
        self._ifreq = ifreq
        self._ofreq = None
        self._phy = None
        self._amp = None
        self._pll_state = None
        self._pll_doubler_state = None
        self._pll_factor = None
        
    def connect(self, vendor_id=VENDOR_ID, product_id=PRODUCT_ID):
        """Configure USB device defined by is VID:PID.
        :param vendor_id: identification number of vendor (int)
        :param product_id: identification number of product (int)
        :returns: True if connection is Ok else returns False (bool)
        """
        if self._fx2.connect(vendor_id, product_id) is False:
            return False
        try:
            self._fx2.config(config_id=self._CONFIG_ID,
                             interface_id=self._INTERFACE_ID,
                             alt_interface_id=self._ALT_INTF_ID,
                             in_ep_id=self._IN_EP_ID,
                             out_ep_id=self._OUT_EP_ID,
                             in_dat_ep_id=self._IN_DAT_EP_ID,
                             out_dat_ep_id=self._OUT_DAT_EP_ID)
        except Exception as ex:
            logging.error("FX2 USB config failed: %r", ex)
            return False
        self.set_led(False)  # Disable LED blinking of development board
        self._init()
        logging.debug("Connected to AD9912 board")
        return True

    def is_connected(self):
        return self._fx2.is_connected()

    def _init(self):
        """Init properties
        """
        # !warning! parameter order initialisation is important
        if self._pll_state is None:
            self._pll_state = self.get_pll_state()
        else:
            self.set_pll_state(self._pll_state)
        if self._pll_doubler_state is None:
            self._pll_doubler_state = self.get_pll_doubler_state()
        else:
            self.set_pll_doubler_state(self._pll_doubler_state)
        if self._pll_factor is None:
            self._pll_factor = self.get_pll_multiplier_factor()
        else:
            self.set_pll_multiplier_factor(self._pll_factor)
        if self._ofreq is None:
            self._ofreq = self.get_ofreq()
        else:
            self.set_ofreq(self._ofreq)
        if self._phy is None:
            self._phy = self.get_phy()
        else:
            self.set_phy(self._phy)
        if self._amp is None:
            self._amp = self.get_amp()
        else:
            self.set_amp(self._amp)

    def set_ifreq(self, ifreq):
        """Set input frequency.
        :param ifreq: Input frequency value (float)
        :returns: None
        """
        self._ifreq = ifreq
        logging.debug("Set input frequency: %s", str(ifreq))
        # Update DDS device because ofreq = f(ifreq)
        self.set_ofreq(self._ofreq)

    def get_ifreq(self):
        """Get input frequency.
        :returns: Current input frequency value (float)
        """
        return self._ifreq

    def get_sysfreq(self):
        """Get system frequency.
        :returns: Current system frequency value (float)
        """
        if self._pll_state is True:
            ifreq = self._ifreq
            if self._pll_doubler_state is True:
                doubler = 2.0
            else:
                doubler = 1.0
            factor = self._pll_factor
            sfreq = ifreq * doubler * factor
        else:
            sfreq = self._ifreq
        return sfreq

    def set_ofreq(self, ofreq):
        """Set output frequency on DDS.
        Take the input and output frequency as argument and set the adequat
        register in the DDS and return the actual output frequency (see
        _actual_ofreq()).
        output frequency may be (a bit) different than  The
        :param ofreq: Output frequency (float).
        :returns: Actual output frequency (float)
        """
        if self.is_connected() is False:
            self._ofreq = ofreq
            return ofreq
        # Compute the Frequency Tuning Word (FTW).
        ftw = int((ofreq * (1 << FTW_SIZE)) / self.get_sysfreq())
        # Prepare list of value to send to the 6 FTW0 registers.
        ftw_val_list = split_len(format(ftw, '012x'), 2)
        # Send values to the 6 FTW0 registers of the DDS.
        for idx, ftw_val in enumerate(ftw_val_list):
            self.set_reg(self._regName2addr['Ftw0_5']-idx, int(ftw_val, 16))
        # Return the actual output frequency.
        self._ofreq = self._actual_ofreq(self.get_sysfreq(), ftw, FTW_SIZE)
        logging.debug("Set output frequency: %s", str(self._ofreq))
        return self._ofreq

    def get_ofreq(self):
        """Get output frequency of DDS.
        :returns: Output frequency of DDS (float).
        """
        # Get back the Frequency Tuning Word (FTW) from device.
        ftw = 0
        for idx in range(0, 6):
            ftw += self.get_reg(self._regName2addr['Ftw0_0']+idx) << (idx*8)
        self._ofreq = self._actual_ofreq(self.get_sysfreq(), ftw, FTW_SIZE)
        return self._ofreq

    def set_phy(self, phy):
        """Set phase of output signal on DDS.
        Take the queried output phase (in degree) as argument and set
        the adequat register in the DDS.
        :param phy:  Output phase (float).
        :returns: Actual output phase (float)
        """
        if self.is_connected() is False:
            self._phy = phy
            return phy
        # Compute dphy ("delta phase")
        dphy = int((phy * (1 << PHASE_SIZE)) / 360)
        # Prepare list of value to send to the dphy registers.
        dphy_val_list = split_len(format(dphy, '04x'), 2)
        # Send values to the dphy registers of the DDS.
        # TODO Search a better way to find reg address.
        for idx, val in enumerate(dphy_val_list):
            self.set_reg(self._regName2addr['ADphase']-idx, int(val, 16))
        # Return the actual output phase
        adphy = self.actual_phy(dphy)
        logging.debug("Set phase: %s", str(adphy))
        return adphy

    def get_phy(self):
        """Get output phase of DDS.
        :returns:  Output phase of DDS (float).
        """
        # Get back the dphy register content
        dphy = 0
        for idx in range(0, 2):
            dphy += self.get_reg(self._regName2addr['ACphase']+idx) << (idx*8)
        # return the ofreq.
        return self.actual_phy(dphy)

    def set_amp(self, amp):
        """Set amplitude tuning word of output signal on DDS.
        Take the input and output frequency as argument and set the adequat
        register in the DDS.
        :param amp: Output amplitude (int)
        :returns: fsc register value if transfert is ok (int)
        """
        # If value is out of range, bound value and raise Warning.
        if not(0 <= amp <= AMAX):
            amp = bound_value(amp, 0, AMAX)
            logging.warning("Amplitude value out of range")
            logging.info("Amplitude set to " + str(amp))
        if self.is_connected() is False:
            self._amp = amp
            return amp
        # Prepare list of value to send to the fsc registers.
        fsc_val_list = split_len(format(amp, '04x'), 2)
        # Send values to the fsc registers of the DDS.
        # TODO Search a better way to find reg address.
        for idx, val in enumerate(fsc_val_list):
            self.set_reg(self._regName2addr['DacFsMsb']-idx, int(val, 16))
        # Return the amplitude value if transfert ok.
        logging.debug("Set output amplitude: %s", str(amp))
        return amp

    def get_amp(self):
        """Get output amplitude tuning word of DDS.
        :returns:  Output amplitude tuning of DDS (float).
        """
        # Get back the FSC register (Full Scale) register content
        fsc = 0
        for idx in range(0, 2):
            fsc += self.get_reg(self._regName2addr['DacFsLsb']+idx) << (idx*8)
        # Return the amplitude tuning word.
        return fsc

    def actual_phy(self, dphy):
        """Public function for specific AD9912 product.
        :param dphy: Phase register value (float).
        :returns: Actual output phase offset in degree (float).
        """
        return self._actual_phy(dphy, PHASE_SIZE)

    def set_hstl_output_state(self, state=False):
        """Set HSTL output state.
        :param state: - False  Disable HSTL output. (bool)
                      - True   Enable HSTL output.
        :returns: None
        """
        if self.is_connected() is not True:
            return
        reg = self.get_reg(self._regName2addr['PDEn'])
        if state == True:
            mask = ~(1 << 7)
            msg = reg & mask
        else:
            mask = 1 << 7
            msg = reg | mask
        self.set_reg(self._regName2addr['PDEn'], msg)
        logging.debug("Set HSTL output state to: %s", str(state))

    def get_hstl_output_state(self):
        """Get HSTL output state.
        :returns: HSTL output state (bool)
        """
        # Get back the Power Down and Enable register
        pd_en = self.get_reg(self._regName2addr['PDEn'])
        # return the HSTL output state
        hstl = pd_en & (1 << 7)
        if hstl == 0:
            retval = True
        else:
            retval = False
        return retval

    def set_cmos_output_state(self, state=False):
        """Set CMOS output state.
        :param state: - False  Disable CMOS output. (bool)
                      - True   Enable CMOS output.
        :returns: None
        """
        if self.is_connected() is not True:
            return
        reg = self.get_reg(self._regName2addr['PDEn'])
        if state == True:
            mask = 1 << 6
            msg = reg | mask
        else:
            mask = ~(1 << 6)
            msg = reg & mask
        self.set_reg(self._regName2addr['PDEn'], msg)
        logging.debug("Set CMOS output state to: %s", str(state))

    def get_cmos_output_state(self):
        """Get CMOS output state.
        :returns: CMOS output state (bool)
        """
        # Get back the Power Down and Enable register
        pd_en = self.get_reg(self._regName2addr['PDEn'])
        # return the CMOS output state
        cmos = pd_en & (1 << 6)
        if cmos == 0:
            retval = False
        else:
            retval = True
        return retval

    def set_pll_state(self, state=False):
        """Set PLL multiplier state.
        Note: A modification of the PLL state modify the output frequency.
        :param state: - False  Disable PLL. (bool)
                      - True   Enable PLL.
        :returns: None
        """
        if self.is_connected() is True:
            reg = self.get_reg(self._regName2addr['PDEn'])
            if state == True:
                mask = ~(1 << 4)
                msg = reg & mask
            else:
                mask = 1 << 4
                msg = reg | mask
            self.set_reg(self._regName2addr['PDEn'], msg)
        self._pll_state = state
        logging.debug("Set PLL state to: %s", str(state))

    def get_pll_state(self):
        """Get PLL state.
        :returns: PLL state (bool)
        """
        # Get back the Power Down and Enable register
        pd_en = self.get_reg(self._regName2addr['PDEn'])
        # return the PLL state
        doubler = pd_en & (1 << 4)
        if doubler == 0:
            retval = True
        else:
            retval = False
        return retval

    def set_pll_doubler_state(self, flag=False):
        """Set SysClk PLL doubler state.
        Note: A modification of the PLL doubler state modify the output
        frequency.
        :param flag: - False  Disable frequency doubler. (bool)
                     - True   Enable frequency doubler.
        :returns: None
        """
        if self.is_connected() is True:
            reg = self.get_reg(self._regName2addr['PllParam'])
            if flag == True:
                mask = 1 << 3
                msg = reg | mask
            else:
                mask = ~(1 << 3)
                msg = reg & mask
            self.set_reg(self._regName2addr['PllParam'], msg)
        self._pll_doubler_state = flag
        logging.debug("Set PLL doubler state to: " + str(flag))

    def get_pll_doubler_state(self):
        """Get PLL doubler state.
        :returns: PLL doubler state (bool)
        """
        # Get back the Pll Parameters register
        pll_param = self.get_reg(self._regName2addr['PllParam'])
        # return the PLL doubler state
        doubler = pll_param & (1 << 3)
        if doubler == 1 << 3:
            retval = True
        else:
            retval = False
        return retval

    def set_pll_multiplier_factor(self, factor):
        """Set SysClk PLL multiplier factor.
        Note1: here we assign the overall multiplier factor, so the prescaler
        divider by 2 in the SysClk PLL multiplier block is include in the given
        factor.
        Note2: A modification of the PLL pultiplier factor modify the output
        frequency.
        :param factor: factor of PLL multiplier (between 4 to 66) (int)
        :returns: None
        """
        factor = bound_value(factor, 4, 66, "multiplier")
        if self.is_connected() is True:
            msg = factor / 2 # To take account of prescaler
            self.set_reg(self._regName2addr['Ndivider'], msg)
        self._pll_factor = factor
        logging.debug("Set PLL multiplier factor to: " + str(factor))

    def get_pll_multiplier_factor(self):
        """Get SysClk PLL multiplier factor.
        Note that here we get the overall multiplier factor, so the prescaler
        divider by 2 in the SysClk PLL multiplier block is include in the
        returned factor.
        :returns: factor of PLL multiplier (between 4 to 66) (int)
        """
        n_divider = self.get_reg(self._regName2addr['Ndivider'])
        return n_divider

    def set_cp_current(self, value=0):
        """Set charge pump current value.
        :param value: charge pump current: - 0: 250 uA
                                           - 1: 375 uA
                                           - 2: off
                                           - 3: 125 uA
        :returns: None
        """
        if self.is_connected() is not True:
            return
        reg = self.get_reg(self._regName2addr['PllParam'])
        reg = reg & ~((1<<1) + (1<<0))
        msg = reg + value
        self.set_reg(self._regName2addr['PllParam'], msg)
        logging.debug("Set charge pump current to: " + str(value))

    def get_cp_current(self):
        """Get charge pump current configuration value.
        Charge pump current: - 0: 250 uA
                             - 1: 375 uA
                             - 2: off
                             - 3: 125 uA
        :returns: charge pump current (int)
        """
        # Get back the Pll Parameters register
        pll_param = self.get_reg(self._regName2addr['PllParam'])
        # return the CP current config value.
        retval = pll_param & 3
        return retval

    def set_vco_range(self, value=None):
        """Set VCO range.
        :param value: vco range: - 0 = low range (int)
                                 - 1 = high range
                                 - others = autorange
        :returns: None
        """
        if self.is_connected() is not True:
            return
        reg = self.get_reg(self._regName2addr['PllParam'])
        if value == 0:
            # Disable autorange
            mask = ~(1 << 7)
            reg = reg & mask
            # Set low range
            mask = ~(1 << 2)
            msg = reg & mask
        elif value == 1:
            # Disable autorange
            mask = ~(1 << 7)
            reg = reg & mask
            # Set high range
            mask = 1 << 2
            msg = reg | mask
        else:
            mask = 1 << 7
            msg = reg | mask
        self.set_reg(self._regName2addr['PllParam'], msg)
        logging.debug("Set VCO range to: " + str(value))

    def get_vco_range(self):
        """Get VCO range configuration value.
        vco range: - 0 = low range
                   - 1 = high range
                   - 2 = autorange
        :returns: vco range (int)
        """
        # Get back the Pll Parameters register
        pll_param = self.get_reg(self._regName2addr['PllParam'])
        autorange = pll_param & (1 << 7)
        vcorange = pll_param & (1 << 2)
        # return the VCO range config value.
        if autorange == 1 << 7:
            retval = 2
        else:
            retval = vcorange >> 2
        return retval

    def set_hstl_doubler_state(self, flag=False):
        """Set HSTL output doubler state: multiply HSTL frequecy by 2.
        :param flag: - False  Disable frequency doubler. (bool)
                     - True   Enable frequency doubler.
        :returns: None
        """
        if self.is_connected() is not True:
            return
        # Set HSTL driver register
        reg = self.get_reg(self._regName2addr['HstlDrv'])
        if flag == True:
            mask = 1 << 0
            msg = reg | mask
            mask = ~(1 << 1)
            msg = reg & mask
        else:
            mask = 1 << 1
            msg = reg | mask
            mask = ~(1 << 0)
            msg = reg & mask
        self.set_reg(self._regName2addr['HstlDrv'], msg)
        # Set Power-Down and Enable register
        reg = self.get_reg(self._regName2addr['PDEn'])
        if flag == True:
            mask = 1 << 5
            msg = reg | mask
        else:
            mask = ~(1 << 5)
            msg = reg & mask
        self.set_reg(self._regName2addr['PDEn'], msg)
        #
        logging.debug("Set HSTL doubler state to: " + str(flag))

    def get_hstl_doubler_state(self):
        """Get HSTL doubler state.
        :returns: HSTL doubler state (bool)
        """
        # Get back the Pll Parameters register
        pll_param = self.get_reg(self._regName2addr['HstlDrv'])
        # return the PLL doubler state
        doubler = pll_param & (1 << 1) & (1 << 0)
        if doubler == 2:
            retval = True
        else:
            retval = False
        return retval

    def set_led(self, flag=False):
        """This gives the user control over the USB Status LED on the board.
        :param flag: - False  Stop the firmware controled LED Flashing and
                              gives control to the software.
                     - True   Resume the firmware controled LED Flashing.
        :returns: None
        """
        if self.is_connected() is not True:
            return
        if flag == True:
            msg = array('H', (0x0F, 0x1))
        else:
            msg = array('H', (0x0F, 0x0))
        try:
            self._fx2.write_ctrl(msg)
        except usb.core.USBError as ex:
            logging.error("Could set LED blink: " + str(ex))

    def set_reg(self, address, value):
        """Set register value @ address.
        :param address: Address of the register to write (int).
        :param value: Value to write (int).
        :returns: None
        """
        value = int(value)
        # Build a list of binary value corresponding to the instruction
        bword = self._build_instruct(0, 0, address, value)
        bword = (bin(bword)).replace('0b', '')
        bword = list(bword)
        # Build the formated instruction message
        bword.reverse()
        msg = array('H', [0 for i in range(24)])
        for idx, val in enumerate(bword):
            if val == '1':
                msg[len(msg)-1-idx] = 1
        # Write real data
        self._fx2.write(msg)
        # End write cycle (Set value to portA's pins of FX2 device)
        try:
            end = array('H', (0x01, 0x0B))
            self._fx2._ep_out.write(end)
            end = array('H', (0x01, 0x03))
            self._fx2._ep_out.write(end)
        except usb.core.USBError as ex:
            logging.error("Could not set " + str(value) + " @address " \
                          + str(address) + ", error: " + str(ex))

    def get_reg(self, address):
        """Get register value @ address.
        :param address: address of the register to write (int).
        :returns: register value (int).
        """
        # Sets the number of bytes that must be read back to 8 (0x8).
        init = array('H', (0x07, 0x00, 0x8))
        try:
            self._fx2._ep_out.write(init)
        except usb.core.USBError as ex:
            logging.error("Could not init get register cycle: %s", str(ex))
        # Query register reading operation
        bword = self._build_instruct(1, 0, address)
        bword = (bin(bword)).replace('0b', '')
        bword = list(bword)
        bword.reverse()
        msg = array('H', [0 for i in range(16)])
        for idx, val in enumerate(bword):
            if val == '1':
                msg[len(msg)-1-idx] = 1
        self._fx2.write(msg)
        # Read result.
        raw_data = self._fx2.read()
        # Disable single byte read mode (readback mode).
        end = array('H', (0x04, 0x00))
        try:
            self._fx2._ep_out.write(end)
        except usb.core.USBError as ex:
            logging.error("Could not finish get register cycle: %s", str(ex))
        # Build the register value from the raw data.
        result = 0
        for idx, val in enumerate(raw_data):
            result += int(val) << len(raw_data)-1-idx
        return result

    @staticmethod
    def _build_instruct(rw, bytes2send, reg_addr, reg_value=0):
        """Builds an instruction.
        Take arguments to form adequat instruction.
        Return an array containing the serie of instruction bits
        (i.e. each case of array contains '0' or '1').
        Details:   Prototype of transmission on AD9912 serial bus:
             16 bits header    | (up to) 4 bytes data
        R/W | W1:W0 |  A12:A0  |     ............
        ex: read FTW0_0 register
         1  |  0:0  |  0x0000  |
         => 0x8000
        ex: read Part ID (2 bytes)
         1  |  0:1  |  0x0002  |
         => 0xA002
        :param rw: 1 = read, 0 = Write (int).
        :param bytes2Send: 0=1Byte, 1=2Bytes, 2=3Bytes, 3=4Bytes or more (int).
        :param regAddr: enter the register address to write to (int).
        :param regValue: only if register writing is requested (int).
        :returns: instruction (int)
        """
        if rw == 1:
            rw = 1 << 15
            bytes2send = bytes2send << 13
            instruct = rw + bytes2send + reg_addr
        else:
            bytes2send = bytes2send << 21
            reg_addr = reg_addr << 8
            instruct = rw + bytes2send + reg_addr + reg_value
        return instruct

    @staticmethod
    def _actual_ofreq(ifreq, ftw, rsize):
        """Return the actual output frequency.
        Due to the resolution of the DDS, the actual output frequency
        may be (a bit) different than the queried.
        :param ftw: Frequency Tuning Word register value (int).
        :param rsize: Size of register (int).
        :returns: Actual output frequency (float).
        """
        return (ftw * ifreq) / (1 << rsize)

    @staticmethod
    def _actual_phy(dphy, bit):
        """Return the actual output phase.
        Due to the resolution of the DDS, the actual output phase
        may be (a bit) different than the queried.
        :param dphy: Phase register value (int).
        :param bit: Number of bits used for the phase resolution (int)
        :returns: Actual output phase offset in degree (float).
        """
        return float(360 * dphy) / (1 << bit)

#==============================================================================
if __name__ == '__main__':
    # Setup logger
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s (%(lineno)d): ' \
        +'%(message)s'
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    IFREQ = 10000000.0
    OFREQ = 1000000.0
    DDS = Ad9912Dev()
    DDS.set_ofreq(OFREQ)
    DDS.set_ifreq(IFREQ)
