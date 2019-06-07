from lib5c.util.parallelization import parallelize_regions
from lib5c.algorithms.variance.deviation import deviation_variance
from lib5c.algorithms.variance.cross_rep import cross_rep_variance
from lib5c.algorithms.variance.lognorm_dispersion import \
    dispersion_to_variance_direct


@parallelize_regions
def cross_rep_plus_deviation_variance(obs, exp, rep, model='lognorm',
                                      min_disp=1e-8):
    """
    Estimates pixel-wise variance as the squared deviation between observed and
    expected values.

    Parameters
    ----------
    obs : dict or list of np.ndarray
        Dict values or list entries are are square, symmetric count matrices
        across replicates.
    exp : np.ndarray
        Square, symmetric matrix of expected values.
    rep : int or str
        The index into ``obs`` identifying which replicate to compute variance
        estimates for.
    model : {'lognorm', 'norm'}
        Statistical model to use.
    min_disp : float
        Force a minimum value of the dispersion parameter.

    Returns
    -------
    tuple of np.ndarray
        The first three elements are the mean parameter estimate, dispersion
        estimate, and variance estimate, respectively, for each pixel. The
        fourth element is a boolean matrix showing which pixels are considered
        to be overdispersed.
    """
    _, cross_disp, _, cross_idx_od = cross_rep_variance(
        obs.values(), model=model, min_disp=min_disp)
    mean, dev_disp, _, dev_idx_od = deviation_variance(
        obs[rep], exp, model=model, min_disp=min_disp)
    combined_disp = cross_disp + dev_disp
    if model == 'norm':
        var = combined_disp
    elif model == 'lognorm':
        var = dispersion_to_variance_direct(combined_disp, mean)
    else:
        raise NotImplementedError('model must be lognorm or norm')
    return mean, combined_disp, var, cross_idx_od | dev_idx_od
