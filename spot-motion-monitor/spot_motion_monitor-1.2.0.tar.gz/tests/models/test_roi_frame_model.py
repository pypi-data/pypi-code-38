#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import pytest

from spot_motion_monitor.camera.gaussian_camera import GaussianCamera
from spot_motion_monitor.models.roi_frame_model import RoiFrameModel
from spot_motion_monitor.utils import FrameRejected

class TestRoiFrameModel():

    def setup_class(cls):
        cls.model = RoiFrameModel()

    def checkFrame(self, flux):
        return flux > 3000

    def test_parametersAfterConstruction(self):
        assert self.model.thresholdFactor == 0.3

    def test_frameCalculations(self):
        # This test requires the generation of a CCD frame which will be
        # provided by the GaussianCamera
        camera = GaussianCamera()
        camera.seed = 1000
        camera.startup()
        frame = camera.getRoiFrame()
        info = self.model.calculateCentroid(frame)
        assert info.centerX == 24.492516009567165
        assert info.centerY == 24.46080549340329
        assert info.flux == 2592.2000000000003
        assert info.maxAdc == 125.30000000000001
        assert info.objectSize == 54
        #assert info.stdNoObjects == 5.1785375980622534
        # See speed improvement in RoiFrameModel::calculateCentroid
        assert info.stdNoObjects == -999

    def test_failedFrameCheck(self):
        # This test requires the generation of a CCD frame which will be
        # provided by the GaussianCamera
        self.model.frameCheck = self.checkFrame
        camera = GaussianCamera()
        camera.seed = 1000
        camera.startup()
        frame = camera.getRoiFrame()
        with pytest.raises(FrameRejected):
            self.model.calculateCentroid(frame)
        self.model.frameCheck = None
