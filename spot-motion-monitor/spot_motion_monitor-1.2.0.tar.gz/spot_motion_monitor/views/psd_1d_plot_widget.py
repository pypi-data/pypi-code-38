#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from pyqtgraph import GraphicsLayoutWidget

from spot_motion_monitor.utils import HTML_NU, noneToDefaultOrValue

__all__ = ['Psd1dPlotWidget']

class Psd1dPlotWidget(GraphicsLayoutWidget):

    """This class handles managing the 1D Power Spectrum Distribution plots
       for both x and y components.

    Attributes
    ----------
    autoscale : .AutoscaleState
        The status of auto scaling the plot.
    curve : pyqtgraph.PlotDataItem
        Instance of the line in the plot.
    plot : pyqtgraph.PlotItem
        Instance of the graphics plot.
    yRange : list
        The bounds for the y axis of the plot when disabling auto range.
    """

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.plot = self.addPlot()
        self.plot.setLogMode(y=True)
        self.curve = self.plot.plot([], [])
        self.autoscale = True
        self.yRange = None

    def clearPlot(self):
        """Reset all data and clear the plot.
        """
        self.curve.setData([], [])
        self.plot.setRange(xRange=(0, 1), yRange=(0.1, 1), padding=0, disableAutoRange=False)

    def getConfiguration(self):
        """Get the current plot configuration.

        Returns
        -------
        dict
            The set of current configuration parameters.
        """
        config = {}
        config['autoscale'] = self.autoscale
        if self.yRange is not None:
            config['minimum'] = self.yRange[0]
            config['maximum'] = self.yRange[1]
        else:
            config['minimum'] = None
            config['maximum'] = None
        return config

    def setConfiguration(self, config):
        """Set the new parameters into the widget.

        Parameters
        ----------
        config : dict
            The new parameters to apply.
        """
        self.autoscale = config['autoscale']
        if self.autoscale:
            self.plot.enableAutoRange()
            self.yRange = None
        else:
            minimum = noneToDefaultOrValue(config['minimum'], default=0)
            maximum = noneToDefaultOrValue(config['maximum'], default=1000)
            self.yRange = [minimum, maximum]
            self.plot.setRange(yRange=self.yRange)
            self.plot.disableAutoRange()

    def setup(self, axisLabel):
        """Provide information for setting up the plot.

        Parameters
        ----------
        axisLabel : str
            The label for the axis.
        """
        self.plot.setLabel('bottom', '{} {}'.format(axisLabel, HTML_NU), units='Hz')
        self.plot.setLabel('left', 'PSD', units='pixel^2 s')

    def updatePlot(self, psdData, frequencies):
        """Update the plot with new PSD and frequency arrays.

        Parameters
        ----------
        psdData : numpy.array
            Instance of the current Power Spectrum Distribution data.
        frequencies : numpy.array
            Instance of the current frequency axis for the PSD data.
        """
        self.curve.setData(frequencies, psdData)
