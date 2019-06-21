#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from datetime import datetime

import numpy as np

from spot_motion_monitor.models.buffer_model import BufferModel
from spot_motion_monitor.utils.frame_information import GenericFrameInformation

class TestBufferModel():

    def setup_class(cls):
        cls.offset = (264, 200)
        cls.timestamp = datetime(2018, 10, 24, 1, 30, 0)

    def test_parametersAfterConstruction(self):
        model = BufferModel()
        assert model.bufferSize == 1024
        assert model.pixelScale == 1.0
        assert model.rollBuffer is False
        assert model.counter == 0
        assert model.timestamp is not None
        assert model.maxAdc is not None
        assert model.flux is not None
        assert model.centerX is not None
        assert model.centerY is not None
        assert model.objectSize is not None
        assert model.stdMax is not None

    def test_listsAfterPassingGenericFrameInfo(self):
        model = BufferModel()
        info = GenericFrameInformation(self.timestamp, 20.42, 30.42, 3245.32543, 119.24245, 60, 1.432435)
        model.updateInformation(info, self.offset)
        assert model.timestamp == [info.timestamp]
        assert model.maxAdc == [info.maxAdc]
        assert model.flux == [info.flux]
        assert model.centerX == [info.centerX + self.offset[0]]
        assert model.centerY == [info.centerY + self.offset[1]]
        assert model.objectSize == [info.objectSize]
        assert model.stdMax == [info.stdNoObjects]
        assert model.rollBuffer is False
        assert model.counter == 1

    def test_listSizesAfterBufferSizeReached(self):
        model = BufferModel()
        bufferSize = 3
        model.bufferSize = bufferSize
        assert model.counter == 0
        info = GenericFrameInformation(self.timestamp, 20.42, 30.42, 3245.32543, 119.24245, 60, 1.432435)
        for i in range(bufferSize):
            model.updateInformation(info, self.offset)
        assert model.rollBuffer is True
        assert len(model.flux) == bufferSize
        # Update one more time, buffer size should be fixed
        model.updateInformation(info, self.offset)
        assert model.rollBuffer is True
        assert len(model.flux) == bufferSize
        assert model.counter == bufferSize + 1

    def test_reset(self):
        model = BufferModel()
        bufferSize = 3
        model.bufferSize = bufferSize
        info = GenericFrameInformation(self.timestamp, 20.42, 30.42, 3245.32543, 119.24245, 60, 1.432435)
        for i in range(bufferSize):
            model.updateInformation(info, self.offset)
        model.reset()
        assert len(model.timestamp) == 0
        assert len(model.maxAdc) == 0
        assert len(model.flux) == 0
        assert len(model.centerX) == 0
        assert len(model.centerY) == 0
        assert len(model.objectSize) == 0
        assert len(model.stdMax) == 0
        assert model.rollBuffer is False
        assert model.counter == 0

    def test_getRoiFrameInformation(self):
        model = BufferModel()
        bufferSize = 3
        currentFps = 40
        duration = bufferSize / currentFps
        model.bufferSize = bufferSize
        model.pixelScale = 0.35

        info = model.getInformation(currentFps)
        assert info is None

        np.random.seed(2000)
        x = np.random.random(3)
        model.rollBuffer = True
        model.maxAdc = 119.53 + x
        model.flux = 2434.35 + x
        model.centerX = 200 + x
        model.centerY = 321.3 + x
        model.objectSize = np.random.randint(60, 65, bufferSize)
        model.stdMax = 1.42 + x
        model.counter = bufferSize

        info = model.getInformation(currentFps)
        assert info.flux == 2434.8911626243757
        assert info.maxAdc == 120.07116262437593
        assert info.centerX == 200.54116262437594
        assert info.centerY == 321.84116262437595
        assert info.rmsX == 0.013075758426286251
        assert info.rmsY == 0.013075758426290931
        # assert info.objectSize == 64.0
        # assert info.stdNoObjects == 1.9611626243759368
        assert info.validFrames == (bufferSize, duration)

        # model.stdMax[1] = np.nan
        # info = model.getInformation(duration)
        # assert info.stdNoObjects == 1.9494795589614855

    def test_getCentroids(self):
        model = BufferModel()
        bufferSize = 3
        model.bufferSize = bufferSize
        centroids = model.getCentroids()
        assert centroids == (None, None)
        info = GenericFrameInformation(self.timestamp, 20.42, 30.42, 3245.32543, 119.24245, 60, 1.432435)
        model.updateInformation(info, self.offset)
        centroidX = info.centerX + self.offset[0]
        centroidY = info.centerY + self.offset[1]
        centroids = model.getCentroids()
        assert centroids == (centroidX, centroidY)

    def test_getPsd(self):
        model = BufferModel()
        bufferSize = 3
        currentFps = 40
        model.bufferSize = bufferSize
        model.pixelScale = 0.35

        psd = model.getPsd(currentFps)
        assert psd == (None, None, None)

        np.random.seed(2000)
        x = np.random.random(3)
        model.rollBuffer = True
        model.timestamp = [self.timestamp] * 3
        model.maxAdc = (119.53 + x).tolist()
        model.flux = (2434.35 + x).tolist()
        model.centerX = (200 + x).tolist()
        model.centerY = (321.3 + x).tolist()
        model.objectSize = np.random.randint(60, 65, bufferSize).tolist()
        model.stdMax = (1.42 + x).tolist()
        model.counter = bufferSize

        assert model.counter == bufferSize
        psd = model.getPsd(currentFps)
        assert psd[0] is not None
        assert psd[1] is not None
        assert psd[2] is not None

        # Update by hand
        info = GenericFrameInformation(self.timestamp, 200.1423, 321.583, 2434.35982, 119.5382, 60, 1.432435)
        model.updateInformation(info, self.offset)

        assert model.counter == bufferSize + 1
        psd = model.getPsd(currentFps)
        assert psd == (None, None, None)
