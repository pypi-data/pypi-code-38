#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
from PyQt5.QtCore import Qt

from spot_motion_monitor.controller import PlotPsdController
from spot_motion_monitor.views import PsdWaterfallPlotWidget, Psd1dPlotWidget

class TestPlotPsdController:

    def setup_class(cls):
        cls.arraySize = 5
        cls.timeScale = 10

    def test_parametersAfterContruction(self, qtbot):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        assert pfc.psdWaterfallXPlot is not None
        assert pfc.psdWaterfallYPlot is not None
        assert pfc.psd1dXPlot is not None
        assert pfc.psd1dYPlot is not None

    def test_parametersAfterSetup(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        mockSetup1dXPlot = mocker.patch.object(pfc.psd1dXPlot, 'setup')
        mockSetup1dYPlot = mocker.patch.object(pfc.psd1dYPlot, 'setup')
        pfc.setup(self.arraySize, self.timeScale)
        assert pfc.psdWaterfallXPlot.arraySize == self.arraySize
        assert pfc.psdWaterfallYPlot.arraySize == self.arraySize
        assert mockSetup1dXPlot.call_count == 1
        assert mockSetup1dYPlot.call_count == 1

    def test_update(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        np.random.seed(3000)
        psdDataX = np.random.random(7)
        psdDataY = np.random.random(7)
        freqs = np.random.random(7)

        mockPsdWaterfallXPlotUpdatePlot = mocker.patch.object(pfc.psdWaterfallXPlot, 'updatePlot')
        mockPsdWaterfallYPlotUpdatePlot = mocker.patch.object(pfc.psdWaterfallYPlot, 'updatePlot')
        mockPsd1dXPlotUpdatePlot = mocker.patch.object(pfc.psd1dXPlot, 'updatePlot')
        mockPsd1dYPlotUpdatePlot = mocker.patch.object(pfc.psd1dYPlot, 'updatePlot')

        pfc.update(psdDataX, psdDataY, freqs)

        assert mockPsdWaterfallXPlotUpdatePlot.call_count == 1
        assert mockPsdWaterfallYPlotUpdatePlot.call_count == 1
        assert mockPsd1dXPlotUpdatePlot.call_count == 1
        assert mockPsd1dYPlotUpdatePlot.call_count == 1

    def test_badFftData(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        mockPsdXPlotUpdatePlot = mocker.patch.object(pfc.psdWaterfallXPlot, 'updatePlot')
        mockPsdYPlotUpdatePlot = mocker.patch.object(pfc.psdWaterfallYPlot, 'updatePlot')
        mockPsd1dXPlotUpdatePlot = mocker.patch.object(pfc.psd1dXPlot, 'updatePlot')
        mockPsd1dYPlotUpdatePlot = mocker.patch.object(pfc.psd1dYPlot, 'updatePlot')
        pfc.update(None, None, None)

        assert mockPsdXPlotUpdatePlot.call_count == 0
        assert mockPsdYPlotUpdatePlot.call_count == 0
        assert mockPsd1dXPlotUpdatePlot.call_count == 0
        assert mockPsd1dYPlotUpdatePlot.call_count == 0

    def test_updateTimeScale(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        mockPsdXPlotSetTimeScale = mocker.patch.object(pfc.psdWaterfallXPlot, 'setTimeScale')
        mockPsdYPlotSetTimeScale = mocker.patch.object(pfc.psdWaterfallYPlot, 'setTimeScale')
        pfc.updateTimeScale(100)

        assert mockPsdXPlotSetTimeScale.call_count == 1
        assert mockPsdYPlotSetTimeScale.call_count == 1

    def test_getPlotConfiguration(self, qtbot):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        currentConfig = pfc.getPlotConfiguration()
        assert len(currentConfig) == 3
        assert list(currentConfig.keys()) == ['waterfall', 'xPSD', 'yPSD']

    def test_setPlotConfiguration(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        mockPsdXWaterfallSetConfig = mocker.patch.object(pfc.psdWaterfallXPlot, 'setConfiguration')
        mockPsdYWaterfallSetConfig = mocker.patch.object(pfc.psdWaterfallYPlot, 'setConfiguration')
        mockPsdX1dSetConfig = mocker.patch.object(pfc.psd1dXPlot, 'setConfiguration')
        mockPsdY1dSetConfig = mocker.patch.object(pfc.psd1dYPlot, 'setConfiguration')

        truthConfig = {'waterfall': {'numBins': 10, 'colorMap': None},
                       'xPSD': {'autoscale': True},
                       'yPSD': {'autoscale': True}}
        pfc.setPlotConfiguration(truthConfig)

        assert mockPsdXWaterfallSetConfig.call_count == 1
        assert mockPsdYWaterfallSetConfig.call_count == 1
        assert mockPsdX1dSetConfig.call_count == 1
        assert mockPsdY1dSetConfig.call_count == 1

    def test_handleAcquireRoiStateChange(self, qtbot, mocker):
        psdwfx = PsdWaterfallPlotWidget()
        psdwfy = PsdWaterfallPlotWidget()
        psd1dx = Psd1dPlotWidget()
        psd1dy = Psd1dPlotWidget()
        qtbot.addWidget(psdwfx)
        qtbot.addWidget(psdwfy)
        qtbot.addWidget(psd1dx)
        qtbot.addWidget(psd1dy)

        pfc = PlotPsdController(psdwfx, psdwfy, psd1dx, psd1dy)
        pfc.setup(self.arraySize, self.timeScale)

        mockPsdXWaterfallClearPlot = mocker.patch.object(pfc.psdWaterfallXPlot, 'clearPlot')
        mockPsdYWaterfallClearPlot = mocker.patch.object(pfc.psdWaterfallYPlot, 'clearPlot')
        mockPsdX1dClearPlot = mocker.patch.object(pfc.psd1dXPlot, 'clearPlot')
        mockPsdY1dClearPlot = mocker.patch.object(pfc.psd1dYPlot, 'clearPlot')

        pfc.handleAcquireRoiStateChange(Qt.Unchecked)

        assert mockPsdXWaterfallClearPlot.call_count == 1
        assert mockPsdYWaterfallClearPlot.call_count == 1
        assert mockPsdX1dClearPlot.call_count == 1
        assert mockPsdY1dClearPlot.call_count == 1
