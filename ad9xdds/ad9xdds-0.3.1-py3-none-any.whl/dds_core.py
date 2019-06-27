# -*- coding: utf-8 -*-

"""package ad9xdds
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2018
license   GPL v3.0+
brief     API to control various DDS.
details   Interface that must be used to handle DDS-like device.
          The interface represent minimum method that must be implemented
          to be used in the package.
"""

from PyQt5.QtCore import QObject, pyqtSignal


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
def bound_value(value, vmin, vmax):
    """Check that a value is included in the range [min, max], if not the value
    is bounded to the range, ie:
    - if value < min  ->  min = value
    - if value > max  ->  max = value
    arg    value Value that is checked
    arg    vmin  Minimum valid value.
    arg    vmax  Maximum valid value.
    return       Bounded value.
    """
    if value < vmin:

        return vmin
    elif value > vmax:
        return vmax
    else:
        return value


# =============================================================================
class AbstractDds(QObject):
    """Abstract class of DDS classes. Define common properties and method for
    inherited classes.
    """

    newFreqOut = pyqtSignal(float)
    newFreqIn = pyqtSignal(float)
    newPhase = pyqtSignal(float)
    newAmp = pyqtSignal(int)


    def set_ifreq(self, ifreq):
        """Set input frequency.
        :param ifreq: Input frequency value (float)
        :returns: None
        """
        pass

    def get_ifreq(self):
        """Get input frequency.
        :returns: Current input frequency value (float)
        """
        pass

    def set_amp(self, fsc):
        """Set amplitude tuning word of output signal on DDS.
        Take the input and output frequency as argument and set the adequat
        register in the DDS.
        :param fsc: Output amplitude (int).
        :returns: fsc register value if transfert is ok (int).
        """
        pass

    def get_amp(self):
        """Get output amplitude tuning word of DDS.
        :returns: Output amplitude tuning of DDS (float).
        """
        pass

    def set_phy(self, phy):
        """Set phase of output signal on DDS.
        Take the queried output phase (in degree) as argument and set
        the adequat register in the DDS.
        :param phy:  Output phase (float).
        :returns: Actual output phase (float)
        """
        pass

    def get_phy(self):
        """Get output phase of DDS.
        :returns:  Output phase of DDS (float).
        """
        pass

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
