#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import collections

from PyQt5.QtCore import Qt

try:
    import pymba  # noqa
    VimbaFound = True
except AssertionError:
    VimbaFound = False

from spot_motion_monitor.controller.camera_controller import CameraController
from spot_motion_monitor.utils import CameraNotFound, FrameRejected, ONE_SECOND_IN_MILLISECONDS
from spot_motion_monitor.views.camera_control_widget import CameraControlWidget

class TestCameraController():

    def test_parametersAfterConstruction(self, qtbot):
        ccWidget = CameraControlWidget()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        assert cc.cameraControlWidget is not None
        assert cc.camera is None
        assert cc.frameTimer is not None
        assert cc.updater is not None
        assert cc.doAutoRun is False

    def test_cameraObject(self, qtbot):
        ccWidget = CameraControlWidget()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        assert cc.camera is not None
        assert hasattr(cc.camera, "seed")

    def test_cameraStartStop(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.startup')
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        assert cc.camera.startup.call_count == 1
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.shutdown')
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        assert cc.camera.shutdown.call_count == 1

    def test_cameraAcquireFrames(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        assert cc.frameTimer.isActive()
        interval = int((1 / cc.currentCameraFps()) * ONE_SECOND_IN_MILLISECONDS)
        assert cc.frameTimer.interval() == interval
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        assert not cc.frameTimer.isActive()

    def test_cameraCurrentFps(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        fps = cc.currentCameraFps()
        assert fps == 24
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        fps = cc.currentCameraFps()
        assert fps == 40

    def test_cameraAcquireRoiFrames(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        interval = int((1 / cc.currentCameraFps()) * ONE_SECOND_IN_MILLISECONDS)
        assert cc.frameTimer.interval() == interval
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        interval = int((1 / cc.currentCameraFps()) * ONE_SECOND_IN_MILLISECONDS)
        assert cc.frameTimer.interval() == interval
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)

    def test_cameraAcquireExpectedFrame(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        frame = cc.getFrame()
        assert frame.shape == (480, 640)
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        frame = cc.getFrame()
        assert frame.shape == (50, 50)

    def test_isRoiMode(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        isRoiMode = cc.isRoiMode()
        assert isRoiMode is False
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        isRoiMode = cc.isRoiMode()
        assert isRoiMode is True

    def test_currentOffset(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.camera.seed = 1000
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        offset = cc.currentOffset()
        assert offset == (264, 200)

    def test_currentStatus(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.camera.seed = 1000
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        status = cc.currentStatus()
        assert status.currentFps == 24
        assert status.isRoiMode is False
        assert status.frameOffset == (264, 200)
        assert status.showFrames is True
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        qtbot.mouseClick(ccWidget.showFramesCheckBox, Qt.LeftButton)
        status = cc.currentStatus()
        assert status.currentFps == 40
        assert status.isRoiMode is True
        assert status.frameOffset == (264, 200)
        assert status.showFrames is False

    def test_currentRoiFps(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        roiFps = cc.currentRoiFps()
        assert roiFps == 40

    def test_changeRoiFps(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        truthRoiFps = 70
        cc.cameraControlWidget.roiFpsSpinBox.setValue(truthRoiFps)
        assert cc.currentRoiFps() == truthRoiFps

    def test_changeBufferSize(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        with qtbot.waitSignal(cc.updater.bufferSizeChanged) as blocker:
            cc.cameraControlWidget.bufferSizeSpinBox.stepUp()
        assert blocker.args == [2048]

    def test_badCameraStartup(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.camera.startup = mocker.Mock(side_effect=CameraNotFound)
        cc.startStopCamera(True)
        assert ccWidget.startStopButton.isChecked() is False

    def test_frameChecks(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        check1, check2 = cc.getFrameChecks()
        assert check1(1, 1, 1, 1) is True
        assert check2(1) is True

    def test_cameraAcquireRejectedFrame(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.camera.getFullFrame = mocker.Mock(side_effect=FrameRejected)
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        frame = cc.getFrame()
        assert frame is None
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)

    def test_getUpdateFrame(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        frame = cc.getUpdateFrame()
        assert frame.shape == (480, 640)

    def test_updateCameraOffset(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        cameraOffset = mocker.patch.object(cc.camera, 'updateOffset')
        cc.updateCameraOffset(200, 400)
        assert cameraOffset.call_count == 1

    def test_getAvailableCameras(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cameras = cc.getAvailableCameras()
        if VimbaFound:
            assert len(cameras) == 2
            assert cameras[0] == 'Vimba'
        else:
            assert len(cameras) == 1
            assert cameras[0] == 'Gaussian'

    def test_getCameraConfiguration(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        config = cc.getCameraConfiguration()
        assert len(config) == 6

    def test_setCameraConfiguration(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")

        mockSetCameraConfiguration = mocker.patch.object(cc.camera, 'setConfiguration')

        cc.setCameraConfiguration({})
        assert mockSetCameraConfiguration.call_count == 1

    def test_setCommandLineConfig(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")

        args = collections.namedtuple('args', ['auto_run', 'vimba_camera_index'])
        args.auto_run = True

        cc.setCommandLineConfig(args)
        assert cc.doAutoRun is True

    def test_autoRun(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        cc.doAutoRun = True
        cc.autoRun()

        fps = cc.currentCameraFps()
        assert fps == 40

    def test_safeShutdown(self, qtbot, mocker):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.safeShutdown')
        cc.shutdownCamera()
        assert cc.camera.safeShutdown.call_count == 1

    def test_stateAtAcquireFramesStop(self, qtbot):
        ccWidget = CameraControlWidget()
        ccWidget.show()
        qtbot.addWidget(ccWidget)
        cc = CameraController(ccWidget)
        cc.setupCamera("GaussianCamera")
        qtbot.mouseClick(ccWidget.startStopButton, Qt.LeftButton)
        #cc.startStopCamera(True)
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        qtbot.mouseClick(ccWidget.acquireRoiCheckBox, Qt.LeftButton)
        assert cc.isRoiMode() is True
        qtbot.mouseClick(ccWidget.acquireFramesButton, Qt.LeftButton)
        assert cc.isRoiMode() is False
        assert cc.currentCameraFps() == 24
        assert ccWidget.acquireFramesButton.isChecked() is False
