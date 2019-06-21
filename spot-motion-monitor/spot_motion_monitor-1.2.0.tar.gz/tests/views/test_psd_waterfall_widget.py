#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.views import PsdWaterfallPlotWidget

class TestPsdWaterfallPlotWidget:

    def setImage(*args):
        # args[0] is test class instance
        # args[1] is argument to ImageItem::setImage call
        args[0].pwpw1.image.image = args[1]

    def setup_class(cls):
        cls.pwpw1 = PsdWaterfallPlotWidget()
        cls.timeScale = 10
        cls.p1 = np.arange(5, dtype=float) + 1
        cls.p2 = np.arange(5, 10, dtype=float) + 1
        cls.p3 = np.linspace(0.2, 1.2, 5)

    def test_parametersAfterConstruction(self, qtbot):
        pwpw = PsdWaterfallPlotWidget()
        qtbot.addWidget(pwpw)
        assert pwpw.image is not None
        assert pwpw.data is None
        assert pwpw.arraySize is None
        assert pwpw.boundingRect is None
        assert pwpw.timeScale is None
        assert pwpw.colorMap == 'viridis'

    def test_parametersAfterSetup(self, qtbot):
        pwpw = PsdWaterfallPlotWidget()
        qtbot.addWidget(pwpw)
        arraySize = 5
        pwpw.setup(arraySize, self.timeScale, 'X')
        assert pwpw.arraySize == arraySize
        assert pwpw.timeScale == self.timeScale

    def test_parametersAfterUpdatePlot(self, qtbot, mocker):
        qtbot.addWidget(self.pwpw1)
        mockSetImage = mocker.patch.object(self.pwpw1.image, 'setImage')
        mockSetImage.side_effect = self.setImage
        arraySize = 3
        self.pwpw1.setup(arraySize, self.timeScale, 'X')

        self.pwpw1.updatePlot(self.p1, self.p3)
        assert self.pwpw1.data.shape == (arraySize, self.p1.size)
        assert (self.pwpw1.data[0, ...] == np.log(self.p1)).all()
        assert mockSetImage.call_count == 1
        rectCoords = self.pwpw1.boundingRect.getCoords()
        assert rectCoords[0] == 0
        assert rectCoords[1] == 0
        assert rectCoords[2] == 1.2
        assert rectCoords[3] == 30

        self.pwpw1.updatePlot(self.p2, self.p3)
        assert (self.pwpw1.data[0, ...] == np.log(self.p2)).all()
        assert (self.pwpw1.data[1, ...] == np.log(self.p1)).all()
        assert mockSetImage.call_count == 2

    def test_updateTimeScale(self, qtbot, mocker):
        self.pwpw1 = PsdWaterfallPlotWidget()
        qtbot.addWidget(self.pwpw1)
        mockSetImage = mocker.patch.object(self.pwpw1.image, 'setImage')
        mockSetImage.side_effect = self.setImage
        arraySize = 3
        self.pwpw1.setup(arraySize, self.timeScale, 'X')

        self.pwpw1.updatePlot(self.p1, self.p3)
        newTimeScale = 20
        self.pwpw1.setTimeScale(newTimeScale)
        assert self.pwpw1.timeScale == newTimeScale
        assert self.pwpw1.boundingRect is None
        assert self.pwpw1.data is None

        self.pwpw1.updatePlot(self.p2, self.p3)
        rectCoords = self.pwpw1.boundingRect.getCoords()
        assert rectCoords[0] == 0
        assert rectCoords[1] == 0
        assert rectCoords[2] == 1.2
        assert rectCoords[3] == 60

    def test_getConfiguration(self, qtbot):
        self.pwpw1 = PsdWaterfallPlotWidget()
        qtbot.addWidget(self.pwpw1)
        arraySize = 5
        self.pwpw1.setup(arraySize, self.timeScale, 'X')
        config = {'numBins': 5, 'colorMap': 'viridis'}
        currentConfig = self.pwpw1.getConfiguration()
        assert currentConfig == config

    def test_setConfiguration(self, qtbot):
        pwpw2 = PsdWaterfallPlotWidget()
        qtbot.addWidget(pwpw2)
        arraySize = 5
        pwpw2.setup(arraySize, self.timeScale, 'X')
        truthConfig = {'numBins': 10, 'colorMap': 'plasma'}
        pwpw2.setConfiguration(truthConfig)
        assert pwpw2.arraySize == truthConfig['numBins']
        assert pwpw2.data is None
        assert pwpw2.boundingRect is None
        assert pwpw2.colorMap == truthConfig['colorMap']

    def test_clearPlot(self, qtbot, mocker):
        pwpw2 = PsdWaterfallPlotWidget()
        qtbot.addWidget(pwpw2)
        arraySize = 5
        mockImageClear = mocker.patch.object(pwpw2.image, 'clear')
        pwpw2.setup(arraySize, self.timeScale, 'X')
        pwpw2.clearPlot()
        assert pwpw2.data is None
        assert pwpw2.boundingRect is None
        assert mockImageClear.call_count == 1
