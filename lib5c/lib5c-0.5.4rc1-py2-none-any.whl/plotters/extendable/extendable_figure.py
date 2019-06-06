"""
Module for the ExtendableFigure base class.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from lib5c.util.system import check_outdir


class ExtendableFigure(object):
    """
    Base class for figures that can interactively and sequentially tack on new
    axes to themselves.

    Uses a ``divider`` attribute obtained from
    ``mpl_toolkits.axes_grid1.make_axes_locatable()`` to add new axes to the
    figure. Clients can call ``add_ax()`` to add a new axis.

    All the axes in the ExtendableFigure can be accessed by name using a dict-
    like interface: ``f[name]`` where ``f`` is the ExtendableFigure instance and
    ``name`` is the name of the axis. The ExtendableFigure starts out with one
    axis already present, called 'root'.

    Attributes
    ----------
    axes : dict of matplotlib.axes.Axes
        The collection of named Axes represented by this object.
    fig : matplotlib.figure.Figure
        The Figure instance this object represents.
    divider : mpl_toolkits.axes_grid1.axes_divider.AxesDivider
        This object serves as a coordinator for the allocation of new Axes to be
        appended to this ExtendableFigure.

    Examples
    --------
    >>> import numpy as np
    >>> from lib5c.plotters.extendable.extendable_figure import ExtendableFigure
    >>> xs = np.arange(0, 10)
    >>> f = ExtendableFigure()
    >>> f['root'].imshow(np.arange(100).reshape((10,10)))
    <matplotlib.image.AxesImage object at ...>
    >>> f.add_ax('sin')
    <matplotlib.axes._axes.Axes object at ...>
    >>> f['sin'].plot(xs, np.sin(xs))
    [<matplotlib.lines.Line2D object at ...>]
    >>> f.add_colorbar('root')
    >>> f.save('test/extendablefigure.png')
    """
    def __init__(self):
        self.axes = {}
        self.fig, self.axes['root'] = plt.subplots()
        self.divider = make_axes_locatable(self.axes['root'])

    def __getitem__(self, item):
        return self.axes[item]

    def add_ax(self, name, loc='bottom', size='10%', pad=0.1):
        """
        Adds a new axis to this ExtendableFigure.

        Parameters
        ----------
        name : str
            A name for the new axis. The axis will be accessible as
            ``f[new_ax_name]`` where ``f`` is this ExtendableFigure instance.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the figure to add the new axis to.
        size : str
            The size of the new axis as a percentage of the main figure size.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.

        Returns
        -------
        pyplot axis
            The newly created axis.
        """
        if name in self.axes:
            raise ValueError('an axis with name %s already exists!' % name)
        self.axes[name] = self.divider.append_axes(loc, size, pad)
        return self.axes[name]

    def add_colorbar(self, source_ax_name, loc='right', size='10%', pad=0.1,
                     new_ax_name='colorbar'):
        """
        Adds a colorbar to the heatmap in a new axis.

        Parameters
        ----------
        source_ax_name : str
            The name of the axis that this should be the colorbar for. This is
            where matplotlib will look to find color information for the new
            colorbar.
        loc : {'top', 'bottom', 'left', 'right'}
            Which side of the figure to add the new colorbar to.
        size : str
            The size of the new axis as a percentage of the main figure size.
            Should be passed as a string ending in '%'.
        pad : float
            The padding to use between the existing parts of the figure and the
            newly added axis.
        new_ax_name : str
            A name for the new axis. The axis will be accessible as
            ``f[new_ax_name]`` where ``f`` is this ExtendableFigure instance.
        """
        self.add_ax(new_ax_name, loc, size, pad)
        self.fig.colorbar(self.axes[source_ax_name].images[0],
                          cax=self.axes[new_ax_name])

    def save(self, filename):
        """
        Saves this ExtendableHeatmap to the disk as an image file.

        Parameters
        ----------
        filename : str
            The filename to save the image to.
        """
        check_outdir(filename)
        self.fig.savefig(filename, dpi=800, bbox_inches='tight')

    def close(self):
        """
        Clears and closes the pyplot figure related to this ExtendableFigure.
        """
        self.fig.clf()
        plt.close(self.fig)
