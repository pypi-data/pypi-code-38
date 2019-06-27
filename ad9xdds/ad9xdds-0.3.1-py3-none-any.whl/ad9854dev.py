# -*- coding: utf-8 -*-

"""package ad9xdds
author  Benoit Dubois
brief   API to control AD9852/4.
details Ad9854Dev: AD9852/4 DDS development card class.
        Note need importlib module for all class, parallel for Ad9854Dev class.
"""

import time
import logging
from dds_core import AbstractDds, bound_value, split_len


#==============================================================================
class Ad9854Dev(AbstractDds):
    """Class representing AD9854 development card.
    Board integrates a parallel port for transmission with PC. AD9854 device
    can be use with a serial or a parallel interface paradigm while parallel
    port of PC is being used for communication. Note that board parallel
    interface allow only register writing.
    """

    FTW_SIZE = 48               # Frequency Tuning Word size (bit)
    PHASE_SIZE = 14             # Phase register size (bit)
    DAC_OUT_SIZE = 12           # Output DAC resolution (bit)
    IFMAX = 300000000           # Input maximum frequency (Hz)
    OFMAX = 120000000           # Output maximum frequency (Hz)
    AMAX = (1<<DAC_OUT_SIZE)-1  # Output maximum amplitude (a.u.)
    
    WR_BIT = 0
    RD_BIT = 1
    MRES_BIT = 2
    UDCLK_BIT = 3
    SPMOD_BIT = 4   # Serial/Parallel mode selection
    ORAMP_BIT = 5
    FDATA_BIT = 6

    _regName2addr = {'Phy1m': 0x0, 'Phy1l': 0x1, 'Phy2m': 0x2, 'Phy2l': 0x3,
                     'Ftw1_5': 0x4, 'Ftw1_4': 0x5, 'Ftw1_3': 0x6,
                     'Ftw1_2': 0x7, 'Ftw1_1': 0x8, 'Ftw1_0': 0x9,
                     'Ftw2_5': 0xa, 'Ftw2_4': 0xb, 'Ftw2_3': 0xc,
                     'Ftw2_2': 0xd, 'Ftw2_1': 0xe, 'Ftw2_0': 0xf,
                     'DFw_5': 0x10, 'DFw_4': 0x11, 'DFw_3': 0x12,
                     'DFw_2': 0x13, 'DFw_1': 0x14, 'DFw_0': 0x15,
                     'UpClk_3': 0x16, 'UpClk_2': 0x17, 'UpClk_1': 0x18,
                     'UpClk_0': 0x19, 'RrClk_2': 0x1a, 'RrClk_1': 0x1b,
                     'RrClk_0': 0x1c, 'Ctr_3': 0x1d, 'Ctr_2': 0x1e,
                     'Ctr_1': 0x1f, 'Ctr_0': 0x20, 'OskIm': 0x21,
                     'OskIl': 0x22, 'OskQm': 0x23, 'OskQl': 0x24,
                     'OskRr': 0x25, 'Qdacm': 0x26, 'Qdacl': 0x27}


    def __init__(self, port=0):
        """The constructor."""
        # Import specific parallel device packages
        try:
            parallel = importlib.import_module("parallel")
        except KeyError as ex:
            print("Problem during parallel class import.")
            print("DDS class %s not found" % str(ex))
        except Exception as ex:
            print("Error during parallel class import: %s" % str(ex))
        try:
            self.pdev = parallel.Parallel(port)
        except OSError:
            print("Error during parallel port initialization.")
            print("Is lp module unloaded and ppdev module loaded?")
            print("Have you write permissions to parallel port file?")
            raise
        except IOError:
            print("Error during parallel port initialization.")
            print("Parallel device file %s is not found" % str(port))
            raise
        except Exception:
            print("Error during parallel port initialization.")
            raise
        # Reset DDS device
        self.reset_dev()
        # Initialize parallel port Ctrl pins
        self.pdev.setDataStrobe(1)
        self.pdev.setAutoFeed(1)
        self.pdev.setInitOut(0) # Note: enable ADDR0 line
        self.pdev.setSelect(1)
        # Initialize data lines
        self.pdev.setData(0xff)
        self._latch_data()
        # Initialize address lines
        self.pdev.setData(0xff)
        self._latch_addr()
        # Initialize WRBAR,RDBAR,PMODE high.
        # Initialize RESET,UDCLK low.
        # Initialize FDATA,ORAMP accordingly.
        # Note: PMODE high enables ADDR1 line.
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()
        # Initialize control register.
        # Ctr_3 disable power_down mode
        self.set_reg(self._regName2addr['Ctr_3'], 0x00)
        # Disable PLL by default
        self.set_reg(self._regName2addr['Ctr_2'], 0x64)
        # Ctr_1 must be configured because its SPMOD_BIT controls
        # the comportment of the 'IO UD CLK' pin.
        self.set_reg(self._regName2addr['Ctr_1'], 0x00)
        # Set 'OSK EN' high to allow user control of amplitude
        self.set_reg(self._regName2addr['Ctr_0'], 0x20)

    def set_ifreq(self, ifreq):
        """Set input frequency.
        :param ifreq: Input frequency value (float)
        :returns: None
        """
        self._ifreq = float(ifreq)

    def get_ifreq(self):
        """Get input frequency.
        :returns: Current input frequency value (float)
        """
        return self._ifreq

    def reset_dev(self):
        """ Reset DDS device: set MRESET pin @ 1 during 10 system clock cycles.
        """
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.MRES_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()
        time.sleep(0.1) # Conservative value for 10 system clock cycles
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()

    def _latch_data(self):
        """ Macro for latching parallel data on data bus of the device.
        """
        self.pdev.setDataStrobe(0)
        self.pdev.setDataStrobe(1)

    def _latch_addr(self):
        """ Macro for latching parallel data on address bus of the device.
        """
        self.pdev.setAutoFeed(0)
        self.pdev.setAutoFeed(1)

    def _latch_ctrl(self):
        """ Macro for latching bits of control of device (\WR, \RD, RESET...).
        """
        self.pdev.setSelect(0)
        self.pdev.setSelect(1)

    def _upclock(self):
        """ Update clock (external update mode).
        """
        # Set WRBAR,RDBAR,UDCLK,PMODE high.
        # Set RESET low.
        # Set FDATA,ORAMP accordingly.
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.UDCLK_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()
        # Set WRBAR,RDBAR,PMODE high.
        # Set RESET,UDCLK low.
        # Set FDATA,ORAMP accordingly.
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()

    def _actual_phy(self, dphy):
        """Public function for specific AD9854 product.
        arg    dphy Phase register value (int).
        return      Actual output phase offset in degree (float).
        """
        self._actual_phy(dphy, self.PHASE_SIZE)
        
    def set_reg(self, address, value):
        """Write value @ address register.
        arg    address  Address of the register to write (int).
        arg    value    Value to write (int).
        return          None
        Rmp: ici l'ecriture dans les registres fonctionnent si on considère
        les registres en mode "parallèle", alors que la lecture utilise le
        mode série. => passer en mode série également
        """
        # Prepare data and address bus.
        self.pdev.setData(0xff-value) # Complement binary code
        self._latch_data()
        self.pdev.setData(0xff-address) # Complement binary code
        self._latch_addr()
        # Write value @ address in the I/O buffer register.
        # WRBAR,RESET,UDCLK = lo
        # RDBAR,PMODE = hi
        self.pdev.setData(0xff - ((1 << self.RD_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()
        # RESET,UDCLK = lo
        # WRBAR,RDBAR,PMODE = hi
        self.pdev.setData(0xff - ((1 << self.WR_BIT) + \
                                  (1 << self.RD_BIT) + \
                                  (1 << self.SPMOD_BIT)))
        self._latch_ctrl()

    def get_reg(self, address):
        """Read value @ address.
        arg    address  Address of the register to read (int)
        return   Register value (int)
        """
        self.pdev.setData(0xff - 1)
        self._latch_ctrl()
        self.pdev.setData(0xff - 0)
        self._latch_ctrl()
        # Build serial read request message:
        # Read (1b) | Don't Care (3b) | address (4b)
        msg = "1000" + format(address, '04b')
        prv_str = "0"
        # Get eight bits.
        for i in range(8):
            tmp_str = msg[i]
            # Change data bit only if necessary.
            if ((tmp_str == "1") and (prv_str == "0")):
                self.pdev.setData(0xfe)
                self._latch_addr()
                prv_str = "1"
            elif ((tmp_str == "0") and (prv_str == "1")):
                self.pdev.setData(0xff)
                self._latch_addr()
                prv_str = "0"
            # Set SCLK high.
            self.pdev.setData(0xff - 1)
            self._latch_ctrl()
            if (i < 8):
                # Set SCLK low.
                self.pdev.setData(0xff - 0)
                self._latch_ctrl()
        self.pdev.setData(0xff)
        self._latch_addr()
        # Set line for 2 wire mode (default mode).
        self.pdev.setInitOut(1)
        # Default: MSB first.
        bits_to_read = address
        # Determine number of bits to read.
        if bits_to_read == 10:
            bits = 8
        elif (bits_to_read == 0 or bits_to_read == 1 or bits_to_read == 8 or \
              bits_to_read == 9 or bits_to_read == 11):
            bits = 16
        elif bits_to_read == 6:
            bits = 24
        elif (bits_to_read == 5 or bits_to_read == 7):
            bits = 32
        elif (bits_to_read == 2 or bits_to_read == 3 or bits_to_read == 4):
            bits = 48
        else:
            raise ValueError, "Bad address to read"
        # Initialize readback string.
        tmp_str = ""
        for i in range(bits):
            # Take SCLK low.
            self.pdev.setData(0xff - 0)
            self._latch_ctrl()
            # Readback port and mask unwanted bits.
            res = self.pdev.getInError()
            # Build string.
            # Note: Data are inverted on customer eval board.
            if res == True :
                tmp_str = tmp_str + "0"
            else:
                tmp_str = tmp_str + "1"
            # Take SCLK high.
            self.pdev.setData(0xff - 1)
            self._latch_ctrl()
        deta = tmp_str
        # De-Set line for 2 wire mode (default mode).
        #if (2WireModeEnabled):
        self.pdev.setInitOut(0)
        self.pdev.setData(0xff - 3)
        self._latch_ctrl()
        return int(deta, 2)

    def set_ofreq(self, ofreq):
        """Set output frequency on DDS.
        Take the input and output frequency as argument and set the adequat
        register in the DDS and return the actual output frequency (see
        _actual_ofreq()).
        output frequency may be (a bit) different than the requested frequency.
        arg    ofreq  Output frequency (float).
        return        Actual output frequency (float)
        """
        # Compute the Frequency Tuning Word (FTW).
        ftw = int((ofreq * (1 << self.FTW_SIZE)) / self.ifreq)
        # Prepare list of value to send to the 6 FTW registers.
        ftw_val_list = split_len(format(ftw, '012x'), 2)
        # Send values to the 6 FTW0 registers of the DDS.
        # TODO Search a better way to find reg address.
        for idx, ftw_val in enumerate(ftw_val_list) :
            try:
                self.set_reg(self._regName2addr['Ftw1_5']+idx, int(ftw_val, 16))
            except Exception as ex:
                print("Setting frequency failed:", str(ex))
                raise
        # Request clock update (manual mode)
        self._upclock()
        # Return the actual output frequency.
        return self._actual_ofreq(self.get_sysfreq(), ftw, self.FTW_SIZE)

    def get_ofreq(self):
        """Get output frequency of DDS.
        return:       Output frequency of DDS (float).
        """
        # Get back the Frequency Tuning Word (FTW) from device.
        ftw = 0
        for idx in range(0, 6):
            ftw += self.get_reg(self._regName2addr['Ftw1_5']+idx) << (idx*8)
        return self._actual_ofreq(self.get_sysfreq(), ftw, self.FTW_SIZE)

    def set_phy(self, phy):
        """Set phase of output signal on DDS.
        Take the queried output phase (in degree) as argument and set
        the adequat register in the DDS.
        arg    phy  Output phase (float).
        return      Actual output phase (float)
        """
        # Raise error if value is out of range.
        if not(0 <= phy < 360):
            raise ValueError('Phase value out of range.')
        # Compute dphy (Delta_phase).
        dphy = int((phy * (1 << 14)) / 360)
        # Prepare list of value to send to the dphy registers.
        dphy_val_list = split_len(format(dphy, '04x'), 2)
        # Send values to the dphy registers of the DDS.
        # TODO Search a better way to find reg address.
        for idx, val in enumerate(dphy_val_list):
            self.set_reg(self._regName2addr['Phy1m']+idx, int(val, 16))
        # Request clock update (manual mode)
        self._upclock()
        # Return the actual output phase
        return self._actual_phy(dphy)

    def get_phy(self):
        """Get output phase of DDS.
        return:  Output phase of DDS (float).
        """
        # Get back the dphy register content
        dphy = 0
        for idx in range(0, 2):
            dphy += self.get_reg(self._regName2addr['Phy1m']+idx) << (idx*8)
        # return the ofreq.
        return self._actual_phy(dphy)

    def set_amp(self, amp):
        """Set amplitude tuning word of output signal on DDS.
        Take the input and output frequency as argument and set the adequat
        register in the DDS.
        :param amp: Output amplitude (int).
        :returns: Amplitude register value if transfert is ok (int).
        """
        # If value is out of range, bound value and raise Warning.
        if not(0 <= amp <= self.AMAX):
            amp = bound_value(amp, 0, self.AMAX)
            #raise UserWarning('Amplitude tuning value out of range.')
        # Prepare list of value to send to the amp registers.
        amp_val_list = split_len(format(amp, '04x'), 2)
        # Send values to the amp registers of the DDS.
        # TODO Search a better way to find reg address.
        for idx, val in enumerate(amp_val_list):
            self.set_reg(self._regName2addr['OskIm']+idx, int(val, 16))
        # Request clock update (manual mode)
        self._upclock()
        # Return the amplitude value if transfert is ok.
        return amp

    def get_amp(self):
        """Get output amplitude tuning word of DDS.
        return:  Output amplitude tuning of DDS (float).
        """
        # Get back the AMP register (Full Scale) register content
        amp = 0
        for idx in range(0, 2):
            amp += self.get_reg(self._regName2addr['OskIm']+idx) << (idx*8)
        # Return the amplitude tuning word.
        return amp


#==============================================================================
if __name__ == '__main__':
    IFREQ = 1000000.0
    OFREQ = 100000.0
    DDS = Ad9854Dev()
    DDS.set_ifreq(IFREQ)
    DDS.set_ofreq(OFREQ)
