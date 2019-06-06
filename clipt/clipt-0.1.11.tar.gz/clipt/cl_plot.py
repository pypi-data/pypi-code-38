# Copyright (c) 2018 Stephen Wasilewski
# =======================================================================
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# =======================================================================

"""console script for graphing data."""

from __future__ import print_function

from clasp import click
import matplotlib.colors as mplc

import clasp.click_ext as clk

from clipt import get_root, __version__
import clasp.script_tools as mgr
import clipt.plot as ruplot


@click.group()
@clk.shared_decs(clk.main_decs(__version__))
def main(ctx, config, outconfig, configalias, inputalias):
    """help configuration and process management commands."""
    template = get_root() + "/templates/master.cfg"
    clk.get_config(ctx, config, outconfig, configalias, inputalias, template)


# used by all
shared = [
          click.option('-drange', callback=clk.split_int,
                       help="index range for data series, if None gets all"),
          click.option('--ticklines/--no-ticklines', default=False,
                       help="plot tick lines"),
          click.option('--areaonly/--no-areaonly', default=False,
                       help="only plot plot area, no legend or axes, for use "
                       "as background"),
          click.option('-fg', default="black",
                       help="foreground color"),
          click.option('-bg', default="white",
                       help="background color"),
          click.option('--legend/--no-legend', default=True,
                       help="include legend in plot"),
          click.option('-colors', default='med',
                       callback=clk.color_inp,
                       help="cmap name* or space seperated list of rgb tuples "
                       "0,0,0 120,120,120 etc. if fewer than # series picks ."
                       "from gradient includes ru_colors: 'blu', 'org', 'pur'"
                       ", 'red', 'blg', 'mag', 'brn', 'grn', 'yel', 'ggr', "
                       "'dark', 'med', 'light', 'xlight'"),
          click.option('-comment', default='#',
                       help='regex "^[{}].*" indicating comment line '
                       'indicator'),
          click.option('-positions', default=None,
                       callback=clk.split_float,
                       help="if cmap is a list positions are the mapping "
                       "points else positions are the sample points used to "
                       "remap"),
          click.option('-step', default=None, type=int,
                       help="steps for color map"),
          click.option('-labelweight', default='bold', type=click.Choice(['ultralight', 'light', 'normal', 'regular', 'book', 'medium', 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black']),
                       help="text weight for axes labels"),
          click.option('-width', default=10.5, type=float,
                       help="image width"),
          click.option('-height', default=5.0, type=float,
                       help="image height"),
          click.option('-dpi', default=200, type=int,
                       help="image dpi"),
          click.option('-background', type=click.Path(exists=True),
                       help="background image for graph area"),
          click.option('-alpha', type=float, default=.5,
                       help="transparency for background"),
          click.option('--front/--no-front', default=False,
                       help="plot background in front of data"),
          click.option('--opts', '-opts', is_flag=True,
                       help="check parsed options"),
          click.option('--debug', is_flag=True,
                       help="show traceback on exceptions"),
          click.option('-outf',
                       help="graph output file (defaults to basename of first "
                       "dataf)"),
          click.option('--weatherfile/--no-weatherfile', default=False,
                       help="input files will be read as weather files: "
                       "0 month, 1 day, 2 hour, 3 dirnorn, 4 difhoriz, 5 "
                       "globhoriz, 6 skycover")
]


# used by bar, scatter, histo
sharedA = [
           click.option('-fcol', default=0.0, type=float,
                        help="colormap position for first color"),
           click.option('--xgrid/--no-xgrid', default=False,
                        help="plot x grid lines"),
           click.option('--ygrid/--no-ygrid', default=False,
                        help="plot y grid lines"),
           click.option('-yticks', type=int,
                        help="number of y-ticks/gridlines"),
           click.option('-xticks', type=int,
                        help="number of x-ticks/gridlines"),
           click.option('--polar/--no-polar', default=False,
                        help="plot on polar axes"),
           click.option('-labels', callback=clk.split_str,
                        help="input custom series labels, by default uses "
                        "file name and index or --header option"),
           click.option('--rows/--no-rows', default=False,
                        help="get data rows instead of columns"),
           click.option('-ecolors', default="1,1,1", callback=clk.color_inp,
                        help="marker edge colors"),
           click.option('-epositions', default=None,
                        callback=clk.split_float,
                        help="if cmap is a list positions are the mapping "
                        "pointselse positions are the sample points used to "
                        "remap"),
           click.option('-estep', default=None, type=int,
                        help="steps for color map"),
           click.option('--ylog/--no-ylog', default=False,
                        help="plot y on log scale"),
           click.option('--header/--no-header', default=False,
                        help="indicates that data has a header row to get "
                        "series labels (overridden by labels)"),
           click.option('-bottom', type=float, default=0.0,
                        help="use with polar to set bottom of y-axis same "
                        "units as axes")
]


# used by scatter, heatmap
sharedB = [
]


@main.command('bar')
@click.argument('dataf', callback=clk.are_files)
@click.option('-rwidth', default=0.95, type=float,
              help="relative width of bar clusters")
@click.option('-bwidth', default=.8, type=float,
              help="relative width of bars")
@click.option('--stacked/--no-stacked', default=False,
              help="make stacked bars")
@click.option('-ew', default="0", callback=clk.split_float,
              help="bar edge width")
@click.option('-brng', default="0 1", callback=clk.split_float,
              help="range within axes limits that bars are plotted")
@click.option('--polar0/--no-polar0', default=True,
              help="plot center of first bar at xmin")
@click.option('--polarauto/--no-polarauto', default=True,
              help="ignore x-axis min,max and plot 0-360")
@click.option('-y_vals', default="-1", callback=clk.split_int,
              help="index for yvals")
@click.option('-axes', default="X,0,10,Y,0,ymax",
              help="enter as xname,xmin,xmax,yname,ymin,ymax - default uses"
              "min and max of data enter xmin etc to maintain autoscale")
@click.option('-xlabels', callback=clk.split_str,
              help="input custom xaxis labels, by default uses file name and"
              "row number or --xheader option")
@click.option('--xheader/--no-xheader', default=False,
              help="indicates that data has a header column to get x-axis "
              "labels (overridden by xlabels)")
@clk.shared_decs(shared + sharedA)
@click.pass_context
def bar(ctx, dataf, **kwargs):
    '''
    dataf should be a tsv or csv with the following format: xaxis label,
    series1 ,series2, etc.. category1, 0,0,... category2, 0,0,... etc...,...

    arguments:

    * dataf: data file to plot
    '''
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(dataf, **kwargs)
    else:
        try:
            axext = ruplot.get_axes(kwargs['axes'], [], [], kwargs['polar'],
                                    kwargs['polarauto'])
            a1 = mgr.kwarg_match(mgr.read_data, kwargs)
            a1['autox'] = axext['xdata']
            xs, ys, labels = mgr.read_all_data(dataf, **a1)
            if kwargs['xheader']:
                a1['y_vals'] = [0]
                a1['x_vals'] = []
                a1['coerce'] = False
                a1['xheader'] = False
                a1['rows'] = False
                _, xlabels, _ = mgr.read_data(dataf[0], **a1)
                xlabels = xlabels[0]
            else:
                xlabels = []
            xlabels = ruplot.get_labels(xlabels, kwargs['xlabels'])
            labels = ruplot.get_labels(labels, kwargs['labels'])
            if kwargs['rows']:
                la = labels
                labels = xlabels
                xlabels = la
            a3 = mgr.kwarg_match(ruplot.plot_setup, kwargs)
            ax, fig = ruplot.plot_setup(**a3)
            a4 = mgr.kwarg_match(ruplot.ticks, kwargs)
            a4.pop('labels', None)
            a4['xlabels'] = xlabels
            ax = ruplot.tick_from_arg(ax, xs, ys, a4, kwargs)
            a5 = mgr.kwarg_match(ruplot.get_colors, kwargs)
            cmap = ruplot.get_colors(kwargs['colors'], **a5)
            a5['positions'] = kwargs['epositions']
            a5['step'] = kwargs['estep']
            emap = ruplot.get_colors(kwargs['ecolors'], **a5)
            a6 = mgr.kwarg_match(ruplot.plot_bar, kwargs)
            a6['emap'] = emap
            a6.pop('labels', None)
            ax, handles = ruplot.plot_bar(ax, xs, ys, labels, cmap, **a6)
            if kwargs['outf']:
                outf = kwargs['outf']
            else:
                outf = dataf[0].rsplit(".", 1)[0] + ".png"
            a7 = mgr.kwarg_match(ruplot.plot_graph, kwargs)
            ruplot.plot_graph(fig, outf, handles=handles, **a7)
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'bar', kwargs, ctx


@main.command('heatmap')
@click.argument('dataf', callback=clk.is_file)
@click.option('-pph', default=1, type=int,
              help="data points per hour in annual data")
@click.option('-hpd', default=24, type=int,
              help="hours per day (y axis shape)")
@click.option('-dpy', default=365, type=int,
              help="days per year (x axis shape)")
@click.option('-sh', default=0, type=int,
              help="start hour (24 hour time)")
@click.option('-plotidx', default=-1, type=int,
              help="column idx of data to plot")
@click.option('-vmax', type=float,
              help="scale max")
@click.option('-vmin', type=float,
              help="scale max")
@click.option('-lw', default=.5, type=float,
              help="lineweight of grid around cells (try .5)")
@click.option('-gridc', default=.5, type=float,
              help="opacity of gridlines (color is bg)")
@click.option('--dst/--no-dst', default=False,
              help="shift data for DST")
@click.option('-labels', callback=clk.split_str,
              help="labels for legend")
@click.option('-ticks', callback=clk.split_float,
              help="locations for legend labels (must be same # of items)")
@clk.shared_decs(shared + sharedB)
@click.pass_context
def heatmap(ctx, dataf, **kwargs):
    '''def plot_heatmap(fig, ax, data, colormap, vmin=None, vmax=None,
                 DST=False, ticks=None, labels=None, **kwargs)'''
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(dataf, **kwargs)
    else:
        try:
            if (dataf.split('.')[-1] in ['epw', 'wea'] and
                kwargs['comment'] == '#'):
                kwargs['comment'] = '^\-\d'
            y_vals = [kwargs['plotidx']]
            _, ys, _ = mgr.read_data(dataf, y_vals=y_vals,
                                     comment=kwargs['comment'],
                                     autox=(0, kwargs['dpy']),
                                     weatherfile=kwargs['weatherfile'])
            a3 = mgr.kwarg_match(ruplot.plot_setup, kwargs)
            ax, fig = ruplot.plot_setup(**a3)
            a4 = mgr.kwarg_match(ruplot.ticks, kwargs)
            a4.pop('labels', None)
            ax = ruplot.ticks(ax, annualx=True, dayy=True, **a4)
            a5 = mgr.kwarg_match(ruplot.get_colors, kwargs)
            colormap = ruplot.get_colors(kwargs['colors'], **a5)
            a6 = mgr.kwarg_match(ruplot.plot_heatmap, kwargs)
            a6['legend'] = a6['legend'] and not kwargs['areaonly']
            edgecolor = list(mplc.to_rgba(kwargs['bg']))
            edgecolor[3] = kwargs['gridc']
            a6.update({'lw': kwargs['lw'], 'edgecolors': edgecolor})
            ax = ruplot.plot_heatmap(fig, ax, ys[0], colormap, **a6)
            if kwargs['outf']:
                outf = kwargs['outf']
            else:
                outf = dataf.rsplit(".", 1)[0] + ".png"
            a7 = mgr.kwarg_match(ruplot.plot_graph, kwargs)
            ruplot.plot_graph(fig, outf, **a7)
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'heatmap', kwargs, ctx


@main.command('histo')
@click.argument('dataf', callback=clk.are_files)
@click.option('-y_vals', default="-1", callback=clk.tup_int,
              help="index for yvals")
@click.option('-axes', default="X,0,1,Y,0,ymax",
              help="enter as xname,xmin,xmax,yname,ymin,ymax - default uses"
              "min and max of data enter xmin etc to maintain autoscale")
@click.option('-bins', default=None, callback=clk.split_float,
              help="bins can be 'auto' an integer or a sequence"
              "1 2 3 4:12:2 14:16 = 1,2,3,4,6,8,10,14,15")
@click.option('-autobin', default='auto',
              help="see numpy.histogram_bin_edges for options"
              "1 2 3 4:12:2 14:16 = 1,2,3,4,6,8,10,14,15")
@click.option('-brange', default=None, callback=clk.split_float,
              help="defaults to min and max")
@click.option('--tails/--no-tails', default=False,
              help="include values below and above range in first and last bin"
              "(requires -brange)")
@click.option('-rwidth', default=0.95, type=float,
              help="relative width of bars")
@click.option('-bwidth', default=.8, type=float,
              help="relative width of bars")
@click.option('--stacked/--no-stacked', default=False,
              help="make stacked bars")
@click.option('--density/--no-density', default=False,
              help="plot as probability density (area sums to 1)")
@click.option('-xlabels', callback=clk.split_str,
              help="input custom xaxis labels, by default uses file name and"
              "row number or --xheader option")
@click.option('--xheader/--no-xheader', default=False,
              help="indicates that data has a header column to get x-axis "
              "labels (overridden by xlabels)")
@clk.shared_decs(shared + sharedA)
@click.pass_context
def histo(ctx, dataf, **kwargs):
    '''
    plot histogram bar plot
'''
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(dataf, **kwargs)
    else:
        try:
            axext = ruplot.get_axes(kwargs['axes'], [], [])
            a1 = mgr.kwarg_match(mgr.read_data, kwargs)
            a1['autox'] = axext['xdata']
            xs, ys, labels = mgr.read_all_data(dataf, **a1)
            if kwargs['xheader']:
                a1['y_vals'] = [0]
                a1['x_vals'] = []
                a1['coerce'] = False
                a1['xheader'] = False
                a1['rows'] = False
                _, xlabels, _ = mgr.read_data(dataf[0], **a1)
                xlabels = xlabels[0]
            else:
                xlabels = []
            xlabels = ruplot.get_labels(xlabels, kwargs['xlabels'])
            labels = ruplot.get_labels(labels, kwargs['labels'])
            if kwargs['rows']:
                la = labels
                labels = xlabels
                xlabels = la
            a3 = mgr.kwarg_match(ruplot.plot_setup, kwargs)
            ax, fig = ruplot.plot_setup(**a3)
            a4 = mgr.kwarg_match(ruplot.ticks, kwargs)
            a4.pop('labels', None)
            a4['xlabels'] = xlabels
            ax = ruplot.tick_from_arg(ax, xs, ys, a4, kwargs)
            a5 = mgr.kwarg_match(ruplot.get_colors, kwargs)
            cmap = ruplot.get_colors(kwargs['colors'], **a5)
            a6 = mgr.kwarg_match(ruplot.plot_histo, kwargs)
            a6.pop('labels', None)
            if kwargs['bins'] is None:
                a6['bins'] = kwargs['autobin']
            elif len(kwargs['bins']) == 1:
                a6['bins'] = int(kwargs['bins'][0])
            ax, handles = ruplot.plot_histo(ax, ys, labels, cmap,
                                            axext['ydata'], **a6)
            if kwargs['outf']:
                outf = kwargs['outf']
            else:
                outf = dataf[0].rsplit(".", 1)[0] + ".png"
            a7 = mgr.kwarg_match(ruplot.plot_graph, kwargs)
            ruplot.plot_graph(fig, outf, handles=handles, **a7)
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'histo', kwargs, ctx


@main.command('scatter')
@click.argument('dataf', callback=clk.are_files)
@click.option('-autox', default=None,
              callback=clk.split_float,
              help="auto assign xvals between min,max from axes")
@click.option('-weax', default=None, callback=clk.split_int,
              help="use months as x-axis (8760 data) give idx for month and"
              "day ex: 1 2 for epw 0 1 for wea"
              "when using --weatherfile use 0 1 for both")
@click.option('-x_vals', default="0,0",
              callback=clk.tup_int, help="index for xvals")
@click.option('-y_vals', default="-1", callback=clk.tup_int,
              help="index for yvals")
@click.option('-c_vals', default=None, callback=clk.tup_int,
              help="optional index for color vals, only uses 1 index")
@click.option('-cmax', type=float,
              help="scale max for color")
@click.option('-cmin', type=float,
              help="scale min for color")
@click.option('--flipxy/--no-flipxy', default=False,
              help="plot x on vertical axis")
@click.option('--polarauto/--no-polarauto', default=True,
              help="ignore x-axis min,max and plot 0-360")
@click.option('-axes', default="X,xmin,xmax,Y,ymin,ymax",
              help="enter as xname,xmin,xmax,yname,ymin,ymax - default uses"
              "min and max of data enter xmin etc to maintain autoscale")
@click.option('--xlog/--no-xlog', default=False,
              help="plot x on log scale")
@click.option('-pery', default=None, type=int,
              help="label y-axis by percentile with N bins")
@click.option('--reverse/--no-reverse', default=False,
              help="reverse order of y data (sometimes useful with -autox)")
@click.option('-ms', default="0", callback=clk.split_float,
              help="marker size if fewer than # series uses last")
@click.option('-mew', default="0", callback=clk.split_float,
              help="marker edge width")
@click.option('-mrk', default='o', callback=clk.split_str,
              help="marker style if fewer than # series loops")
@click.option('-criteria',
              help="plot markers based on criteria (either x=VAL or y=VAL)"
              "assumes single solution")
@click.option('-lw', default="2", callback=clk.split_float,
              help="line weight if fewer than # series uses last")
@clk.shared_decs(shared + sharedA + sharedB)
@click.pass_context
def scatter(ctx, dataf, **kwargs):
    '''arguments for x_vals and y_vals are a space seperated list of indices or
    index pairs. A single number is applied to all files, a comma seperated
    pair: i,j gets the jth column from the ith file. if a tuple x_val is given
    all y_data will share, else x will be index value from each file.  for
    y_val entry a single number will grab from all files, a comma pair gets one
    column of data.  use the argument -rows to get data by rows instead.'''
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(dataf, **kwargs)
    else:
        try:
            a1 = mgr.kwarg_match(mgr.read_data, kwargs)
            if kwargs['weax'] is not None:
                a1['x_vals'] = [0]
            xs, ys, labels = mgr.read_all_data(dataf, **a1)
            if kwargs['c_vals'] is not None:
                a1['y_vals'] = kwargs['c_vals']
                cs = mgr.read_all_data(dataf, **a1)[1]
            else:
                cs = None
            labels = ruplot.get_labels(labels, kwargs['labels'])
            a3 = mgr.kwarg_match(ruplot.plot_setup, kwargs)
            ax, fig = ruplot.plot_setup(**a3)
            a4 = mgr.kwarg_match(ruplot.ticks, kwargs)
            a4.pop('labels', None)
            ax = ruplot.tick_from_arg(ax, xs, ys, a4, kwargs)
            a5 = mgr.kwarg_match(ruplot.get_colors, kwargs)
            cmap = ruplot.get_colors(kwargs['colors'], **a5)
            a5['positions'] = kwargs['epositions']
            a5['step'] = kwargs['estep']
            emap = ruplot.get_colors(kwargs['ecolors'], **a5)
            a6 = mgr.kwarg_match(ruplot.plot_scatter, kwargs)
            a6.pop('labels', None)
            ax, handles = ruplot.plot_scatter(ax, xs, ys, labels, cmap,
                                              emap=emap, cs=cs, **a6)
            if kwargs['outf']:
                outf = kwargs['outf']
            else:
                outf = dataf[0].rsplit(".", 1)[0] + ".png"
            a7 = mgr.kwarg_match(ruplot.plot_graph, kwargs)
            ruplot.plot_graph(fig, outf, handles=handles, **a7)
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'scatter', kwargs, ctx


@main.command('box')
@click.argument('dataf', callback=clk.are_files)
@click.option('-y_vals', default="-1", callback=clk.tup_int,
              help="index for yvals")
@click.option('-axes', default="X,0,1,Y,0,ymax",
              help="enter as xname,xmin,xmax,yname,ymin,ymax - default uses"
              "min and max of data enter xmin etc to maintain autoscale")
@click.option('-rwidth', default=0.95, type=float,
              help="relative width of bars")
@click.option('-xlabels', callback=clk.split_str,
              help="input custom xaxis labels, by default uses file name and"
              "row number or --xheader option")
@click.option('--xheader/--no-xheader', default=False,
              help="indicates that data has a header column to get x-axis "
              "labels (overridden by xlabels)")
@clk.shared_decs(shared + sharedA)
def box(dataf, **kwargs):
    """
    create boxplot from data files.

    """
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(arg1, **kwargs)
    else:
        try:
            axext = ruplot.get_axes(kwargs['axes'], [], [])
            a1 = mgr.kwarg_match(mgr.read_data, kwargs)
            a1['autox'] = axext['xdata']
            xs, ys, labels = mgr.read_all_data(dataf, **a1)
            if kwargs['xheader']:
                a1['y_vals'] = [0]
                a1['x_vals'] = []
                a1['coerce'] = False
                a1['xheader'] = False
                a1['rows'] = False
                _, xlabels, _ = mgr.read_data(dataf[0], **a1)
                xlabels = xlabels[0]
            else:
                xlabels = []
            xlabels = ruplot.get_labels(xlabels, kwargs['xlabels'])
            labels = ruplot.get_labels(labels, kwargs['labels'])
            if kwargs['rows']:
                la = labels
                labels = xlabels
                xlabels = la
            a3 = mgr.kwarg_match(ruplot.plot_setup, kwargs)
            ax, fig = ruplot.plot_setup(**a3)
            a4 = mgr.kwarg_match(ruplot.ticks, kwargs)
            a4.pop('labels', None)
            a4['xlabels'] = xlabels
            ax = ruplot.tick_from_arg(ax, xs, ys, a4, kwargs)
            a5 = mgr.kwarg_match(ruplot.get_colors, kwargs)
            cmap = ruplot.get_colors(kwargs['colors'], **a5)
            a6 = mgr.kwarg_match(ruplot.plot_box, kwargs)
            a6.pop('labels', None)
            ax, handles = ruplot.plot_box(ax, ys, labels, cmap,
                                            axext['ydata'], **a6)
            if kwargs['outf']:
                outf = kwargs['outf']
            else:
                outf = dataf[0].rsplit(".", 1)[0] + ".png"
            a7 = mgr.kwarg_match(ruplot.plot_graph, kwargs)
            ruplot.plot_graph(fig, outf, handles=handles, **a7)
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'box', kwargs


@main.command('colors')
@click.option('-outf',
              help="output file")
@click.option('--ru/--mat', default=True,
              help="plot radutil colors (--mat plots matplotlib)")
@click.option('--rgb/--no-tgb', default=True,
              help="print rgb values for radutil")
@click.option('--radf/--no-radf', default=False,
              help="print rgb values on 0-1 scale")
@click.option('--opts', '-opts', is_flag=True,
              help="check parsed options")
@click.option('--debug', is_flag=True,
              help="show traceback on exceptions")
def colors(**kwargs):
    """
    create plot color palettes and formatted rgbs
    """
    if kwargs['opts']:
        kwargs['opts'] = False
        clk.echo_args(**kwargs)
    else:
        try:
            if kwargs['outf'] is not None:
                fig = ruplot.plot_cmaps(kwargs['ru'])
                ruplot.plot_graph(fig, kwargs['outf'], width=5, height=10)
            else:
                click.echo("specify -outf to generate image", err=True)
            if kwargs['rgb'] and kwargs['ru']:
                rucol = ruplot.CliptColors()
                click.echo("      " + "".join(["{: <13}".format(i)
                                               for i in rucol.shades]))
                for k in rucol.colors:
                    v = rucol.cdict255[k]
                    fmt = [",".join(["{:03d}".format(j) for j in i])
                           for i in v]
                    click.echo("{}:  {}".format(k, "  ".join(fmt)))
                click.echo("\n         " + "".join(["{: <13}".format(i)
                                                    for i in rucol.colors]))
                for k in rucol.shades:
                    v = rucol.cdict255[k]
                    fmt = [",".join(["{:03d}".format(j) for j in i])
                           for i in v]
                    click.echo("{: >6}:  {}".format(k, "  ".join(fmt)))
                if kwargs['radf']:
                    click.echo("      " + "".join(["{: <28}".format(i)
                                                   for i in rucol.shades]))
                    for k in rucol.colors:
                        v = rucol.cdict255[k]
                        fmt = [" ".join(["{:06f}".format(j/255.**2.2)
                                         for j in i]) for i in v]
                        click.echo("{}:  {}".format(k, "  ".join(fmt)))
        except click.Abort:
            raise
        except Exception as ex:
            clk.print_except(ex, kwargs['debug'])
    return 'box', kwargs


@main.resultcallback()
@click.pass_context
def printconfig(ctx, opts, **kwargs):
    """callback to save config file"""
    try:
        clk.tmp_clean(opts[2])
    except Exception:
        pass
    if kwargs['outconfig']:
        clk.print_config(ctx, opts, kwargs['outconfig'], kwargs['config'],
                         kwargs['configalias'])
