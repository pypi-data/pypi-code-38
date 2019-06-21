#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

from spot_motion_monitor.utils import boolToCheckState
from spot_motion_monitor.views import GaussianCameraConfigTab

class TestGaussianCameraConfigTab:

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
        gcConfigTab = GaussianCameraConfigTab()
        qtbot.addWidget(gcConfigTab)

        assert gcConfigTab.name == 'Gaussian'
        assert gcConfigTab.spotOscillationCheckBox.isChecked() is False
        assert gcConfigTab.spotOscillationGroupBox.isEnabled() is False

    def test_setParametersFromConfiguration(self, qtbot):
        gcConfigTab = GaussianCameraConfigTab()
        qtbot.addWidget(gcConfigTab)

        config = {'roiSize': 30, 'doSpotOscillation': False,
                  'xAmplitude': 2, 'xFrequency': 50.0,
                  'yAmplitude': 7, 'yFrequency': 25.0}

        gcConfigTab.setConfiguration(config)
        assert int(gcConfigTab.roiSizeLineEdit.text()) == config['roiSize']
        state = gcConfigTab.spotOscillationCheckBox.checkState()
        boolState = True if state == Qt.Checked else False
        assert boolState == config['doSpotOscillation']
        assert int(gcConfigTab.xAmpLineEdit.text()) == config['xAmplitude']
        assert float(gcConfigTab.xFreqLineEdit.text()) == config['xFrequency']
        assert int(gcConfigTab.yAmpLineEdit.text()) == config['yAmplitude']
        assert float(gcConfigTab.yFreqLineEdit.text()) == config['yFrequency']

    def test_getParametersFromConfiguration(self, qtbot):
        gcConfigTab = GaussianCameraConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        truthConfig = {'roiSize': 30, 'doSpotOscillation': True,
                       'xAmplitude': 2, 'xFrequency': 50.0,
                       'yAmplitude': 7, 'yFrequency': 25.0}

        gcConfigTab.roiSizeLineEdit.setText(str(truthConfig['roiSize']))
        gcConfigTab.spotOscillationCheckBox.setChecked(boolToCheckState(truthConfig['doSpotOscillation']))
        gcConfigTab.xAmpLineEdit.setText(str(truthConfig['xAmplitude']))
        gcConfigTab.xFreqLineEdit.setText(str(truthConfig['xFrequency']))
        gcConfigTab.yAmpLineEdit.setText(str(truthConfig['yAmplitude']))
        gcConfigTab.yFreqLineEdit.setText(str(truthConfig['yFrequency']))

        config = gcConfigTab.getConfiguration()
        assert config == truthConfig

        truthConfig = {'roiSize': 50, 'doSpotOscillation': False}

        gcConfigTab.roiSizeLineEdit.setText(str(truthConfig['roiSize']))
        gcConfigTab.spotOscillationCheckBox.setChecked(boolToCheckState(truthConfig['doSpotOscillation']))

        config = gcConfigTab.getConfiguration()
        assert config == truthConfig

    def test_validLineEditParameters(self, qtbot):
        gcConfigTab = GaussianCameraConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.roiSizeLineEdit.setText,
                              [20, 200, 150])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.xAmpLineEdit.setText,
                              [1, 20, 10])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.xFreqLineEdit.setText,
                              [1.0, 100.0, 4e1])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.yAmpLineEdit.setText,
                              [1, 20, 10])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, True, gcConfigTab.yFreqLineEdit.setText,
                              [1.0, 100.0, 4e1])

    def test_invalidLineEditParameters(self, qtbot):
        gcConfigTab = GaussianCameraConfigTab()
        qtbot.addWidget(gcConfigTab)
        gcConfigTab.show()

        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.roiSizeLineEdit.setText,
                              [10, 40.1, 201])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.xAmpLineEdit.setText,
                              [0, 30, 5.1])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.xFreqLineEdit.setText,
                              [0.05, 5.6352, 2e2])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.yAmpLineEdit.setText,
                              [0, 30, 5.1])
        self.checkValidations(qtbot, gcConfigTab.hasValidInput, False, gcConfigTab.yFreqLineEdit.setText,
                              [0.05, 5.6352, 2e2])
