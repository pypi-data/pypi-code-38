#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import time

from PyQt5.QtCore import Qt, QTimer

import spot_motion_monitor.camera
import spot_motion_monitor.utils as smmUtils

__all__ = ["CameraController"]

class CameraController():

    """This class manages the interactions between the CameraControlWidget and
       a particular instance of a BaseCamera.

    Attributes
    ----------
    camera : .BaseCamera
        A particular concrete instance of a camera.
    cameraControlWidget : .CameraControlWidget
        The instance of the camera control widget.
    frameTimer : QtCore.QTimer
        Instance of the timer which controls the frame request cycle.
    offsetTimer : QtCore.QTimer
        Instance of the timer which controls the offset update request.
    updater : InformationUpdater
        Instance of the information updater.
    """

    def __init__(self, ccw):
        """Initialize the class.

        Parameters
        ----------
        ccw : .CameraControlWidget
            An instance of the camera control widget
        """
        self.cameraControlWidget = ccw
        self.camera = None
        self.updater = smmUtils.InformationUpdater()
        self.frameTimer = QTimer()
        self.offsetTimer = QTimer()
        self.doAutoRun = False

        self.cameraControlWidget.cameraState.connect(self.startStopCamera)
        self.cameraControlWidget.acquireFramesState.connect(self.acquireFrame)
        self.cameraControlWidget.acquireRoiState.connect(self.acquireRoiFrame)
        self.cameraControlWidget.bufferSizeValue.connect(self.bufferSize)
        self.cameraControlWidget.roiFpsSpinBox.valueChanged.connect(self.setRoiFps)

    def acquireFrame(self, state):
        """Start or stop the timer for full frame acquisition.

        Parameters
        ----------
        state : bool
            The current state of the Start Frame Acquisition button.
        """
        if state:
            self.updater.displayStatus.emit('Starting Frame Acquisition',
                                            smmUtils.ONE_SECOND_IN_MILLISECONDS)
            if self.frameTimer.isActive():
                self.frameTimer.stop()
            current_fps = self.currentCameraFps()
            fps = current_fps if current_fps is not None else smmUtils.DEFAULT_FPS
            self.frameTimer.start(smmUtils.ONE_SECOND_IN_MILLISECONDS / fps)
        else:
            if self.cameraControlWidget.acquireRoiCheckBox.isChecked():
                self.cameraControlWidget.acquireRoiCheckBox.setChecked(Qt.Unchecked)

            self.updater.displayStatus.emit('Stopping Frame Acquistion',
                                            smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.frameTimer.stop()

    def acquireRoiFrame(self, state):
        """Start or stop the timer for ROI frame acquisition.

        Parameters
        ----------
        state : bool
            The current state of the Acquire ROI checkbox.
        """
        if state:
            if self.frameTimer.isActive():
                self.frameTimer.stop()
            self.updater.displayStatus.emit('Starting ROI Frame Acquistion',
                                            smmUtils.ONE_SECOND_IN_MILLISECONDS)

            self.offsetTimer.timeout.emit()
            self.camera.waitOnRoi()
            # Wait for full frame acquires to empty
            time.sleep(0.3)
            current_fps = self.currentCameraFps()
            fps = current_fps if current_fps is not None else smmUtils.DEFAULT_FPS
            self.frameTimer.start(smmUtils.ONE_SECOND_IN_MILLISECONDS / fps)
        else:
            self.frameTimer.stop()
            self.updater.displayStatus.emit('Stopping ROI Frame Acquistion',
                                            smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.camera.resetOffset()
            if self.cameraControlWidget.acquireFramesButton.isChecked():
                self.acquireFrame(True)
        self.updater.acquireRoiState.emit(state)

    def autoRun(self):
        """Start the program in ROI mode if requested.
        """
        if self.doAutoRun:
            self.cameraControlWidget.startStopButton.click()
            self.cameraControlWidget.acquireFramesButton.click()
            self.cameraControlWidget.acquireRoiCheckBox.click()

    def bufferSize(self, value):
        """Rebroadcast a buffer size change request.

        Parameters
        ----------
        value : int
            The requested buffer size.
        """
        self.updater.bufferSizeChanged.emit(value)

    def currentCameraFps(self):
        """Get the current camera FPS.

        Returns
        -------
        int
            Get the current camera FPS based on the acquisition mode.
        """
        if self.cameraControlWidget.acquireRoiCheckBox.isChecked():
            return self.camera.fpsRoiFrame
        else:
            return self.camera.fpsFullFrame

    def currentOffset(self):
        """The current frame offset for the CCD.

        Returns
        -------
        (float, float)
            The x, y pixel coordinated of the current frame offset.
        """
        return self.camera.getOffset()

    def currentRoiFps(self):
        """The current camera ROI FPS.

        Returns
        -------
        float
            Get the current camera ROI FPS.
        """
        return self.camera.fpsRoiFrame

    def currentStatus(self):
        """The current status of the camera.

        Returns
        -------
        .CameraStatus
            The instance containing all of the current camera status.
        """
        name = self.camera.name
        fps = self.currentCameraFps()
        mode = self.isRoiMode()
        offset = self.currentOffset()
        showFrames = self.cameraControlWidget.showFramesCheckBox.isChecked()
        return spot_motion_monitor.camera.CameraStatus(name, fps, mode, offset, showFrames)

    def getAvailableCameras(self):
        """Determine which cameras are available.

        Returns
        -------
        list(str)
            The cameras available to the program.
        """
        available = []
        for name in spot_motion_monitor.camera.names:
            try:
                getattr(spot_motion_monitor.camera, '{}Camera'.format(name))()
                available.append(name)
            except AttributeError:
                pass
        return available

    def getCameraConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        dict
            The set of current camera configuration parameters.
        """
        return self.camera.getConfiguration()

    def getFrame(self):
        """Get the frame from the camera.

        Returns
        -------
        numpy.array
            A frame from a camera CCD.
        """
        try:
            if self.cameraControlWidget.acquireRoiCheckBox.isChecked():
                return self.camera.getRoiFrame()
            else:
                return self.camera.getFullFrame()
        except (smmUtils.FrameCaptureFailed, smmUtils.FrameRejected) as err:
            self.updater.displayStatus.emit(str(err), smmUtils.ONE_SECOND_IN_MILLISECONDS)
            return None

    def getFrameChecks(self):
        """Get the frame checking routines from the camera.

        Returns
        -------
        (func, func)
            The full frame and ROI frame check functions from the camera.
        """
        return (self.camera.checkFullFrame, self.camera.checkRoiFrame)

    def getUpdateFrame(self):
        """Get a full frame from the camera for updating offset.

        Returns
        -------
        numpy.array
            A full frame from a camera CCD.
        """
        return self.camera.getFullFrame()

    def isRoiMode(self):
        """The current acquisition mode.

        Returns
        -------
        bool
            True if in ROI mode, False if in full frame mode.
        """
        return self.cameraControlWidget.acquireRoiCheckBox.isChecked()

    def setRoiFps(self, roiFps):
        """Set the ROI FPS on the camera.

        Parameters
        ----------
        roiFps : int
            The requested FPS for the ROI frame.
        """
        self.camera.fpsRoiFrame = roiFps
        self.updater.roiFpsChanged.emit(roiFps)

    def setCameraConfiguration(self, config):
        """Set the current configuration on the camera.

        Parameters
        ----------
        config : dict
            The current configuration parameters.
        """
        self.camera.setConfiguration(config)

    def setCommandLineConfig(self, options):
        """Set new configurations based on command-line options.

        Parameters
        ----------
        options : Namespace
            The options from command-line arguments.
        """
        self.doAutoRun = options.auto_run
        config = {'cameraIndex': options.vimba_camera_index}
        self.setCameraConfiguration(config)

    def setupCamera(self, cameraStr):
        """Create a specific concrete instance of a camera.

        Parameters
        ----------
        cameraStr : str
            Class name for concrete camera instance.
        """
        self.camera = getattr(spot_motion_monitor.camera, cameraStr)()

    def showFrameStatus(self, check):
        """Show the frame status for the current camera.

        Parameters
        ----------
        check : bool
            If flag is True, report the frame status, if False, don't.
        """
        if check:
            self.camera.showFrameStatus()

    def shutdownCamera(self):
        """Shutdown the camera safely.
        """
        self.camera.safeShutdown()

    def startStopCamera(self, state):
        """Start or stop the camera.

        Parameters
        ----------
        state : bool
            The current state of the camera.
        """
        if state:
            try:
                self.updater.displayStatus.emit('Starting Camera', smmUtils.ONE_SECOND_IN_MILLISECONDS)
                self.camera.startup()
                self.updater.displayStatus.emit('Camera Started Successfully',
                                                smmUtils.ONE_SECOND_IN_MILLISECONDS)
                self.updater.cameraState.emit(state)
            except smmUtils.CameraNotFound as err:
                self.updater.displayStatus.emit(str(err),
                                                smmUtils.ONE_SECOND_IN_MILLISECONDS * 5)

        else:
            self.updater.displayStatus.emit('Stopping Camera', smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.camera.shutdown()
            self.updater.displayStatus.emit('Camera Stopped Successfully',
                                            smmUtils.ONE_SECOND_IN_MILLISECONDS)
            self.updater.cameraState.emit(state)

    def updateCameraOffset(self, centroidX, centroidY):
        """Pass along the current centroid values to update camera offset.

        Parameters
        ----------
        centroidX : float
            The current x component of the centroid from a full frame.
        centroidY : float
            The current y component of the centroid from a full frame.
        """
        self.camera.updateOffset(centroidX, centroidY)
