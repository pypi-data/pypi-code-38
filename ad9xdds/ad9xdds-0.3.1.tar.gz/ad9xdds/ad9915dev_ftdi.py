# -*- coding: utf-8 -*-

"""package dds
author    Benoit Dubois
copyright FEMTO ENGINEERING
license   GPL v3.0+
brief     API to control AD9915 DDS development board.
details   AD9915 development board is configurable by USB through an external
          USB to spi transceiver from FTDI (Cx232HM device). Class allows
          configuration of principle DDS parameters (frequency, phase,
          amplitude, PLL handling, output handling...).
"""
import logging
import time
from array import array
from pyftdi.spi import SpiController
from pyftdi.gpio import GpioController, GpioException
#from .dds_core import AbstractDds, bound_value, split_len

FT232H_VENDOR_ID = 0x0403
FT232H_PRODUCT_ID = 0x6014

FTW_SIZE = 48               # Frequency Tuning Word register size (bit)
PHASE_SIZE = 16             # Phase register size (bit)
DAC_OUT_SIZE = 12           # Output DAC resolution (bit)

VENDOR_ID = FT232H_VENDOR_ID
PRODUCT_ID = FT232H_PRODUCT_ID
    
IFMAX = 2500000000          # Input maximum frequency (Hz)
OFMAX = 1000000000          # Output maximum frequency (Hz)
AMAX = (1<<DAC_OUT_SIZE)-1  # Output maximum amplitude (a.u.)


#==============================================================================
class Ad9915DevCx232Hm(object):
    """Class for AD9915 development board.
    Board communicates with PC through an USB Hi-Speed to "MPSSE" Cables from
    FTDI (reference Cx232HM) connected to integrated SPI port of DDS.
    """



    _regSerialAddr = {'CFR1': 0x00, 'CFR2': 0x01, 'CFR3': 0x02, 'CFR4': 0x03,
                      'DigRampLowLim': 0x4, 'DigRampUpLim': 0x5,
                      'RisDigRampStepSize': 0x06, 'FalDigRampStepSize': 0x07,
                      'DigRampRate': 0x08,
                      'LowFreqJump': 0x9, 'UpFreqJump': 0x0A,
                      'P0FTW': 0x0B, 'P0PhasAmp': 0x0C,
                      'P1FTW': 0x0D, 'P1PhasAmp': 0x0E,
                      'P2FTW': 0x0F, 'P2PhasAmp': 0x10,
                      'P3FTW': 0x11, 'P3PhasAmp': 0x12,
                      'P4FTW': 0x13, 'P4PhasAmp': 0x14,
                      'P5FTW': 0x15, 'P5PhasAmp': 0x16,
                      'P6FTW': 0x17, 'P6PhasAmp': 0x18,
                      'P7FTW': 0x19, 'P7PhasAmp': 0x1A,
                      'USR0': 0x1B}

    def __init__(self):
        """The constructor.
        :returns: None
        """
        super().__init__()

        ###self._ctrl, self._spi = self.config_interface(VENDOR_ID, PRODUCT_ID)
        self._ctrl, self._spi, self._gpio = self.config_interface(VENDOR_ID, PRODUCT_ID)
        self._gpio.write_port(0x0)
        self.send_reset()
        self._spi.set_frequency(10000)
        
        # Init properties
        # !warning! parameter order initialisation is important
        #self._ifreq = IFMAX
        #self._pll_state = self.get_pll_state()  # cache
        #self._pll_doubler_state = self.get_pll_doubler_state() # cache
        #self._pll_factor = self.get_pll_multiplier_factor() # cache
        #self._ofreq = self.get_ofreq() # cache


    @staticmethod
    def config_interface(vendor, product, interface=1, cs=0, freq=None):
        GPIO_MASK = 0xf0 # (L3 L2 L1 L0 Na Na Na Na) Out Out Out Out Na Na Na Na
        gpio = GpioController()
        print(gpio.open_from_url('ftdi:///?'))
        gpio.open_from_url('ftdi:///{:d}'.format(interface), direction=GPIO_MASK)    
        
        ctrl = SpiController(silent_clock=False)
        ctrl.configure('ftdi:///{:d}'.format(interface+1))
        spi = ctrl.get_port(cs)
        if freq:
            spi.set_frequency(freq)
        
        return ctrl, spi, gpio
    
    def send_io_update(self):
        self._gpio.write_port(0x10)  # The IO Update is active on logic high, so we send the pin high for an update
        self._gpio.write_port(0x0)   # Then low to end it. The delay between rise and fall is many clock cycles, so no delay between the high and low commands is needed

    def send_reset(self):
        self._gpio.write_port(0x40)  # The reset is active on logic high, so we send the pin high for an update
        self._gpio.write_port(0x0)   # Then low to end it. The delay between rise and fall is many clock cycles, so no delay between the high and low commands is needed
        
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



    def actual_phy(self, dphy):
        """Public function for specific AD9915 product.
        :param dphy: Phase register value (float).
        :returns: Actual output phase offset in degree (float).
        """
        return self._actual_phy(dphy, PHASE_SIZE)


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
        :param state: - False  Disable PLL. (bool)
                      - True   Enable PLL.
        :returns: None
        """
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
        # Update DDS device because ofreq = f(pll_state)
        self.set_ofreq(self._ofreq)

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
        :param flag: - False  Disable frequency doubler. (bool)
                     - True   Enable frequency doubler.
        :returns: None
        """
        reg = self.get_reg(self._regName2addr['PllParam'])
        if flag == True:
            mask = 1 << 3
            msg = reg | mask
        else:
            mask = ~(1 << 4)
            msg = reg & mask
        self.set_reg(self._regName2addr['PllParam'], msg)
        self._pll_doubler_state = flag
        logging.debug("Set PLL doubler state to: " + str(flag))
        # Update DDS device because ofreq = f(pll_doubler)
        self.set_ofreq(self._ofreq)

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
        Note that here we assign the overall multiplier factor, so the prescaler
        divider by 2 in the SysClk PLL multiplier block is include in the given
        factor.
        :param factor: factor of PLL multiplier (between 4 to 66) (int)
        :returns: None
        """
        if factor < 4:
            factor = 4
            logging.warning("PLL multiplier factor out of range. Set to: " \
                            + str(factor))
        elif factor > 66:
            factor = 66
            logging.warning("PLL multiplier factor out of range. Set to: " \
                            + str(factor))
        msg = factor / 2 # To take account of prescaler
        self.set_reg(self._regName2addr['Ndivider'], msg)
        self._pll_factor = factor
        logging.debug("Set PLL multiplier factor to: " + str(factor))
        # Update DDS device because ofreq = f(pll_factor))
        self.set_ofreq(self._ofreq)

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
        if flag == True:
            msg = array('H', (0x0F, 0x1))
        else:
            msg = array('H', (0x0F, 0x0))
        try:
            self.write_ctrl(msg)
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
        self.write(msg)
        # End write cycle (Set value to portA's pins of FX2 device)
        try:
            end = array('H', (0x01, 0x0B))
            self._ep_out.write(end)
            end = array('H', (0x01, 0x03))
            self._ep_out.write(end)
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
            self._ep_out.write(init)
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
        self.write(msg)
        # Read result.
        raw_data = self.read()
        # Disable single byte read mode (readback mode).
        end = array('H', (0x04, 0x00))
        try:
            self._ep_out.write(end)
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
        Details:   Prototype of transmission on AD9915 serial bus:
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




        
#==============================================================================

# Constructor function initializes communication pinouts
class AD9915(object):

    def __init__(self, ssPin, resetPin, updatePin, ps0, ps1, ps2, osk):
        #Master_reset pin?
        """The constructor.
        :returns: None
        """
        super().__init__()

        RESOLUTION  = 4294967296.0
        _ssPin = ssPin
        _resetPin = resetPin
        _updatePin = updatePin
        _ps0 = ps0
        _ps1 = ps1
        _ps2 = ps2
        self._osk = osk

        # sets up the pinmodes for output
        """pinMode(_ssPin, OUTPUT)
        pinMode(_resetPin, OUTPUT)
        pinMode(_updatePin, OUTPUT)
        pinMode(_ps0, OUTPUT)
        pinMode(_ps1, OUTPUT)
        pinMode(_ps2, OUTPUT)
        pinMode(_osk, OUTPUT)"""

        # defaults for pin logic levels
        """digitalWrite(_ssPin, HIGH)
        digitalWrite(_resetPin, LOW)
        digitalWrite(_updatePin, LOW)
        digitalWrite(_ps0, LOW)
        digitalWrite(_ps1, LOW)
        digitalWrite(_ps2, LOW)
        digitalWrite(_osk, LOW)"""


        
    def digitalWrite(self):
        pass


    def set_ifreq(self, ifreq):
        """Set input frequency.
        :param ifreq: Input frequency value (float)
        :returns: None
        """
        #self.newFreqIn.emit(ifreq)
        self._ifreq = ifreq
        logging.debug("Set input frequency: %s", str(ifreq))
        # Update output frequency because ofreq = f(ifreq)
        self.set_ofreq(self._ofreq)

    def get_ifreq(self):
        """Get input frequency.
        :returns: Current input frequency value (float)
        """
        return self._ifreq

    def initialize(self, ref_clk):
        """initialize(refClk) - initializes DDS with reference clock frequency
        refClk (assumes you are using an external clock, not the internal PLL)
        """
        self._refIn = ref_clk
        self._refClk = ref_clk
        self.reset()
        time.sleep(0.1)
        self._profile_mode = False #profile mode is disabled by default
        self._osk = False #OSK is disabled by default
        self._active_profile = 0 
        #Disable the PLL - I think this is disabled by default, so comment it out for now
        #registerInfo[] = 0x02, 4
        #data[] = 0x00, 0x00, 0x00, 0x00
        #self.writeRegister(registerInfo, data)    
        self.dacCalibrate() # Calibrate DAC 

    # reset() - takes no arguments resets DDS
    def reset(self):
        digitalWrite(_resetPin, HIGH)
        time.sleep(0.001)
        digitalWrite(_resetPin, LOW)

    # update() - sends a logic pulse to IO UPDATE pin on DDS updates frequency output to 
    #      newly set frequency (FTW0)
    def update(self):
        digitalWrite(_updatePin, HIGH)
        time.sleep(0.001)
        digitalWrite(_updatePin, LOW)

    def set_ofreq(self, freq, profile=0):
        if profile > 7: 
            return # invalid profile, return without doing anything
        # set _freq and _ftw variables
        self._freq[profile] = freq
        self._ftw[profile] = round(freq * RESOLUTION / _refClk) 
        # divide up ftw into four bytes
        ftw =  [lowByte(self._ftw[profile] >> 24),
                lowByte(self._ftw[profile] >> 16), \
                lowByte(self._ftw[profile] >> 8), \
                lowByte(self._ftw[profile]) ]
        # register info -- writing four bytes to register 0x04, 
        registerInfo = [0x0B, 4]
        #select the right register for the commanded profile number
        #    else if (profile == 0)
        #      registerInfo[0]=0x0B
        #     else if (profile == 1) 
        #      registerInfo[0]=0x0D
        #     else if (profile == 2) 
        #      registerInfo[0]=0x0F
        #     else if (profile == 3)
        #      registerInfo[0]=0x11
        #     else if (profile == 4) 
        #      registerInfo[0]=0x13
        #     else if (profile == 5) 
        #      registerInfo[0]=0x15
        #     else if (profile == 6) 
        #      registerInfo[0]=0x17
        #     else if (profile == 7) 
        #      registerInfo[0]=0x19
        registerInfo[0] += 2*profile #select the right register for the commanded profile number
        #CFR1[] =  0x00, 0x00, 0x00, 0x00 
        #CFR1Info[] = 0x00, 4
        # actually writes to register
        #self.writeRegister(CFR1Info, CFR1)
        self.writeRegister(registerInfo, ftw)
        # issues update command
        self.update()

    def set_amp(self, scaled_amp, profile=0):
        if profile > 7:
            return # invalid profile, return without doing anything
        self._scaled_amp[profile] = scaled_amp
        self._asf[profile] = round(scaledAmp*4096)
        self._scaled_amp_db[profile] = 20.0*log10(_asf[profile]/4096.0)
        if _asf[profile] >= 4096:
            self._asf[profile] = 4095 # write max value
        elif scaledAmp < 0:
            self._asf[profile] = 0 # write min value
        self.writeAmp(_asf[profile],profile)

    def set_amp_db(self, scaled_amp_db, profile=0):
        if profile > 7:
            return # invalid profile, return without doing anything
        if scaled_amp_db > 0:
            return # dB should be less than 0, return without doing anything
        self._scaled_amp_db[profile] = scaled_amp_db
        self._asf[profile] = round(pow(10, scaled_amp_db/20.0)*4096.0)
        self._scaled_amp[profile] = _asf[profile]/4096.0
        if (_asf[profile] >= 4096):
            self._asf[profile]=4095 # write max value
        self.writeAmp(_asf[profile],profile)
    
    def get_amp(self, profile=0):
        return self._scaled_amp[profile]

    def get_amp_db(self, profile=0):
        return self._scaled_amp_db[profile]

    def get_asf(self, profile=0):
        return self._asf[profile]

    def get_freq(self, profile=0):
        return _freq[profile]

    def set_ftw(self, ftw, profile=0):
        """Set FTW register. Accepts 32-bit frequency tuning word ftw
        updates instance variables for FTW and Frequency, and writes ftw to DDS.
        """
        if profile > 7:
            return #invalid profile, return without doing anything
        # set freqency and ftw variables
        self._ftw[profile] = ftw
        self._freq[profile] = ftw * _refClk / RESOLUTION
        # divide up ftw into four bytes
        data =  [lowByte(ftw >> 24), lowByte(ftw >> 16), \
                 lowByte(ftw >> 8), lowByte(ftw)]
        # register info -- writing four bytes to register 0x04, 
        registerInfo = [0x0B, 4]
        registerInfo[0] += 2*profile #select the right register for the commanded profile number
        #CFR1[] =  0x00, 0x00, 0x00, 0x00 
        #CFR1Info[] = 0x00, 4
        #self.writeRegister(CFR1Info, CFR1)
        self.writeRegister(registerInfo, data)
        self.update()

    def set_profile_mode(self, enable=True):
        """Set the profile select mode.
        """
        if enable is True:
            #write 0x01, 23 high
            self._profile_mode = true
            registerInfO = [0x01, 4]
            data = [0x00, 0x80, 0x09, 0x00]
        else:
            #write 0x01, 23 low
            self._profile_mode = false
            registerInfo = [0x01, 4]
            data = [0x00, 0x00, 0x09, 0x00]
        self.writeRegister(registerInfo, data)
        self.update()

    def set_osk(self, enable=True):
        if enable is True:
            #write 0x00, 8 high
            self._osk = true
            registerInfo = [0x00, 4]
            data = [0x00, 0x01, 0x01, 0x08]
        else:
            #write 0x00, 8 low
            self._osk = false
            registerInfo = [0x00, 4]
            data = [0x00, 0x01, 0x00, 0x08]
        self.writeRegister(registerInfo, data)
        self.update()

    def get_profile_select_mode(self):
        """return boolean indicating if profile select mode is activated
        """
        return self._profile_mode

    def get_osk_mode(self):
        return self._osk

    def set_sync_clck(self, enable=True):
        if enable is True:
            #write 0x01, 11 high 
            registerInfo = [0x01, 4]
            data = [0x00, 0x80, 0x09, 0x00]
        else:
            #write 0x01, 11 low
            registerInfo = [0x01, 4]
            data = [0x00, 0x80, 0x01, 0x00]
        self.writeRegister(registerInfo, data)
        self.update()

    def select_profile(self, profile):
        # Possible improvement: write PS pin states all at once using register masks
        self._active_profile = profile
        if profile > 7:
            return #not a valid profile number, return without doing anything

        if (B00000001 & profile) > 0:  #rightmost bit is 1
            digitalWrite(_ps0, HIGH)
        else:
            digitalWrite(_ps0,LOW)
        if (B00000010 & profile) > 0:  #next bit is 1
            digitalWrite(_ps1, HIGH)
        else:
            digitalWrite(_ps1,LOW)
        if (B00000100 & profile) > 0:  #next bit is 1
            digitalWrite(_ps2, HIGH)
        else:
            digitalWrite(_ps2,LOW)

    def get_profile(self):
      return self._active_profile

    def _write_register(self, registerInfo, data):
        """Writes SPI to particular register. registerInfo is a 2-element
        array which contains [register, number of bytes].
        """
        digitalWrite(_ssPin, LOW)
        # Writes the register value
        SPI.transfer(registerInfo[0])
        # Writes the data
        for i in range(registerInfo[1]):
            SPI.transfer(data[i])

        digitalWrite(_ssPin, HIGH)

    def _dac_calibrate(self):
      """Calibrate DAC (0x03, bit 24 -> high then low)
      """
      registerInfo = [0x03, 4]
      data = [0x01, 0x05, 0x21, 0x20] #write bit high
      self.writeRegister(registerInfo, data)
      self.update()
      time.sleep(0.001)
      data[0] = 0x00 #write bit low
      self.writeRegister(registerInfo, data) 
      self.update()

    def _write_amp(self, ampScaleFactor, profile):
      registerInfo = [0x0C, 4]
      registerInfo[0] += 2*profile #select the right register for the commanded profile number
      # divide up ASF into two bytes, pad with 0s for the phase offset
      atw = [lowByte(ampScaleFactor >> 8), lowByte(ampScaleFactor), 0x00, 0x00]
      # actually writes to register
      self.writeRegister(registerInfo, atw)
      self.update()

#==============================================================================
if __name__ == '__main__':
    # Setup logger
    LOG_FORMAT = '%(asctime)s %(levelname)s %(filename)s (%(lineno)d): ' \
        +'%(message)s'
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    IFREQ = 10000000.0
    OFREQ = 1000000.0
    DDS = Ad9915DevCx232Hm()
    DDS._spi.write([0x05])
    DDS.send_io_update()
    #print(DDS._spi.read(1))
    ###DDS._spi.read(1)
    DDS._ctrl.terminate()
    DDS._gpio.close()