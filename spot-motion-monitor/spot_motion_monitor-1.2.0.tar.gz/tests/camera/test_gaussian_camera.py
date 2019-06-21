#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.camera.gaussian_camera import GaussianCamera

class TestGaussianCamera():

    def setup_class(self):
        self.camera = GaussianCamera()

    def test_parametersAfterConstruction(self):
        assert self.camera.name == 'Gaussian'
        assert self.camera.seed is None
        assert self.camera.height == 480
        assert self.camera.width == 640
        assert self.camera.spotSize == 20
        assert self.camera.fpsFullFrame == 24
        assert self.camera.fpsRoiFrame == 40
        assert self.camera.roiSize == 50
        assert self.camera.postageStamp is None
        assert self.camera.xPoint is None
        assert self.camera.yPoint is None
        assert self.camera.doSpotOscillation is True
        assert self.camera.xAmp == 10
        assert self.camera.xFreq == 1.0
        assert self.camera.yAmp == 5
        assert self.camera.yFreq == 2.0

    def test_parametersAfterStartup(self):
        self.camera.startup()
        assert self.camera.postageStamp is not None
        assert self.camera.xPoint is not None
        assert self.camera.yPoint is not None

    def test_getFullFrame(self):
        self.camera.seed = 1000
        self.camera.startup()
        frame = self.camera.getFullFrame()
        assert frame.shape == (480, 640)
        max_point1, max_point2 = np.where(frame == np.max(frame))
        assert max_point1[0] == 225
        assert max_point2[0] == 288

    def test_getRoiFrame(self):
        self.camera.seed = 1000
        self.camera.startup()
        frame = self.camera.getRoiFrame()
        assert frame.shape == (50, 50)
        max_point1, max_point2 = np.where(frame == np.max(frame))
        assert max_point1[0] == 26
        assert max_point2[0] == 26

    def test_getOffset(self):
        self.camera.seed = 1000
        self.camera.startup()
        offset = self.camera.getOffset()
        assert offset == (264, 200)

    def test_getConfiguration(self):
        config = {'roiSize': 50, 'doSpotOscillation': True,
                  'xAmplitude': 10, 'xFrequency': 1.0,
                  'yAmplitude': 5, 'yFrequency': 2.0}
        currentConfig = self.camera.getConfiguration()
        assert currentConfig == config

    def test_setConfiguration(self):
        camera = GaussianCamera()
        truthConfig = {'roiSize': 75, 'doSpotOscillation': True,
                       'xAmplitude': 1, 'xFrequency': 40.0,
                       'yAmplitude': 8, 'yFrequency': 75.0}
        camera.setConfiguration(truthConfig)
        assert camera.roiSize == truthConfig['roiSize']
        assert camera.doSpotOscillation == truthConfig['doSpotOscillation']
        assert camera.xAmp == truthConfig['xAmplitude']
        assert camera.xFreq == truthConfig['xFrequency']
        assert camera.yAmp == truthConfig['yAmplitude']
        assert camera.yFreq == truthConfig['yFrequency']
