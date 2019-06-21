#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np

from spot_motion_monitor.camera import BaseCamera

__all__ = ['GaussianCamera']

class GaussianCamera(BaseCamera):

    """This class creates a camera that produces a frame with random Poisson
       noise and a Gaussian spot placed at random within the frame.

    Attributes
    ----------
    counter : int
        The progress of the oscillation in time.
    fpsFullFrame : int
        The Frames per Second rate in full frame mode.
    fpsRoiFrame : int
        The Frames per Second rate in ROI frame mode.
    height : int
        The pixel height of the CCD.
    postageStamp : numpy.array
        The array containing the Gaussian postage stamp.
    roiSize : int
        The size of a (square) ROI region in pixels.
    seed : int
        The seed for the random number generator.
    spotSize : int
        The box size in pixels for the Gaussian spot.
    width : int
        The pixel width of the CCD.
    xAmp : int
        The amplitude of the x-axis oscillation.
    xFreq : float
        The frequency of the x-axis oscillation.
    xPoint : int
        The x-coordinate of the Gaussian postage stamp insertion point.
    xPointOriginal : int
        The x-coordinate of the original postage stamp insertion point.
    yAmp : int
        The amplitude of the y-axis oscillation.
    yFreq : float
        The frequency of the y-axis oscillation.
    yPoint : int
        The y-coordinate of the Gaussian postage stamp insertion point.
    yPointOriginal : int
        The y-coordinate of the original postage stamp insertion point.
    """

    TWO_PI = 2.0 * np.pi
    seed = None

    def __init__(self):
        """Initalize the class.
        """
        super().__init__()
        self.spotSize = 20
        self.height = 480
        self.width = 640
        self.fpsFullFrame = 24
        self.fpsRoiFrame = 40
        self.roiSize = 50
        self.postageStamp = None
        self.xPoint = None
        self.yPoint = None
        # Parameters for spot oscillation.
        self.doSpotOscillation = True
        self.counter = 0
        self.xFreq = 1.0
        self.xAmp = 10
        self.yFreq = 2.0
        self.yAmp = 5
        self.xPointOriginal = None
        self.yPointOriginal = None

    def findInsertionPoint(self):
        """Determine the Gaussian spot insertion point.
        """
        percentage = 0.2
        xRange = percentage * self.width
        yRange = percentage * self.height
        # Pick lower left corner for insertion
        xHalfwidth = self.width / 2
        yHalfwidth = self.height / 2
        self.xPoint = np.random.randint(xHalfwidth - xRange, xHalfwidth + xRange + 1)
        self.yPoint = np.random.randint(yHalfwidth - yRange, yHalfwidth + yRange + 1)
        self.xPointOriginal = self.xPoint
        self.yPointOriginal = self.yPoint

    def getConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        dict
            The set of current configuration parameters.
        """
        config = {}
        config['roiSize'] = self.roiSize
        config['doSpotOscillation'] = self.doSpotOscillation
        config['xAmplitude'] = self.xAmp
        config['xFrequency'] = self.xFreq
        config['yAmplitude'] = self.yAmp
        config['yFrequency'] = self.yFreq
        return config

    def getFullFrame(self):
        """Get the full frame from the CCD.

        Returns
        -------
        numpy.array
            The current full CCD frame.
        """
        # Create base CCD frame
        ccd = np.random.poisson(20.0, (self.height, self.width))

        if self.doSpotOscillation:
            self.oscillateSpot()

        # Merge CCD frame and postage stamp
        ccd[self.yPoint:self.yPoint + self.postageStamp.shape[1],
            self.xPoint:self.xPoint + self.postageStamp.shape[0]] += self.postageStamp

        return ccd

    def getOffset(self):
        """Get the offset for ROI mode.

        Returns
        -------
        (float, float)
            The x, y pixel positions of the offset for ROI mode.
        """
        # Offset is same for both axes since spot and ROI are square.
        offset = (self.roiSize - self.spotSize) // 2
        xStart = self.xPointOriginal - offset
        yStart = self.yPointOriginal - offset
        return (xStart, yStart)

    def getRoiFrame(self):
        """Get the ROI frame from the CCD.

        Returns
        -------
        numpy.array
            The current ROI CCD frame.
        """
        ccd = self.getFullFrame()
        xOffset, yOffset = self.getOffset()
        roi = ccd[yOffset:yOffset + self.roiSize, xOffset:xOffset + self.roiSize]
        return roi

    def makePostageStamp(self):
        """Create the Gaussian spot.
        """
        linear_space = np.linspace(-2, 2, self.spotSize)
        x, y = np.meshgrid(linear_space, linear_space)
        d = np.sqrt(x * x + y * y)
        sigma, mu = 0.5, 0.0
        a = 200.0 / (sigma * np.sqrt(2.0 * np.pi))
        self.postageStamp = a * np.exp(-((d - mu)**2 / (2.0 * sigma**2)))
        self.postageStamp = self.postageStamp.astype(np.int64)

    def oscillateSpot(self):
        """Calculate the oscillation of the spot.
        """
        self.xPoint = int(self.xPointOriginal +
                          self.xAmp * np.sin(self.TWO_PI * self.xFreq * (self.counter / self.fpsRoiFrame)))
        self.yPoint = int(self.yPointOriginal +
                          self.yAmp * np.sin(self.TWO_PI * self.yFreq * (self.counter / self.fpsRoiFrame)))
        self.counter += 1

    def resetOffset(self):
        """Reset the camera offsets back to zero.

        For the Gaussian camera, this is a no-op.
        """
        pass

    def safeShutdown(self):
        """Check camera status before shutting down.

        For the Gaussian camera, this is a no-op.
        """
        pass

    def setConfiguration(self, config):
        """Set the comfiguration on the camera.

        Parameters
        ----------
        config : dict
            The current configuration.
        """

        if 'roiSize' in config:
            self.roiSize = config['roiSize']
        if 'doSpotOscillation' in config:
            self.doSpotOscillation = config['doSpotOscillation']
            if self.doSpotOscillation:
                if 'xFrequency' in config:
                    self.xFreq = config['xFrequency']
                if 'xAmplitude' in config:
                    self.xAmp = config['xAmplitude']
                if 'yFrequency' in config:
                    self.yFreq = config['yFrequency']
                if 'yAmplitude' in config:
                    self.yAmp = config['yAmplitude']

    def showFrameStatus(self):
        """Show frame status from the camera.

        The Gaussian camera does not use this function since all frames are
        good.
        """
        pass

    def shutdown(self):
        """Handle the shutdown of the camera.
        """
        pass

    def startup(self):
        """Handle the startup of the camera.
        """
        np.random.seed(self.seed)
        self.makePostageStamp()
        self.findInsertionPoint()

    def updateOffset(self, centroidX, centroidY):
        """Update the camera's internal offset values from the provided
           centroid.

        For the Gaussian camera, this is a no-op, but helps test the mechanism.

        Parameters
        ----------
        centroidX : float
            The x component of the centroid for offset update.
        centroidY : float
            The y component of the centroid for offset update.
        """
        pass

    def waitOnRoi(self):
        """Wait on information to be updated for ROI mode use.

        The Gaussian camera does not make use of this currently.
        """
        pass
