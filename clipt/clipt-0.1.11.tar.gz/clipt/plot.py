# Copyright (c) 2018 Stephen Wasilewski
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================

"""functions for plotting with matplotlib"""

from __future__ import print_function

import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import Circle
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.transforms import Bbox


daycount = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]


def tick_from_arg(ax, xs, ys, a4, kwargs):
    """sets ticks based on standard argument parsing

    Parameters
    ----------
    ax: matplotlib subplot
    a4: kwargs for ticks
    kwargs: input arguments
    Returns
    -------
    ax: matplotlib subplot
    """
    if 'pery' not in kwargs:
        pery = False
    else:
        pery = kwargs['pery'] is not None
    try:
        if kwargs['xlog']:
            a4['xscale'] = 'log'
    except Exception:
        pass
    try:
        if kwargs['ylog']:
            a4['yscale'] = 'log'
    except Exception:
        pass
    try:
        if kwargs['weax'] is not None:
            a4['annualx'] = True
    except Exception:
        pass
    try:
        a4['tcol'] = kwargs['fg']
    except Exception:
        pass
    for i in ['polar', 'stacked', 'polarautp']:
        try:
            kwargs[i] = kwargs[i]
        except Exception:
            kwargs[i] = False
    try:
        a4.update(get_axes(kwargs['axes'], xs, ys, kwargs['polar'],
                           kwargs['polarauto'], kwargs['stacked'], pery=pery))
    except Exception, ex:
        try:
            a4.update(get_axes(kwargs['axes'], xs, ys, kwargs['polar'], stacked=kwargs['stacked'], pery=pery))
        except Exception, ex:
            raise
            pass
    ax = ticks(ax, **a4)
    return ax


def get_labels(labels, mlab):
    """returns data based on standard argument parsing

    Parameters
    ----------
    labels: list
        labels retruned by read_all_data
    mlab: list
        manual labels for data
    Returns
    -------
    labels: list
        list of labels for each y_val
    """
    if mlab is not None:
        for i, l in enumerate(mlab):
            try:
                labels[i] = l
            except Exception:
                labels.append(l)
    return labels


def get_axes(arg, xs, ys, polar=False, polarauto=True, stacked=False, pery=False):
    """parse axes string argument xname,xmin,xmax,yname,ymin,ymax"""
    def smin(x):
        try:
            return min(x)
        except Exception:
            return None

    def smax(x):
        try:
            return max(x)
        except Exception:
            return None
    x = flat(xs)
    if stacked:
        try:
            y = [sum([i[j] for i in ys]) for j in range(len(ys[0]))]
        except:
            y = []
    else:
        y = flat(ys)
    axes = ['X', smin(x), smax(x), 'Y', smin(y), smax(y)]
    try:
        ax = arg.split(",")
        for i, v in enumerate(ax):
            if i in [0, 3]:
                axes[i] = v
            else:
                try:
                    axes[i] = float(v)
                except Exception:
                    pass
    except Exception:
        raise ValueError(arg)
    naxes = {'labels': [axes[0], axes[3]],
             'xdata': [axes[1], axes[2]],
             'ydata': [axes[4], axes[5]]}
    if pery:
        naxes['ydata'] = y
    if polar and polarauto:
        naxes['xdata'] = [0, 2*math.pi]
    elif polar:
        naxes['xdata'] = [axes[1]*math.pi/180, axes[2]*math.pi/180]
    return naxes


def plot_setup(fg='black', bg='white', polar=False, areaonly=False, params={}):
    """
    setup plot with uniform styling and create axes for plot

    Parameters
    ----------
    fg: color
        foreground color
    bg: color
        background color
    polar: bool
        if true make polar plot
    params: dict
        rcParams to update
    Returns
    -------
    ax: matplotlib sublot
    fig: matplotlib figure
    """
    defparam = {
        'font.weight': 'ultralight',
        'font.family': 'sans-serif',
        'font.size': 7,
        'axes.linewidth': 0.5,
        'axes.edgecolor': fg
    }
    rcParams.update(defparam)
    fig = plt.figure()
    if areaonly:
        if polar:
            ax = fig.add_subplot(1, 1, 1, position=[0, 0, 1, 1], facecolor=bg,
                                 polar=polar, frame_on=True)
        else:
            ax = fig.add_subplot(1, 1, 1, position=[0, 0, 1, 1], facecolor=bg,
                                 polar=polar, frame_on=False)
    else:
        ax = fig.add_subplot(1, 1, 1, facecolor=bg, polar=polar)
    return ax, fig


def ticks(ax, xdata=[0, 1], ydata=[0, 1], tcol='black', labels=['X', 'Y'],
          xgrid=False, ygrid=False, xscale='linear', yscale='linear',
          annualx=False, dayy=False, pery=False, ticklines=False, pph=1,
          bottom=None, bg='white', xlabels=None, dpy=365, hpd=24, sh=0,
          polar=False, xticks=None, yticks=None, labelweight='bold'):
    """
    setup ticks/axes for plot

    Parameters
    ----------
    ax: matplotlib sublot
    xdata: list
        x data (or min and max)
    ydata: list
        y data (or min and max)
    tcol: color
        tick color
    labels: list
        x and y axis labels
    xgrid: bool
        show x grid
    ygrid: bool
        show y grid
    xscale: str
        linear or log
    yscale: str
        linear or log
    annualx: bool
        plot xaxis as full year with month labels
    dayy: bool
        plot yaxis as day with hour labels
    pery: bool/int
        if > 1 label y axis according to percentile of data with pery bins
    ticklines: bool
        if not grid, show ticklines
    """
    xmin = xdata[0]
    xmax = xdata[-1]
    ymin = min(ydata)
    ymax = max(ydata)
    ax.xaxis.grid(linestyle="-", linewidth=0.3, color=tcol)
    ax.yaxis.grid(linestyle="-", linewidth=0.3, color=tcol, zorder=1)
    ax.xaxis.grid(xgrid)
    ax.yaxis.grid(ygrid)
    ax.set_xlim(left=xmin, right=xmax)
    ax.set_ylim(bottom=ymin, top=ymax)
    ax.set_yscale(yscale)
    ax.set_xscale(xscale)
    ax.set_axisbelow(True)
    ax.axes.set_xlabel(labels[0], weight=labelweight, size=9, color=tcol)
    ax.axes.set_ylabel(labels[1], weight=labelweight, size=9, color=tcol)
    if annualx:
        ax = ticks_x_annual(ax, tcol, dpy)
    if dayy:
        ax = ticks_y_day(ax, tcol, pph, hpd, sh)
    elif pery:
        ax = ticks_y_per(ax, ydata, pery, tcol)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(7)
        tick.label.set_color(tcol)
    for t in ax.yaxis.get_ticklines() + ax.yaxis.get_ticklines(minor=True):
        t.set_visible(ticklines and not ygrid)
        t.set_color(tcol)
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(7)
        tick.label.set_color(tcol)
    for t in ax.xaxis.get_ticklines() + ax.xaxis.get_ticklines(minor=True):
        t.set_visible(ticklines and not xgrid)
        t.set_color(tcol)
    if bottom is not None and bottom > 0:
        ylim = [ymin, ymax]
        ylimb = [i+bottom for i in ylim]
        ax.set_ylim(bottom=ylim[0], top=ylimb[1])
        ax.get_yaxis().get_major_formatter().set_useOffset(bottom)
    if xlabels is not None and len(xlabels) > 0:
        inc = (xmax-xmin)/len(xlabels)
        if polar:
            ax.set_xticks(np.arange(xmin, xmax, inc))
            ax.set_xticklabels(xlabels)
            ax.set_xlim(left=xmin, right=xmax)
        else:
            ax.set_xticks(np.arange(xmin+inc/2, xmax+inc/2, inc))
            if max([len(i) for i in xlabels]) > 10:
                ro = 'vertical'
            else:
                ro = 'horizontal'
            ax.set_xticklabels(xlabels, rotation=ro)
            for t in ax.xaxis.get_ticklines():
                t.set_visible(False)
    if polar:
        if bottom is not None and bottom > 0:
            ci = Circle((0, 0), zorder=2, radius=bottom, fill=True,
                        linewidth=0.3, edgecolor=tcol, facecolor=bg,
                        transform=ax.transData._b)
            ax.add_artist(ci)
        ci = Circle((0, 0), zorder=-200, radius=(bottom+ymax-ymin),
                    fill=False, linewidth=0, edgecolor='blue',
                    facecolor='blue', transform=ax.transData._b)
        ax.add_artist(ci)
        ax.yaxis.set_ticklabels([])
        ax.axes.set_ylabel("")
    if bottom is None:
        bottom = 0
    if yticks is not None:
        ax.set_yticks(np.append(np.arange(bottom+ymin, ymax+bottom,
                      (ymax-ymin)/(yticks)),ymax+bottom))
    if xticks is not None:
        ax.set_xticks(np.append(np.arange(xmin, xmax, (xmax-xmin)/(xticks)),xmax))
    return ax


def plot_legend(handles, bbox_to_anchor=(1.05, 1), loc=2,
                fg='black', bg='white'):
    """add legend to figure"""
    leg = plt.legend(handles=handles, frameon=False,
                     bbox_to_anchor=bbox_to_anchor, loc=loc, facecolor=bg)
    for text in leg.get_texts():
        text.set_color(fg)


def add_colorbar(fig, pc, axes=[0.3, 0.0, 0.4, 0.02],
                 ticks=None, ticklabels=None):
    """add colorbar scale to figure below plot"""
    cbaxes = fig.add_axes(axes)
    if ticklabels is not None:
        if ticks is None:
            vmin, vmax = pc.get_clim()
            ticks = np.linspace(vmin, vmax, len(ticklabels))
        cb = fig.colorbar(pc, orientation="horizontal",
                          cax=cbaxes, ticks=ticks)
        if ticklabels is not None:
            cb.ax.set_xticklabels(ticklabels)
    else:
        cb = fig.colorbar(pc, orientation="horizontal", cax=cbaxes)
    cb.ax.tick_params(labelsize=8)
    cb.outline.set_linewidth(.5)
    for t in cb.ax.get_xticklines():
        t.set_visible(False)


def plot_graph(fig, saveimage, width=10.5, height=5, bg='white', fg='black',
               handles=[], dpi=200, bbox_to_anchor=(1.05, 1),
               loc=2, legend=False, format='png', background=None,
               front=False, alpha=.5, areaonly=False, polar=False):
    """add legend and save image of plot"""
    fig.set_size_inches(width, height)
    if legend and not areaonly:
        plot_legend(handles=handles, bbox_to_anchor=bbox_to_anchor,
                    loc=loc, bg=bg, fg=fg)
    if polar:
        if background is not None:
            im = plt.imread(background)
            ax = fig.axes[0]
            ax2 = fig.add_axes([0, 0, 1, 1])
            extent = ax2.get_xlim() + ax2.get_ylim()
            plt.imshow(im, extent=extent, alpha=alpha, aspect='auto')
            if front:
                ax.set_zorder(ax2.get_zorder()-1)
            else:
                ax.set_zorder(ax2.get_zorder()+1)
                ax.patch.set_visible(False)
            ax2.axis('off')
        if areaonly:
            ax = fig.axes[0]
            ax.axes.set_xlabel("")
            ax.axes.set_ylabel("")
            ax.xaxis.set_ticklabels([])
            ci = [i.get_extents() for i in ax.get_children()
                  if type(i) == Circle]
            extent = Bbox([[min([i.xmin for i in ci]),
                            min([i.ymin for i in ci])],
                           [max([i.xmax for i in ci]),
                            max([i.ymax for i in ci])]])
            wi = width*(extent.xmax-extent.xmin)/500
            he = height*(extent.ymax-extent.ymin)/500
            ow = width*extent.xmin/500
            oh = height*extent.ymin/500
            extent = Bbox([[ow, oh], [wi+ow, he+oh]])
            plt.savefig(saveimage, dpi=dpi, bbox_inches=extent, aspect='auto',
                        facecolor=bg, pad_inches=0)
        else:
            plt.savefig(saveimage, dpi=dpi, bbox_inches='tight', facecolor=bg)
    else:
        if areaonly:
            ax = fig.axes[0]
            if background is not None:
                im = plt.imread(background)
                ax.imshow(im, extent=ax.get_xlim() + ax.get_ylim(),
                          alpha=alpha, aspect='auto')
            plt.savefig(saveimage, dpi=dpi, bbox_inches=None, aspect='auto',
                        facecolor=bg, pad_inches=0)
        else:
            if background is not None:
                im = plt.imread(background)
                ax = fig.axes[0]
                ax2 = ax.twinx()
                plt.imshow(im, extent=ax2.get_xlim() + ax2.get_ylim(),
                           alpha=alpha, aspect='auto')
                if front:
                    ax.set_zorder(ax2.get_zorder()-1)
                else:
                    ax.set_zorder(ax2.get_zorder()+1)
                    ax.patch.set_visible(False)
                ax2.axis('off')
            plt.savefig(saveimage, dpi=dpi, bbox_inches='tight', facecolor=bg)
    plt.close()


def get_colors(cmap, step=None, positions=None, funcs=[]):
    """get colormap from cmap name, color list or CliptColors spec

    Parameters
    ----------
    cmap: str or list of color tuples
        cmap selector
    positions: list
        if cmap is a list positions are the mapping points
        else positions are the sample points used to remap
    step: int or None
        # of steps to map colors using step function
    funcs: list of custom color map functions to try before standard 
        matplotlib cmap name check and cmap_from_list
        func should accept a cmap argument, and step and position
        (call cmap_tune within to utilize) and return a 
        matplotlib.cm.ScalarMappable

    Returns
    -------
    colormap: matplotlib.colors.LinearSegmentedColormap
    """
    efuncs = funcs + [cmap_from_mpl, cmap_from_clipt, cmap_from_list]
    e = []
    for func in efuncs:
        try:
            colormap = func(cmap, step, positions)
            break
        except Exception, err:
            e.append(str(err))
            continue
    else:
        raise ValueError("\n\n".join(e))
    return colormap


def plot_cmaps(ru=False):
    """plot predefined colormaps showing impact of step and position

    Returns
    -------

    fig: matplotlib graph
        can be saved using plt.savefig(...) or plotutil.plot_graph(...)
    """
    if ru:
        cmaps = [('hues', ['blu', 'org', 'pur', 'red', 'blg',
                  'mag', 'brn', 'grn', 'yel', 'ggr']),
                 ('shades', ['dark', 'med', 'light', 'xlight'])
                 ]
    else:
        cmaps = [('Perceptually Uniform Sequential', [
                    'viridis', 'plasma', 'inferno', 'magma']),
                 ('Sequential', [
                    'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                    'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                    'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
                 ('Sequential (2)', [
                    'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                    'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                    'hot', 'afmhot', 'gist_heat', 'copper']),
                 ('Diverging', [
                    'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                    'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr',
                    'seismic']),
                 ('Qualitative', [
                    'Pastel1', 'Pastel2', 'Paired', 'Accent',
                    'Dark2', 'Set1', 'Set2', 'Set3',
                    'tab10', 'tab20', 'tab20b', 'tab20c']),
                 ('Miscellaneous', [
                    'flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                    'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix',
                    'brg', 'hsv', 'gist_rainbow', 'rainbow', 'jet',
                    'nipy_spectral', 'gist_ncar'])]
    nrows = sum(len(cmap_list)
                for cmap_category, cmap_list in cmaps) + len(cmaps)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    fig, axes = plt.subplots(nrows=nrows)
    fig.set_size_inches(3, 10)
    fig.subplots_adjust(top=0.95, bottom=0.01, left=0.2, right=0.99)
    if ru:
        axes[0].set_title('clipt colors', fontsize=14)
    else:
        axes[0].set_title('matplotlib colors', fontsize=14)
    i = 0
    for cmap_category, cmap_list in cmaps:
        ax = axes[i]
        pos = list(ax.get_position().bounds)
        y_text = pos[1] + pos[3]/2.
        fig.text(.6, y_text, cmap_category, va='center',
                 ha='center', fontsize=6)
        i += 1
        if cmap_category == 'hues':
            step = 4
        elif cmap_category == 'shades':
            step = 10
        else:
            step = None
        for name in cmap_list:
            ax = axes[i]
            colorbar = get_colors(name, step=step)
            ax.imshow(gradient, aspect='auto', cmap=colorbar.cmap)
            pos = list(ax.get_position().bounds)
            x_text = pos[0] - 0.01
            y_text = pos[1] + pos[3]/2.
            fig.text(x_text, y_text, name, va='center', ha='right', fontsize=6)
            i += 1
    for ax in axes:
        ax.set_axis_off()
    return fig


def plot_criteria(ax, x, y, criteria, flipxy=False,
                  kwargs={'linewidth': 0, 'marker': "o", 'markersize': 4,
                          'mew': 0}):
    """add dot on line matching criteria to scatter plot"""
    filtx = []
    filty = []
    val = [float(criteria.split("=")[-1])]
    if criteria[0] == 'x':
        filtx = val
        filty = np.interp(val, x, y)
    elif criteria[0] == 'y':
        xs = [ix for _, ix in sorted(zip(y, x))]
        ys = sorted(y)
        filtx = np.interp(val, ys, xs)
        filty = val
    if flipxy:
        ax.plot(filty, filtx, **kwargs)
    else:
        ax.plot(filtx, filty, **kwargs)


def plot_scatter(ax, xs, ys, labels, colormap, criteria=None, lw=2, ms=0,
                 mrk='o', step=None, fcol=0.0, mew=0.0, emap=None,
                 flipxy=False, cs=None, cmin=None, cmax=None, **kwargs):
    """adds scatterplots/lines to ax and returns ax and handles for legend"""
    nlab = len(labels)
    for i in range(len(ys)):
        if i >= nlab:
            labels.append("series{:02d}".format(i))
    handles = []
    if step is not None:
        inc = (1.-fcol)/(step-1)
    else:
        try:
            inc = (1.-fcol)/(len(ys)-1)
        except ZeroDivisionError:
            inc = 1
    if emap is None:
        emap = colormap
    for i, (x, y, l) in enumerate(zip(xs, ys, labels)):
        lwa = get_nth(lw, i)
        msa = get_nth(ms, i)
        mka = get_nth_loop(mrk, i)
        mewa = get_nth_loop(mew, i)
        if step is not None or inc > 1:
            cinc = (fcol + i*inc) % 1
        else:
            cinc = fcol + i*inc
        c = colormap.to_rgba(cinc)
        mec = emap.to_rgba(cinc)
        if cs is not None:
            if cmax is None:
                cmax = max(flat(cs))
            if cmin is None:
                cmin = min(flat(cs))
            plotargs = {'linewidth': lwa, 's': msa**2, 'label': l,
                        'marker': mka, 'cmap': colormap.cmap, 'linewidth': mewa,
                        'vmin': cmin, 'vmax': cmax, 'c': cs[i], 'edgecolors': mec,
                        'norm': colormap.norm}
            plotargs.update(kwargs)
            ax.scatter(x, y, **plotargs)
        else:
            plotargs = {'linewidth': lwa, 'markersize': msa, 'label': l,
                        'marker': mka, 'color': c, 'mfc': c, 'mec': mec,
                        'mew': mewa}
            plotargs.update(kwargs)
            if flipxy:
                ax.plot(y, x, **plotargs)
            else:
                ax.plot(x, y, **plotargs)
        if criteria:
            copts = {'linewidth': 0, 'mfc': c, 'mew': 0,
                     'markersize': lwa*2.5, 'marker': 'o'}
            plot_criteria(ax, x, y, criteria, flipxy, copts)
    handles, labels = ax.get_legend_handles_labels()
    return ax, handles


def plot_heatmap(fig, ax, data, colormap, vmin=None, vmax=None,
                 dst=False, ticks=None, labels=None, legend=True, hpd=24,
                 dpy=365, sh=0, **kwargs):
    """adds heatmap and colorbar to ax returns ax"""
    xlim = ax.axes.get_xlim()
    xrng = abs(xlim[1]-xlim[0])
    ppd = int(len(data)/xrng)
    if dst:
        data = shift_data(data, ppd/hpd, hpd=hpd, dpy=dpy, sh=sh)
    try:
        mtx = np.reshape(data, (int(xrng), ppd))
        tmtx = np.transpose(mtx)
    except Exception:
        raise ValueError('expected {} data points got {}'.format(
                         int(xrng)*ppd, len(data)))
    if vmax is None:
        vmax = max(data)
    if vmin is None:
        vmin = min(data)
    pc = ax.pcolor(tmtx, cmap=colormap.cmap, vmax=vmax, vmin=vmin, snap=True,
                   **kwargs)
    if legend:
        add_colorbar(fig, pc, ticks=ticks, ticklabels=labels)
    return ax


def plot_bar(ax, xs, ys, labels, colormap, stacked=False, rwidth=.8, step=None,
             bwidth=.9, brng=[0, 1], bottom=0, polar=False, polar0=False,
             emap=None, ew=[0], **kwargs):
    """adds bar plots to ax and returns ax and handles for legend"""
    nlab = len(labels)
    if emap is None:
        emap = colormap
    for i in range(len(ys)):
        if i >= nlab:
            labels.append("series{:02d}".format(i))
    if stacked:
        nlab = 1
    else:
        nlab = len(labels)
    if step is not None:
        inc = 1./(step-1)
    else:
        try:
            inc = 1./(len(ys)-1)
        except ZeroDivisionError:
            inc = 1
    xl = ax.axes.get_xlim()
    xlim = [xl[0]+brng[0]*(xl[1]-xl[0]), xl[0]+brng[1]*(xl[1]-xl[0])]
    xrng = abs(xlim[1]-xlim[0])/float(len(xs[0]))
    lxs = len(xs[0])
    width = xrng/nlab*rwidth
    try:
        xsc = (lxs - 1.0)/lxs
    except ZeroDivisionError:
        xsc = 1
    xsc = xsc * (brng[1] - brng[0])
    if polar and polar0:
        off0 = brng[0] * abs(xl[1]-xl[0])
    else:
        off0 = xrng/2-width*(nlab-1)/2 + xlim[0]
    w2 = width*bwidth
    bot = 0
    for i, (x, y, l) in enumerate(zip(xs, ys, labels)):
        c = colormap.to_rgba(i*inc)
        e = emap.to_rgba(i*inc)
        ewa = get_nth_loop(ew, i)
        plotargs = {'label': l, 'color': c, 'linewidth': ewa, 'edgecolor': e}
        plotargs.update(kwargs)
        if stacked:
            if i > 0:
                bot = np.array(ys[i-1]) + bot
            ax.bar(np.array(x)*xsc+off0, y, w2, bottom=bot+bottom, **plotargs)
        else:
            offset = i*width
            ax.bar(np.array(x)*xsc+offset+off0, y, w2, bottom=bottom,
                   **plotargs)
    handles, labels = ax.get_legend_handles_labels()
    return ax, handles


def plot_box(ax, data, labels, colormap, ylim, rwidth=.8,
               step=None, **kwargs):
    """adds box plots to ax and returns ax and handles for legend"""
    nlab = len(labels)
    for i in range(len(data)):
        if i >= nlab:
            labels.append("series{:02d}".format(i))
    try:
        inc = 1./(len(data)-1)
    except ZeroDivisionError:
        inc = 1
    c = [colormap.to_rgba(i*inc) for i in range(len(data))]
    plotargs = {
        'boxprops' : {'linewidth':0,'color':c[0]},
        'capprops' : {'color':c[0],'linewidth':2,'solid_capstyle':'butt'},
        'whiskerprops' : {'color':c[0],'linewidth':2,'solid_capstyle':'butt'},
        'medianprops' : {'linewidth':2,'color':'white','solid_capstyle':'butt'}
    }
    plotargs.update(kwargs)
    boxplot = ax.boxplot(data, patch_artist=True, widths=rwidth, whis='range', bootstrap=1000,
                         **plotargs)
    handles, labels = ax.get_legend_handles_labels()
    # if ylim[1] is None:
    #     ymax = max(flat(boxplot[0]))*1.1
    # else:
    #     ymax = ylim[1]
    # ymin = ylim[0]
    # ax.set_ylim(bottom=ymin, top=ymax)
    # ax.set_xlim(left=min(boxplot[1]), right=max(boxplot[1]))
    return ax, handles


def plot_histo(ax, data, labels, colormap, ylim, stacked=False, rwidth=.8,
               step=None, bwidth=.9, bins='auto', brange=None, tails=False,
               ylog=False, density=False, **kwargs):
    """adds histo plots to ax and returns ax and handles for legend"""
    nlab = len(labels)
    for i in range(len(data)):
        if i >= nlab:
            labels.append("series{:02d}".format(i))
    try:
        inc = 1./(len(data)-1)
    except ZeroDivisionError:
        inc = 1
    c = [colormap.to_rgba(i*inc) for i in range(len(data))]
    if brange and tails:
        data = [np.clip(np.array(y), brange[0], brange[1]) for y in data]
    plotargs = {'linewidth': 0}
    plotargs.update(kwargs)
    histo = plt.hist(data, bins=bins, log=ylog, range=brange, label=labels,
                     color=c, rwidth=rwidth, stacked=stacked, density=density, **plotargs)
    handles, labels = ax.get_legend_handles_labels()
    if ylim[1] is None:
        ymax = max(flat(histo[0]))*1.1
    else:
        ymax = ylim[1]
    ymin = ylim[0]
    ax.set_ylim(bottom=ymin, top=ymax)
    ax.set_xlim(left=min(histo[1]), right=max(histo[1]))
    return ax, handles


def dayhour(mo, day, ho=0, hpd=24, dpy=365, sh=0):
    """returns hour of year (no DST)"""
    # return daycount[mo-1]*24+(day-1)*24+ho
    return hpd*daycount[mo-1]*dpy/365. + hpd*(day-1)*dpy/365. + ho*hpd/24.


def shift_data(data, pph=1, sa=(3, 10), fb=(11, 2), hpd=24, dpy=365, sh=0):
    """
    shift annual data for DST for correct hour axis on heatmap

    Parameters
    ----------
    data: list
        length 8760*pph
    pph: int
        data points per hour in data.
    sa: tuple of ints
        (month, day) for spring ahead
    fb: tuple of ints
        (month, day) for fall back

    Returns
    -------
    data2: list
        data with 2AM on "spring ahead" duplicated and 1AM on "fall back"
        deleted
    """
    spr = int(dayhour(*sa, ho=2, hpd=hpd, dpy=dpy, sh=sh))*pph
    fal = int(dayhour(*fb, ho=1, hpd=hpd, dpy=dpy, sh=sh))*pph
    if hpd != 24:
        spr = spr - spr % hpd + hpd
        fal = fal - fal % hpd + hpd
    data2 = data[:spr] + data[spr:spr+pph] + data[spr:fal] + data[fal+pph:]
    return data2


def get_tick_distribution(data, divisions):
    """
    returns values demarcating equal size bins on data

    Parameters
    ----------
    data: list
        list of float values
    divisions: int
        number of divisions to make (cannot exceed len(data))

    Returns
    -------
    ticks: list
        values from data at each division point
    """
    binsize = 100./divisions
    bins = np.arange(binsize, 100.+binsize, binsize)
    df = flat(data)
    dmin = min(df)
    dmax = max(df) 
    ticks = np.percentile([i for i in df if i > 0], bins)
    ticks = [int(round(i)) for i in ticks]
    return ticks


def flat(l):
    """flattens any depth iterable (except strings)"""
    a = []
    try:
        if type(l) != str:
            for i in l:
                a += flat(i)
        else:
            a.append(l)
    except Exception:
        a.append(l)
    return a


def pad_scale(data, n=8760, mult=1, missing=0.0):
    """scale and pad data returns numpy.array"""
    data = np.array(data)*mult
    if len(data) < n:
        missing = np.ones(n-len(data))*missing
        data = np.concatenate((data, missing))
    elif len(data) > n:
        data = data[:n]
    return data


def ticks_x_annual(ax, fg='black', dpy=365):
    """set xaxis to days in year with month labels"""
    ax.xaxis.set_ticks([i*dpy/365.0 for i in daycount[1:]])
    monthlabel = [(i+15)*dpy/365.0 for i in daycount]
    ax.set_xticks(monthlabel, minor=True)
    ax.set_xticklabels(
        labels=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        size=8, minor=True, color=fg)
    ax.set_xticklabels(labels=[])
    for t in ax.xaxis.get_ticklines(minor=True):
        t.set_visible(False)
    for t in ax.xaxis.get_ticklines():
        t.set_visible(False)
    ax.xaxis.set_tick_params(length=2.5)
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlim([0, dpy])
    ax.axes.set_xlabel("Month", weight="bold", size=9, color=fg)
    return ax


def ticks_y_day(ax, tcol='black', pph=1, hpd=24, sh=0):
    """set yaxis to hours in day"""
    hlabels = ['12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM',
               '7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM',
               '2PM', '3PM', '4PM', '5PM', '6PM', '7PM', '8PM', '9PM',
               '10PM', '11PM']
    ax.set_yticks(np.arange(0, hpd*pph, pph)+pph*0.5, minor=True)
    ax.set_yticks(np.arange(1, hpd*pph, pph), minor=False)
    ax.set_yticklabels(hlabels[sh:sh+hpd], size=8, minor=True, color=tcol)
    ax.set_yticklabels(labels=[])
    ax.yaxis.set_ticks_position('left')
    ax.set_ylim([hpd*pph, 0])
    ax.axes.set_ylabel("Hour", weight="bold", size=9, color=tcol)
    return ax


def ticks_y_per(ax, ydata, tickdiv, tcol="black"):
    """label y axis according to percentile of data with pery bins"""
    tickinc = 100./tickdiv
    ticks = get_tick_distribution(ydata, tickdiv)
    ax.yaxis.set_ticks(ticks)
    yticklabels = []
    for i in range(len(ticks)):
        yticklabels.append("{0} ({1:.0f}%)".format(ticks[i], (i+1)*tickinc))
    ax.set_yticklabels(labels=yticklabels, size=7, color=tcol)
    return ax


class CliptColors(object):
    """class containing custom clipt colors"""

    def __getitem__(self, key):
        return self.cdict[key]

    def __init__(self):
        self.cdict255 = {
            'blu': [(23, 55, 93), (31, 73, 125),
                    (83, 142, 213), (141, 180, 227)],
            'org': [(151, 72, 7), (228, 109, 10),
                    (255, 153, 0), (250, 192, 144)],
            'pur': [(120, 0, 204), (180, 102, 255),
                    (204, 153, 255), (204, 192, 218)],
            'red': [(171, 21, 21), (204, 51, 0),
                    (255, 0, 0), (217, 151, 149)],
            'blg': [(33, 88, 103), (49, 132, 155),
                    (147, 205, 221), (181, 221, 232)],
            'mag': [(153, 0, 153), (204, 51, 153),
                    (255, 51, 153), (255, 153, 204)],
            'brn': [(74, 69, 42), (148, 139, 84),
                    (197, 190, 151), (221, 217, 195)],
            'grn': [(36, 140, 83), (0, 176, 80),
                    (146, 208, 80), (149, 253, 35)],
            'yel': [(188, 184, 0), (216, 220, 40),
                    (255, 255, 0), (255, 255, 153)],
            'ggr': [(79, 98, 40), (117, 146, 60),
                    (194, 214, 154), (215, 228, 188)]
        }
        self.cdict = {}
        for k, v in self.cdict255.iteritems():
            self.cdict[k] = [tuple(i/255. for i in j) for j in v]
        self.colors = ['blu', 'org', 'pur', 'red', 'blg',
                       'mag', 'brn', 'grn', 'yel', 'ggr']
        self.clist = [self.cdict[i] for i in self.colors]
        self.clist255 = [self.cdict255[i] for i in self.colors]
        self.shades = ['dark', 'med', 'light', 'xlight']
        for i, v in enumerate(self.shades):
            self.cdict[v] = [j[i] for j in self.clist]
            self.cdict255[v] = [j[i] for j in self.clist255]


def cmap_from_list(cmap, step=None, positions=None, name='custom'):
    """return colormap from list of colors"""
    try:
        if max(flat(cmap)) > 1:
            cmap = [tuple(i/255. for i in j) for j in cmap]
        if positions is not None and len(cmap) > 1:
            cmap = [(i, j) for i, j in zip(positions, cmap)]
            name += "_pos"
        if len(cmap) == 1:
            cmap.append(cmap[0])
        colorm = colors.LinearSegmentedColormap.from_list(name, cmap)
    except Exception:
        raise ValueError('cmap_from_list expected list of color tuples')
    norm = colors.Normalize(vmin=0, vmax=1)
    colormap = cmx.ScalarMappable(cmap=colorm, norm=norm)
    if step is not None:
        cmap2 = []
        cmap2.append((0, colormap.to_rgba(0)))
        pinc = 1/float(step-1)
        inc = 1/float(step)
        for i in range(step):
            t = i*inc
            t1 = min((i+1)*inc, 1)
            cmap2.append((t, colormap.to_rgba(i*pinc)))
            cmap2.append((t1, colormap.to_rgba(i*pinc)))
        name += "_step"
        colorm = colors.LinearSegmentedColormap.from_list(name, cmap2)
        colormap = cmx.ScalarMappable(cmap=colorm, norm=norm)
    return colormap


def cmap_tune(colormap, step=None, positions=None, name='custom'):
    if positions is not None:
        cmap2 = []
        pos2 = []
        for i, p in enumerate(positions):
            inc = i/float(len(positions)-1)
            cmap2.append(colormap.to_rgba(p))
            pos2.append(inc)
        colormap = cmap_from_list(cmap2, None, pos2, name)
    if step is not None:
        cmap2 = []
        for i in range(step):
            inc = i/float(step-1)
            cmap2.append(colormap.to_rgba(inc))
        colormap = cmap_from_list(cmap2, step, None, name)
    return colormap


def cmap_from_mpl(cmap, step=None, positions=None):
    """return colormap from matplotlib colormaps"""
    norm = colors.Normalize(vmin=0, vmax=1)
    colormap = cmx.ScalarMappable(cmap=cmap, norm=norm)
    colormap = cmap_tune(colormap, step, positions, cmap)
    return colormap


def cmap_from_clipt(cmap, step=None, positions=None):
    """return colormap from CliptColors key"""
    clcol = CliptColors()
    try:
        clist = clcol[cmap]
    except Exception:
        clopts = ", ".join(clcol.cdict.keys())
        note = "Additional clipt colors values:"
        message = "{}\n\n{}".format(note, clopts)
        raise ValueError(message)
    else:
        colorm = colors.LinearSegmentedColormap.from_list(cmap, clist)
        norm = colors.Normalize(vmin=0, vmax=1)
        colormap = cmx.ScalarMappable(cmap=colorm, norm=norm)
        colormap = cmap_tune(colormap, step, positions, cmap)
    return colormap


def get_nth(li, i):
    """if i < len(l) returns l[i] else l[-1]"""
    try:
        return li[min(i, len(li)-1)]
    except Exception:
        return li


def get_nth_loop(li, i):
    """returns l[i % len(l)]"""
    try:
        return li[i % len(li)]
    except Exception:
        return li
