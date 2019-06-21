#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import collections

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QMainWindow
import pytest

from spot_motion_monitor.camera import CameraStatus
from spot_motion_monitor.utils import CameraNotFound, FrameRejected, ONE_SECOND_IN_MILLISECONDS
from spot_motion_monitor.views.main_window import SpotMotionMonitor

class TestMainWindow():

    # def setup_class(cls):
    #     cls.fastTimeout = 1250  # ms

    def test_mainWindowExit(self, qtbot, mocker):
        mocker.patch('PyQt5.QtWidgets.QMainWindow.close')
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        mw.actionExit.trigger()
        assert QMainWindow.close.call_count == 1

    def test_mainWindowAbout(self, qtbot, mocker):
        mocker.patch('spot_motion_monitor.views.main_window.SpotMotionMonitor.about')
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        mw.actionAbout.trigger()
        assert SpotMotionMonitor.about.call_count == 1

    def test_setActionIcon(self, qtbot):
        mw = SpotMotionMonitor()
        qtbot.addWidget(mw)
        action = QAction()
        mw.setActionIcon(action, "test.png", True)
        assert action.icon() is not None
        assert action.isIconVisibleInMenu() is True

    def test_updateStatusBar(self, qtbot):
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        message1 = "Hello World!"
        mw.cameraController.updater.displayStatus.emit(message1, ONE_SECOND_IN_MILLISECONDS)
        assert mw.statusbar.currentMessage() == message1
        message2 = "Have a nice evening!"
        mw.plotController.updater.displayStatus.emit(message2, ONE_SECOND_IN_MILLISECONDS)
        assert mw.statusbar.currentMessage() == message2
        message3 = "See you later!"
        mw.dataController.updater.displayStatus.emit(message3, ONE_SECOND_IN_MILLISECONDS)
        assert mw.statusbar.currentMessage() == message3

    def test_statusForFrameRejection(self, qtbot, mocker):
        mw = SpotMotionMonitor()
        mw.cameraController.setupCamera('GaussianCamera')
        qtbot.addWidget(mw)
        mockCamCont = mocker.patch('spot_motion_monitor.views.main_window.CameraController',
                                   spec=True)
        mocker.patch('spot_motion_monitor.camera.gaussian_camera.GaussianCamera.getFullFrame')
        mockCamCont.getFrame = mocker.MagicMock(return_value=np.ones((3, 5)))
        emessage = "Frame failed!"
        mw.cameraController.currentStatus = mocker.Mock(return_value=CameraStatus('Gaussian', 24, False,
                                                                                  (0, 0), True))
        mw.dataController.fullFrameModel.calculateCentroid = mocker.Mock(side_effect=FrameRejected(emessage))
        mw.plotController.passFrame = mocker.Mock(return_value=None)
        mw.acquireFrame()
        assert mw.statusbar.currentMessage() == emessage
        assert mw.plotController.passFrame.call_count == 1

    def test_updateBufferSize(self, qtbot):
        mw = SpotMotionMonitor()
        qtbot.addWidget(mw)
        truth_buffer_size = 2048
        mw.cameraController.updater.bufferSizeChanged.emit(truth_buffer_size)
        assert mw.dataController.getBufferSize() == truth_buffer_size

    def test_statusForCameraNotFound(self, qtbot, mocker):
        mw = SpotMotionMonitor()
        qtbot.addWidget(mw)
        emessage = "Camera Not Found!"
        mw.cameraController.camera.startup = mocker.Mock(side_effect=CameraNotFound(emessage))
        qtbot.mouseClick(mw.cameraControl.startStopButton, Qt.LeftButton)
        assert mw.statusbar.currentMessage() == emessage

    def test_cameraMenu(self, qtbot, mocker):
        mocker.patch('spot_motion_monitor.views.main_window.SpotMotionMonitor.handleCameraSelection')
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        numCameras = len(mw.cameraController.getAvailableCameras())
        assert len(mw.menuCamera.actions()) == numCameras
        # Force camera setup
        mw.cameraController.setupCamera('GaussianCamera')
        assert mw.menuCamera.isEnabled() is True
        qtbot.mouseClick(mw.cameraControl.startStopButton, Qt.LeftButton)
        assert mw.menuCamera.isEnabled() is False

    def test_configurationMenu(self, qtbot):
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        # Force camera setup
        mw.cameraController.setupCamera('GaussianCamera')
        assert mw.actionCameraConfig.isEnabled() is True
        assert mw.actionPlotsConfig.isEnabled() is True
        assert mw.actionGeneralConfig.isEnabled() is True
        qtbot.mouseClick(mw.cameraControl.startStopButton, Qt.LeftButton)
        assert mw.actionCameraConfig.isEnabled() is False
        assert mw.actionPlotsConfig.isEnabled() is True
        assert mw.actionGeneralConfig.isEnabled() is True

    def test_commandLineConfiguration(self, qtbot, mocker):
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        # Force camera setup
        mw.cameraController.setupCamera('GaussianCamera')
        mockDataContollerSetCliConf = mocker.patch.object(mw.dataController, 'setCommandLineConfig')
        mockCameraControllerSetCliConf = mocker.patch.object(mw.cameraController, 'setCommandLineConfig')

        args = collections.namedtuple('args', ['profile', 'telemetry_dir', 'config_file', 'auto_run'])
        args.telemetry_dir = None
        args.auto_run = False

        mw.handleConfig(args)
        assert mockDataContollerSetCliConf.call_count == 1
        assert mockCameraControllerSetCliConf.call_count == 1
        assert args.config is None
        with pytest.raises(AttributeError):
            args.config_file

    def test_autoRun(self, qtbot, mocker):
        mw = SpotMotionMonitor()
        mw.show()
        qtbot.addWidget(mw)
        # Force camera setup
        mw.cameraController.setupCamera('GaussianCamera')
        mockCameraControllerAutoRun = mocker.patch.object(mw.cameraController, 'autoRun')

        args = collections.namedtuple('args', ['profile', 'telemetry_dir', 'config_file', 'auto_run',
                                               'vimba_camera_index'])
        args.telemetry_dir = None
        args.auto_run = True

        mw.handleConfig(args)
        mw.autoRunIfNecessary()
        assert mockCameraControllerAutoRun.call_count == 1

    # def test_acquire_frame(self, qtbot, mocker):
    #     mw = SpotMotionMonitor()
    #     qtbot.addWidget(mw)
    #     mocker.patch('spot_motion_monitor.views.main_window.SpotMotionMonitor.acquireFrame')
    #     signals = [mw.cameraController.cc_widget.acquireFramesState,
    #                mw.cameraController.frameTimer.timeout]
    #     with qtbot.waitSignals(signals):  # , timeout=self.fastTimeout):
    #         qtbot.mouseClick(mw.cameraControl.acquireFramesButton, Qt.LeftButton)
    #     assert mw.acquireFrame.call_count == 1
    #     qtbot.mouseClick(mw.cameraControl.acquireFramesButton, Qt.LeftButton)
