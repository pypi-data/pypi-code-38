#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.views import CentroidScatterPlotWidget

class TestCentroidScatterPlotWidget:

    def makeColorTuple(self, obj):
        return (obj.color().red(), obj.color().blue(), obj.color().green())

    def test_parametersAfterConstruction(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        assert cspw.scatterPlot is not None
        assert cspw.dataSize is None
        assert cspw.xData is None
        assert cspw.yData is None
        assert cspw.xHistogramItem is None
        assert cspw.yHistogramItem is None
        assert cspw.numBins == 40
        assert cspw.rollArray is False
        assert cspw.dataCounter == 0
        assert cspw.brushes is None
        color = (159, 159, 159)
        assert cspw.brushColor == color
        assert cspw.maxAlpha == 255
        assert cspw.minAlpha == 127
        hFillBrush = self.makeColorTuple(cspw.histogramFillBrush)
        assert hFillBrush == color
        pBrush = self.makeColorTuple(cspw.pointBrush)
        assert pBrush == color

    def test_parametersAfterSetup(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        arraySize = 1000
        cspw.setup(arraySize)
        assert cspw.scatterPlot is not None
        assert cspw.dataSize == arraySize
        assert cspw.xData is not None
        assert cspw.yData is not None
        assert cspw.xHistogramItem is not None
        assert cspw.yHistogramItem is not None
        assert cspw.rollArray is False
        assert cspw.dataCounter == 0
        assert cspw.brushes is not None
        assert len(cspw.brushes) == arraySize
        assert cspw.brushes[0].color().alpha() == 127
        assert cspw.brushes[200].color().alpha() == 152
        assert cspw.brushes[400].color().alpha() == 178
        assert cspw.brushes[600].color().alpha() == 203
        assert cspw.brushes[800].color().alpha() == 229
        assert cspw.brushes[-1].color().alpha() == 255

    def test_updateData(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        arraySize = 3
        cspw.setup(arraySize)
        truthAlpha = [127, 191, 255]
        alpha = [x.color().alpha() for x in cspw.brushes]
        assert alpha == truthAlpha
        valuesX = [254.43, 254.86, 253.91, 254.21]
        valuesY = [355.25, 355.10, 354.89, 355.57]
        cspw.updateData(valuesX[0], valuesY[0])
        assert cspw.xData.tolist() == [valuesX[0]]
        assert cspw.yData.tolist() == [valuesY[0]]
        assert cspw.dataCounter == 1
        cspw.updateData(valuesX[1], valuesY[1])
        cspw.updateData(valuesX[2], valuesY[2])
        assert cspw.xData.tolist() == valuesX[:-1]
        assert cspw.yData.tolist() == valuesY[:-1]
        assert cspw.dataCounter == arraySize
        assert cspw.rollArray is True
        cspw.updateData(valuesX[3], valuesY[3])
        assert cspw.xData.tolist() == valuesX[1:]
        assert cspw.yData.tolist() == valuesY[1:]
        assert cspw.dataCounter == arraySize
        assert cspw.rollArray is True

    def test_showPlot(self, qtbot, mocker):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        arraySize = 3
        cspw.setup(arraySize)
        # Add some data so plot doesn't fail
        valuesX = [254.43, 254.86, 253.91, 254.21]
        valuesY = [355.25, 355.10, 354.89, 355.57]
        for x, y in zip(valuesX, valuesY):
            cspw.updateData(x, y)
        mockScatterSetData = mocker.patch.object(cspw.scatterPlotItem, 'setData')
        mockXHistSetData = mocker.patch.object(cspw.xHistogramItem, 'setData')
        mockYHistSetData = mocker.patch.object(cspw.yHistogramItem, 'setData')
        cspw.showPlot()
        assert mockScatterSetData.call_count == 1
        assert mockXHistSetData.call_count == 1
        assert mockYHistSetData.call_count == 1

    def test_updateArraySize(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        arraySize = 3
        cspw.setup(arraySize)
        cspw.rollArray = True
        newArraySize = 20
        cspw.setArraySize(newArraySize)
        assert cspw.dataSize == newArraySize
        assert cspw.xData.shape[0] == 0
        assert cspw.yData.shape[0] == 0
        assert len(cspw.brushes) == newArraySize
        assert cspw.rollArray is False

    def test_getConfiguration(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        config = {'numHistogramBins': 40}
        currentConfig = cspw.getConfiguration()
        assert currentConfig == config

    def test_setConfiguration(self, qtbot):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        truthConfig = {'numHistogramBins': 50}
        cspw.setConfiguration(truthConfig)
        cspw.numBins == truthConfig['numHistogramBins']

    def test_clearPlot(self, qtbot, mocker):
        cspw = CentroidScatterPlotWidget()
        qtbot.addWidget(cspw)
        arraySize = 3
        cspw.setup(arraySize)
        valuesX = [254.43, 254.86, 253.91, 254.21]
        valuesY = [355.25, 355.10, 354.89, 355.57]
        for x, y in zip(valuesX, valuesY):
            cspw.updateData(x, y)
        cspw.clearPlot()
        assert cspw.rollArray is False
        assert cspw.dataCounter == 0
        assert len(cspw.xData) == 0
        assert len(cspw.yData) == 0
