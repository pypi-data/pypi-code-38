import matplotlib.pyplot as plt
from matplotlib import ticker, cm
import numpy as np
from .figfuncs import formatFigure

## Plotter functions.
def plotter(**kwargs):
    SweepType = kwargs['SweepType']

    if 'scale' in kwargs.keys():
        scale = kwargs['scale']
    else:
        scale = 'lin'

    if 'Constrain' in kwargs.keys():
        constrain = kwargs['Constrain']
    else:
        constrain = {'Bool': False}

    fig = plt.figure()
    if SweepType == '1D':

        x = kwargs['x']
        y = kwargs['y']
        xlabel = kwargs['xlabel']
        ylabel = kwargs['ylabel']
        color = kwargs['Color']

        ax = fig.add_subplot(111)

        if scale == 'lin':
            ax.plot(x, y, linewidth=2.0, color=color)
        elif scale == 'log':
            ax.semilogy(x, y, linewidth=2.0, color=color)

        if constrain['Bool']:
            if constrain['xlim_min'] != constrain['xlim_max']:
                ax.set_xlim([constrain['xlim_min'], constrain['xlim_max']])
            if constrain['ylim_min'] != constrain['ylim_max']:
                ax.set_xlim([constrain['ylim_min'], constrain['ylim_max']])

        if 'tickoffsety' in kwargs.keys():
            tickoffsety = kwargs['tickoffsety']
        else:
            tickoffsety = 0

        if 'tickseparationy' in kwargs.keys():
            tickseparationy = kwargs['tickseparationy']
        else:
            tickseparationy = 2

        if 'tickoffsetx' in kwargs.keys():
            tickoffsetx = kwargs['tickoffsetx']
        else:
            tickoffsetx = 0

        if 'tickseparationx' in kwargs.keys():
            tickseparationx = kwargs['tickseparationx']
        else:
            tickseparationx = 2

        ax = formatFigure(ax=ax, projection='2d', labels={'xlabel': xlabel, 'ylabel': ylabel},
                          tickseparationy=tickseparationy, tickoffsety=tickoffsety,
                          tickseparationx=tickseparationx, tickoffsetx=tickoffsetx)
        if 'legend' in kwargs.keys():
            if kwargs['legend']:
                ax.legend(loc='lower center', ncol=4, bbox_to_anchor=(0.5, 1.0))

        if 'show' in kwargs.keys():
            if kwargs['show']:
                plt.show()
        else:
            plt.show()

    elif SweepType == 'Multiple':
        xlist = kwargs['x']
        ylist = kwargs['y']
        xlabel = kwargs['xlabel']
        ylabel = kwargs['ylabel']
        colors = kwargs['Color']
        labels = kwargs['labels']

        ax = fig.add_subplot(111)

        for x, y, label, color in zip(xlist, ylist, labels, colors):
            if scale == 'lin':
                ax.plot(x, y, linewidth=2.0, color=color, label=label)
            if scale == 'log':
                ax.semilogy(x, abs(y), linewidth=2.0, color=color, label=label)

        if constrain['Bool']:
            if constrain['xlim_min'] != constrain['xlim_max']:
                ax.set_xlim([constrain['xlim_min'], constrain['xlim_max']])
            if constrain['ylim_min'] != constrain['ylim_max']:
                ax.set_xlim([constrain['ylim_min'], constrain['ylim_max']])

        if 'tickoffsety' in kwargs.keys():
            tickoffsety = kwargs['tickoffsety']
        else:
            tickoffsety = 0

        if 'tickseparationy' in kwargs.keys():
            tickseparationy = kwargs['tickseparationy']
        else:
            tickseparationy = 2

        if 'tickoffsetx' in kwargs.keys():
            tickoffsetx = kwargs['tickoffsetx']
        else:
            tickoffsetx = 0

        if 'tickseparationx' in kwargs.keys():
            tickseparationx = kwargs['tickseparationx']
        else:
            tickseparationx = 2

        ax = formatFigure(ax=ax, projection='2d', labels={'xlabel': xlabel, 'ylabel': ylabel},
                          tickseparationy=tickseparationy, tickoffsety=tickoffsety,
                          tickseparationx=tickseparationx, tickoffsetx=tickoffsetx)

        if 'legend' in kwargs.keys():
            if kwargs['legend']:
                ax.legend(loc='lower center', ncol=4, bbox_to_anchor=(0.5, 1.0))

        if 'show' in kwargs.keys():
            if kwargs['show']:
                plt.show()
        else:
            plt.show()

    elif SweepType == '2D':
        x = kwargs['x']
        y = kwargs['y']
        z = kwargs['z']
        xx, yy = np.meshgrid(x, y)

        xlabel = kwargs['xlabel']
        ylabel = kwargs['ylabel']
        zlabel = kwargs['zlabel']
        colorbar = kwargs['ColorBar']

        ax = fig.add_subplot(111)
        if scale == 'log':
            cp = ax.contourf(xx, yy, np.abs(z), locator=ticker.LogLocator(), cmap=colorbar)
        elif scale == 'lin':
            cp = ax.contourf(xx, yy, np.transpose(z), cmap=colorbar)

        if constrain['Bool']:
            if constrain['xlim_min'] != constrain['xlim_max']:
                ax.set_xlim([constrain['xlim_min'], constrain['xlim_max']])
            if constrain['ylim_min'] != constrain['ylim_max']:
                ax.set_xlim([constrain['ylim_min'], constrain['ylim_max']])

        cbar = plt.colorbar(cp)
        cbar.set_label(zlabel, fontsize=14)
        ax = formatFigure(ax=ax, projection='2d', labels={'xlabel': xlabel, 'ylabel': ylabel, 'zlabel': zlabel})

        if 'show' in kwargs.keys():
            if kwargs['show']:
                plt.show()
            else:
                plt.show()

    else:
        ax = 0

    return ax, fig
