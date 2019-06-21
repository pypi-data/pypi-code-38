#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.config import CentroidPlotConfig

class TestCentroidPlotConfig:

    def setup_class(cls):
        cls.config = CentroidPlotConfig()

    def test_parametersAfterConstruction(self):
        assert self.config.autoscaleX is False
        assert self.config.minimumX == 0
        assert self.config.maximumX == 100
        assert self.config.autoscaleY is False
        assert self.config.minimumY == 0
        assert self.config.maximumY == 100
        assert self.config.numHistogramBins == 40
