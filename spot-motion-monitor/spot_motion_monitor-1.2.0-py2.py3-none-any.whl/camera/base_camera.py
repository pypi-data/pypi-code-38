#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
_all__ = ['BaseCamera']

class BaseCamera():
    """Base API for all Camera classes

    Attributes
    ----------
    fpsFullFrame : int
        The Frames per Second rate in full frame mode.
    fpsRoiFrame : int
        The Frames per Second rate in ROI frame mode.
    height : int
        The height in pixels of the camera CCD
    roiSize : int
        The size of a (square) ROI region in pixels.
    width : int
        The width in pixels of the camera CCD
    """

    height = None
    width = None
    fpsFullFrame = None
    fpsRoiFrame = None
    roiSize = None

    def __init__(self):
        """Initialize the class.
        """
        pass

    @property
    def name(self):
        """Get the name of the camera type.

        Returns
        -------
        str
            The name of the camera type.
        """
        cname = self.__class__.__name__
        return cname.split('Camera')[0]

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
        return True

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
        return True

    def getConfiguration(self):
        """Return the current camera configuration.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def getFullFrame(self):
        """Return a full CCD frame from the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def getOffset(self):
        """Return the offset of the CCD frame.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def getRoiFrame(self):
        """Return a ROI CCD frame from the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def resetOffset(self):
        """Reset the camera offsets back to zero.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def safeShutdown(self):
        """Check camera status before shutting down.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def setConfiguration(self, config):
        """Set the comfiguration on the camera.

        Parameters
        ----------
        config : dict
            The current configuration.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def showFrameStatus(self):
        """Show frame status from the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def shutdown(self):
        """Shutdown the camera safely.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def startup(self):
        """Startup the camera.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def updateOffset(self, centroidX, centroidY):
        """Update the camera's internal offset values from the provided centroid.

        Parameters
        ----------
        centroidX : float
            The x component of the centroid for offset update.
        centroidY : float
            The y component of the centroid for offset update.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def waitOnRoi(self):
        """Wait on information to be updated for ROI mode use.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError
