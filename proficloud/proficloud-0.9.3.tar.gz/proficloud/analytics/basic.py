import pandas as pd
import bisect
#
from math import pi
from numpy import arange
from itertools import chain
from collections import OrderedDict
#
from bokeh.models import ColorBar, LinearColorMapper
from bokeh.plotting import figure, show

import itertools 
from bokeh.palettes import plasma as palette
import matplotlib

def getCorrelationMatrixBokeh(data, showPlot=False, width=950, height=950, title="Correlation Coefficient Heatmap"):
    correlation = data.corr()

    from bokeh.palettes import RdBu as colors  # just make sure to import a palette that centers on white (-ish)
    colors = list(reversed(colors[9]))  # we want an odd number to ensure 0 correlation is a distinct color
    labels = data.columns
    nlabels = len(labels)

    def get_bounds(n):
        """Gets bounds for quads with n features"""
        bottom = list(chain.from_iterable([[ii]*nlabels for ii in range(nlabels)]))
        top = list(chain.from_iterable([[ii+1]*nlabels for ii in range(nlabels)]))
        left = list(chain.from_iterable([list(range(nlabels)) for ii in range(nlabels)]))
        right = list(chain.from_iterable([list(range(1,nlabels+1)) for ii in range(nlabels)]))
        return top, bottom, left, right

    def get_colors(corr_array, colors):
        """Aligns color values from palette with the correlation coefficient values"""
        ccorr = arange(-1, 1, 1/(len(colors)/2))
        color = []
        for value in corr_array:
            ind = bisect.bisect_left(ccorr, value)
            color.append(colors[ind-1])
        return color

    p = figure(plot_width=width, plot_height=height,
            x_range=(0,nlabels), y_range=(0,nlabels),
            title=title,
            toolbar_location=None, tools='')

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.xaxis.major_label_orientation = pi/2
    p.yaxis.major_label_orientation = 2*pi

    top, bottom, left, right = get_bounds(nlabels)  # creates sqaures for plot
    color_list = get_colors(correlation.values.flatten(), colors)

    p.quad(top=top, bottom=bottom, left=left,
        right=right, line_color='white',
        color=color_list)

    # Set ticks with labels
    ticks = [tick+0.5 for tick in list(range(nlabels))]
    tick_dict = OrderedDict([[tick, labels[ii]] for ii, tick in enumerate(ticks)])
    # Create the correct number of ticks for each axis 
    p.xaxis.ticker = ticks
    p.yaxis.ticker = ticks
    # Override the labels 
    p.xaxis.major_label_overrides = tick_dict
    p.yaxis.major_label_overrides = tick_dict

    # Setup color bar
    mapper = LinearColorMapper(palette=colors, low=-1, high=1)
    color_bar = ColorBar(color_mapper=mapper, location=(0, 0))
    p.add_layout(color_bar, 'right')

    if showPlot:
        show(p)

    return { "plot": p, "correlation": correlation }

def getCorrelationMatrix(data, size=10):
    import matplotlib.pyplot as plt
    corr = data.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    x = ax.matshow(corr)
    
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    fig.colorbar(x)

    return { "plot": fig, "correlation": corr }

def plotSignalsLine(data, timecol, signals, bokeh=False):
    colors = itertools.cycle(palette(len(signals)))
    
    if bokeh:
        TOOLS="hover,box_zoom,reset,save,box_select"
        p = figure(tools=TOOLS,plot_width=950, plot_height=400, x_axis_type="datetime")
        for s in signals:
            p.line(data[timecol].values, data[s].values, legend=s, color=next(colors))
        show(p)
        return p
    else:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(20,10))
        
        for s in signals:
            plt.plot(timecol, s, data=data, color = next(colors))
        
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))

        return plt

    