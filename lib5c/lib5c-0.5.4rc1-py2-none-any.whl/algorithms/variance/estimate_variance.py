import numpy as np

from lib5c.algorithms.variance.local import local_variance
from lib5c.algorithms.variance.deviation import deviation_variance
from lib5c.algorithms.variance.cross_rep import cross_rep_variance
from lib5c.algorithms.variance.mle import mle_variance
from lib5c.algorithms.variance.combined import cross_rep_plus_deviation_variance
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance as lognorm_disp_to_var
from lib5c.algorithms.variance.nbinom_dispersion import \
    dispersion_to_variance as nbinom_disp_to_var
from lib5c.util.counts import flatten_and_filter_counts, \
    unflatten_counts_from_list
from lib5c.util.lowess import lowess_fit, group_fit, constant_fit


def estimate_variance(obs_counts, exp_counts, key_rep=None, model='lognorm',
                      source='deviation', source_kwargs=None, fitter='lowess',
                      fitter_agg='lowess', fitter_kwargs=None, x_unit='dist',
                      y_unit='disp', logx=False, logy=False, min_disp=1e-8,
                      min_obs=2, min_dist=6, regional=False):
    """
    Convenience function for computing variance estimates.

    Parameters
    ----------
    obs_counts : dict of np.ndarray or dict of dict of np.ndarray
        Counts dict of observed values (keys are region names, values are square
        symmetric matrices), or superdict (outer keys are replicate names, inner
        keys are region names, values are square symmetric matrices) if
        ``source='cross_rep'``.
    exp_counts : dict of np.ndarray
        Counts dict of expected values.
    key_rep : str
        If ``obs_counts`` is a dict of dict of np.ndarray, pass a string naming
        the specific replicate to compute variance estimates for.
    model : {'lognorm', 'loglogistic', 'nbinom', 'poisson'}
        Statistical model to use.
    source : {'local', 'cross_rep', 'deviation', 'mle'}
        Specify the source of the variance estimates.
    source_kwargs : dict
        Kwargs to pass through to the variance source function.
    fitter : {'constant', 'group', 'lowess', 'none'}
        Select fitting method to use for trend fitting. Pass 'none' to skip
        trend fitting and simply return unfiltered point-wise estimates.
    fitter_agg : {'median', 'mean', 'lowess'}
        If ``fitter`` is 'group' or 'constant', select what function to use to
        aggregate values (within groups for group fitting or across the whole
        dataset for constant fitting).
    fitter_kwargs : dict
        Kwargs to pass through to the fitting function.
    x_unit : {'dist', 'exp'}
        The x-unit to fit the variance relationship against.
    y_unit : {'disp', 'var'}
        The y-unit to fit the variance relationship against. When
        ``model='nbinom'``, "disp" refers to the negative binomial dispersion
        parameter. When ``model='lognorm'``, "disp" refers to the variance
        parameter of the normal distribution describing the logarithm of the
        observed counts.
    logx, logy : bool
        Pass True to fit the variance relationship on the scale of ``log(x)``
        and/or ``log(y)``.
    min_disp : float
        When ``model='nbinom'``, this sets the minimum value of the negative
        binomial dispersion parameter. When ``model='lognormal'``, this sets the
        minimum value of the variance of logged observed counts.
    min_obs : float
        Points with observed values below this threshold in any replicate will
        be excluded from MLE estimation and relationship fitting.
    min_dist : int
        Points with interaction distances (in bin units) below this threshold
        will be excluded from MLE estimation and relationship fitting.
    regional : bool
        Pass True to perform MLE estimation and relationship fitting on a
        per-region basis.

    Returns
    -------
    dict of np.ndarray
        The variance estimates as a counts dict.
    """
    # short circuit for regional
    if regional:
        regions = exp_counts.keys()
        reshaped_obs = {region: {rep: {region: obs_counts[rep][region]}
                                 for rep in obs_counts.keys()}
                        for region in regions} if source == 'cross_rep' \
            else {region: {region: obs_counts[region]} for region in regions}
        reshaped_exp = {region: {region: exp_counts[region]}
                        for region in regions}
        return {
            region: estimate_variance(
                reshaped_obs[region], reshaped_exp[region], key_rep=key_rep,
                model=model, source=source, source_kwargs=source_kwargs,
                fitter=fitter, fitter_agg=fitter_agg,
                fitter_kwargs=fitter_kwargs, x_unit=x_unit, y_unit=y_unit,
                logx=logx, logy=logy, min_disp=min_disp, min_obs=min_obs,
                min_dist=min_dist, regional=False)[region]
            for region in regions
        }

    # short circuit for poisson
    if model == 'poisson':
        return exp_counts

    # short circuit for MLE
    if source == 'mle':
        return mle_variance(obs_counts, exp_counts, model=model,
                            min_obs=min_obs, min_dist=min_dist, **source_kwargs)

    # pixel-wise estimates
    var_fn = {
        'local': local_variance,
        'deviation': deviation_variance,
        'cross_rep': cross_rep_variance,
        'cross_rep_plus_deviation': cross_rep_plus_deviation_variance
    }
    args = (obs_counts, exp_counts) if source == 'deviation' \
        else ({region: {rep: obs_counts[rep][region] for rep in obs_counts}
               for region in obs_counts.values()[0]},) if source == 'cross_rep'\
        else ({region: {rep: obs_counts[rep][region] for rep in obs_counts}
               for region in obs_counts.values()[0]}, exp_counts, key_rep)\
        if source == 'cross_rep_plus_deviation' else (obs_counts,)
    mean, disp, var, idx_od = \
        var_fn[source](*args, model=model, min_disp=min_disp,
                       **source_kwargs if source_kwargs else {})

    # flatten and filter
    counts_types = {
        'mean': mean,
        'disp': disp,
        'var': var,
        'idx_od': idx_od,
        'exp': exp_counts
    }
    min_filters = {'dist': min_dist, 'exp': 0.01}
    if 'cross_rep' in source:
        for rep in obs_counts:
            counts_types[rep] = obs_counts[rep]
            min_filters[rep] = min_obs
    else:
        counts_types['obs'] = obs_counts
        min_filters['obs'] = min_obs

    flattened_counts, idx, region_order = \
        flatten_and_filter_counts(counts_types, min_filters=min_filters)

    # if no fitting was requested we're done
    if fitter == 'none':
        var = np.tile(np.nan, idx.shape)
        var[idx] = flattened_counts['var']
        return unflatten_counts_from_list(var, region_order, exp_counts)

    # fit
    fit_fn = {
        'group': group_fit,
        'lowess': lowess_fit,
        'constant': constant_fit
    }
    fitter_kwargs = fitter_kwargs if fitter_kwargs else {}
    if fitter in ['group', 'constant']:
        fitter_kwargs['agg'] = fitter_agg
    fit = fit_fn[fitter](flattened_counts[x_unit], flattened_counts[y_unit],
                         logx=logx, logy=logy,
                         **fitter_kwargs if fitter_kwargs else {})

    # re-flatten, excluding mean, disp, var
    del counts_types['var']
    del counts_types['disp']
    del counts_types['mean']
    flattened_counts, idx, region_order = \
        flatten_and_filter_counts(counts_types, min_filters=min_filters)

    # apply fit and convert disp to var if necessary
    disp_to_var = {
        'nbinom': nbinom_disp_to_var,
        'lognorm': lognorm_disp_to_var,
        'loglogistic': lognorm_disp_to_var
    }
    y_hat = fit(flattened_counts[x_unit])
    var = np.tile(np.nan, idx.shape)
    if y_unit == 'disp' and model in disp_to_var:
        var[idx] = disp_to_var[model](y_hat, flattened_counts['exp'])
    else:
        # no implementation for conversion implies that disp = var
        # even if y_unit is disp
        var[idx] = y_hat

    return unflatten_counts_from_list(var, region_order, exp_counts)
