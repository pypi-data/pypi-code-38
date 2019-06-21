#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
#from datetime import datetime
import numpy as np

from spot_motion_monitor.utils import psd_calculator
from spot_motion_monitor.utils.frame_information import RoiFrameInformation

__all__ = ['BufferModel']

class BufferModel():

    """This class handles calculations for a set of ROI CCD frames.

    Attributes
    ----------
    bufferSize : int
        The size of the buffer to perform calculations.
    centerX : list
        Array of ROI centroid x coordinates.
    centerY : list
        Array of ROI centroid y coordinates.
    counter : int
        Running counter for buffer insertions.
    flux : list
        Array of ROI total fluxes.
    maxAdc : list
        Array of ROI maximum ADC values.
    objectSize : list
        Array of number of pixels in centroiding region.
    pixelScale : float
        The pixel scale of the CCD camera system.
    rollBuffer : bool
        Flag to determine if rolling buffer mode is active.
    stdMax : list
        Array of standard deviations of ROI frames without object pixels.
    timestamp : list
        Array of measurement date/times.
    """

    def __init__(self):
        """Initialize the class.
        """
        self.bufferSize = 1024
        self.rollBuffer = False
        self.counter = 0
        self.pixelScale = 1.0
        self.timestamp = []
        self.maxAdc = []
        self.flux = []
        self.centerX = []
        self.centerY = []
        self.objectSize = []
        self.stdMax = []

    def getCentroids(self):
        """Return the current pair of centroid values.

        Returns
        -------
        (float, float)
            A tuple containing the current pair of centroid values. If no
            values in buffer, return (None, None)
        """
        try:
            return (self.centerX[-1], self.centerY[-1])
        except IndexError:
            return (None, None)

    def getInformation(self, currentFps):
        """Retrieve the current information from the accumulated buffer.

        Parameters
        ----------
        currentFps : float
            The current Frames per Second rate from the camera.

        Returns
        -------
        .RoiFrameInformation, optional
            The instance containing the current information.
        """
        if self.rollBuffer:
            meanFlux = np.mean(self.flux)
            meanMaxAdc = np.mean(self.maxAdc)
            meanCenterX = np.mean(self.centerX)
            meanCenterY = np.mean(self.centerY)
            rmsX = self.pixelScale * np.std(self.centerX)
            rmsY = self.pixelScale * np.std(self.centerY)
            # meanObjectSize = np.mean(self.objectSize)
            # meanStdMax = np.nanmean(self.stdMax)
            return RoiFrameInformation(meanCenterX, meanCenterY, meanFlux, meanMaxAdc,
                                       rmsX, rmsY, (self.bufferSize, self.bufferSize / currentFps))
        else:
            return None

    def getPsd(self, currentFps):
        """Return the current power spectrum distribution (PSD) calculations.

        Parameters
        ----------
        currentFps : float
            The current Frames per Second rate from the camera.

        Returns
        -------
        (numpy.array, numpy.array, numpy.array)
            The PSDX, PSDY and Frequencies from the PSD calculation.
            If not rolling buffer return (None, None, None)
        """
        if self.rollBuffer and self.counter % self.bufferSize == 0:
            #print("Buffer ready: {}".format(datetime.now()))
            return psd_calculator(np.array(self.centerX), np.array(self.centerY), currentFps)
        else:
            return (None, None, None)

    def reset(self):
        """Reset all of the arrays and turn off rolling buffer mode.
        """
        self.rollBuffer = False
        self.counter = 0
        self.timestamp = []
        self.maxAdc = []
        self.flux = []
        self.centerX = []
        self.centerY = []
        self.objectSize = []
        self.stdMax = []

    def updateInformation(self, info, offset):
        """Add current information into the buffer.

        Parameters
        ----------
        info : .GenericInformation
            The instance containing the ROI frame information.
        offset : (float, float)
            The x, y pixel coordinates of the frame offset.
        """
        if self.rollBuffer:
            self.timestamp.pop(0)
            self.maxAdc.pop(0)
            self.flux.pop(0)
            self.centerX.pop(0)
            self.centerY.pop(0)
            self.objectSize.pop(0)
            self.stdMax.pop(0)

        self.timestamp.append(info.timestamp)
        self.maxAdc.append(info.maxAdc)
        self.flux.append(info.flux)
        self.centerX.append(info.centerX + offset[0])
        self.centerY.append(info.centerY + offset[1])
        self.objectSize.append(info.objectSize)
        self.stdMax.append(info.stdNoObjects)
        self.counter += 1

        if not self.rollBuffer:
            if len(self.flux) == self.bufferSize:
                self.rollBuffer = True
