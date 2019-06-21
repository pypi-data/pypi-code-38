#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt

from spot_motion_monitor.views.camera_control_widget import CameraControlWidget

class TestCameraControl():

    def setup_class(self):
        self.fast_timeout = 250  # ms

    def stateIsFalse(self, state):
        return not state

    def stateIsTrue(self, state):
        return state

    def test_startStopCameraButton(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert not cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Start Camera"
        assert cc.acquireRoiCheckBox.isEnabled() is False
        assert cc.acquireFramesButton.isEnabled() is False
        with qtbot.waitSignal(cc.cameraState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Stop Camera"
        assert cc.acquireRoiCheckBox.isEnabled() is True
        assert cc.acquireFramesButton.isEnabled() is True
        with qtbot.waitSignal(cc.cameraState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert not cc.startStopButton.isChecked()
        assert cc.startStopButton.text() == "Start Camera"

    def test_acquireFramesButton(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert not cc.acquireFramesButton.isChecked()
        assert cc.acquireFramesButton.text() == "Start Acquire Frames"
        with qtbot.waitSignal(cc.acquireFramesState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.acquireFramesButton, Qt.LeftButton)
        assert cc.acquireFramesButton.isChecked()
        assert not cc.startStopButton.isEnabled()
        assert cc.acquireFramesButton.text() == "Stop Acquire Frames"
        with qtbot.waitSignal(cc.acquireFramesState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.acquireFramesButton, Qt.LeftButton)
        assert not cc.acquireFramesButton.isChecked()
        assert cc.acquireFramesButton.text() == "Start Acquire Frames"
        assert cc.startStopButton.isEnabled()

    def test_acquireRoiCheckbox(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        qtbot.mouseClick(cc.startStopButton, Qt.LeftButton)
        assert not cc.acquireRoiCheckBox.isChecked()
        with qtbot.waitSignal(cc.acquireRoiState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsTrue):
            qtbot.mouseClick(cc.acquireRoiCheckBox, Qt.LeftButton)
        assert cc.acquireRoiCheckBox.isChecked()
        assert not cc.roiFpsSpinBox.isEnabled()
        assert not cc.bufferSizeSpinBox.isEnabled()
        with qtbot.waitSignal(cc.acquireRoiState, timeout=self.fast_timeout,
                              check_params_cb=self.stateIsFalse):
            qtbot.mouseClick(cc.acquireRoiCheckBox, Qt.LeftButton)
        assert not cc.acquireRoiCheckBox.isChecked()
        assert cc.roiFpsSpinBox.isEnabled()
        assert cc.bufferSizeSpinBox.isEnabled()

    def test_roiFpsSpinBox(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert cc.roiFpsSpinBox.value() == 40
        cc.roiFpsSpinBox.setValue(0)
        assert cc.roiFpsSpinBox.value() == 1
        cc.roiFpsSpinBox.setValue(200)
        assert cc.roiFpsSpinBox.value() == 150
        cc.roiFpsSpinBox.stepUp()
        assert cc.roiFpsSpinBox.value() == 150
        cc.roiFpsSpinBox.stepDown()
        assert cc.roiFpsSpinBox.value() == 149

    def test_bufferSizeSpinBox(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert cc.bufferSizeSpinBox.value() == 1024
        cc.bufferSizeSpinBox.stepUp()
        assert cc.bufferSizeSpinBox.value() == 2048
        cc.bufferSizeSpinBox.setValue(1024)
        cc.bufferSizeSpinBox.stepDown()
        assert cc.bufferSizeSpinBox.value() == 512

    def test_showFramesCheckBox(self, qtbot):
        cc = CameraControlWidget()
        cc.show()
        qtbot.addWidget(cc)
        assert cc.showFramesCheckBox.isChecked()
        qtbot.mouseClick(cc.showFramesCheckBox, Qt.LeftButton)
        assert not cc.showFramesCheckBox.isChecked()
