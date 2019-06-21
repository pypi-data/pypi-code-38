#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.views import CentroidPlotConfigTab
from spot_motion_monitor.utils import AutoscaleState

class TestCentroidPlotConfigTab:

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
        configTab = CentroidPlotConfigTab()
        qtbot.addWidget(configTab)
        assert configTab.name == 'Centroid'

    def test_setParametersFromConfiguration(self, qtbot):
        configTab = CentroidPlotConfigTab()
        qtbot.addWidget(configTab)

        config = {'xCentroid': {'autoscale': AutoscaleState.OFF.name, 'pixelAddition': None,
                                'minimum': 10, 'maximum': 1000},
                  'yCentroid': {'autoscale': AutoscaleState.ON.name, 'pixelAddition': None,
                                'minimum': None, 'maximum': None},
                  'scatterPlot': {'numHistogramBins': 50}}

        configTab.setConfiguration(config)
        xState = configTab.autoscaleXComboBox.currentText()
        assert xState == config['xCentroid']['autoscale']
        assert configTab.pixelAdditionXLineEdit.text() == ''
        assert configTab.pixelAdditionXLabel.isEnabled() is False
        assert configTab.pixelAdditionXLineEdit.isEnabled() is False
        assert configTab.minXLimitLabel.isEnabled() is True
        assert configTab.minXLimitLineEdit.isEnabled() is True
        assert configTab.maxXLimitLabel.isEnabled() is True
        assert configTab.maxXLimitLineEdit.isEnabled() is True
        assert int(configTab.minXLimitLineEdit.text()) == config['xCentroid']['minimum']
        assert int(configTab.maxXLimitLineEdit.text()) == config['xCentroid']['maximum']
        yState = configTab.autoscaleYComboBox.currentText()
        assert yState == config['yCentroid']['autoscale']
        assert configTab.pixelAdditionYLabel.isEnabled() is False
        assert configTab.pixelAdditionYLineEdit.isEnabled() is False
        assert configTab.minYLimitLabel.isEnabled() is False
        assert configTab.minYLimitLineEdit.isEnabled() is False
        assert configTab.maxYLimitLabel.isEnabled() is False
        assert configTab.maxYLimitLineEdit.isEnabled() is False
        assert configTab.pixelAdditionXLineEdit.text() == ''
        assert configTab.minYLimitLineEdit.text() == ''
        assert configTab.maxYLimitLineEdit.text() == ''
        assert int(configTab.numHistoBinsLineEdit.text()) == config['scatterPlot']['numHistogramBins']

        config['yCentroid']['autoscale'] = AutoscaleState.PARTIAL.name
        config['yCentroid']['pixelAddition'] = 10
        configTab.setConfiguration(config)
        yState = configTab.autoscaleYComboBox.currentText()
        assert yState == config['yCentroid']['autoscale']
        assert configTab.pixelAdditionYLineEdit.isEnabled() is True
        assert configTab.minYLimitLineEdit.isEnabled() is False
        assert configTab.maxYLimitLineEdit.isEnabled() is False
        assert int(configTab.pixelAdditionYLineEdit.text()) == config['yCentroid']['pixelAddition']

    def test_getParametersFromConfiguration(self, qtbot):
        configTab = CentroidPlotConfigTab()
        qtbot.addWidget(configTab)
        configTab.show()

        truthConfig = {'xCentroid': {'autoscale': AutoscaleState.OFF.name, 'minimum': 10, 'maximum': 1000},
                       'yCentroid': {'autoscale': AutoscaleState.ON.name},
                       'scatterPlot': {'numHistogramBins': 30}}

        configTab.autoscaleXComboBox.setCurrentText(truthConfig['xCentroid']['autoscale'])
        configTab.minXLimitLineEdit.setText(str(truthConfig['xCentroid']['minimum']))
        configTab.maxXLimitLineEdit.setText(str(truthConfig['xCentroid']['maximum']))
        configTab.autoscaleYComboBox.setCurrentText(truthConfig['yCentroid']['autoscale'])
        configTab.numHistoBinsLineEdit.setText(str(truthConfig['scatterPlot']['numHistogramBins']))
        config = configTab.getConfiguration()
        assert config == truthConfig

        truthConfig['yCentroid']['autoscale'] = AutoscaleState.PARTIAL.name
        truthConfig['yCentroid']['pixelAddition'] = 10
        configTab.autoscaleYComboBox.setCurrentText(truthConfig['yCentroid']['autoscale'])
        configTab.pixelAdditionYLineEdit.setText(str(truthConfig['yCentroid']['pixelAddition']))
        config = configTab.getConfiguration()
        assert config == truthConfig

    def test_validLineEditParameters(self, qtbot):
        configTab = CentroidPlotConfigTab()
        qtbot.addWidget(configTab)
        configTab.show()

        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.pixelAdditionXLineEdit.setText,
                              [1, 10000, 150])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.minXLimitLineEdit.setText,
                              [0, int(1e9), int(1e4)])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.maxXLimitLineEdit.setText,
                              [0, int(1e9), int(1e4)])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.pixelAdditionYLineEdit.setText,
                              [1, 10000, 150])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.minYLimitLineEdit.setText,
                              [0, int(1e9), int(1e4)])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.maxYLimitLineEdit.setText,
                              [0, int(1e9), int(1e4)])
        self.checkValidations(qtbot, configTab.hasValidInput, True, configTab.numHistoBinsLineEdit.setText,
                              [1, int(1e9), int(1e4)])

    def test_invalidLineEditParameters(self, qtbot):
        configTab = CentroidPlotConfigTab()
        qtbot.addWidget(configTab)
        configTab.show()

        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.pixelAdditionXLineEdit.setText,
                              [0, 10001, 40.1])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.minXLimitLineEdit.setText,
                              [-1, int(1e10), 1.1e4])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.maxXLimitLineEdit.setText,
                              [-1, int(1e10), 1.1e4])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.pixelAdditionYLineEdit.setText,
                              [0, 10001, 40.1])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.minYLimitLineEdit.setText,
                              [-1, int(1e10), 1.1e4])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.maxYLimitLineEdit.setText,
                              [-1, int(1e10), 1.1e4])
        self.checkValidations(qtbot, configTab.hasValidInput, False, configTab.numHistoBinsLineEdit.setText,
                              [0, int(1e10), 1.1e4])
