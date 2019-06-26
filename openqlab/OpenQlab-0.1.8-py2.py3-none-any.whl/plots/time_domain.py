from OpenQlab.conversion import db
from OpenQlab.io import DataContainer
import numpy as np
import matplotlib.pyplot as plt
import re


def zero_span(traces, normalize=True, title='Zero Span'):
    """
    Create a sensible plot for zero-span squeezing `scope` measurements.

    Args:
        traces : A Pandas :obj:`DataFrame` containing the zero-span traces,
            where the time-base is given in the frame's index.
        normalize (bool, optional):
            Normalize the data to the vacuum trace, which requires a column
            name starting with "*vac*".
        title (str, optional): The figure title.

    Returns:
        matplotlib.figure.Figure: A handle to the created matplotlib figure.
    """
    fig, ax = plt.subplots()
    plt.subplots_adjust(right=0.85)

    ylabel = 'Noise Power (dBm)'
    unit = 'dBm'
    vac_trace = None
    for trace in traces:
        if re.match('vac', trace, re.IGNORECASE):
            vac_trace = trace
            break

    if vac_trace and normalize:
        vac_level = db.mean(traces[vac_trace])
        traces = traces - vac_level
        ylabel = 'Relative Noise (dB)'
        unit = 'dB'

    traces.plot(ax=ax, title=title)
    ax.legend(loc='best', frameon=True)
    plt.ylabel(ylabel)
    plt.grid(True)

    # add average values for those traces that don't fluctuate too much, i.e.
    # not for McDonald's _type traces
    ii = 0
    for trace in traces:
        std = traces[trace].std()
        if std < 0.3:
            mean_val = db.mean(traces[trace])
            ax.annotate('{0:.2f}{1}'.format(mean_val, unit),
                        (traces.index[-1], mean_val),
                        (10, 0), textcoords='offset points',
                        horizontalalignment='left',
                        verticalalignment='center',
                        color=ax.lines[ii].get_color())
        ii += 1
    return fig


# SCOPE
#
# A very simple plot of time-domain traces, e.g. from an oscilloscope
def scope(traces, title='Oscilloscope View'):
    """
    Create plot for oscilloscope data.

    This function plots up to four channels from oscilloscope time-voltage
    data into one plot. Each trace will have its own auto-scaled y axis.

    Args:
        traces : A Pandas :obj:`DataFrame` containing the time-domain traces,
            where the time-base is given by the frame's index.
        title : The figure title.

    Returns:
        matplotlib.figure.Figure: A handle to the created matplotlib figure.
    """
    from mpl_toolkits.axes_grid1 import host_subplot
    import mpl_toolkits.axisartist as AA

    traces = DataContainer(
        traces)  # then you can also conviniently put in a single column, which would otherwise be a series
    offset = 50
    Ntraces = len(traces.columns)
    if Ntraces > 4:
        raise Exception('This plot only works with up to four traces.')

    fig = plt.figure()
    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(right=1.0 - 0.11 * (Ntraces - 1))

    line, = host.plot(traces.index, traces.iloc[:, 0], label=traces.columns[0])
    host.set_ylabel(traces.columns[0])
    host.set_xlabel(traces.index.name)
    host.axis['left'].label.set_color(line.get_color())

    for ii in range(1, Ntraces):
        ax = host.twinx()
        if ii >= 2:
            new_fixed_axis = ax.get_grid_helper().new_fixed_axis
            pax = new_fixed_axis(loc="right",
                                 axes=ax,
                                 offset=((ii - 1) * offset, 0))

            pax.line.set_linewidth(0.5)
            pax.line.set_color('k')
            pax.major_ticks.set_linewidth(0.5)
            pax.major_ticks.set_color('k')
            pax.major_ticks.set_ticksize(4.0)
            ax.axis['right'] = pax

        line, = ax.plot(traces.index, traces.iloc[:, ii], label=traces.columns[ii])
        ax.axis['right'].toggle(all=True)
        ax.set_ylabel(traces.columns[ii])
        ax.axis['right'].label.set_color(line.get_color())

    host.grid(True, zorder=1)
    host.set_title(title)
    return fig
