# -*- coding: utf-8 -*-

"""package ddsctrl
author    Benoit Dubois
copyright FEMTO ENGINEERING
license   GPL v3.0+
brief     User Interface of the DDS controller.
"""

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QGridLayout, \
     QVBoxLayout, QHBoxLayout, QGroupBox, QTabWidget, QComboBox, QSpinBox, \
     QDoubleSpinBox, QCheckBox

from ddsctrl.constants import VCO_RANGE, CP_CURRENT

#==============================================================================
class InControllerUi(QWidget):
    """Controller UI form used to control DDS device.
    """

    sys_clock_changed = pyqtSignal(float)

    def __init__(self):
        """The constructor.
        """
        super().__init__()
        self.ifreq_dsb = QDoubleSpinBox()
        self.sfreq_led = QLineEdit()
        self.sfreq_led.setReadOnly(True)
        self.apply_btn = QPushButton("&Apply")
        self.advanced_config_gbox = self._create_advanced_config()
        ifreq_layout = QVBoxLayout()
        ifreq_layout.addWidget(QLabel("Input clock frequency (Hz)"))
        ifreq_layout.addWidget(self.ifreq_dsb)
        ifreq_layout.addWidget(QLabel("System clock frequency (Hz)"))
        ifreq_layout.addWidget(self.sfreq_led)
        ifreq_layout.addWidget(self.advanced_config_gbox)
        ifreq_layout.addStretch(1)
        ifreq_layout.addWidget(self.apply_btn)
        self.setLayout(ifreq_layout)
        self.advanced_config_gbox.toggled.connect(self.update_sys_clock_label)
        self.pll_doubler_ckbox.toggled.connect(self.update_sys_clock_label)
        self.pll_factor_sbox.valueChanged.connect(self.update_sys_clock_label)
        self.apply_btn.released.connect(self.update_sys_clock_label)
        self._init_ui()

    @pyqtSlot(float)
    def set_ifmax(self, value):
        """Define maximum frequency handled by widget.
        :param value: New maximal value of parameter (float)
        :returns: None
        """
        self.ifreq_dsb.setMaximum(value)

    def _create_advanced_config(self):
        """Create advanced configuration groupbox for system PLL.
        :returns: the advanced configuration groupbox (QGroupBox)
        """
        self.pll_doubler_ckbox = QCheckBox("Enable input frequency doubler")
        self.pll_factor_sbox = QSpinBox()
        self.pll_factor_sbox.setRange(4, 66)
        self.pll_factor_sbox.setSingleStep(2)
        self.vco_range_cbox = QComboBox()
        self.cp_current_cbox = QComboBox()
        group_box = QGroupBox("Enable System Clock PLL")
        group_box.setCheckable(True)
        group_box.setChecked(False)
        advanced_layout = QVBoxLayout()
        advanced_layout.addWidget(self.pll_doubler_ckbox)
        advanced_layout.addWidget(QLabel("PLL multiplier"))
        advanced_layout.addWidget(self.pll_factor_sbox)
        advanced_layout.addWidget(QLabel("VCO range"))
        advanced_layout.addWidget(self.vco_range_cbox)
        advanced_layout.addWidget(QLabel("Charge pump current"))
        advanced_layout.addWidget(self.cp_current_cbox)
        group_box.setLayout(advanced_layout)
        return group_box

    def _init_ui(self):
        """Init UI.
        :returns: None
        """
        for k, val in VCO_RANGE.items():
            self.vco_range_cbox.insertItem(k, val)
        for k, val in CP_CURRENT.items():
            self.cp_current_cbox.insertItem(k, val)
        self.update_sys_clock_label()

    @pyqtSlot()
    def update_sys_clock_label(self):
        """Update system clock display.
        :returns: None
        """
        if self.advanced_config_gbox.isChecked() is True:
            if self.pll_doubler_ckbox.isChecked() is True:
                doubler = 2.0
            else:
                doubler = 1.0
            ifreq = self.ifreq_dsb.value()
            factor = self.pll_factor_sbox.value()
            sfreq_value = ifreq * doubler * factor
        else:
            sfreq_value = self.ifreq_dsb.value()
        self.sys_clock_changed.emit(sfreq_value)
        self.sfreq_led.setText(str(sfreq_value))


#==============================================================================
class OutControllerUi(QWidget):
    """Controller UI form used to control DDS device.
    """

    def __init__(self, ofmax=400000000.0, amax=1023):
        """The constructor.
        """
        super().__init__()
        self.auto_update_ckbox = QCheckBox("Automatic update")
        ofreq_lab = QLabel("Output frequency (Hz)")
        self.ofreq_tuning = QDoubleSpinBox()
        self.ofreq_tuning.setDecimals(6)
        self.ofreq_tuning.setRange(0.0, ofmax)
        ofreq_layout = QVBoxLayout()
        ofreq_layout.addWidget(ofreq_lab)
        ofreq_layout.addWidget(self.ofreq_tuning)
        ofreq_layout.addStretch(1)
        phy_lab = QLabel("Output phase (deg.)")
        self.phy_tuning = QDoubleSpinBox()
        self.phy_tuning.setRange(0.0, 359.9)
        self.phy_tuning.setDecimals(2)
        self.phy_tuning.setSingleStep(1.0)
        phy_layout = QVBoxLayout()
        phy_layout.addWidget(phy_lab)
        phy_layout.addWidget(self.phy_tuning)
        phy_layout.addStretch(1)
        amp_lab = QLabel("Output amplitude (a.u.)")
        self.amp_tuning = QDoubleSpinBox()
        self.amp_tuning.setRange(0, amax)
        self.amp_tuning.setDecimals(0)
        self.amp_tuning.setSingleStep(1)
        amp_layout = QVBoxLayout()
        amp_layout.addWidget(amp_lab)
        amp_layout.addWidget(self.amp_tuning)
        amp_layout.addStretch(1)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.addLayout(ofreq_layout)
        ctrl_layout.addLayout(phy_layout)
        ctrl_layout.addLayout(amp_layout)
        self.out_hstl_ckbox = QCheckBox("Enable HSTL output")
        self.out_cmos_ckbox = QCheckBox("Enable CMOS output")
        self.hstl_doubler_ckbox = QCheckBox("Enable HSTL frequency doubler")
        ##self.out_cmos_div_sbox = QSpinBox()
        ##self.out_cmos_div_sbox.setRange(1, 65535)
        out_layout = QGridLayout()
        out_layout.addWidget(self.out_hstl_ckbox, 0, 0)
        out_layout.addWidget(self.out_cmos_ckbox, 1, 0)
        out_layout.addWidget(self.hstl_doubler_ckbox, 2, 0)
        ##out_layout.addWidget(self.out_cmos_div_sbox, 3, 0)
        ##out_layout.addWidget(QLabel("CMOS output divider factor"), 3, 1)
        self.apply_btn = QPushButton("&Apply")
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.apply_btn)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.auto_update_ckbox)
        self.layout.addLayout(ctrl_layout)
        self.layout.addLayout(out_layout)
        self.layout.addStretch(1)
        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)
        # Set state of CMOS divider with respect to CMOS output state
        ##self.out_cmos_ckbox.toggled.connect(self.out_cmos_div_sbox.setEnabled)
        ##self.out_cmos_div_sbox.setEnabled(False)
        # Set state of HSTL doubler with respect to HSTL output state
        self.out_hstl_ckbox.toggled.connect(self.hstl_doubler_ckbox.setEnabled)
        self.hstl_doubler_ckbox.setEnabled(False)
        # Handle apply button state in respect with auto update checkbox
        self.auto_update_ckbox.stateChanged.connect(self.apply_btn.setDisabled)

    @pyqtSlot(float)
    def set_ofmax(self, value):
        """Define maximum frequency handled by widget.
        :param value: New maximal value of parameter (float)
        :returns: None
        """
        self.ofreq_tuning.setMaximum(value)

    @pyqtSlot(int)
    def set_amax(self, value):
        """Define maximum amplitude handled by widget.
        :param value: New maximal value of parameter (float)
        :returns: None
        """
        self.amp_tuning.setMaximum(value)


#==============================================================================
class DebugUi(QWidget):
    """Debug UI form used to debug script.
    """

    def __init__(self):
        """The constructor."""
        super().__init__()
        self.reg_add_led = QLineEdit("0x000")
        self.reg_val_led = QLineEdit("0x00")
        self.get_reg_btn = QPushButton("&Get register")
        self.set_reg_btn = QPushButton("&Set register")
        layout = QGridLayout()
        layout.addWidget(QLabel("Address"), 0, 0)
        layout.addWidget(QLabel("Value"), 0, 1)
        layout.addWidget(self.reg_add_led, 1, 0)
        layout.addWidget(self.reg_val_led, 1, 1)
        layout.addWidget(self.get_reg_btn, 2, 0)
        layout.addWidget(self.set_reg_btn, 2, 1)
        vbox = QVBoxLayout()
        vbox.addLayout(layout)
        vbox.addStretch(1)
        self.setLayout(vbox)


#==============================================================================
class DdsCtrlUi(QWidget):
    """User Interface of DDS controller project.
    """

    def __init__(self):
        """The constructor.
        """
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Setup UI and defines basic handling between widget.
        """
        self.ddsctrl_tabs = QTabWidget()
        self.ocontroller_ui = OutControllerUi()
        self.icontroller_ui = InControllerUi()
        self.debug_ui = DebugUi()
        # UI building
        self.ddsctrl_tabs.addTab(self.ocontroller_ui, "Output control")
        self.ddsctrl_tabs.addTab(self.icontroller_ui, "Input control")
        self.ddsctrl_tabs.addTab(self.debug_ui, "Debug")
        self.ddsctrl_tabs.show()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.ddsctrl_tabs)
        self.setLayout(self.layout)


#==============================================================================
if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication

    APP = QApplication(sys.argv)
    UI = DdsCtrlUi()
    UI.show()
    sys.exit(APP.exec_())
