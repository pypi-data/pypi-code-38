"""
General plotting facilities.

Graphical representations of TREPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.
Additionally, savers (and stylers) are implemented.

"""

import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

import aspecd.plotting
import trepr.dataset


from colour import Color
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap

left = Color(rgb=(102/255, 0/255, 204/255))
middle = Color(rgb=(1, 1, 1))
right = Color(rgb=(255/255, 51/255, 51/255))

R_left = np.linspace(102 / 255, 1, 128)
G_left = np.linspace(0, 1, 128)
B_left = np.linspace(204 / 255, 1, 128)

A_left = np.linspace(1, 0, 128)
A_right = np.linspace(0, 1, 128)

R_right = np.linspace(1, 255/255, 128)
G_right = np.linspace(1, 51/255, 128)
B_right = np.linspace(1, 51/255, 128)

colors_left = list(left.range_to(middle, 128))
colors_right = list(middle.range_to(right, 128))
for i in range(len(colors_left)):
    colors_left[i] = list(colors_left[i].rgb)
for i in range(len(colors_right)):
    colors_right[i] = list(colors_right[i].rgb)

for i in range(len(colors_left)):
    colors_left[i][0] = R_left[i]
    colors_left[i][1] = G_left[i]
    colors_left[i][2] = B_left[i]

for i in range(len(colors_right)):
    colors_right[i][0] = R_right[i]
    colors_right[i][1] = G_right[i]
    colors_right[i][2] = B_right[i]

viridis = cm.get_cmap('viridis', 256)
jara_colors = viridis(np.linspace(0,1,256))

for i in range(0, 128):
    jara_colors[i][0:3] = [102/255, 0, 204/255]
    jara_colors[i][3] = A_left[i]
for i in range(128,255):
    jara_colors[i][0:3] = [1, 51/255, 51/255]
    jara_colors[i][3] = A_right[i-128]



jara_cmap = ListedColormap(jara_colors)


class ScaledImagePlot(aspecd.plotting.SinglePlotter):
    """Create a scaled image of a given dataset.

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

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '2D plot as scaled image.'
        # protected properties
        self._extent = list()
        self._style_dict = {'interpolation': 'bilinear',
                            'cmap': jara_cmap,
                            'origin': 'lower',
                            'aspect': 'auto'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (0, 0),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset with axes labels and a normed colormap."""
        self._get_extent()
        self._set_style()
        self._display_data()
        self._format_ticklabels()

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _display_data(self):
        """Display the data with adjusted colormap."""
        colormap_adjuster = ColormapAdjuster(dataset=self.dataset)
        colormap_adjuster.adjust()
        self.axes.imshow(self.dataset.data.data,
                         norm=colormap_adjuster.normalised_colormap,
                         extent=self._extent,
                         **self._style_dict)

    def _format_ticklabels(self):
        """Set the format for the ticklabels"""
        plt.ticklabel_format(axis='x', **self._ticklabel_format)

    def _get_extent(self):
        """Define the start and end values of the axes."""
        x_axis_start = self.dataset.data.axes[0].values[0]
        x_axis_end = self.dataset.data.axes[0].values[-1]
        y_axis_start = self.dataset.data.axes[1].values[0]
        y_axis_end = self.dataset.data.axes[1].values[-1]
        self._extent = [x_axis_start, x_axis_end, y_axis_start, y_axis_end]


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

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '1D line plot.'
        self.parameters['color'] = None
        # protected properties
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        self._set_style()
        self._display_zero_line()
        self._display_data()
        self._set_axes()

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)


    def _display_data(self):
        """Plot the data."""
        self.axes.plot(self.dataset.data.axes[0].values,
                       self.dataset.data.data, color=self.parameters['color'])

    def _set_axes(self):
        """Set the limits of the x-axis as well as the ticklabel format."""
        self.axes.set_xlim([self.dataset.data.axes[0].values[0],
                            self.dataset.data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)


class MultiLinePlot(aspecd.plotting.MultiPlotter):

    def __init__(self):
        super().__init__()
        self.description = '1D line plot for multiple lines.'
        self.parameters['color'] = None
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        self._display_zero_line()
        self._display_data()
        self._set_axes()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _display_data(self):
        for i, dataset in enumerate(self.datasets):
            if self.parameters['color']:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data,
                               color=self.parameters['color'][i])
            else:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data)

    def _set_axes(self):
        self.axes.set_xlim([self.datasets[0].data.axes[0].values[0],
                            self.datasets[0].data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)


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
