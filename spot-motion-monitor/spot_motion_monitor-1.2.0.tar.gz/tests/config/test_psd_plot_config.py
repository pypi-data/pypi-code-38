#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.config import PsdPlotConfig

class TestPsdPlotConfig:

    def setup_class(cls):
        cls.config = PsdPlotConfig()

    def test_parametersAfterConstruction(self):
        assert self.config.autoscaleX1d is False
        assert self.config.x1dMaximum == 1000
        assert self.config.autoscaleY1d is False
        assert self.config.y1dMaximum == 1000
        assert self.config.numWaterfallBins == 25
        assert self.config.waterfallColorMap == 'viridis'
