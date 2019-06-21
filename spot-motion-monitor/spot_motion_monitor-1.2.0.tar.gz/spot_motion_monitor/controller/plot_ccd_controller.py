#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import spot_motion_monitor.utils as smmUtils

__all__ = ['PlotCcdController']

class PlotCcdController():

    """This class manages the interactions between the all of the plot widgets
       and calculation data models.

    Attributes
    ----------
    cameraPlotWidget : .CameraPlotWidget
        An instance of the camera plot widget.
    updater : .InformationUpdater
        An instance of the status bar updater.
    """

    def __init__(self, cpw):
        """Initialize the class.

        Parameters
        ----------
        cpw : .CameraPlotWidget
            An instance of the camera plot widget.
        """
        self.cameraPlotWidget = cpw
        self.updater = smmUtils.InformationUpdater()

    def passFrame(self, frame, showFrames):
        """Receive and handle the camera CCD frame.

        Parameters
        ----------
        frame : numpy.array
            A frame from a camera CCD.
        showFrames : bool
            Flag to show camera CCD frames.
        """
        if frame is None:
            return
        if showFrames:
            self.cameraPlotWidget.image.setImage(frame)
