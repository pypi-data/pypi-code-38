#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.config import VimbaCameraConfig

class TestVimbaCameraConfig:

    def setup_class(cls):
        cls.config = VimbaCameraConfig()

    def test_parametersAfterConstruction(self):
        assert self.config.roiSize == 50
        assert self.config.roiFluxMinimum == 2000
        assert self.config.roiExposureTime == 3000
