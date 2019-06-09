import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from geopy.distance import geodesic
import math
import gpx2dzg.functions as fx


def setup(ax, xmax=5):
    """Gets the axis ready for number line style plotting.

    Parameters
    ----------
    ax : matplotlib axis instance
        The plot axis to operate on.
    xmax : int or float
        The maximum x value to plot on the number line.
    """

    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.yaxis.set_major_locator(ticker.NullLocator())
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(which='major', width=1.00)
    ax.tick_params(which='major', length=5)
    ax.tick_params(which='minor', width=0.75)
    ax.tick_params(which='minor', length=2.5)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 1)
    ax.patch.set_alpha(0.0)


def sanityplot(gpx=None, gpxname='GPX', dzx=None, dzxname='DZX'):
    """Creates two number line plots for comparison of mark location and scan number.

    Parameters
    ----------
    gpx : gpxpy.GPX
        The list of GPX waypoints to plot.
    gpxname : str
        The name of the GPX file being read. This will be used as axis label text.
    dzx : list
        The list of DZX marks to plot. Each item in the list is a scan number at which a mark was recorded.
    gpxname : str
        The name of the DZX file being read. This will be used as axis label text.

    Returns
    -------
    plot instance
        Creates a matplotlib figure with two axes showing number lines with mark locaitons plotted on each.
    """
    n = 1
    name = [gpxname, gpxname, dzxname]
    label = ['distance (m)', 'time (s)',  'scan number', 'time (s)']
    units = ['m/mark', 's/mark', 'scans/mark', 'm/s']
    title = ['Sanity check plot: GPX and DZT marks', '', '']
    dist, spd, tm = fx.distance_speed_time(gpx)
    fig = plt.figure(figsize=(10, 5))
    fig.set_facecolor('white')
    for data in [dist, tm, dzx]:
        ax = plt.subplot(4, 1, n)
        setup(ax, xmax=data[-1])
        ax.xaxis.set_major_locator(ticker.LinearLocator(3))
        ax.xaxis.set_minor_locator(ticker.LinearLocator(31))
        ax.text(0.0, 0.4, "%s marks - count: %s, mean: %.2f %s" % (name[n-1], len(data), data[-1]/len(data), units[n-1]),
                fontsize=10, transform=ax.transAxes)
        plt.xlabel(label[n-1])
        plt.title(title[n-1])
        for x in data:
            ax.scatter(x,0.1)
        n += 1

    # this is messy but effective
    ax = plt.subplot(4, 1, 4)
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(which='major', width=1.00)
    ax.tick_params(which='major', length=5)
    ax.tick_params(which='minor', width=0.75)
    ax.tick_params(which='minor', length=2.5)
    ax.set_xlim(0, max(tm))
    ax.set_ylim(min(spd)*0.9, max(spd)*1.1)
    plt.xlabel(label[n-1])
    ax.xaxis.set_major_locator(ticker.LinearLocator(3))
    ax.xaxis.set_minor_locator(ticker.LinearLocator(31))
    ax.text(0.0, 1.1, "Speed between gpx marks (m/s)",
            fontsize=10, transform=ax.transAxes)
    n = 0
    ux = []
    for u in spd:
        ux.append(fx.mean([tm[n], tm[n+1]]))
        n += 1
    plt.plot(ux, spd, linewidth=1.5)

    plt.tight_layout()
    plt.show()