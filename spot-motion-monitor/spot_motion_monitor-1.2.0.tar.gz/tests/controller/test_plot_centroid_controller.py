#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

from spot_motion_monitor.controller import PlotCentroidController
from spot_motion_monitor.views import Centroid1dPlotWidget, CentroidScatterPlotWidget

class TestPlotCentroidController:

    def setup_class(cls):
        cls.bufferSize = 3
        cls.roiFps = 2

    def test_parametersAfterConstruction(self, qtbot):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)

        p1cc = PlotCentroidController(cxp, cyp, csp)
        assert p1cc.x1dPlot is not None
        assert p1cc.y1dPlot is not None
        assert p1cc.scatterPlot is not None

    def test_parametersAfterSetup(self, qtbot):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)

        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)

        assert p1cc.x1dPlot.dataSize == self.bufferSize
        assert p1cc.y1dPlot.dataSize == self.bufferSize
        assert p1cc.scatterPlot.dataSize == self.bufferSize

    def test_update(self, qtbot):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)

        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        centroidX = 253.543
        centroidY = 313.683
        p1cc.update(centroidX, centroidY)

        assert p1cc.x1dPlot.data[0] == centroidX
        assert p1cc.y1dPlot.data[0] == centroidY
        assert p1cc.scatterPlot.xData[0] == centroidX
        assert p1cc.scatterPlot.yData[0] == centroidY

    def test_badCentroidsUpdate(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        mocker.patch('spot_motion_monitor.views.centroid_1d_plot_widget.Centroid1dPlotWidget.updatePlot')
        mocker.patch('spot_motion_monitor.views.centroid_scatter_plot_widget.'
                     'CentroidScatterPlotWidget.updateData')

        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        p1cc.update(None, None)
        assert p1cc.x1dPlot.updatePlot.call_count == 0
        assert p1cc.y1dPlot.updatePlot.call_count == 0
        assert p1cc.scatterPlot.updateData.call_count == 0

    def test_showScatterPlots(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        mocker.patch('spot_motion_monitor.views.centroid_scatter_plot_widget.'
                     'CentroidScatterPlotWidget.showPlot')
        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        centroidX = 253.543
        centroidY = 313.683
        p1cc.update(centroidX, centroidY)
        p1cc.showScatterPlots(False)
        assert p1cc.scatterPlot.showPlot.call_count == 0
        p1cc.showScatterPlots(True)
        assert p1cc.scatterPlot.showPlot.call_count == 1

    def test_updateRoiFps(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        p1cc = PlotCentroidController(cxp, cyp, csp)
        mockXSetRoiFps = mocker.patch.object(p1cc.x1dPlot, 'setRoiFps')
        mockYSetRoiFps = mocker.patch.object(p1cc.y1dPlot, 'setRoiFps')
        p1cc.setup(self.bufferSize, self.roiFps)
        p1cc.updateRoiFps(20)
        assert mockXSetRoiFps.call_count == 1
        assert mockYSetRoiFps.call_count == 1

    def test_updateBufferSize(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        mockXSetArraySize = mocker.patch.object(p1cc.x1dPlot, 'setArraySize')
        mockYSetArraySize = mocker.patch.object(p1cc.y1dPlot, 'setArraySize')
        mockScatterSetArraySize = mocker.patch.object(p1cc.scatterPlot, 'setArraySize')
        p1cc.updateBufferSize(512)
        assert mockXSetArraySize.call_count == 1
        assert mockYSetArraySize.call_count == 1
        assert mockScatterSetArraySize.call_count == 1

    def test_getPlotConfiguration(self, qtbot):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        p1cc = PlotCentroidController(cxp, cyp, csp)
        currentConfig = p1cc.getPlotConfiguration()
        assert len(currentConfig) == 3
        assert list(currentConfig.keys()) == ['scatterPlot', 'xCentroid', 'yCentroid']

    def test_setPlotConfiguration(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        mockXSetConfiguration = mocker.patch.object(p1cc.x1dPlot, 'setConfiguration')
        mockYSetConfiguration = mocker.patch.object(p1cc.y1dPlot, 'setConfiguration')
        mockScatterSetConfiguration = mocker.patch.object(p1cc.scatterPlot, 'setConfiguration')

        truthConfig = {'xCentroid': {'autoscale': False, 'minimum': 10, 'maximum': 1000},
                       'yCentroid': {'autoscale': True, 'minimum': None, 'maximum': None},
                       'scatterPlot': {'numHistogramBins': 50}}
        p1cc.setPlotConfiguration(truthConfig)
        assert mockXSetConfiguration.call_count == 1
        assert mockYSetConfiguration.call_count == 1
        assert mockScatterSetConfiguration.call_count == 1

    def test_handleAcquireRoiStateChange(self, qtbot, mocker):
        cxp = Centroid1dPlotWidget()
        cyp = Centroid1dPlotWidget()
        csp = CentroidScatterPlotWidget()
        qtbot.addWidget(cxp)
        qtbot.addWidget(cyp)
        qtbot.addWidget(csp)
        p1cc = PlotCentroidController(cxp, cyp, csp)
        p1cc.setup(self.bufferSize, self.roiFps)
        mockXClearPlot = mocker.patch.object(p1cc.x1dPlot, 'clearPlot')
        mockYClearPlot = mocker.patch.object(p1cc.y1dPlot, 'clearPlot')
        mockScatterClearPlot = mocker.patch.object(p1cc.scatterPlot, 'clearPlot')
        p1cc.handleAcquireRoiStateChange(Qt.Unchecked)
        assert mockXClearPlot.call_count == 1
        assert mockYClearPlot.call_count == 1
        assert mockScatterClearPlot.call_count == 1
