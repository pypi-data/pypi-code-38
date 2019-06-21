#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import pytest

from spot_motion_monitor.camera.base_camera import BaseCamera

class TestBaseCamera(object):

    def setup_class(self):
        self.baseCamera = BaseCamera()

    def test_nullParametersAfterConstruction(self):
        assert self.baseCamera.height is None
        assert self.baseCamera.width is None
        assert self.baseCamera.fpsFullFrame is None
        assert self.baseCamera.fpsRoiFrame is None
        assert self.baseCamera.roiSize is None
        assert self.baseCamera.name == 'Base'

    def test_noApiAfterConstruction(self):
        with pytest.raises(NotImplementedError):
            self.baseCamera.startup()

        with pytest.raises(NotImplementedError):
            self.baseCamera.shutdown()

        with pytest.raises(NotImplementedError):
            self.baseCamera.getFullFrame()

        with pytest.raises(NotImplementedError):
            self.baseCamera.getRoiFrame()

        with pytest.raises(NotImplementedError):
            self.baseCamera.getOffset()

        with pytest.raises(NotImplementedError):
            self.baseCamera.updateOffset(1, 1)

        with pytest.raises(NotImplementedError):
            self.baseCamera.resetOffset()

        with pytest.raises(NotImplementedError):
            self.baseCamera.waitOnRoi()

        with pytest.raises(NotImplementedError):
            self.baseCamera.showFrameStatus()

        with pytest.raises(NotImplementedError):
            self.baseCamera.getConfiguration()

        with pytest.raises(NotImplementedError):
            self.baseCamera.setConfiguration({})

        with pytest.raises(NotImplementedError):
            self.baseCamera.safeShutdown()

        assert self.baseCamera.checkFullFrame(1, 1, 1, 1) is True
        assert self.baseCamera.checkRoiFrame(1) is True
