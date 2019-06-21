#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLineEdit

import pytest

from spot_motion_monitor.views import BaseConfigTab

class TestBaseConfigTab:

    def setup_class(self):
        self.fast_timeout = 250  # ms

    def stateIsFalse(self, state):
        return not state

    def stateIsTrue(self, state):
        return state

    def test_parametersAfterConstruction(self, qtbot):
        baseTab = BaseConfigTab()
        qtbot.addWidget(baseTab)
        assert baseTab.name == 'Base'

    def test_noApiCallAfterConstruction(self, qtbot):
        baseTab = BaseConfigTab()
        qtbot.addWidget(baseTab)

        with pytest.raises(NotImplementedError):
            baseTab.getConfiguration()

        with pytest.raises(NotImplementedError):
            baseTab.setConfiguration({})

    def test_validInput(self, qtbot):
        baseTab = BaseConfigTab()
        qtbot.addWidget(baseTab)

        # Insert a widget for testing
        baseTab.lineEdit = QLineEdit()
        baseTab.lineEdit.setValidator(QIntValidator(1, 5))
        baseTab.lineEdit.textChanged.connect(baseTab.validateInput)

        with qtbot.waitSignal(baseTab.hasValidInput, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue) as valid:
            baseTab.lineEdit.setText('3')

        assert valid.signal_triggered

        with qtbot.waitSignal(baseTab.hasValidInput, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse) as valid:
            baseTab.lineEdit.setText('6')

        assert valid.signal_triggered
