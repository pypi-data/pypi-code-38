import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

import aspecd.plotting
import trepr.dataset

class LinePlot(aspecd.plotting.SinglePlotter):
    """Create a 1D line plot of a given dataset.

    Parameters
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    description : str
        Describes the aim of the class.

    filename : str
        Name of the resulting plot file.

    """

    def __init__(self, dataset=None):
        super().__init__()
        # public properties
        self.dataset = dataset
        self.style = ''
        self.description = '1D line plot.'
        self.filename = ''
        # protected properties
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        self._set_style()
        self._display_data()
        self._set_axes()
        self._display_zero_line()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _set_axes(self):
        """Set the limits of the x-axis as well as the ticklabel format."""
        self.axes.set_xlim([self.dataset.data.axes[0].values[0],
                            self.dataset.data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)

    def _display_data(self):
        """Plot the data."""
        self.axes.plot(self.dataset.data.axes[0].values,
                       self.dataset.data.data)

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()


class ColormapAdjuster:
    """General facilities to adjust the colormap.

    This class makes sure that the zero point of the colormap is equal to the
    zero point of the dataset.

    Parameters
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    normalised_colormap : :class:`matplotlib.colormap`
        Colormap normalised to data of dataset.

    """

    def __init__(self, dataset=trepr.dataset.ExperimentalDataset()):
        # public properties
        self.dataset = dataset
        self.normalised_colormap = None
        # protected properties
        self._bound = None

    def adjust(self):
        """Perform all methods to adjust the colormap."""
        self._get_min_and_max()
        self._set_norm()

    def _get_min_and_max(self):
        """Calculate the minimum an maximum of the intensity."""
        min_ = np.amin(self.dataset.data.data)
        max_ = np.amax(self.dataset.data.data)
        self._bound = np.amax([abs(min_), max_])

    def _set_norm(self):
        """Normalize the colormap."""
        self.normalised_colormap = \
            mpl.colors.Normalize(vmin=self._bound * -1, vmax=self._bound)


class Saver(aspecd.plotting.Saver):

    pass

