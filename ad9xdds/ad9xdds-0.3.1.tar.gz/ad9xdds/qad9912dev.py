# -*- coding: utf-8 -*-

"""package ad9xdds
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
brief     API to control AD9912 DDS development board with PyQt facilities.
details   Class derived Ad9912Dev class to add PyQt facilities
          i.e. signals/slots facilities
"""

from PyQt5.QtCore import QObject, pyqtSignal
from ad9xdds.ad9912dev import Ad9912Dev


# =============================================================================
class QAd9912Dev(QObject, Ad9912Dev):
    """Class derived from Ad9912Dev class to add PyQt facilities.
    """

    ifreqUpdated = pyqtSignal(float)
    ofreqUpdated = pyqtSignal(float)
    phaseUpdated = pyqtSignal(float)
    ampUpdated = pyqtSignal(int)
    pllStateUpdated = pyqtSignal(bool)
    pllDoublerUpdated = pyqtSignal(bool)
    pllFactorUpdated = pyqtSignal(int)

    def __init__(self, **kwargs):
        QObject.__init__(self, **kwargs)
        Ad9912Dev.__init__(self, **kwargs)

    def connect(self, **kwargs):
        return Ad9912Dev.connect(self, **kwargs)

    def set_ifreq(self, ifreq):
        Ad9912Dev.set_ifreq(self, ifreq)
        self.ifreqUpdated.emit(ifreq)

    def set_ofreq(self, ofreq):
        aofreq = Ad9912Dev.set_ofreq(self, ofreq)
        self.ofreqUpdated.emit(aofreq)
        return aofreq

    def set_phy(self, phy):
        aphy = Ad9912Dev.set_phy(self, phy)
        self.phaseUpdated.emit(aphy)
        return aphy

    def set_amp(self, amp):
        aamp = Ad9912Dev.set_amp(self, amp)
        self.ampUpdated.emit(aamp)
        return aamp

    def set_pll_state(self, state):
        Ad9912Dev.set_pll_state(self, state)
        self.pllStateUpdated.emit(state)

    def set_pll_doubler_state(self, flag):
        Ad9912Dev.set_pll_doubler_state(self, flag)
        self.pllDoublerUpdated.emit(flag)

    def set_pll_multiplier_factor(self, factor):
        Ad9912Dev.set_pll_multiplier_factor(self, factor)
        self.pllFactorUpdated.emit(factor)
