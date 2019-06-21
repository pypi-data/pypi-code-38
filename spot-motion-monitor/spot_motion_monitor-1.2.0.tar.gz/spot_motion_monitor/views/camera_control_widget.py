#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from spot_motion_monitor.views.forms.ui_camera_control import Ui_CameraControl

__all__ = ['CameraControlWidget']

class CameraControlWidget(QWidget, Ui_CameraControl):

    """This class handles the interactions from the Camera Control Widget on
    the Main Window.

    Attributes
    ----------
    acquireFramesState : pyqtSignal
        Signal the state of acquiring frames.
    acquireRoiState : pyqtSignal
        Signal the state of acquiring in ROI mode.
    bufferSizeValue : pyqtSignal
        Signal the value of the buffer size.
    cameraState : pyqtSignal
        Signal state of camera.
    currentBufferSize : int
        The current buffer size.
    """

    acquireFramesState = pyqtSignal(bool)
    acquireRoiState = pyqtSignal(bool)
    bufferSizeValue = pyqtSignal(int)
    cameraState = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialze the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.currentBufferSize = self.bufferSizeSpinBox.value()

        self.startStopButton.toggled.connect(self.handleStartStop)
        self.acquireFramesButton.toggled.connect(self.handleAcquireFrames)
        self.acquireRoiCheckBox.toggled.connect(self.handleAcquireRoi)
        self.bufferSizeSpinBox.valueChanged.connect(self.handleBufferSize)

    def handleAcquireFrames(self, checked):
        """Perform actions related to acquiring frames.

        Parameters
        ----------
        checked : bool
            State of the toggle button.
        """
        if checked:
            self.acquireFramesButton.setText("Stop Acquire Frames")
        else:
            self.acquireFramesButton.setText("Start Acquire Frames")
        self.startStopButton.setEnabled(not checked)
        self.acquireFramesState.emit(checked)

    def handleAcquireRoi(self, checked):
        """Perform actions related to acquiring in ROI mode.

        Parameters
        ----------
        checked : bool
            State of the checkbox.
        """
        self.roiFpsSpinBox.setEnabled(not checked)
        self.bufferSizeSpinBox.setEnabled(not checked)
        self.acquireRoiState.emit(checked)

    def handleBufferSize(self, value):
        """Make sure buffer sizes are powers of 2.

        Parameters
        ----------
        value : int
            Current requested value.
        """
        diff = value - self.currentBufferSize
        if diff > 0:
            self.currentBufferSize *= 2
        elif diff < 0:
            self.currentBufferSize /= 2
        else:
            return
        self.bufferSizeSpinBox.setValue(self.currentBufferSize)
        self.bufferSizeValue.emit(self.currentBufferSize)

    def handleStartStop(self, checked):
        """Perform actions related to startup/shutdown of the camera.

        Parameters
        ----------
        checked : bool
            State of the toggle button.
        """
        if checked:
            self.startStopButton.setText("Stop Camera")

        else:
            self.startStopButton.setText("Start Camera")
        self.acquireFramesButton.setEnabled(checked)
        self.acquireRoiCheckBox.setEnabled(checked)
        self.cameraState.emit(checked)
