#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
__all__ = ['PlotPsdController']

class PlotPsdController:

    """This class handles the interactions between the main program and the
       power spectrum distribution (PSD) waterfall plots.

    Attributes
    ----------
    psd1dXPlot : Psd1dPlotWidget
        The instance of the 1d plot for the PSD x coordinates.
    psd1dYPlot : Psd1dPlotWidget
        The instance of the 1d plot for the PSD y coordinates.
    psdWaterfallXPlot : PsdWaterfallPlotWidget
        The instance of the waterfall plot for the PSD x coordinates.
    psdWaterfallYPlot : PsdWaterfallPlotWidget
        The instance of the waterfall plot for the PSD y coordinates.
    """

    def __init__(self, psdwfx, psdwfy, psd1dx, psd1dy):
        """Initialize the class.

        Parameters
        ----------
        psdwfx : PsdWaterfallPlotWidget
            The instance of the waterfall plot for the PSD x coordinates.
        psdwfy : PsdWaterfallPlotWidget
            The instance of the waterfall plot for the PSD y coordinates.
        psd1dx : Psd1dPlotWidget
            The instance of the 1d plot for the PSD x coordinates.
        psd1dy : Psd1dPlotWidget
            The instance of the 1d plot for the PSD y coordinates.
        """
        self.psdWaterfallXPlot = psdwfx
        self.psdWaterfallYPlot = psdwfy
        self.psd1dXPlot = psd1dx
        self.psd1dYPlot = psd1dy

    def getPlotConfiguration(self):
        """Get the current camera configuration.

        Returns
        -------
        dict
            The set of current camera configuration parameters.
        """
        config = {}
        config['waterfall'] = self.psdWaterfallXPlot.getConfiguration()
        config['xPSD'] = self.psd1dXPlot.getConfiguration()
        config['yPSD'] = self.psd1dYPlot.getConfiguration()
        return config

    def handleAcquireRoiStateChange(self, checked):
        """Deal with changes in the Acquire ROI checkbox.

        Parameters
        ----------
        checked : bool
            State of the Acquire ROI checkbox.
        """
        if not checked:
            self.psd1dXPlot.clearPlot()
            self.psd1dYPlot.clearPlot()
            self.psdWaterfallXPlot.clearPlot()
            self.psdWaterfallYPlot.clearPlot()

    def setPlotConfiguration(self, config):
        """Set a new configuration on the PSD plots.

        Parameters
        ----------
        config : dict
            The new configuration parameters.
        """
        self.psdWaterfallXPlot.setConfiguration(config['waterfall'])
        self.psdWaterfallYPlot.setConfiguration(config['waterfall'])
        self.psd1dXPlot.setConfiguration(config['xPSD'])
        self.psd1dYPlot.setConfiguration(config['yPSD'])

    def setup(self, arraySize, timeScale):
        """Setup the controller's internal information.

        Parameters
        ----------
        arraySize : int
            The vertical dimension of the PSD waterfall plot data.
        timeScale : float
            The total accumulation time from the buffer size and ROI FPS.
        """
        self.psdWaterfallXPlot.setup(arraySize, timeScale, 'X')
        self.psdWaterfallYPlot.setup(arraySize, timeScale, 'Y')
        self.psd1dXPlot.setup('X')
        self.psd1dYPlot.setup('Y')

    def update(self, psdDataX, psdDataY, frequencies):
        """Update the controller's plot widgets with the data provided.

        NOTE: If NoneType data is provided, the updatePlot methods are not called.

        Parameters
        ----------
        psdDataX : numpy.array
            The array of the PSD x coordinate data.
        psdDataY : numpy.array
            The array of the PSD y coordinate data.
        frequencies : numpy.array
            The frequency array associated with the PSD data.

        Returns
        -------
        TYPE
            Description
        """
        if psdDataX is None or psdDataY is None or frequencies is None:
            return

        self.psdWaterfallXPlot.updatePlot(psdDataX, frequencies)
        self.psdWaterfallYPlot.updatePlot(psdDataY, frequencies)
        self.psd1dXPlot.updatePlot(psdDataX, frequencies)
        self.psd1dYPlot.updatePlot(psdDataY, frequencies)

    def updateTimeScale(self, newTimeScale):
        """Update the stored timescale in the plot widgets.

        Parameters
        ----------
        newTimeScale : float
            The new timescale.
        """
        self.psdWaterfallXPlot.setTimeScale(newTimeScale)
        self.psdWaterfallYPlot.setTimeScale(newTimeScale)
