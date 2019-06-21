#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import QObject, pyqtSignal

__all__ = ['InformationUpdater']

class InformationUpdater(QObject):

    """Small class to allow any object to update the main application
       or other controllers.

    Attributes
    ----------
    acquireRoiState : pyqtSignal
        Signal used to update data controller on acquire ROI state changes.
    bufferSizeChanged : pyqtSignal
        Signal used to update data controller with a new buffer size.
    cameraState : pyqtSignal
        Signal used to update application UI based on camera state.
    displayStatus : pyqtSignal
        Signal used for updating the main application status bar.
    roiFpsChanged : pyqtSignal
        Signal used to update controllers with a new ROI FPS.
    """

    acquireRoiState = pyqtSignal(bool)
    bufferSizeChanged = pyqtSignal(int)
    cameraState = pyqtSignal(bool)
    roiFpsChanged = pyqtSignal(int)
    displayStatus = pyqtSignal(str, int)
