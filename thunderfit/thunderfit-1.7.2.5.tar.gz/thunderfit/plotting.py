import logging
import matplotlib.pyplot as plt
import matplotlib
from numpy import ndarray, full
matplotlib.use('TkAgg')

"""
These functions all plot slightly different things, in future these will be combined into one or two functions and cleaned up
for now they are fairly self explanatory so no details docstrings added
"""

# todo fix the assertions in these


def plot_data(x, y, fig=False, ax=False, line='r-', linethickness=0.5):
    """
    quick funtion to plot the data
    :param x:
    :param y:
    :param fig:
    :param ax:
    :param line:
    :param linethickness:
    :return:
    """
    logging.debug('plotting data')
    if ax:
        # assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
        " an axes object"
    else:
        fig, ax = plt.subplots()

    ax.plot(x, y, line, linewidth=linethickness, alpha=0.5)
    return ax, plt, fig


def plot_fits(x, peaks, fig=False, ax=False, linethickness=0.5):
    logging.debug('plotting fits')
    if ax:
        # assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
        " an axes object"
    else:
        fig, ax = plt.subplots()

    for peak in peaks.values():
        if isinstance(peak, ndarray):
            ax.plot(x, peak, linewidth=linethickness)
        elif isinstance(peak, float) or isinstance(peak, int):
            ax.plot(x, full(x.shape, peak), linewidth=linethickness)

    return ax, plt, fig


def plot_background(
        x,
        background_data,
        fig=False,
        ax=False,
        line='b--',
        linethickness=0.5):
    logging.debug('plotting bg')
    if ax:
        # assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
        " an axes object"
    else:
        fig, ax = plt.subplots()

    ax.plot(x, background_data, line, linewidth=linethickness)
    return ax, plt, fig


# option of including background
def plot_fit_sum(
        x,
        peak_sum,
        background,
        fig=False,
        ax=False,
        line='k-',
        linethickness=0.5):
    logging.debug('plotting fit sum')
    if ax:
        # assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
        " an axes object"
    else:
        fig, ax = plt.subplots()

    sum = peak_sum + background

    ax.plot(x, sum, line, linewidth=linethickness)
    return ax, plt, fig


def plot_uncertainty_curve(
        x,
        eval_unc,
        peak_sum,
        fig=False,
        ax=False,
        color="#ABABAB"):
    logging.debug('plotting fit uncertainty curve')
    if ax:
        # assert isinstance(ax, axes._subplots.AxesSubplot), "the figure passed isn't the correct format, please pass" \
        " an axes object"
    else:
        fig, ax = plt.subplots()

    ax.fill_between(x, peak_sum - eval_unc, peak_sum + eval_unc,
                    color=color)  # plot a grey band of uncertainty

    return ax, plt, fig
