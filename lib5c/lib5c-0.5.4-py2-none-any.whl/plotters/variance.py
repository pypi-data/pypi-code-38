"""
Module for plotting mean-variance relationships.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from lib5c.util.counts import flatten_obs_and_exp, flatten_obs_and_exp_counts
from lib5c.util.grouping import group_obs_by_exp
from lib5c.util.plotting import plotter
from lib5c.util.parallelization import parallelize_regions
from lib5c.plotters.scatter import scatter as plot_scatter


@plotter
def plot_mvr(exp, var, obs=None, num_groups=100, group_fractional_tolerance=0.1,
             exclude_offdiagonals=5, log=False, logx=False, logy=False,
             vst=False, scatter=False, hexbin=False, trim_limits=False,
             xlim=None, ylim=None, **kwargs):
    """
    Plots a scatterplot of exp vs var.

    Optionally, pass obs to instead scatterplot exp vs freshly re-estimated
    group variances, and overlay exp vs var as a smooth curve.

    Parameters
    ----------
    exp : np.ndarray or dict of np.ndarray
        Regional matrix of expected values. Pass a counts dict to combine all
        regions together.
    var : np.ndarray or dict of np.ndarray
        Regional matrix of variances. Pass a counts dict to combine all regions
        together.
    obs : np.ndarray or dict of np.ndarray, optional
        Regional matrix of observed values. Pass a counts dict to combine all
        regions together.
    num_groups : int
        The number of groups to re-esimtate group variances for.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    exclude_offdiagonals : int
        Exclude this many off-diagonals from the variance re-estimation. Pass 0
        to exclude only the exact diagonal. Pass -1 to exclude nothing.
    log : bool
        Pass True to log both exp and var.
    logx, logy : bool
        Pass True to draw the x- and/or y-axis on a log-scale.
    vst : bool
        Pass True to log only the exp (e.g., when var is already stabilized).
    scatter : bool
        Pass True to force plotting exp vs var as a scatterplot when obs is not
        passed. By default it will be a line plot.
    hexbin : bool
        Pass True when ``scatter=True`` to replace the scatterplot with a hexbin
        plot.
    trim_limits : bool
        If `obs` is passed, pass True to trim the x- and y-limits to the range
        of the group expected and variance values.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # prepare data for plotting
    exp, var, sort_idx, raw_exps, raw_vars = prepare_exp_var_for_plotting(
        exp, var, obs=obs, num_groups=num_groups,
        group_fractional_tolerance=group_fractional_tolerance,
        exclude_offdiagonals=exclude_offdiagonals, log=log, vst=vst)

    # plot
    if obs is None:
        if scatter:
            plot_scatter(exp, var, logx=logx, logy=logy, hexbin=hexbin,
                         xlim=xlim, ylim=ylim)
        else:
            plt.plot(exp[sort_idx], var[sort_idx], color='r')
    else:
        plt.scatter(raw_exps, raw_vars, color='b')
        plt.plot(exp[sort_idx], var[sort_idx], color='r')

        if trim_limits:
            plt.xlim(np.min(raw_exps), np.max(raw_exps))
            plt.ylim(np.min(raw_vars), np.max(raw_vars))
    if logx:
        plt.gca().set_xscale('log')
    if logy:
        plt.gca().set_yscale('log')


plot_mvr_parallel = parallelize_regions(plot_mvr)


@plotter
def plot_overlay_mvr(exp, var, obs=None, num_groups=100,
                     group_fractional_tolerance=0.1, exclude_offdiagonals=5,
                     log=False, logx=False, logy=False, vst=False,
                     scatter=False, scatter_colors=None, line_colors=None,
                     legend='outside', **kwargs):
    """
    Plots a comparison of mean-variance relationships across regions.

    Parameters
    ----------
    exp : dict of np.ndarray
        Counts dict of expected values.
    var : dict of np.ndarray
        Counts dict of variance values.
    obs : dict of np.ndarray, optional
        Counts dict of observed values.
    num_groups : int
        The number of groups to re-esimtate group variances for.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    exclude_offdiagonals : int
        Exclude this many off-diagonals from the variance re-estimation. Pass 0
        to exclude only the exact diagonal. Pass -1 to exclude nothing.
    log : bool
        Pass True to log both exp and var.
    logx, logy : bool
        Pass True to draw the x- and/or y-axis on a log-scale.
    vst : bool
        Pass True to log only the exp (e.g., when var is already stabilized).
    scatter : bool
        Pass True to force plotting exp vs var as a scatterplot when obs is not
        passed. By default it will be a line plot.
    scatter_colors, line_colors : str or dict of str, optional
        Mapping from region names to the color to use for that region. Pass None
        to use randomly assigned colors. Pass a single string to use the same
        color for all regions.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    pyplot axis
        The axis plotted on.
    """
    # prepare data for plotting
    exp, var, sort_idx, raw_exps, raw_vars = \
        prepare_exp_var_for_plotting_parallel(
            exp, var, obs=obs, num_groups=num_groups,
            group_fractional_tolerance=group_fractional_tolerance,
            exclude_offdiagonals=exclude_offdiagonals, log=log, vst=vst)

    # resolve colors
    regions = sorted(exp.keys())
    palette = sns.color_palette('husl', len(regions))
    default_colors = {regions[i]: palette[i] for i in range(len(regions))}
    if scatter_colors is None:
        scatter_colors = default_colors
    elif type(scatter_colors) == str:
        scatter_colors = {region: scatter_colors for region in regions}
    if line_colors is None:
        line_colors = default_colors
    elif type(line_colors) == str:
        line_colors = {region: line_colors for region in regions}

    # plot
    if obs is None:
        if scatter:
            for region in regions:
                plt.scatter(exp[region], var[region],
                            color=scatter_colors[region], label=region)
        else:
            for region in regions:
                plt.plot(exp[region][sort_idx[region]],
                         var[region][sort_idx[region]],
                         color=line_colors[region], label=region)
    else:
        for region in regions:
            plt.scatter(raw_exps[region], raw_vars[region],
                        color=scatter_colors[region], label='%s data' % region)
        for region in regions:
            plt.plot(exp[region][sort_idx[region]],
                     var[region][sort_idx[region]],
                     color=line_colors[region], label='%s mvr' % region)
    if logx:
        plt.gca().set_xscale('log')
    if logy:
        plt.gca().set_yscale('log')


def prepare_exp_var_for_plotting(exp, var, obs=None, num_groups=100,
                                 group_fractional_tolerance=0.1,
                                 exclude_offdiagonals=5, log=False, vst=False):
    """
    Prepares expected value and variance data for plotting.

    Parameters
    ----------
    exp : np.ndarray or dict of np.ndarray
        Regional matrix of expected values. Pass a counts dict to combine all
        regions together.
    var : np.ndarray or dict of np.ndarray
        Regional matrix of variances. Pass a counts dict to combine all regions
        together.
    obs : np.ndarray or dict of np.ndarray, optional
        Regional matrix of observed values. Pass a counts dict to combine all
        regions together.
    num_groups : int
        The number of groups to re-esimtate group variances for.
    group_fractional_tolerance : float
        The width of each group, specified as a fractional tolerance in the
        expected value.
    exclude_offdiagonals : int
        Exclude this many off-diagonals from the variance re-estimation. Pass 0
        to exclude only the exact diagonal. Pass -1 to exclude nothing.
    log : bool
        Pass True to log both exp and var.
    vst : bool
        Pass True to log only the exp (e.g., when var is already stabilized).

    Returns
    -------
    tuple of np.ndarray
        The first and second elements are parallel arrays of the exp, var pairs.
        The third element is a sort index into the exp, var pairs. The fourth
        and fifth elements are None if obs was not passed. If obs was passed,
        they are parallel arrays of raw obs, raw var pairs.
    """
    # prepare raw exp, var pairs if obs was passed
    if obs is not None:
        raw_exps, groups = group_obs_by_exp(
            obs, exp,
            num_groups=num_groups,
            group_fractional_tolerance=group_fractional_tolerance,
            exclude_offdiagonals=exclude_offdiagonals)
        if vst:
            raw_exps = np.log(raw_exps + 1)
            raw_vars = np.array([np.nanvar(np.log(group + 1))
                                 for group in groups])
        else:
            raw_vars = np.array([np.nanvar(group) for group in groups])
        if log:
            raw_exps = np.log(raw_exps + 1)
            raw_vars = np.log(raw_vars + 1)
    else:
        raw_exps = None
        raw_vars = None

    # prepare exp, var pairs
    if type(exp) == dict:
        exp, var = flatten_obs_and_exp_counts(exp, var, log=log)
    else:
        exp, var = flatten_obs_and_exp(exp, var, log=log)
    if vst:
        exp = np.log(exp + 1)

    # compute sort index for exp/var pairs
    sort_idx = np.argsort(exp)

    return exp, var, sort_idx, raw_exps, raw_vars


prepare_exp_var_for_plotting_parallel = parallelize_regions(
    prepare_exp_var_for_plotting)
