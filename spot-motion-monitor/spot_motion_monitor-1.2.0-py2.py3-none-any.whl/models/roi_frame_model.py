#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
from scipy import ndimage

from spot_motion_monitor.utils import FrameRejected, GenericFrameInformation, getTimestamp, passFrame

__all__ = ['RoiFrameModel']

class RoiFrameModel():

    """This class handles the calculations for a ROI CCD frame.

    The class handles all of the calculations necessary to produce information
    to fill out a GenericFrameInformation instance.

    Attributes
    ----------
    thresholdFactor : float
        Description
    """

    def __init__(self):
        """Initialize the class.
        """
        self.thresholdFactor = 0.3
        self.frameCheck = None

    def calculateCentroid(self, roiFrame):
        """This function performs calculations for the ROI CCD frame.

        Parameters
        ----------
        roiFrame : numpy.array
            A ROI CCD frame.

        Returns
        -------
        GenericInformation
            The instance containing the results of the calculations.

        Raises
        ------
        FrameRejected
            Raised if ROI frame does not pass flux threshold.
        """
        if self.frameCheck is None:
            self.frameCheck = passFrame

        newFrame = np.copy(roiFrame)
        newFrame = newFrame - self.thresholdFactor * newFrame.max()
        newFrame[newFrame < 0] = 0
        maxAdc = newFrame.max()
        flux = np.sum(newFrame)
        if self.frameCheck(flux):
            comY, comX = ndimage.center_of_mass(newFrame)
            objectSize = np.count_nonzero(newFrame)
            # Get standard deviation of original image without object pixels
            # Removing this for speed improvement. MAR 2018/10/05
            # maxStd = np.std(np.ma.masked_array(roiFrame, mask=newFrame))
            maxStd = -999
            return GenericFrameInformation(getTimestamp(), comX, comY, flux, maxAdc, objectSize, maxStd)
        else:
            raise FrameRejected('ROI frame rejected due to low flux')
