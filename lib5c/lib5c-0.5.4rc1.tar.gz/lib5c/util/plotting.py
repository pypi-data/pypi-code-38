"""
Module containing utilities related to plotting.
"""

import inspect
from functools import wraps

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.pretty_decorator import pretty_decorator
from lib5c.util.system import check_outdir
from lib5c.util.dictionaries import reduced_get


DEFAULT_RC = {
    'text.color'     : 'black',
    'xtick.color'    : 'black',
    'ytick.color'    : 'black',
    'axes.labelcolor': 'black',
    'axes.edgecolor' : 'black'
}


@pretty_decorator
def plotter(func):
    """
    Multi-purpose decorator for plotting functions.

    Decorated functions should accept ``**kwargs`` in their signature. Clients
    can then pass a wide variety of kwargs to the decorated function. This
    includes all kwargs of ``adjust_plot()`` as well as ``outfile`` (saves the
    plot to disk), ``dpi`` (sets the DPI for the saved plot), and ``style``
    (sets the seaborn style for the plot).
    """
    @wraps(func)
    def decorated_func(*args, **kwargs):
        # inspect func
        names, _, _, defaults = inspect.getargspec(func)
        if defaults is None:
            defaults = {}
        defaults_dict = dict(zip(names[len(names)-len(defaults):], defaults))
        kwargs_dict = dict(zip(names[len(names)-len(defaults):],
                               args[len(args)-len(defaults):]))

        # extract params not used by adjust_plot() from **kwargs
        dicts_to_search = [defaults_dict, kwargs_dict, kwargs]
        ax = reduced_get('ax', dicts_to_search)
        outfile = reduced_get('outfile', dicts_to_search)
        dpi = reduced_get('dpi', dicts_to_search, 100)
        style = reduced_get('style', dicts_to_search, 'ticks')

        # construct plot_kwargs, honoring defaults defined by func
        adj_names, _, _, adj_defaults = inspect.getargspec(adjust_plot)
        plot_kwargs = dict(zip(adj_names[len(adj_names)-len(adj_defaults):],
                               adj_defaults))
        plot_kwargs.update({key: defaults_dict[key] for key in adj_names
                            if key in defaults_dict})
        plot_kwargs.update({key: kwargs_dict[key] for key in adj_names
                            if key in kwargs_dict})
        plot_kwargs.update({key: kwargs[key] for key in adj_names
                            if key in kwargs})

        # special case: if the plotter function has a legend=True kwarg, don't
        # redraw the legend
        if 'legend' in plot_kwargs and plot_kwargs['legend'] is True and \
                'legend' in defaults_dict:
            plot_kwargs['legend'] = None

        # create other_kwargs as "everything else"
        other_kwargs = dict(defaults_dict)
        other_kwargs.update({key: kwargs_dict[key]
                             for key in defaults_dict.keys()
                             if key in kwargs_dict})

        # honor ax
        if ax is not None:
            plt.sca(ax)

        # clear figure if plotting in `outfile` mode
        if outfile is not None:
            plt.clf()

        # do the actual plotting
        if style is not None:
            # prepare sns
            sns.set(color_codes=True)

            with sns.axes_style(style, DEFAULT_RC):
                retval = func(*args[:len(args)-len(defaults)], **other_kwargs)
        else:
            retval = func(*args[:len(args) - len(defaults)], **other_kwargs)

        # save figure
        if outfile is not None:
            check_outdir(outfile)
            if plot_kwargs:
                adjust_plot(**plot_kwargs)
            plt.savefig(outfile, dpi=dpi, bbox_inches='tight')
            plt.close()

        # reset seaborn
        sns.reset_orig()

        # return something sensible
        if retval is None:
            return plt.gca()
        elif type(retval) == tuple:
            return tuple([plt.gca()] + list(retval))
        return plt.gca(), retval

    return decorated_func


def adjust_plot(ax=None, xlim=None, ylim=None, xlabel=None, ylabel=None,
                xticks=None, yticks=None, title=None, despine=True,
                legend=None):
    """
    Multipurpose plot adjustment method.

    Parameters
    ----------
    ax : pyplot axis
        The axis to operate on.
    xlim : tuple of numeric
        Pass a tuple of the form (min, max) to set the x-limits of the plot.
    ylim : tuple of numeric
        Pass a tuple of the form (min, max) to set the y-limits of the plot.
    xlabel : str
        Label for the x-axis.
    ylabel : str
        Label for the y-axis.
    xticks : int, list of int, or tuple of list of ints
        Pass an int to use this as the spacing for the xticks. Pass anything
        else to pass it directly to plt.xticks().
    yticks : int, list of int, or tuple of list of ints
        Pass an int to use this as the spacing for the yticks. Pass anything
        else to pass it directly to plt.yticks().
    title : str
        Title for the plot.
    despine : bool
        Pass True to despine the plot.
    legend : str or bool or None
        Pass False to remove the legend, pass True to add a default legend, pass
        'outside' to move the legend outside the plot area, pass None to leave
        the legend alone.
    """
    if ax is None:
        ax = plt.gca()
    else:
        plt.sca(ax)
    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)
    if xlabel is not None:
        plt.xlabel(xlabel)
    if ylabel is not None:
        plt.ylabel(ylabel)
    if xticks is not None:
        if type(xticks) == int:
            start, stop = plt.xlim()
            xticks = np.arange(start, stop + xticks, xticks)
        plt.xticks(xticks)
    if yticks is not None:
        if type(yticks) == int:
            start, stop = plt.ylim()
            yticks = np.arange(start, stop + yticks, yticks)
        plt.yticks(yticks)
    if title is not None:
        plt.title(title)
    if despine:
        sns.despine()
    if legend is not None:
        if legend == 'outside':
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        if legend is False and ax.legend_:
            ax.legend_.remove()
        if legend is True:
            plt.legend()


def compute_hexbin_extent(xlim, ylim, logx=False, logy=False):
    """
    Helper function for computing the ``extent`` kwarg of ``plt.hexbin()``.

    Parameters
    ----------
    xlim, ylim : tuple, optional
        Tuple of `(x_min, x_max)` and `(y_min, y_max)`, respectively. If either
        is None, no attempt will be made to set the extent.
    logx, logy: bool
        Whether or not ``plt.hexbin()`` is being called with ``xscale='log'``
        and/or ``yscale='log'``, respectively.

    Returns
    -------
    list or None
        The extent if it could be computed or None otherwise.
    """
    if xlim is None or ylim is None:
        return None
    xlim = [np.log10(x) if x > 0 else 0 for x in xlim] if logx else list(xlim)
    ylim = [np.log10(x) if x > 0 else 0 for x in ylim] if logy else list(ylim)
    return xlim + ylim
