#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.views import DataConfigTab

class TestDataConfigTab:

    def setup_class(self):
        self.fast_timeout = 250  # ms

    def stateIsFalse(self, state):
        return not state

    def stateIsTrue(self, state):
        return state

    def checkValidations(self, qtbot, checkSignal, checkState, checkFunc, valuesToCheck):
        if checkState:
            statusCheck = self.stateIsTrue
        else:
            statusCheck = self.stateIsFalse

        for valueToCheck in valuesToCheck:
            with qtbot.waitSignal(checkSignal, timeout=self.fast_timeout, check_params_cb=statusCheck):
                checkFunc(str(valueToCheck))

    def test_parametersAfterConstruction(self, qtbot):
        gcConfigTab = DataConfigTab()
        qtbot.addWidget(gcConfigTab)

        assert gcConfigTab.name == 'Data'

    def test_setParametersFromConfiguration(self, qtbot):
        gcConfigTab = DataConfigTab()
        qtbot.addWidget(gcConfigTab)

        config = {'pixelScale': 0.34}

        gcConfigTab.setConfiguration(config)
        assert float(gcConfigTab.pixelScaleLineEdit.text()) == config['pixelScale']

    def test_getParametersFromConfiguration(self, qtbot):
        gcConfigTab = DataConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        truthConfig = {'pixelScale': 0.75}

        gcConfigTab.pixelScaleLineEdit.setText(str(truthConfig['pixelScale']))

        config = gcConfigTab.getConfiguration()
        assert config == truthConfig

    def test_validLineEditParameters(self, qtbot):
        gcConfigTab = DataConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.pixelScaleLineEdit.setText,
                              [0.0, 1e200, 15000.532])

    def test_invalidLineEditParameters(self, qtbot):
        gcConfigTab = DataConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.pixelScaleLineEdit.setText,
                              [-1.0, 1e201, 0.05286930])
