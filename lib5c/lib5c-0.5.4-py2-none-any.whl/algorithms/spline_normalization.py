"""
Module for fitting b-splines to 5C counts data as a method of bias correction.
"""

import numpy as np
from scipy.interpolate import LSQBivariateSpline

from lib5c.util.counts import parallel_subtract_counts, abs_diff_counts,\
    norm_counts, parallel_log_counts, parallel_unlog_counts
from lib5c.util.mathematics import gmean


class DiscreteBivariateEmpiricalSurface(object):
    def __init__(self, xs, ys, zs):
        # coerce to np array
        xs = np.array(xs)
        ys = np.array(ys)
        zs = np.array(zs)

        # identify unique values
        self.range_x = np.unique(xs)
        self.range_y = np.unique(ys)

        # compute empirical surface
        surface = {(x, y): np.nanmean(zs[(xs == x) & (ys == y)])
                   for x in self.range_x for y in self.range_y}

        # fill nan's in the surface
        self.surface = dict(surface)
        for x in self.range_x:
            for y in self.range_y:
                if not np.isfinite(self.surface[x, y]):
                    self.surface[x, y] = np.nanmean(
                        [surface[x_prime, y] for x_prime in self.range_x] +
                        [surface[x, y_prime] for y_prime in self.range_y])

    def ev(self, x, y):
        return self.surface[x, y]


def fit_spline(counts_list, primermap, bias_factor, knots=10, asymmetric=False):
    """
    Fits a 2-D cubic b spline surface to the counts data as a function of the
    specified upstream and downstream bias factors.

    Parameters
    ----------
    counts_list : List[Dict[str, np.ndarray]]
        The counts data to fit the splines with.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap describing the loci. The ``bias_factor`` must be a key of
        the inner dict.
    bias_factor : str
        The bias factor to fit the model with.
    knots : Optional[int]
        The number of knots to use for the spline. If the bias factor is
        discrete, pass 0 to use an empirical discrete surface instead of a
        spline.
    log : Optional[bool]
        Pass true to fit the spline to logged data.
    asymmetric : Optional[bool]
        Pass True to iterate over only the upper triangular entries of the
        counts matrices. The default is False, which iterates over the whole
        counts matrices.

    Returns
    -------
    Tuple[LSQBivariateSpline, Dict[str, np.ndarray],
            List[Dict[str, np.ndarray]]]
        The first element of the tuple is the spline surface fit to the data.
        The second element contains the values of the spline surface evaluated
        at each point in the original counts dict. The third element contains
        the bias-corrected counts dicts.
    """
    # infer regions
    regions = counts_list[0].keys()

    # construct arrays
    x = []
    y = []
    z = []
    for counts in counts_list:
        for region in regions:
            for i in range(len(counts[region])):
                if asymmetric:
                    jrange = range(i + 1)
                else:
                    jrange = range(len(counts[region]))
                for j in jrange:
                    if np.isfinite(counts[region][i, j]):
                        x.append(primermap[region][i][bias_factor])
                        y.append(primermap[region][j][bias_factor])
                        z.append(counts[region][i, j])

    # fit spline or empirical surface
    if knots:
        # place knots
        x_unique = np.unique(x)
        x_knots = np.percentile(x, np.linspace(0, 100, knots)) \
            if len(x_unique) > knots else np.linspace(min(x), max(x), knots)
        y_unique = np.unique(y)
        y_knots = np.percentile(y, np.linspace(0, 100, knots)) \
            if len(y_unique) > knots else np.linspace(min(y), max(y), knots)

        # fit spline
        spline = LSQBivariateSpline(x, y, z, x_knots, y_knots)
    else:
        spline = DiscreteBivariateEmpiricalSurface(x, y, z)

    # evaluate spline
    spline_values = {region: np.copy(counts_list[0][region])
                     for region in regions}
    for region in regions:
        for i in range(len(spline_values[region])):
            for j in range(i + 1):
                spline_value = spline.ev(primermap[region][i][bias_factor],
                                         primermap[region][j][bias_factor])
                if not np.isfinite(spline_value):
                    raise ValueError('infinite spline value, probably due to '
                                     'too many knots')
                spline_values[region][i, j] = spline_value
                spline_values[region][j, i] = spline_value

    # correct original matrix
    corrected = [parallel_subtract_counts(counts, spline_values)
                 for counts in counts_list]

    return spline, spline_values, corrected


def iterative_spline_normalization(counts_list, exp_list, primermap, bias_list,
                                   max_iter=100, eps=1e-4, knots=10, log=True,
                                   asymmetric=False):
    """
    Convenience function for iteratively applying a set of spline normalization
    steps to a set of counts dicts.

    Parameters
    ----------
    counts_list : List[Dict[str, np.ndarray]]
        A list of observed counts dicts to normalize.
    exp_list : List[Dict[str, np.ndarray]]
        A list of expected counts dicts corresponding to the counts dicts in
        ``counts_list``.
    primermap : Dict[str, List[Dict[str, Any]]]
        Primermap or pixelmap describing the loci in this region.
    bias_list : List[str]
        A list of bias factors to remove from the counts. These strings must
        match metadata keys in ``primermap``. That is to say, if ``bias_list``
        is ``['length']`` then we expect ``primermap[region][i]['length']`` to
        be a number representing the length of the ``i`` th fragment in the
        region specified by ``region``. If multiple bias factors are specified,
        the algorithm will iteratively remove all of them from the data.
    max_iter : int
        The maximum number of iterations when iterating between bias factors.
    eps : float
        When the relative change in all models drops below this value
        convergence is declared.
    knots : Union[int, List[int]]
        Specifies the number of knots to put into the splines. Pass a single int
        to use the same number of knots in each model. Pass a list of ints of
        length equal to the length of ``bias_list`` to use ``knots[i]`` knots
        for the bias factor named ``bias_list[i]``. If a bias factor is
        discrete, pass 0 for its knot number to use an empirical discrete
        surface instead of a spline.
    log : bool
        Pass True to fit the splines to log-scale data, reducing the effects of
        outliers.
    asymmetric : bool
        Pass True to construct models using only the upper-triangular elements
        of the counts matrices, which can lead to asymmetric models. By default,
        the algorithm iterates over all elements of the counts matrices,
        enforcing symmetry in the bias models but incurring some redundancy in
        the actual counts information.

    Returns
    -------
    Tuple[Dict[str, scipy.interpolate.BivariateSpline],
            List[Dict[str, np.ndarray]], List[Dict[str, np.ndarray]]]
        The first element of the tuple is a dict mapping the bias factors
        specified in ``bias_list`` to BivariateSpline instances. The second
        element in the tuple is a dict mapping the bias factors specified in
        ``bias_list`` to counts dicts containing the evaluations of the spline
        fit to that bias factor at each point in the list of input counts dicts.
        The third element of the tuple is the normalized list of counts.
    """
    # deduce regions
    regions = counts_list[0].keys()

    # the change in each model the last time it was updated
    deltas = np.ones(len(bias_list))

    # the latest version of each model, intially they are all ones
    models = {bias: {region: np.zeros_like(counts_list[0][region], dtype=float)
                     for region in regions}
              for bias in bias_list}

    # spline representations of the models, initially they are None
    splines = {}

    # experimental: if one of the biases is 'gmean', add the geometric row means
    # afted distance dependence subtraction as a bias factor
    if 'gmean' in bias_list:
        partially_corrected_counts_list = [
            parallel_subtract_counts(counts_list[j], exp_list[j])
            for j in range(len(counts_list))]
        for region in regions:
            for i in range(len(counts_list[0][region])):
                primermap[region][i]['gmean'] = gmean(np.concatenate(
                    [partially_corrected_counts_list[j][region][i, :]
                     for j in range(len(counts_list))]))

    # log if appropriate
    if log:
        counts_list = [parallel_log_counts(counts) for counts in counts_list]
        exp_list = [parallel_log_counts(counts) for counts in exp_list]

    # the current iteration number
    i = 0

    while i < max_iter and np.any(deltas > eps):
        # select a model to update
        selected_model = i % len(bias_list)
        print 'iteration %i, updating %s' % (i, bias_list[selected_model])

        # correct the counts for all models except this one
        partially_corrected_counts_list = [
            parallel_subtract_counts(*[counts_list[j], exp_list[j]] +
                                      [models[bias_list[k]]
                                       for k in range(len(bias_list))
                                       if k != selected_model])
            for j in range(len(counts_list))]

        # resolve knots
        if type(knots) == dict:
            resolved_knots = knots[bias_list[selected_model]]
        elif type(knots) == list:
            resolved_knots = knots[selected_model]
        else:
            resolved_knots = knots

        # update selected model based on this data
        try:
            new_spline, new_model, _ = fit_spline(
                partially_corrected_counts_list, primermap,
                bias_list[selected_model], knots=resolved_knots,
                asymmetric=asymmetric)
        except ValueError:
            if i >= len(bias_list) - 1:
                print 'early termination due to infinite spline values'
                print 'all bias factors went through at least one iteration'
                break
            else:
                raise ValueError('infinite spline value before all biases were '
                                 'considered, probably due to too many knots')

        # update deltas
        adf = abs_diff_counts(new_model, models[bias_list[selected_model]])
        deltas[selected_model] = norm_counts(adf) / \
            norm_counts(models[bias_list[selected_model]])
        print 'delta: %s' % deltas[selected_model]

        # update model
        models[bias_list[selected_model]] = new_model

        # save spline
        splines[bias_list[selected_model]] = new_spline

        # increment iteration number
        i += 1

    corrected_counts_list = [
        parallel_subtract_counts(*[counts_list[j]] +
                                  [models[bias_list[k]]
                                   for k in range(len(bias_list))])
        for j in range(len(counts_list))]

    # unlog if appropriate
    if log:
        corrected_counts_list = [parallel_unlog_counts(counts)
                                 for counts in corrected_counts_list]

    return splines, models, corrected_counts_list
