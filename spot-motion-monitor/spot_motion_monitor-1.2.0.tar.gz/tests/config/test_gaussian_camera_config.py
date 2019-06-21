#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.config import GaussianCameraConfig

class TestGaussianCameraConfig:

    def setup_class(cls):
        cls.config = GaussianCameraConfig()

    def test_parametersAfterConstruction(self):
        assert self.config.roiSize == 50
        assert self.config.doSpotOscillation is False
        assert self.config.xAmplitude == 10
        assert self.config.xFrequency == 5.0
        assert self.config.yAmplitude == 5
        assert self.config.yFrequency == 10.0
        assert self.config.deltaTime == 200
