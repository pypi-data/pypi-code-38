"""
Module for computing expected models for 5C interaction data.
"""

import numpy as np
import powerlaw as pl
from statsmodels.nonparametric.smoothers_lowess import lowess

from lib5c.util.parallelization import parallelize_regions
from lib5c.util.bed import get_mid_to_mid_distance
from lib5c.util.mathematics import gmean
from lib5c.util.counts import flatten_regional_counts, propagate_nans
from lib5c.algorithms.donut_filters import donut_filt, lower_left_filt


@parallelize_regions
def make_poly_log_log_fragment_expected_matrix(obs_matrix, regional_primermap):
    """
    Convenience function for quickly making an expected matrix for a
    fragment-level observed counts matrix based on a simple power law
    relationship.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    regional_primermap : List[Dict[str, Any]]
        Primermap describing the loci in the region represented by
        ``obs_matrix``. Necessary to figure out distances between elements in
        the contact matrix.

    Returns
    -------
    np.ndarray
        The expected matrix.
    """
    distance_matrix = make_distance_matrix(regional_primermap)
    distance_expected = poly_log_log_fragment(
        obs_matrix, distance_matrix)
    return make_expected_matrix_from_dict(distance_expected, distance_matrix)


@parallelize_regions
def make_poly_log_log_binned_expected_matrix(obs_matrix,
                                             exclude_near_diagonal=False):
    """
    Convenience function for quickly making an expected matrix for a bin-level
    observed counts matrix based on a simple power law relationship.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    np.ndarray
        The expected matrix.
    """
    distance_expected = poly_log_log_binned(
        obs_matrix, exclude_near_diagonal=exclude_near_diagonal)
    return make_expected_matrix_from_list(distance_expected)


@parallelize_regions
def make_powerlaw_binned_expected_matrix(obs_matrix,
                                         exclude_near_diagonal=False):
    """
    Convenience function for quickly making an expected matrix for a bin-level
    observed counts matrix based on a simple power law relationship.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    np.ndarray
        The expected matrix.
    """
    distance_expected = powerlaw_binned(
        obs_matrix, exclude_near_diagonal=exclude_near_diagonal)
    return make_expected_matrix_from_list(distance_expected)


def get_distance_expected(obs_matrix, regional_primermap=None, level='bin',
                          powerlaw=False, regression=False, degree=1,
                          lowess_smooth=False, lowess_frac=0.8,
                          log_transform='auto', exclude_near_diagonal=False):
    """
    Convenience function for computing a regional one-dimensional expected model
    from a matrix of observed counts, with properties that can be customized by
    kwargs.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts to model.
    regional_primermap : Optional[List[Dict[str, Any]]]
        The primermap for this region. Required if ``obs_matrix`` is
        fragment-level.
    level : {'bin', 'fragment'}
        The level of ``obs_matrix``.
    powerlaw : bool
        Whether or not to fit a discrete power law distribution to the data.
    regression : bool
        Whether or not to use a polynomial regression model.
    degree : int
        The degree of the regression model to use.
    lowess_smooth : bool
        Whether or not to use lowess smoothing to compute the model.
    lowess_frac : float
        The lowess smoothing fraction parameter.
    log_transform : {'counts', 'both', 'none', 'auto'}
        What to transform into log space.
            * counts: log-transform only the counts but not the distances. This
              results in semi-log models, which don't work on fragment-level
              data yet.
            * both: log-transform both the counts and the distances, resulting
              in log-log models.
            * none: don't log anything.
            * auto: automatically pick a reasonably choice based on the other
              kwargs.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    Union[List[float], Dict[int, float]]
        The one-dimensional expected model. For bin-level data, this is a list
        of floats, where the ``i`` th element of the list corresponds to the
        expected value for interactions between loci separated by ``i`` bins.
        For fragment-level data, this is a dict mapping interaction distances in
        units of base pairs to the appropriate expected values.
    """
    # make 1-D expected
    if level == 'bin':
        # bin level, don't need a distance matrix
        if powerlaw:
            print 'using power law 1-D distance model'
            distance_expected = powerlaw_binned(
                obs_matrix, exclude_near_diagonal=exclude_near_diagonal)
        elif regression:
            print 'using polynomial log-log 1-D distance model'
            distance_expected = poly_log_log_binned(
                obs_matrix, degree=degree,
                exclude_near_diagonal=exclude_near_diagonal)
        elif lowess_smooth:
            if log_transform == 'counts':
                print 'using lowess log-counts 1-D distance model'
                distance_expected = lowess_binned_log_counts(
                    obs_matrix, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
            elif log_transform == 'none':
                print 'using lowess unlogged 1-D distance model'
                distance_expected = lowess_binned(
                    obs_matrix, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
            else:  # catches 'both' and 'auto'
                print 'using lowess log-log 1-D distance model'
                distance_expected = lowess_log_log_binned(
                    obs_matrix, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
        else:
            if log_transform == 'none':
                print 'using unlogged empirical binned 1-D distance model'
                distance_expected = empirical_binned(
                    obs_matrix, log_transform=False)
            else:  # catches 'both' and 'auto'; 'counts' is illegal
                print 'defaulting to logged empirical binned 1-D distance model'
                distance_expected = empirical_binned(
                    obs_matrix, log_transform=True)
    else:
        # fragment level, need a distance matrix
        distance_matrix = make_distance_matrix(regional_primermap)
        assert np.issubdtype(distance_matrix[0, 1], int)

        if lowess_smooth:
            print 'using lowess log-log 1-D distance model'
            distance_expected = lowess_log_log_fragment(
                obs_matrix, distance_matrix)
        else:
            print 'defaulting to polynomial log-log 1-D distance model'
            distance_expected = poly_log_log_fragment(
                obs_matrix, distance_matrix, degree=degree)

    return distance_expected


def get_global_distance_expected(counts, primermap=None, level='bin',
                                 powerlaw=False, regression=False, degree=1,
                                 lowess_smooth=False, lowess_frac=0.8,
                                 log_transform='auto',
                                 exclude_near_diagonal=False):
    """
    Convenience function for computing a global one-dimensional expected model
    from a dict of observed counts, with properties that can be customized by
    kwargs.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The dict of observed counts to model.
    primermap : Optional[Dict[str, List[Dict[str, Any]]]]
        A primermap corresponding to ``counts``.
    level : {'bin', 'fragment'}
        The level of ``counts``.
    powerlaw : bool
        Whether or not to fit a discrete power law distribution to the data.
    regression : bool
        Whether or not to use a polynomial regression model.
    degree : int
        The degree of the regression model to use.
    lowess_smooth : bool
        Whether or not to use lowess smoothing to compute the model.
    lowess_frac : float
        The lowess smoothing fraction parameter.
    log_transform : {'counts', 'both', 'none', 'auto'}
        What to transform into log space.
            * counts: log-transform only the counts but not the distances. This
              results in semi-log models, which don't work on fragment-level
              data yet.
            * both: log-transform both the counts and the distances, resulting
              in log-log models.
            * none: don't log anything.
            * auto: automatically pick a reasonably choice based on the other
              kwargs.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    Union[List[float], Dict[int, float]]
        The one-dimensional expected model. For bin-level data, this is a list
        of floats, where the ``i`` th element of the list corresponds to the
        expected value for interactions between loci separated by ``i`` bins.
        For fragment-level data, this is a dict mapping interaction distances in
        units of base pairs to the appropriate expected values.
    """
    # make 1-D expected
    if level == 'bin':
        # bin level, don't need a distance matrix
        if powerlaw:
            print 'using power law 1-D distance model'
            distance_expected = global_powerlaw_binned(
                counts, exclude_near_diagonal=exclude_near_diagonal)
        elif regression:
            print 'using polynomial log-log 1-D distance model'
            distance_expected = global_poly_log_log_binned(
                counts, degree=degree,
                exclude_near_diagonal=exclude_near_diagonal)
        elif lowess_smooth:
            if log_transform == 'counts':
                print 'using lowess log-counts 1-D distance model'
                distance_expected = global_lowess_binned_log_counts(
                    counts, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
            elif log_transform == 'none':
                print 'using lowess unlogged 1-D distance model'
                distance_expected = global_lowess_binned(
                    counts, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
            else:
                print 'using lowess log-log 1-D distance model'
                distance_expected = global_lowess_log_log_binned(
                    counts, frac=lowess_frac,
                    exclude_near_diagonal=exclude_near_diagonal)
        else:
            if log_transform == 'none':
                print 'using unlogged empirical binned 1-D distance model'
                distance_expected = global_empirical_binned(
                    counts, log_transform=False)
            else:
                print 'defaulting to logged empirical binned 1-D distance model'
                distance_expected = global_empirical_binned(
                    counts, log_transform=True)
    else:
        # fragment level, need a distance matrix
        distance_matrix = make_distance_matrix(primermap)

        if lowess_smooth:
            print 'using lowess log-log 1-D distance model'
            distance_expected = global_lowess_log_log_fragment(
                counts, distance_matrix)
        else:
            print 'defaulting to polynomial log-log 1-D distance model'
            distance_expected = global_poly_log_log_fragment(
                counts, distance_matrix, degree=degree)

    return distance_expected


@parallelize_regions
def make_expected_matrix(obs_matrix, regional_primermap=None, level='bin',
                         powerlaw=False, regression=False, degree=1,
                         lowess_smooth=False, lowess_frac=0.8,
                         log_transform='auto', monotonic=False, donut=False,
                         w=15, p=5, donut_frac=0.2, min_exp=0.1,
                         log_donut=False, max_donut_ll=False,
                         distance_expected=None, exclude_near_diagonal=False):
    """
    Convenience function for computing a complete expected matrix given a matrix
    of observed counts that can be customized with a variety of kwargs.

    Parameters
    ----------
    obs_matrix : np.ndarray
        The matrix of observed counts to make an expected matrix for.
    regional_primermap : Optional[List[Dict[str, Any]]]
        The primermap for this region. Required if ``obs_matrix`` is
        fragment-level.
    level : {'bin', 'fragment'}
        The level of ``obs_matrix``.
    powerlaw : bool
        Whether or not to fit a discrete power law distribution to the data.
    regression : bool
        Whether or not to use a polynomial regression model.
    degree : int
        The degree of the regression model to use.
    lowess_smooth : bool
        Whether or not to use lowess smoothing to compute the model.
    lowess_frac : float
        The lowess smoothing fraction parameter.
    log_transform : {'counts', 'both', 'none', 'auto'}
        What to transform into log space.
            * counts: log-transform only the counts but not the distances. This
              results in semi-log models, which don't work on fragment-level
              data yet.
            * both: log-transform both the counts and the distances, resulting
              in log-log models.
            * none: don't log anything.
            * auto: automatically pick a reasonably choice based on the other
              kwargs.
    monotonic : bool
        Pass True to force the one-dimensional expected model to be monotonic.
    donut : bool
        Pass True to apply donut-filter local correction to the expected model.
        Not implemented for fragment-level input data.
    w : int
        The outer width of the donut when using donut correction. Should be an
        odd integer.
    p : int
        The inner width of the donut when using donut correction. Should be an
        odd integer.
    donut_frac : float
        If the fraction of possible elements in the donut that lie wihtin the
        region and have non-infinte values is lower than this fraction then the
        donut-corrected value at that point will be NaN.
    min_exp : float
        If the sum of the 1-D expected matrix under the donut or lower left
        footprint for a particular pixel is less than this value, set the output
        at this pixel to nan to avoid numerical instability related to division
        by small numbers.
    log_donut : bool
        Pass True to perform donut correction in log-counts space.
    max_donut_ll : bool
        If ``donut`` is True, pass True here too to make the donut correction
        use the maximum of the "donut" and "lower-left" regions.
    distance_expected : Optional[Union[List[float], Dict[int, float]]]
        Pass a one-dimensional expected model to use it instead of computing a
        new one from scratch according to the other kwargs.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    Tuple[np.ndarray, Union[List[float], Dict[int, float]], Optional[
    np.ndarray]]
        The first element of the tuple is the expected matrix. The second
        element of the tuple is the one-dimensional expected model, which will
        be a list of expected values if ``level`` was 'bin' or a dict mapping
        integer distances to expected values if ``level`` was 'fragment'. The
        third element will be the pairwise distance matrix if ``level`` was
        'fragment', but will simply be None if ``level`` was 'bin'.
    """
    # get distance expected if it wasn't passed
    if distance_expected is None:
        distance_expected = get_distance_expected(
            obs_matrix, regional_primermap=regional_primermap, level=level,
            powerlaw=powerlaw, regression=regression, degree=degree,
            lowess_smooth=lowess_smooth, lowess_frac=lowess_frac,
            log_transform=log_transform,
            exclude_near_diagonal=exclude_near_diagonal)

    # make a distance matrix if we are at the fragment level
    if level == 'fragment':
        distance_matrix = make_distance_matrix(regional_primermap)
        assert np.issubdtype(distance_matrix[0, 1], int)
    else:
        distance_matrix = None

    # force monotonic
    if monotonic:
        print 'forcing monotonicity'
        distance_expected = force_monotonic(distance_expected)

    # make expected matrix
    if level == 'bin':
        expected_matrix = make_expected_matrix_from_list(distance_expected)
    else:
        expected_matrix = make_expected_matrix_from_dict(
            distance_expected, distance_matrix)
    expected_matrix = expected_matrix[:len(obs_matrix), :len(obs_matrix)]

    # donut filter
    if donut:
        print 'applying donut correction'
        # propagate nan's to expected
        obs_matrix, expected_matrix = propagate_nans(
            obs_matrix, expected_matrix)

        # log transform if requested
        if log_donut:
            obs_matrix = np.log(obs_matrix + 1)
            expected_matrix = np.log(expected_matrix + 1)

        # donut correct
        if not max_donut_ll:
            expected_matrix = donut_filt(
                obs_matrix, expected_matrix, p, w, max_percent=donut_frac,
                min_exp=min_exp)
        else:
            # compute two matrices
            donut_matrix = donut_filt(obs_matrix, expected_matrix, p, w,
                                      max_percent=donut_frac, min_exp=min_exp)
            ll_matrix = lower_left_filt(obs_matrix, expected_matrix, p, w,
                                        max_percent=donut_frac, min_exp=min_exp)

            # max operation
            expected_matrix = np.fmax(donut_matrix, ll_matrix)

        # undo log transform
        if log_donut:
            expected_matrix = np.exp(expected_matrix) - 1

    return expected_matrix, distance_expected, distance_matrix


def make_expected_matrix_from_list(distance_expected):
    """
    Converts a bin-level one-dimensional expected model into an expected matrix.

    Parameters
    ----------
    distance_expected : List[float]
        The one-dimensional distance expected model to make a matrix out of.

    Returns
    -------
    np.ndarray
        The expected matrix.
    """
    expected_matrix = np.zeros((len(distance_expected), len(distance_expected)),
                               dtype=float)
    for i in range(len(expected_matrix)):
        for j in range(i + 1):
            expected_matrix[i, j] = distance_expected[i - j]
            expected_matrix[j, i] = distance_expected[i - j]
    return expected_matrix


def make_expected_matrix_from_dict(distance_expected, distance_matrix):
    """
    Converts a fragment-level one-dimensional expected model into an expected
    matrix.

    Parameters
    ----------
    distance_expected : Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    distance_matrix : np.ndarray
        The pairwise distance matrix for the fragments in this region.

    Returns
    -------
    np.ndarray
        The expected matrix.
    """
    expected_matrix = np.zeros_like(distance_matrix, dtype=float)
    for i in range(len(expected_matrix)):
        for j in range(i + 1):
            expected_matrix[i, j] = distance_expected[distance_matrix[i, j]]
            expected_matrix[j, i] = distance_expected[distance_matrix[i, j]]
    return expected_matrix


def make_expected_dict_from_matrix(expected_matrix, distance_matrix):
    """
    Convert an expected matrix into a dict representation of the one-dimensional
    expected model it embodies.

    Parameters
    ----------
    expected_matrix : np.ndarray
        The expected matrix.
    distance_matrix : np.ndarray
        The pairwise distance matrix for the fragments in this region.

    Returns
    -------
    Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    """
    distance_expected = {}
    for i in range(len(expected_matrix)):
        for j in range(i + 1):
            if np.isfinite(expected_matrix[i, j]):
                distance_expected[distance_matrix[i, j]] = expected_matrix[i, j]
    return distance_expected


@parallelize_regions
def make_distance_matrix(regional_primermap):
    """
    Construct a pairwise distance matrix for the fragments in a region from the
    primermap describing those fragments.

    Parameters
    ----------
    regional_primermap : List[Dict[str, Any]]
        The primermap for this region.

    Returns
    -------
    np.ndarray
        The pairwise distance matrix for all fragments in this region in units
        of base pairs.
    """
    return np.array([[get_mid_to_mid_distance(regional_primermap[i],
                                              regional_primermap[j])
                      for i in range(len(regional_primermap))]
                     for j in range(len(regional_primermap))], dtype=int)


def poly_log_log_fragment(regional_counts, distances, degree=1, pseudocount=1):
    """
    Make a regional one-dimensional fragment-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    distances : np.ndarray
        The pairwise distance matrix for all fragments in this region in units
        of base pairs.
    degree : int
        The degree of the polynomial to fit.
    pseudocount : int
        The pseudocount to add to the counts before logging.

    Returns
    -------
    Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    """
    # log transform
    log_regional_counts = np.log(regional_counts + pseudocount)
    log_distances = np.log(distances + pseudocount)

    # make data of the form [log_distance, log_count], ignoring nans
    data = np.asarray([[log_distances[i, j], log_regional_counts[i, j]]
                       for i in range(len(log_regional_counts))
                       for j in range(i + 1)
                       if np.isfinite(log_regional_counts[i, j])])

    # do the linear fit
    fit = np.poly1d(np.polyfit(data[:, 0], data[:, 1], degree))

    # repackage
    distance_expected = {
        dist: np.exp(fit(np.log(dist + pseudocount))) - pseudocount
        for dist in np.unique(distances.flatten())
    }

    return distance_expected


def global_poly_log_log_fragment(counts, distances, degree=1, pseudocount=1):
    """
    Make a global one-dimensional fragment-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    distances : Dict[str, np.ndarray]
        A dict of pairwise distance matrices describing the genomic distances
        between the elements of the matrices in ``counts``. The keys and array
        dimensions should match the keys and array dimensions of ``counts``.
    degree : int
        The degree of the polynomial to fit.
    pseudocount : int
        The pseudocount to add to the counts before logging.

    Returns
    -------
    Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    """
    # log transform
    log_counts = {region: np.log(counts[region] + pseudocount)
                  for region in counts.keys()}
    log_distances = {region: np.log(distances[region] + pseudocount)
                     for region in distances.keys()}

    # make data of the form [log_distance, log_count], ignoring nans
    data = np.asarray([[log_distances[region][i, j], log_counts[region][i, j]]
                       for region in log_counts.keys()
                       for i in range(len(log_counts[region]))
                       for j in range(i + 1)
                       if np.isfinite(log_counts[region][i, j])])

    # do the linear fit
    fit = np.poly1d(np.polyfit(data[:, 0], data[:, 1], degree))

    # repackage
    distance_expected = {
        dist: np.exp(fit(np.log(dist + pseudocount))) - pseudocount
        for dist in np.unique(np.concatenate([distances[region].flatten()
                                              for region in distances.keys()]))
    }
    return distance_expected


def poly_log_log_binned(regional_counts, degree=1, pseudocount=1,
                        exclude_near_diagonal=False):
    """
    Make a regional one-dimensional bin-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    degree : int
        The degree of the polynomial to fit.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # log transform
    log_regional_counts = np.log(regional_counts + pseudocount)

    # establish total size
    size = len(regional_counts)

    # make data of the form [log_distance, log_count], ignoring nans
    data = np.asarray([[np.log(i - j + pseudocount), log_regional_counts[i, j]]
                       for i in range(len(log_regional_counts))
                       for j in range(i + 1)
                       if np.isfinite(log_regional_counts[i, j])])

    # filter
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    key_log_distance = np.log(key_index + pseudocount)
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_log_distance, data))

    # do the linear fit
    fit = np.poly1d(
        np.polyfit(filtered_data[:, 0], filtered_data[:, 1], degree))

    # get empirical expected
    empirical = empirical_binned(regional_counts, log_transform=True)

    # repackage
    distance_expected = [empirical[i]
                         if i < key_index
                         else np.exp(fit(np.log(i + pseudocount))) - pseudocount
                         for i in range(size)]

    return distance_expected


def global_poly_log_log_binned(counts, degree=1, pseudocount=1,
                               exclude_near_diagonal=False):
    """
    Make a global one-dimensional bin-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    degree : int
        The degree of the polynomial to fit.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # log transform
    log_counts = {region: np.log(counts[region] + pseudocount)
                  for region in counts.keys()}

    # make data of the form [log_distance, log_count], ignoring nans
    data = np.asarray([[np.log(i - j + pseudocount), log_counts[region][i, j]]
                       for region in log_counts.keys()
                       for i in range(len(log_counts[region]))
                       for j in range(i + 1)
                       if np.isfinite(log_counts[region][i, j])])

    # establish total size
    size = max([len(counts[region]) for region in counts.keys()])

    # filter
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    key_log_distance = np.log(key_index + pseudocount)
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_log_distance, data))

    # do the linear fit
    fit = np.poly1d(
        np.polyfit(filtered_data[:, 0], filtered_data[:, 1], degree))

    # get empirical expected
    empirical = global_empirical_binned(counts, log_transform=True)

    # repackage
    distance_expected = [empirical[i]
                         if i < key_index
                         else np.exp(fit(np.log(i + pseudocount))) - pseudocount
                         for i in range(size)]

    return distance_expected


def powerlaw_binned(regional_counts, exclude_near_diagonal=False):
    """
    Make a regional one-dimensional bin-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # fit empirical distance dependence
    empirical = np.array(empirical_binned(regional_counts, log_transform=True))
    empirical_floored = np.floor(empirical).astype(int)

    # make data of the form [distance], ignoring nans
    # empirical_floored represents an empirical un-normalized pdf over distances
    # data represents the empirical distance dependence as a sample from the
    # empirical pdf over distances
    size = len(regional_counts)
    idx = int(size / 3) if exclude_near_diagonal else 1
    data = np.concatenate([[i]*empirical_floored[i] for i in range(idx, size)])

    # fit powerlaw
    # size factor represents how many time we have to draw from the pdf
    # to recover something on the scale of the original empirical data
    fit = pl.Fit(data, xmin=idx, xmax=size-1, discrete=True)
    size_factor = empirical_floored[idx:].sum()
    powerlaw_expected = fit.power_law.pdf(np.arange(idx, size)) * size_factor

    # return stitched distance dependence
    return np.concatenate([empirical[0:idx], powerlaw_expected])


def global_powerlaw_binned(counts, exclude_near_diagonal=False):
    """
    Make a global one-dimensional bin-level expected model by fitting a
    polynomial in log-log space.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # fit empirical distance dependence
    empirical = np.array(global_empirical_binned(counts, log_transform=True))
    empirical_floored = np.floor(empirical).astype(int)

    # establish total size
    size = max([len(counts[region]) for region in counts.keys()])

    # make data of the form [distance], ignoring nans
    # empirical_floored represents an empirical un-normalized pdf over distances
    # data represents the empirical distance dependence as a sample from the
    # empirical pdf over distances
    idx = int(size / 3) if exclude_near_diagonal else 1
    data = np.concatenate([[i]*empirical_floored[i] for i in range(idx, size)])

    # fit powerlaw
    # size factor represents how many time we have to draw from the pdf
    # to recover something on the scale of the original empirical data
    fit = pl.Fit(data, xmin=idx, xmax=size-1, discrete=True)
    size_factor = empirical_floored[idx:].sum()
    powerlaw_expected = fit.power_law.pdf(np.arange(idx, size)) * size_factor

    # return stitched distance dependence
    return np.concatenate([empirical[0:idx], powerlaw_expected])


def lowess_log_log_fragment(regional_counts, distances, pseudocount=1,
                            frac=0.8):
    """
    Make a regional one-dimensional fragment-level expected model by performing
    lowess regression in log-log space.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    distances : np.ndarray
        The pairwise distance matrix for all fragments in this region in units
        of base pairs.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.

    Returns
    -------
    Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    """
    # log transform
    log_regional_counts = np.log(regional_counts + pseudocount)
    log_distances = np.log(distances + pseudocount)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[log_distances[i, j], log_regional_counts[i, j]]
                       for i in range(len(log_regional_counts))
                       for j in range(i + 1)
                       if np.isfinite(log_regional_counts[i, j])])

    # do the lowess fit
    fit = lowess(data[:, 1], data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(data[:, 1]))

    # unlog
    fit_dists = np.rint(np.exp(fit[:, 0]) - pseudocount).astype(int)
    fit_counts = np.exp(fit[:, 1]) - pseudocount

    # repackage
    distance_expected = {fit_dists[i]: fit_counts[i] for i in range(len(fit))}

    # fill nans
    for dist in np.unique(distances.flatten()):
        if dist not in distance_expected:
            distance_expected[dist] = np.nan

    return distance_expected


def global_lowess_log_log_fragment(counts, distances, pseudocount=1, frac=0.8):
    """
    Make a global one-dimensional fragment-level expected model by performing
    lowess regression in log-log space.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    distances : Dict[str, np.ndarray]
        A dict of pairwise distance matrices describing the genomic distances
        between the elements of the matrices in ``counts``. The keys and array
        dimensions should match the keys and array dimensions of ``counts``.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.

    Returns
    -------
    Dict[int, float]
        A mapping from interaction distances in units of base pairs to the
        expected value at that distance.
    """
    # log transform
    log_counts = {region: np.log(counts[region] + pseudocount)
                  for region in counts.keys()}
    log_distances = {region: np.log(distances[region] + pseudocount)
                     for region in distances.keys()}

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[log_distances[region][i, j], log_counts[region][i, j]]
                       for region in log_counts.keys()
                       for i in range(len(log_counts[region]))
                       for j in range(i + 1)
                       if np.isfinite(log_counts[region][i, j])])

    # do the lowess fit
    fit = lowess(data[:, 1], data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(data[:, 1]))

    # unlog
    fit_dists = np.rint(np.exp(fit[:, 0]) - pseudocount).astype(int)
    fit_counts = np.exp(fit[:, 1]) - pseudocount

    # repackage
    distance_expected = {fit_dists[i]: fit_counts[i] for i in range(len(fit))}

    # fill nans
    for dist in np.unique(np.concatenate([distances[region].flatten()
                                          for region in distances.keys()])):
        if dist not in distance_expected:
            distance_expected[dist] = np.nan

    return distance_expected


def lowess_log_log_binned(regional_counts, pseudocount=1, frac=0.8,
                          exclude_near_diagonal=False):
    """
    Make a regional one-dimensional bin-level expected model by performing
    lowess regression in log-log space.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # log transform
    log_regional_counts = np.log(regional_counts + pseudocount)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[np.log(i - j + pseudocount), log_regional_counts[i, j]]
                       for i in range(len(log_regional_counts))
                       for j in range(i + 1)
                       if np.isfinite(log_regional_counts[i, j])])

    # establish total size
    size = len(regional_counts)

    # filter
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    key_log_distance = np.log(key_index + pseudocount)
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_log_distance, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # unlog
    fit_dists = np.rint(np.exp(fit[:, 0]) - pseudocount).astype(int)
    fit_counts = np.exp(fit[:, 1]) - pseudocount

    # get empirical expected
    empirical = empirical_binned(regional_counts, log_transform=True)

    # repackage
    distance_expected = {fit_dists[i]: fit_counts[i] for i in range(len(fit))}
    distance_expected = [empirical[i]
                         if i < key_index
                         else distance_expected[i]
                         if i in distance_expected
                         else np.nan
                         for i in range(size)]

    return distance_expected


def global_lowess_log_log_binned(counts, pseudocount=1, frac=0.8,
                                 exclude_near_diagonal=False):
    """
    Make a global one-dimensional bin-level expected model by performing lowess
    regression in log-log space.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # log transform
    log_counts = {region: np.log(counts[region] + pseudocount)
                  for region in counts.keys()}

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[np.log(i - j + pseudocount), log_counts[region][i, j]]
                       for region in log_counts.keys()
                       for i in range(len(log_counts[region]))
                       for j in range(i + 1)
                       if np.isfinite(log_counts[region][i, j])])

    # establish total size
    size = max([len(counts[region]) for region in counts.keys()])

    # filter
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    key_log_distance = np.log(key_index + pseudocount)
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_log_distance, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # unlog
    fit_dists = np.rint(np.exp(fit[:, 0]) - pseudocount).astype(int)
    fit_counts = np.exp(fit[:, 1]) - pseudocount

    # get empirical expected
    empirical = global_empirical_binned(counts, log_transform=True)

    # repackage
    distance_expected = {fit_dists[i]: fit_counts[i] for i in range(len(fit))}
    distance_expected = [empirical[i]
                         if i < key_index
                         else distance_expected[i]
                         if i in distance_expected
                         else np.nan
                         for i in range(size)]

    return distance_expected


def force_monotonic(distance_expected):
    """
    Force a one-dimensional distance expected to be monotonic.

    Parameters
    ----------
    distance_expected : Union[List[float], Dict[int, float]]
        The one-dimensional expected model to force to monotonicity. If the
        model describes bin-level data, this should be a list of floats, where
        the ``i`` th element of the list corresponds to the expected value for
        interactions between loci separated by ``i`` bins. If the model
        describes fragment-level data, this should be a dict mapping interaction
        distances in units of base pairs to the expected value at that distance.

    Returns
    -------
    Union[List[float], Dict[int, float]]
        The forced-monotonic version of the input one-dimensional expected
        model.
    """
    if type(distance_expected) == list:
        monotonic_expected = []
        min_value = np.inf
        for i in range(len(distance_expected)):
            min_value = min(min_value, distance_expected[i])
            monotonic_expected.append(min_value)
        return monotonic_expected
    elif type(distance_expected) == dict:
        distances = sorted(distance_expected.keys())
        monotonic_expected = {}
        min_value = np.inf
        for dist in distances:
            min_value = min(min_value, distance_expected[dist])
            monotonic_expected[dist] = min_value
        return monotonic_expected
    elif isinstance(distance_expected, np.ndarray):
        return np.minimum.accumulate(distance_expected)
    else:
        raise NotImplementedError('cannot force monotonicity of a %s'
                                  % type(distance_expected))


def empirical_binned(regional_counts, log_transform=True):
    """
    Make a regional one-dimensional bin-level expected model by taking an
    average of the interaction values at each distance.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    log_transform : bool
        Pass True to take the geometric mean instead of the arithmetic mean,
        which is equivalent to averaging log-transformed counts.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # make offdiagonals
    offdiagonals = [np.diag(regional_counts, k=i)
                    for i in range(len(regional_counts))]

    # pick appropriate mean function
    mean_function = np.nanmean
    if log_transform:
        mean_function = gmean

    return [mean_function(offdiagonal)
            if np.any(np.isfinite(offdiagonal))
            else np.nan
            for offdiagonal in offdiagonals]


def global_empirical_binned(counts, log_transform=True):
    """
    Make a global one-dimensional bin-level expected model by taking an
    average of the interaction values at each distance.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    log_transform : bool
        Pass True to take the geometric mean instead of the arithmetic mean,
        which is equivalent to averaging log-transformed counts.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # make offdiagonals
    offdiagonals = [np.concatenate([np.diag(counts[region], k=i)
                                    for region in counts.keys()])
                    for i in range(max([len(counts[region])
                                        for region in counts.keys()]))]

    # pick appropriate mean function
    mean_function = np.nanmean
    if log_transform:
        mean_function = gmean

    return [mean_function(offdiagonal)
            if np.any(np.isfinite(offdiagonal))
            else np.nan
            for offdiagonal in offdiagonals]


def lowess_binned_log_counts(regional_counts, pseudocount=1, frac=0.8,
                             exclude_near_diagonal=False):
    """
    Make a regional one-dimensional bin-level expected model by performing
    lowess regression in log-counts space, excluding the first third of the
    region and only using the emprical geometric means there instead.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # log counts
    regional_counts = np.log(regional_counts + pseudocount)

    # establish size
    size = len(regional_counts)

    # make offdiagonals
    offdiagonals = [np.diag(regional_counts, k=i) for i in range(size)]

    # get empirical expected
    empirical = empirical_binned(regional_counts, log_transform=False)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[dist, count]
                       for dist in range(size)
                       for count in offdiagonals[dist]
                       if np.isfinite(count)])

    # don't try to fit the first third of the region
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_index, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # filter the fit to just the region above the join point
    filtered_fit = np.asarray(filter(lambda x: x[0] >= key_index, fit))

    # construct an array that will represent the joined fit
    joined_fit = np.zeros(size)
    for i in range(key_index):
        joined_fit[i] = empirical[i]
    for i in range(key_index, size):
        query_result = filter(lambda x: x[0] == i, filtered_fit)
        if query_result:
            joined_fit[i] = query_result[0][1]
        else:
            joined_fit[i] = empirical[i]

    # unlog
    joined_fit = [np.exp(x) - pseudocount for x in joined_fit]

    return joined_fit


def lowess_binned(regional_counts, frac=0.8, exclude_near_diagonal=False):
    """
    Make a regional one-dimensional bin-level expected model by performing
    lowess regression in unlogged space, excluding the first third of the
    region and only using the emprical geometric means there instead.

    Parameters
    ----------
    regional_counts : np.ndarray
        The observed counts matrix for this region.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins.
    """
    # establish size
    size = len(regional_counts)

    # make offdiagonals
    offdiagonals = [np.diag(regional_counts, k=i) for i in range(size)]

    # get empirical expected
    empirical = empirical_binned(regional_counts, log_transform=False)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[dist, count]
                       for dist in range(size)
                       for count in offdiagonals[dist]
                       if np.isfinite(count)])

    # don't try to fit the first third of the region
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_index, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # filter the fit to just the region above the join point
    filtered_fit = np.asarray(filter(lambda x: x[0] >= key_index, fit))

    # construct an array that will represent the joined fit
    joined_fit = np.zeros(size)
    for i in range(key_index):
        joined_fit[i] = empirical[i]
    for i in range(key_index, size):
        query_result = filter(lambda x: x[0] == i, filtered_fit)
        if query_result:
            joined_fit[i] = query_result[0][1]
        else:
            joined_fit[i] = empirical[i]

    return joined_fit


def global_lowess_binned_log_counts(counts, pseudocount=1, frac=0.8,
                                    exclude_near_diagonal=False):
    """
    Make a global one-dimensional bin-level expected model by performing
    lowess regression in log-counts space, excluding the first third of the
    distance scales and only using the emprical geometric means there instead.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    pseudocount : int
        The pseudocount to add to the counts before logging.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # log counts
    log_counts = {region: np.log(counts[region] + pseudocount)
                  for region in counts.keys()}

    # establish total size
    size = max([len(log_counts[region]) for region in log_counts.keys()])

    # make offdiagonals
    offdiagonals = [np.concatenate([np.diag(log_counts[region], k=i)
                                    for region in log_counts.keys()])
                    for i in range(size)]

    # get empirical expected
    empirical = global_empirical_binned(log_counts, log_transform=False)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[dist, count]
                       for dist in range(size)
                       for count in offdiagonals[dist]
                       if np.isfinite(count)])

    # don't try to fit the first third of the region
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_index, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # filter the fit to just the region above the join point
    filtered_fit = np.asarray(filter(lambda x: x[0] >= key_index, fit))

    # construct an array that will represent the joined fit
    joined_fit = np.zeros(size)
    for i in range(key_index):
        joined_fit[i] = empirical[i]
    for i in range(key_index, size):
        query_result = filter(lambda x: x[0] == i, filtered_fit)
        if query_result:
            joined_fit[i] = query_result[0][1]
        else:
            joined_fit[i] = empirical[i]

    # unlog
    joined_fit = [np.exp(x) - pseudocount for x in joined_fit]

    return joined_fit


def global_lowess_binned(counts, frac=0.8, exclude_near_diagonal=False):
    """
    Make a global one-dimensional bin-level expected model by performing
    lowess regression in unlogged space, excluding the first third of the
    distance scales and only using the emprical arithmetic means there instead.

    Parameters
    ----------
    counts : Dict[str, np.ndarray]
        The observed counts dict to fit the model to.
    frac : float
        The lowess smoothing fraction parameter to use.
    exclude_near_diagonal : bool
        If regression or lowess_smooth are True, set this kwarg to True to
        ignore the first third of the distance scales when fitting the model.

    Returns
    -------
    List[float]
        The one-dimensional expected model. The ``i`` th element of the list
        corresponds to the expected value for interactions between loci
        separated by ``i`` bins. The length of this list will match the size of
        the largest region in the input counts dict.
    """
    # establish total size
    size = max([len(counts[region]) for region in counts.keys()])

    # make offdiagonals
    offdiagonals = [np.concatenate([np.diag(counts[region], k=i)
                                    for region in counts.keys()])
                    for i in range(size)]

    # get empirical expected
    empirical = global_empirical_binned(counts, log_transform=False)

    # make data of the form [distance, count], ignoring nans
    data = np.asarray([[dist, count]
                       for dist in range(size)
                       for count in offdiagonals[dist]
                       if np.isfinite(count)])

    # don't try to fit the first third of the region
    key_index = np.int(size / 3) if exclude_near_diagonal else 0
    filtered_data = np.asarray(filter(lambda x: x[0] >= key_index, data))

    # do the lowess fit
    fit = lowess(filtered_data[:, 1], filtered_data[:, 0], frac=frac, it=3,
                 delta=0.01*np.ptp(filtered_data[:, 1]))

    # filter the fit to just the region above the join point
    filtered_fit = np.asarray(filter(lambda x: x[0] >= key_index, fit))

    # construct an array that will represent the joined fit
    joined_fit = np.zeros(size)
    for i in range(key_index):
        joined_fit[i] = empirical[i]
    for i in range(key_index, size):
        query_result = filter(lambda x: x[0] == i, filtered_fit)
        if query_result:
            joined_fit[i] = query_result[0][1]
        else:
            joined_fit[i] = empirical[i]

    return joined_fit


@parallelize_regions
def interpolate_expected(expected_matrix, regional_primermap, distance):
    """
    Interpolate the value of an expected model (represented as a matrix) at an
    arbitrary distance scale.

    Parameters
    ----------
    expected_matrix : np.ndarray
        The expected matrix to use as a source for interpolation.
    regional_primermap : List[Dict[str, Any]]
        The primermap for this region.
    distance : int
        The interaction distance at which to estimate the expected value, in
        base pairs.

    Returns
    -------
    float
        The interpolated expected value, or -1 if ``distance`` is outside of the
        range of the expected model.
    """
    # construct distance matrix
    distance_matrix = make_distance_matrix(regional_primermap)

    # flatten matrices
    flat_distance_matrix = np.array(flatten_regional_counts(distance_matrix))
    flat_expected_matrix = np.array(flatten_regional_counts(expected_matrix))

    # filter nan's
    filtered_distance_matrix = flat_distance_matrix[
        np.isfinite(flat_distance_matrix) & np.isfinite(flat_expected_matrix)]
    filtered_expected_matrix = flat_expected_matrix[
        np.isfinite(flat_distance_matrix) & np.isfinite(flat_expected_matrix)]

    # prepare model
    xp = np.unique(filtered_distance_matrix)
    fp = np.array(
        [np.mean(filtered_expected_matrix[filtered_distance_matrix == x])
         for x in xp])

    # interpolate
    return np.interp(distance, xp, fp, left=-1, right=-1)
