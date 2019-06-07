"""
Module for plotting bias heatmaps.
"""

import numpy as np
import scipy.stats as stats
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from lib5c.plotters.asymmetric_colormap import shifted_colormap
from lib5c.plotters.colormaps import get_colormap
from lib5c.util.mathematics import gmean
from lib5c.util.stratification import conservative_qcut
from lib5c.util.plotting import plotter


@plotter
def plot_bias_heatmap(obs_counts, exp_counts, primermap, factor, bins=None,
                      n_bins=None, cmap=None, vmin=None, vmax=None,
                      midpoint=None, log=True, region=None, agg=gmean,
                      asymmetric=False, print_variance=False, shuffle=0,
                      zero_inflated=False, unique=False, despine=False,
                      style='dark', dpi=300, **kwargs):
    """
    Plots a bias heatmap.

    Parameters
    ----------
    obs_counts : Dict[str, np.ndarray]
        The dict of observed counts.
    exp_counts : Dict[str, np.ndarray]
        The dict of expected counts.
    primermap : Dict[str, List[Dict[str, Any]]]
        Primermap or pixelmap describing the loci in ``obs_counts`` and
        ``exp_counts``.
    factor : str
        The bias factor to draw the bias heatmap for. This string must match a
        metadata key in ``primermap``. That is to say, if ``factor`` is
        ``'length'`` then we expect ``primermap[region][i]['length']`` to be a
        number representing the length of the ``i`` th fragment in the region
        specified by ``region``.
    bins : Optional[Sequence[numeric]]
        The endpoints of the bins to use to stratify the bias factor values.
        Either ``bins`` or ``n_bins`` must be specified.
    n_bins : Optional[int]
        The number of even-number bins to use to stratify the bias factor
        values. Either ``bins`` or ``n_bins`` must be specified.
    cmap : Optional[matplotlib.colors.Colormap]
        Pass a colormap to use for the heatmap. If this kwarg is not passed, the
        default 'bias' colormap is used.
    vmin : Optional[float]
        The minimum value to use for the heatmap. If this kwarg is not passed,
        the min of the data will be used.
    vmax : Optional[float]
        The maximum value to use for the heatmap. If this kwarg is not passed,
        the max of the data will be used.
    midpoint : Optional[float]
        The midpoint value to use for the colormap. If this kwarg is not passed,
        the colormap will be symmetric about its midpoint. This kwarg can be
        used to force the midpoint of the colormap to lie at a desired value,
        such as 0.
    log : bool
        Whether or not to show log-scale fold-enrichments in the heatmap.
    region : Optional[str]
        Pass a region name as a string to consider only the contacts in one
        particular region. If this kwarg is not passed, contacts for all regions
        in the input counts dicts will be used to generate the bias heatmap.
    agg : Callable[[np.ndarray], float]
        The aggregation function to use when summarizing the strata. This
        function should take in an array of floats and return a single summary
        value.
    asymmetric : bool
        Pass True to construct heatmaps using only the upper-triangular elements
        of the counts matrices, which can lead to asymmetric heatmaps. By
        default, the algorithm iterates over all elements of the counts
        matrices, enforcing symmetry in the bias models but incurring some
        redundancy in the actual counts information.
    print_variance : bool
        If True, the variance of the bias across the stratification grid will be
        printed in the plot title.
    shuffle : int
        Specify a number of random permutation null hypothesis simulations to
        perform.
    zero_inflated : bool
        Pass True here to treat the bias factor as "zero inflated", which will
        cause all the zero values to land in a dedicated "zero stratum" and
        allocate the remaining bins evenly among the positive data. This kwarg
        is ignored if the bins are passed explicitly.
    unique : bool
        Pass True to override `bins` and `n_bins` and simply put each unique
        value of the bias factor into its own stratum.
    dpi : int
        DPI to save figure at if auto-saving to a raster format.
    kwargs : kwargs
        Typical plotter kwargs.

    Returns
    -------
    Tuple[pyplot axis, float]
        The first element is the pyplot axis plotted on, which will always be
        present. The second element is the variance of the enrichment with
        respect to the bias factor grid. The third element is the percentile
        value for this variance obtained from simulations under the null
        hypothesis. The fourth element is the 95% RI for the null hypothesis.
        These last three will be nan if no simulations were performed.

    Notes
    -----
    The simulations were a cool idea, but in reality the 95% null hypothesis RI
    is incredibly small since it is very unlikely to see any enrichment at all
    if the obs and exp counts are forcibly de-correlated from the bias factors.
    Therefore the recommendation is to not simulate unless you're really sure
    you want it.
    """
    # resolve cmap
    if cmap is None:
        cmap = get_colormap('bias')

    # resolve regions
    regions = obs_counts.keys()
    if region is not None:
        regions = [region]

    # make dataframe
    list_of_dict = []
    for region in regions:
        for i in range(len(obs_counts[region])):
            if asymmetric:
                jrange = range(i + 1)
            else:
                jrange = range(len(obs_counts[region]))
            for j in jrange:
                if np.isfinite(obs_counts[region][i, j]):
                    list_of_dict.append(
                        {'upstream_factor'  : primermap[region][j][factor],
                         'downstream_factor': primermap[region][i][factor],
                         'obs'              : obs_counts[region][i, j],
                         'exp'              : exp_counts[region][i, j]})
    df = pd.DataFrame(list_of_dict)

    # cut/qcut
    if unique or bins is not None:
        if unique:
            bins = np.unique(df.upstream_factor)
            bins = np.concatenate([[bins[0] - 0.001], bins])
        df['Upstream %s' % factor] = pd.cut(df.upstream_factor, bins)
        df['Downstream %s' % factor] = pd.cut(df.downstream_factor, bins)
    elif n_bins is not None:
        if zero_inflated:
            bins = conservative_qcut(df.upstream_factor, n_bins)
            df['Upstream %s' % factor] = pd.cut(df.upstream_factor, bins)
            df['Downstream %s' % factor] = pd.cut(df.downstream_factor, bins)
        else:
            df['Upstream %s' % factor] = pd.qcut(df.upstream_factor, n_bins)
            df['Downstream %s' % factor] = pd.qcut(df.downstream_factor, n_bins)
    else:
        raise ValueError('must pass bins or n_bins, or set unique=True')

    # stratify and aggregate
    plot_df = _group_and_agg(df, factor, agg, log)

    # compute variance
    variance = np.var(
        plot_df.values[np.tril(np.ones_like(plot_df.values, dtype=bool))],
        ddof=1)

    # simulate variance
    simulated_variances = []
    for i in range(shuffle):
        # shuffle
        permutation = np.random.permutation(len(df))
        df.ix[:, 'obs'] = df['obs'][permutation].reset_index(drop=True)
        df.ix[:, 'exp'] = df['exp'][permutation].reset_index(drop=True)

        # stratify and aggregate
        temp_df = _group_and_agg(df, factor, agg, log)

        # compute variance
        simulated_variances.append(np.var(
            temp_df.values[np.tril(np.ones_like(temp_df.values, dtype=bool))],
            ddof=1))
    if simulated_variances:
        simulated_variance_percentile = stats.percentileofscore(
            simulated_variances, variance, kind='strict')
        variance_95_ri = np.percentile(simulated_variances, 95)
    else:
        simulated_variance_percentile = np.nan
        variance_95_ri = np.nan

    # prepare cmap
    if midpoint is not None:
        cmap = shifted_colormap(cmap, midpoint=midpoint)

    # plot
    with sns.plotting_context(context='paper'):
        plt.clf()
        sns.heatmap(plot_df, square=True, cmap=cmap, vmin=vmin, vmax=vmax,
                    cbar_kws={'ticks': [vmin, vmax]})
        plt.yticks(rotation=0)
        plt.xticks(rotation=45, ha='right')
        if print_variance:
            if np.isfinite(simulated_variance_percentile):
                plt.title('Variance: %g (%.1f%%, 95%% H_0 RI = %g)' %
                          (float(variance), simulated_variance_percentile,
                           variance_95_ri))
            else:
                plt.title('Variance: %g' % float(variance))

    return variance, simulated_variance_percentile, variance_95_ri


def _group_and_agg(df, factor, agg=gmean, log=True):
    # prepare plotting dataframe
    plot_df = (df.groupby(['Upstream %s' % factor,
                           'Downstream %s' % factor])['obs']
               .agg(lambda x: agg(x)) /
               df.groupby(['Upstream %s' % factor,
                           'Downstream %s' % factor])['exp']
               .agg(lambda x: agg(x))).unstack().iloc[::-1]
    if log:
        plot_df = np.log2(plot_df)

    return plot_df
