#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.views import Psd1dPlotWidget

class TestPsd1dPlotWidget:

    def test_parametersAfterConstruction(self, qtbot):
        p1dpw = Psd1dPlotWidget()
        qtbot.addWidget(p1dpw)
        assert p1dpw.plot is not None
        assert p1dpw.curve is not None
        assert p1dpw.autoscale is True
        assert p1dpw.yRange is None

    def test_updatePlot(self, qtbot, mocker):
        p1dpw = Psd1dPlotWidget()
        qtbot.addWidget(p1dpw)
        p1dpw.setup('X')
        mockSetData = mocker.patch.object(p1dpw.curve, 'setData')

        data = np.array([10.0, 3.1, 5.1])
        freqs = np.array([1.3, 2.5, 3.9])
        p1dpw.updatePlot(data, freqs)
        assert mockSetData.call_count == 1

    def test_getConfiguration(self, qtbot):
        p1dpw = Psd1dPlotWidget()
        p1dpw.show()
        qtbot.addWidget(p1dpw)
        truthConfig = {'autoscale': True, 'minimum': None, 'maximum': None}
        config = p1dpw.getConfiguration()
        assert config == truthConfig

    def test_setConfiguration(self, qtbot):
        p1dpw = Psd1dPlotWidget()
        p1dpw.show()
        qtbot.addWidget(p1dpw)
        p1dpw.setup('X')
        truthConfig = {'autoscale': False, 'minimum': 10, 'maximum': 100}
        p1dpw.setConfiguration(truthConfig)
        assert p1dpw.autoscale is False
        assert p1dpw.yRange == [truthConfig['minimum'], truthConfig['maximum']]
        truthConfig = {'autoscale': True}
        p1dpw.setConfiguration(truthConfig)
        assert p1dpw.autoscale is True
        assert p1dpw.yRange is None
        truthConfig = {'autoscale': False, 'minimum': None, 'maximum': None}
        p1dpw.setConfiguration(truthConfig)
        assert p1dpw.autoscale is False
        assert p1dpw.yRange == [0, 1000]

    def test_clearPlot(self, qtbot, mocker):
        p1dpw = Psd1dPlotWidget()
        p1dpw.show()
        qtbot.addWidget(p1dpw)
        p1dpw.setup('X')
        mockSetData = mocker.patch.object(p1dpw.curve, 'setData')
        data = np.array([10.0, 3.1, 5.1])
        freqs = np.array([1.3, 2.5, 3.9])
        p1dpw.updatePlot(data, freqs)
        p1dpw.clearPlot()
        assert mockSetData.call_count == 2
