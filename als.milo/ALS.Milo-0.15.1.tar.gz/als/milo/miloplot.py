#!/usr/bin/python

"""miloplot.py

    *) Default plots for both scatter and time series
    *) Customizable options can be provided
"""

__author__ = "Padraic Shafer"
__copyright__ = "Copyright (c) 2014-2019, Padraic Shafer"
__credits__ = [__author__, ]
__license__ = ""
__maintainer__ = "Padraic Shafer"
__email__ = "PShafer@lbl.gov"
__status__ = "Development"

from als.milo import __version__, __date__

import scipy
from numpy import pi, cos, sin, deg2rad, nan
from numpy import array, empty, matrix, newaxis, zeros, arange
from numpy import cross, dot, linspace, outer, sum, product, mean
from numpy import roots, square, sqrt, isfinite
from numpy import logical_and, logical_or, any, all, unique
from numpy import append
from numpy.linalg import norm, solve, lstsq, tensorsolve
from astropy.io import fits
from sys import exit
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib as mpl
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, num2date
from matplotlib.ticker import FuncFormatter
from datetime import datetime, date
import pandas as pd



#---------------------------------------------------------------------------
# FUNCTIONS
#---------------------------------------------------------------------------
def std_datetime_formatter(d, pos=None):
    """Formats time axis of pyplot using actual date+time

        *) Returns label to be displayed on time axis
    """
    dt = num2date(d)
    if (pos == 0):
        fmt = "%b. %d %H:%M"
    elif (dt.strftime("%H") == "00"):
        fmt = "%b. %d %H:%M"
    elif (int(dt.strftime("%H")) < 4):
        fmt = "%b. %d %H:%M"
    else:
        fmt = "%H:%M"
    label = dt.strftime(fmt)
    return label

def anon_datetime_formatter(d, pos=None, start=datetime(1970, 1, 1) ):
    """Formats time axis of pyplot using relative date+time

        *) Returns label to be displayed on time axis
    """
    dt = num2date(d)
    dt = dt.replace(tzinfo=None)
    dt_diff = dt - start
    days = 1 + dt_diff.days
    hours = dt_diff.seconds / 3600
    mins = (dt_diff.seconds % 3600) / 60
    secs = (dt_diff.seconds % 60) + dt_diff.microseconds
    if (pos == 0):
        label = "[ Day {0:0d} ] {1:2d} hrs".format(days, hours)
    elif (hours == 0):
        label = "[ Day {0:0d} ] {1:2d} hrs".format(days, hours)
    elif (hours < 4):
        label = "[ Day {0:0d} ] {1:2d} hrs".format(days, hours)
    else:
        label = "{1:2d} hrs".format(days, hours)
    return label

def anondate_datetime_formatter(d, pos=None, start=datetime(1970, 1, 1) ):
    """Formats time axis of pyplot using relative date + actual time

        *) Returns label to be displayed on time axis
    """
    dt = num2date(d)
    # dt = dt.replace(tzinfo=None)
    days = 1 + dt.toordinal() - start.toordinal()
    if (pos == 0):
        label = "[ Day {0:0d} ] ".format(days)
    elif (dt.strftime("%H") == "00"):
        label = "[ Day {0:0d} ] ".format(days)
    elif (int(dt.strftime("%H")) < 4):
        label = "[ Day {0:0d} ] ".format(days)
    else:
        label = ""
    label += dt.strftime("%H:%M")
    return label

def relative_mins_formatter(d, pos=None, start=datetime(1970, 1, 1) ):
    """Formats time axis of pyplot using relative date+time in minutes

        *) Returns label to be displayed on time axis
    """
    dt = num2date(d)
    dt = dt.replace(tzinfo=None)
    dt_diff = dt - start
    days = 1 + dt_diff.days
    hours = dt_diff.seconds / 3600
    mins = (dt_diff.seconds % 3600) / 60
    secs = (dt_diff.seconds % 60) + dt_diff.microseconds
    if (pos == 0):
        label = "[ Day {0:0d} ] {1:2d} min".format(days, mins)
    elif (hours == 0):
        label = "[ Day {0:0d} ] {1:2d} min".format(days, mins)
    elif (hours < 4):
        label = "[ Day {0:0d} ] {1:2d} min".format(days, mins)
    else:
        label = "{1:2d} min".format(days, hours)
    return label

#---------------------------------------------------------------------------
def make_plot_curve(**kwargs):
    """Generate a dict of curve params for the plot_XXXXX() functions

        *) User-supplied keywords override default paramaters
        *) Returns a dict of curve params for the plot_XXXXX() functions
    """

    dict_plot_curve = dict({
        "df": None,		# PANDAS dataframe
        "x_col": "",	# str name of column for abcissa (X, horizontal axis)
        "y_col": "",	# str name of column for ordinate (Y, vertical axis)
        "z_col": "",	# str name of column for intensity (Z, "color" axis)
        "label": "",
        })

    for (key, value) in kwargs.iteritems():
        dict_plot_curve[key] = value

    return(dict_plot_curve)

#---------------------------------------------------------------------------
def make_plot_params(**kwargs):
    """Generate a dict of options for the plot_XXXXX() functions

        *) User-supplied keywords override default paramaters
        *) Returns a dict of options for the plot_XXXXX() functions
    """

    dict_plot_params = dict({
        "colors": ['b','g','k'],
        "legend_loc": 0,
        "title": "",
        "xlabel": "",
        "ylabel": "",
        "xlim": None,
        "ylim": None,
        "clim": None,
        "hlines": array([]),
        "vlines": array([]),
        "fig_size": (12, 8),
        "filename": None,
        "hide": False,	# Set to True to not display the plot
        "clear": True,	# Set to False to leave previous figure in plot
        "vs_time": False,	# True: plot vs. date+time; False: plot vs. index
        })

    for (key, value) in kwargs.iteritems():
        dict_plot_params[key] = value

    return(dict_plot_params)

#---------------------------------------------------------------------------
def plot_scatter(
        curve_array = array([]),
        plot_options = make_plot_params()
        ):
    """Generates a scatter plot of supplied curves

        *) curve_array: array of curve 'dict's; see make_plot_curve()
        *) plot_options: dict of plotting options; see make_plot_params()
        *) Returns current (figure, axis)
    """

    mpl.rcParams.update({'font.size': 22})
    if plot_options["clear"]:
        plt.clf()

    [plt.plot(
        curve["df"][curve["x_col"] ],
        curve["df"][curve["y_col"] ],
        # plot_options["colors"][i % len(plot_options["colors"])],
        color=plot_options["colors"][i % len(plot_options["colors"])],
        linewidth=2,
        label=curve["label"],
        ) for (i, curve) in enumerate(curve_array)]
    plt.legend(frameon=False, loc=plot_options["legend_loc"])

    # plt.gcf().autofmt_xdate()
    # date_plot_format = DateFormatter("%m/%d %H:%M")
    # date_plot_format = FuncFormatter(anondate_datetime_formatter)
    # date_plot_format = FuncFormatter(std_datetime_formatter)
    fig = plt.gcf()
    ax = fig.gca()
    # ax.xaxis.set_major_formatter(date_plot_format)
    # ax.xaxis.set_major_locator(HourLocator(interval=4))
    # ax.xaxis.set_minor_locator(HourLocator())

    plt.title(plot_options["title"])
    plt.xlabel(plot_options["xlabel"])
    plt.ylabel(plot_options["ylabel"])
    if plot_options["xlim"]:
        plt.xlim(plot_options["xlim"])
    if plot_options["ylim"]:
        plt.ylim(plot_options["ylim"])
    [plt.axhline(
        value, color='k', ls='--') for value in plot_options["hlines"] ]
    [plt.axvline(
        value, color='k', ls='--') for value in plot_options["vlines"] ]
    #ax.autoscale_view()
    # plt.plot(time_endpoints, [50, 50], 'g--')
    # plt.plot(time_endpoints, [30, 30], 'c--')
    # plt.plot(time_endpoints, [10, 10], 'k--')
    # plt.plot(time_endpoints, [0, 0], 'k--')
    fig.set_size_inches(plot_options["fig_size"])

    if plot_options["filename"]:
        plt.savefig(plot_options["filename"])

    if not plot_options["hide"]:
        plt.show()

    return(fig, ax)

#---------------------------------------------------------------------------
def plot_history(
        curve_array = array([]),
        plot_options = make_plot_params()
        ):
    """Generates a "time" plot of supplied curves

        *) curve_array: array of curve 'dict's; see make_plot_curve()
        *) plot_options: dict of plotting options; see make_plot_params()
        *) Returns current (figure, axis)
    """

    mpl.rcParams.update({'font.size': 22})
    if plot_options["clear"]:
        plt.clf()

    if 	plot_options["vs_time"]:
        [plt.plot(
            curve["df"][curve["x_col"] ].tolist(),
            curve["df"][curve["y_col"] ],
            plot_options["colors"][i % len(plot_options["colors"])],
            linewidth=2,
            label=curve["label"],
            ) for (i, curve) in enumerate(curve_array)]
    else:
        [plt.plot(
            curve["df"].index.tolist(),
            curve["df"][curve["y_col"] ],
            plot_options["colors"][i % len(plot_options["colors"])],
            linewidth=2,
            label=curve["label"],
            ) for (i, curve) in enumerate(curve_array)]
        plt.gcf().autofmt_xdate()
    plt.legend(frameon=False, loc=plot_options["legend_loc"])

    fig = plt.gcf()
    ax = fig.gca()

    if 	plot_options["vs_time"]:
        def elapsed_mins_formatter(d, pos=None):
            return relative_mins_formatter(d, pos,
                start=curve["df"].loc[0, curve["x_col"] ])

        fig.autofmt_xdate()
        # date_plot_format = FuncFormatter("%m/%d %H:%M")
        # date_plot_format = FuncFormatter(anondate_datetime_formatter)
        # date_plot_format = FuncFormatter(std_datetime_formatter)
        date_plot_format = FuncFormatter(elapsed_mins_formatter)

        ax.xaxis.set_major_formatter(date_plot_format)
        ax.xaxis.set_major_locator(HourLocator(interval=4))
        ax.xaxis.set_minor_locator(HourLocator())

    plt.title(plot_options["title"])
    plt.xlabel(plot_options["xlabel"])
    plt.ylabel(plot_options["ylabel"])
    if plot_options["xlim"]:
        plt.xlim(plot_options["xlim"])
    if plot_options["ylim"]:
        plt.ylim(plot_options["ylim"])
    [plt.axhline(
        value, color='k', ls='--') for value in plot_options["hlines"] ]
    [plt.axvline(
        value, color='k', ls='--') for value in plot_options["vlines"] ]
    #ax.autoscale_view()
    # plt.plot(time_endpoints, [50, 50], 'g--')
    # plt.plot(time_endpoints, [30, 30], 'c--')
    # plt.plot(time_endpoints, [10, 10], 'k--')
    # plt.plot(time_endpoints, [0, 0], 'k--')
    fig.set_size_inches(plot_options["fig_size"])

    if plot_options["filename"]:
        plt.savefig(plot_options["filename"])

    if not plot_options["hide"]:
        plt.show()

    return(fig, ax)

#---------------------------------------------------------------------------
def plot_points2D(
        curve_array = array([]),
        plot_options = make_plot_params()
        ):
    """Generates a scatter plot of supplied curves

        *) curve_array: array of curve 'dict's; see make_plot_curve()
        *) plot_options: dict of plotting options; see make_plot_params()
        *) Returns current (figure, axis)
    """

    mpl.rcParams.update({'font.size': 22})
    if plot_options["clear"]:
        plt.clf()

    cm = plt.get_cmap()
    scalarMap = cmx.ScalarMappable(cmap=cm)
    def get_intensity_cmap(
            intensity_values = array([])
            ):
        scalarMap.set_array(intensity_values)
        scalarMap.autoscale()
        cm = scalarMap.get_cmap()
        # print scalarMap.get_clim()

    cm_array = [get_intensity_cmap(curve["df"][curve["z_col"] ])
        for curve in curve_array]

    [plt.scatter(
        x = curve["df"][curve["x_col"] ],
        y = curve["df"][curve["y_col"] ],
        c = curve["df"][curve["z_col"] ],
        s=4,
        cmap = cm_array[i],
        edgecolors='none',
        # label=curve["label"],
        ) for (i, curve) in enumerate(curve_array)]
    # plt.legend(frameon=False, loc=plot_options["legend_loc"])

    # plt.gcf().autofmt_xdate()
    # date_plot_format = DateFormatter("%m/%d %H:%M")
    # date_plot_format = FuncFormatter(anondate_datetime_formatter)
    # date_plot_format = FuncFormatter(std_datetime_formatter)
    fig = plt.gcf()
    ax = fig.gca()
    # ax.xaxis.set_major_formatter(date_plot_format)
    # ax.xaxis.set_major_locator(HourLocator(interval=4))
    # ax.xaxis.set_minor_locator(HourLocator())

    plt.title(plot_options["title"])
    plt.xlabel(plot_options["xlabel"])
    plt.ylabel(plot_options["ylabel"])
    if plot_options["xlim"]:
        plt.xlim(plot_options["xlim"])
    if plot_options["ylim"]:
        plt.ylim(plot_options["ylim"])
    if plot_options["clim"]:
        plt.clim(plot_options["clim"])
    [plt.axhline(
        value, color='k', ls='--') for value in plot_options["hlines"] ]
    [plt.axvline(
        value, color='k', ls='--') for value in plot_options["vlines"] ]
    #ax.autoscale_view()
    # plt.plot(time_endpoints, [50, 50], 'g--')
    # plt.plot(time_endpoints, [30, 30], 'c--')
    # plt.plot(time_endpoints, [10, 10], 'k--')
    # plt.plot(time_endpoints, [0, 0], 'k--')
    fig.set_size_inches(plot_options["fig_size"])

    if plot_options["filename"]:
        plt.savefig(plot_options["filename"])

    if not plot_options["hide"]:
        plt.show()

    return(fig, ax)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN body
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    plot_scatter(
        array([
            make_plot_curve(**{
                "df": data_by_avgLoop.xs(z_value, level=z_col),
                "x_col": field_col,
                # "y_col": diff_tey_norm0,
                "y_col": tey_norm0_asym,
                "label": "Z = {0:3.1f} mm".format(z_value),
                }),
            ]),
        make_plot_params(**{
            "title": "CD vs. Field\n",
            "xlabel": "Magnetic Field [ T ]",
            "ylabel": "Circular Difference [ a.u. ]\n",
            "fig_size": (12, 24),
            "filename": "{0:s}field-loops_{1:5d}{2:s}_avg.pdf".format(
                output_path,
                traj_base_num,
                input_postfix,
                ),
            "clear": False,
            "hide": True,
            })
        )

    exit()
