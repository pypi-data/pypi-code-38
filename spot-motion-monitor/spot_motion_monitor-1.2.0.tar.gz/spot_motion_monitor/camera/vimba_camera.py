#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from datetime import datetime
import time

import numpy as np
import pymba as pv

from spot_motion_monitor.camera import BaseCamera
from spot_motion_monitor.utils import CameraNotFound, FrameCaptureFailed, getTimestamp

__all__ = ['VimbaCamera']

class VimbaCamera(BaseCamera):

    """This class handles the connection to an Allied Vision camera through
       the Vimba interface.

    Attributes
    ----------
    badFrames : int
        Counter for the number of failed frame captures.
    cameraIndex : int
        Requested index in list of camera.
    cameraPtr : pymba.VimbaCamera
        Instance of the actual camera object.
    fluxMinRoi : int
        The minimum flux allowed for an ROI frame.
    fpsFullFrame : int
        The Frames per Second rate in full frame mode.
    fpsRoiFrame : int
        The Frames per Second rate in ROI frame mode.
    frame : pymba.VimbaFrame
        Instance of the frame object for the camera.
    goodFrames : int
        Counter for the number of capture frames.
    height : int
        The pixel height of the CCD.
    offsetX : int
        The current offset in X for the camera.
    offsetY : int
        The current offset in Y for the camera.
    roiExposureTime : int
        Description
    roiSize : int
        The size of a (square) ROI region in pixels.
    totalFrames : int
        Counter for the total number of requested frames.
    vimba : pymba.Vimba
        Instance of the Python control library.
    width : int
        The pixel width of the CCD.
    """

    def __init__(self):
        """Initalize the class.
        """
        super().__init__()
        self.vimba = None
        self.cameraIndex = 0
        self.cameraPtr = None
        self.frame = None
        self.fpsFullFrame = 24
        self.fpsRoiFrame = 40
        self.roiSize = 50
        self.roiExposureTime = 8000  # microseconds
        self.fluxMinRoi = 2000
        self.offsetX = 0
        self.offsetY = 0

    def checkFullFrame(self, flux, maxAdc, comX, comY):
        """Use the provided quantities to check frame validity.

        Parameters
        ----------
        flux : float
            The flux of the frame.
        maxAdc : float
            The maximum ADC of the frame.
        comX : float
            The x component of the center-of-mass.
        comY : float
            The y component of the center-of-mass.

        Returns
        -------
        bool
            True if frame is valid, False if not.
        """
        return flux > 100 and maxAdc > 0 and comX > 0 and comY > 0

    def checkRoiFrame(self, flux):
        """Use the provided quantities to check frame validity

        Parameters
        ----------
        flux : float
            The flux of the frame.

        Returns
        -------
        bool
            True if frame is valid, False if not.
        """
        return flux > self.fluxMinRoi

    def getConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        dict
            The set of current configuration parameters.
        """
        config = {}
        config['roiSize'] = self.roiSize
        config['roiFluxMinimum'] = self.fluxMinRoi
        config['roiExposureTime'] = self.roiExposureTime
        return config

    def getFullFrame(self):
        """Get the full frame from the CCD.

        Returns
        -------
        numpy.array
            The current full CCD frame.

        Raises
        ------
        FrameCaptureFailed
            Raises this if the camera fails to capture the frame when
            requested.
        """
        try:
            self.frame.queue_for_capture()
        except pv.VimbaException as err:
            raise FrameCaptureFailed("{} Full frame capture failed: {}".format(datetime.now(), str(err)))

        self.cameraPtr.run_feature_command('AcquisitionStart')
        #self.cameraPtr.run_feature_command('AcquisitionStop')
        self.frame.wait_for_capture(1000)
        frameData = self.frame.buffer_data()

        img = np.ndarray(buffer=frameData, dtype=np.uint16, shape=(self.height, self.width))
        return img

    def getOffset(self):
        """Get the offset for the CCD frame.

        Returns
        -------
        (int, int)
            The current offset of the CCD frame.
        """
        return (self.offsetX, self.offsetY)

    def getRoiFrame(self):
        """Get the ROI frame from the CCD.

        Returns
        -------
        numpy.array
            The current ROI CCD frame.

        Raises
        ------
        FrameCaptureFailed
            Raises this if the camera fails to capture the frame when
            requested.
        """
        self.totalFrames += 1
        try:
            self.frame.queue_for_capture()
        except pv.VimbaException as err:
            self.badFrames += 1
            raise FrameCaptureFailed("{} ROI frame capture failed: {}".format(getTimestamp(), str(err)))
        self.goodFrames += 1
        self.cameraPtr.run_feature_command('AcquisitionStart')
        self.cameraPtr.run_feature_command('AcquisitionStop')
        try:
            self.frame.wait_for_capture(1)
        except pv.VimbaException as err:
            self.goodFrames -= 1
            self.badFrames += 1
            raise FrameCaptureFailed("{} ROI frame capture wait failed: {}".format(getTimestamp(), str(err)))
        frameData = self.frame.buffer_data()

        img = np.ndarray(buffer=frameData, dtype=np.uint16, shape=(self.roiSize, self.roiSize))
        return img

    def resetOffset(self):
        """Reset the camera offsets back to zero.
        """
        self.cameraPtr.OffsetX = 0
        self.cameraPtr.OffsetY = 0
        self.offsetX = 0
        self.offsetY = 0
        self.cameraPtr.Height = self.height
        self.cameraPtr.Width = self.width

    def safeShutdown(self):
        """Check camera status before shutting down.
        """
        if self.cameraPtr is not None:
            self.shutdown()

    def setConfiguration(self, config):
        """Set the comfiguration on the camera.

        Parameters
        ----------
        config : dict
            The current configuration.
        """
        if 'cameraIndex' in config:
            if config['cameraIndex'] is not None:
                self.cameraIndex = config['cameraIndex']
        if 'roiSize' in config:
            self.roiSize = config['roiSize']
        if 'roiFluxMinimum' in config:
            self.fluxMinRoi = config['roiFluxMinimum']
        if 'roiExposureTime' in config:
            self.roiExposureTime = config['roiExposureTime']
            if self.cameraPtr is not None:
                self.cameraPtr.ExposureTimeAbs = self.roiExposureTime

    def showFrameStatus(self):
        """Show frame status from the camera.

        The camera reports the number of good, bad and total frames to the
        system.
        """
        if self.badFrames:
            print("{} {}, {}, {}".format(datetime.now(), self.goodFrames, self.badFrames, self.totalFrames))

    def startup(self):
        """Handle the startup of the camera.

        Raises
        ------
        CameraNotFound
            Raises this exception if there is an issue with the camera.
        """
        self.goodFrames = 0
        self.badFrames = 0
        self.totalFrames = 0
        self.vimba = pv.Vimba()
        self.vimba.startup()
        system = self.vimba.system()
        system.run_feature_command('GeVDiscoveryAllOnce')
        time.sleep(0.2)
        cameraIds = self.vimba.camera_ids()
        try:
            self.cameraPtr = self.vimba.camera(cameraIds[self.cameraIndex])
        except IndexError:
            raise CameraNotFound('Camera not found ... check power or connection!')

        self.cameraPtr.open()
        self.cameraPtr.GevSCPSPacketSize = 1500
        self.cameraPtr.StreamBytesPerSecond = 124000000
        self.height = self.cameraPtr.HeightMax
        self.width = self.cameraPtr.WidthMax
        self.cameraPtr.Height = self.height
        self.cameraPtr.Width = self.width
        self.cameraPtr.OffsetX = 0
        self.cameraPtr.OffsetY = 0
        self.cameraPtr.GainAuto = 'Off'
        self.cameraPtr.GainRaw = 0
        self.cameraPtr.ExposureAuto = 'Off'
        self.cameraPtr.AcquisitionMode = 'Continuous'
        self.cameraPtr.TriggerSource = 'Freerun'
        self.cameraPtr.PixelFormat = 'Mono12'
        self.cameraPtr.ExposureTimeAbs = self.roiExposureTime

        self.frame = self.cameraPtr.new_frame()
        self.frame.announce()
        self.cameraPtr.start_capture()

    def shutdown(self):
        """Handle the shutdown of the camera.
        """
        try:
            self.cameraPtr.end_capture()
            self.cameraPtr.revoke_all_frames()
            self.cameraPtr.close()
        except pv.VimbaException:
            pass
        self.vimba.shutdown()
        self.cameraPtr = None

    def updateOffset(self, centroidX, centroidY):
        """Update the camera's internal offset values from the provided centroid.

        For the Gaussian camera, this is a no-op, but helps test the mechanism.

        Parameters
        ----------
        centroidX : float
            The x component of the centroid for offset update.
        centroidY : float
            The y component of the centroid for offset update.
        """
        self.offsetX = int(centroidX - self.roiSize / 2)
        self.offsetY = int(centroidY - self.roiSize / 2)
        self.cameraPtr.OffsetX = self.offsetX
        self.cameraPtr.OffsetY = self.offsetY
        self.cameraPtr.Height = self.roiSize
        self.cameraPtr.Width = self.roiSize

    def waitOnRoi(self):
        """Wait on information to be updated for ROI mode use.

        Run the loop until both the reported camera height and width are the
        same size as the specified ROI.
        """
        while True:
            if self.cameraPtr.Height == self.roiSize and self.cameraPtr.Width == self.roiSize:
                break
