#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtWidgets import QDialogButtonBox

from spot_motion_monitor.utils import AutoscaleState
from spot_motion_monitor.views import PlotConfigurationDialog

class TestPlotConfigurationDialog:

    def test_parametersAfterConstruction(self, qtbot):
        pcDialog = PlotConfigurationDialog()
        qtbot.addWidget(pcDialog)
        pcDialog.show()

        assert pcDialog.tabWidget.count() == 2

    def test_setPlotConfiguration(self, qtbot, mocker):
        pcDialog = PlotConfigurationDialog()
        mockCentroidTabSetConfig = mocker.patch.object(pcDialog.centroidPlotConfigTab, 'setConfiguration')
        mockPsdTabSetConfig = mocker.patch.object(pcDialog.psdPlotConfigTab, 'setConfiguration')
        qtbot.addWidget(pcDialog)
        pcDialog.show()

        centroidConfig = {'xCentroid': {'autoscale': AutoscaleState.OFF.name, 'pixelAddition': None,
                                        'minimum': 10, 'maximum': 1000},
                          'yCentroid': {'autoscale': AutoscaleState.ON.name, 'pixelAddition': None,
                                        'minimum': None, 'maximum': None},
                          'scatterPlot': {'numHistogramBins': 50}}
        psdConfig = {'waterfall': {'numBins': 15, 'colorMap': None},
                     'xPSD': {'autoscale': True},
                     'yPSD': {'autoscale': False, 'maximum': 1320.0}}

        pcDialog.setPlotConfiguration(centroidConfig, psdConfig)
        assert mockCentroidTabSetConfig.call_count == 1
        assert mockPsdTabSetConfig.call_count == 1

    def test_getPlotConfiguration(self, qtbot, mocker):
        pcDialog = PlotConfigurationDialog()
        mockCentroidTabGetConfig = mocker.patch.object(pcDialog.centroidPlotConfigTab, 'getConfiguration')
        mockPsdTabGetConfig = mocker.patch.object(pcDialog.psdPlotConfigTab, 'getConfiguration')
        qtbot.addWidget(pcDialog)
        pcDialog.show()

        centroidConfig, psdConfig = pcDialog.getPlotConfiguration()
        assert mockCentroidTabGetConfig.call_count == 1
        assert mockPsdTabGetConfig.call_count == 1
        assert centroidConfig is not None
        assert psdConfig is not None

    def test_validInputFromTabs(self, qtbot):
        pcDialog = PlotConfigurationDialog()
        qtbot.addWidget(pcDialog)
        pcDialog.show()

        pcDialog.centroidPlotConfigTab.pixelAdditionXLineEdit.setText(str(-1))
        assert pcDialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        pcDialog.centroidPlotConfigTab.pixelAdditionXLineEdit.setText(str(10))
        assert pcDialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()
        pcDialog.psdPlotConfigTab.waterfallNumBinsLineEdit.setText(str(0))
        assert pcDialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
