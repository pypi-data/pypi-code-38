"""
Module providing utilities for defining and constructing filter functions.
"""

import numpy as np
from scipy.stats import gmean, norm


def make_filter_function(function='gmean', threshold=0.0, norm_order=1,
                         bin_width=4000, sigma=12000.0, inverse=False,
                         gaussian=False):
    """
    Convenience function for quickly constructing filtering functions with
    desired properties.

    Parameters
    ----------
    function : {'sum', 'median', 'amean', 'gmean'}
        The aggregation function to use. This is the operation that will be
        applied to all points in the neighborhood, after weighting their values
        if appropriate.
    threshold : float
        If less than this fraction of the values in a neighborhood are
        non-infinite, the filter function will return nan for that neighborhood.
    norm_order : int
        The order of p-norm to use when computing distances.
    bin_width : int
        The width of each bin in base pairs. This value is used to scale certain
        weights.
    sigma : float
        The value to use for the standard deviation of the Gaussian when using
        Gaussian weights.
    inverse : bool
        Pass True to use "inverse" weights as in Yaffe and Tanay 2011.
    gaussian : bool
        Pass True to use Gaussian weights with standard deviation ``sigma``.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    if function == 'sum':
        filter_function = simple_sum(threshold)
    elif function == 'median':
        filter_function = median(threshold)
    elif function == 'amean':
        if gaussian:
            filter_function = amean_gaussian(sigma=sigma,
                                             norm_ord=norm_order,
                                             check_threshold=threshold)
        elif inverse:
            filter_function = amean_inverse(
                bin_width=bin_width,
                norm_ord=norm_order,
                check_threshold=threshold)
        else:
            filter_function = arithmetic_mean(threshold)
    elif function == 'gmean':
        if gaussian:
            filter_function = gmean_gaussian(sigma=sigma,
                                             norm_ord=norm_order,
                                             check_threshold=threshold)
        elif inverse:
            filter_function = gmean_inverse(
                bin_width=bin_width,
                norm_ord=norm_order,
                check_threshold=threshold)
        else:
            filter_function = geometric_mean(threshold)
    else:
        raise ValueError('function %s not implemented' % function)

    return filter_function


def check_neighboorhood_nonnan(neighborhood, threshold):
    """
    Check to see if a neighborhood clears as specified non-nan fraction
    threshold.

    Parameters
    ----------
    neighborhood : List[Dict[str, Any]]
        A list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    threshold : float
        If less than this fraction of the values in the neighborhood are
        non-infinite, the neighborhood fails the check.

    Returns
    -------
    bool
        True if this neighborhood clears the threshold, otherwise False.
    """
    num_nan = len([1 for i in neighborhood if ~np.isfinite(i['value'])])
    total = len(neighborhood)

    if total == 0 or float(num_nan) / total <= threshold:
        return False
    return True


def check_neighboorhood_positive(neighborhood, threshold):
    """
    Check to see if a neighborhood clears as specified positive fraction
    threshold.

    Parameters
    ----------
    neighborhood : List[Dict[str, Any]]
        A list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    threshold : float
        If less than this fraction of the values in the neighborhood are
        positive, the neighborhood fails the check.

    Returns
    -------
    bool
        True if this neighborhood clears the threshold, otherwise False.
    """
    num_positive = len([1 for i in neighborhood if i['value'] > 0])
    total = len(neighborhood)

    if total == 0 or float(num_positive) / total <= threshold:
        return False
    return True


def value_filter_function(function, function_kwargs=None, pseudocount=0,
                          check_function=None, check_threshold=None):
    """
    Constructs a filter function that passes the values in the neighborhood to
    an aggregation function.

    Parameters
    ----------
    function : Callable[Sequence[float], float]
        The aggregation function to use on the values in each neighborhood.
    function_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to ``function``.
    pseudocount : float
        A pseudocount to be added to the values before applying the aggregation
        function. Useful if the aggregation function has catastrophic behavior
        when one input value is zero.
    check_function : Optional[Callable[[List[Dict[str, Any]], float], bool]]
        A function that takes in a neighborhood and a threshold value and
        performs some sort of test on the neighborhood, returning False if the
        filter function should return NaN for the neighborhood because it fails
        some critical condition.
    check_threshold : float
        The threshold to pass as the second arg to ``check_function``.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    # resolve function_kwargs
    if function_kwargs is None:
        function_kwargs = {}

    def filter_function(neighborhood):
        # honor check API
        if check_function is not None:
            if not check_function(neighborhood, check_threshold):
                return np.nan
        # extract values while adding a pseudocount
        values = [i['value'] + pseudocount
                  for i in neighborhood
                  if np.isfinite(i['value'])]

        # compute result based on function
        if values:
            return function(values, **function_kwargs)
        else:
            return np.nan

    return filter_function


def norm_filter_function(weighted_function, norm_function, weighted_kwargs=None,
                         norm_kwargs=None, pseudocount=0, check_function=None,
                         check_threshold=None):
    """
    Constructs a filter function that passes the value and some distance norm
    (as specified by ``norm_function``) for each point in the neighborhood to a
    special aggregation function capable of performing weighted aggregation
    based on these distances.

    Parameters
    ----------
    weighted_function : Callable[[List[Dict[str, float]], float]
        A special aggregation function that takes in a list of points
        represented as dicts with the following structure::

            {
                'value': float,
                'dist': float
            }

        where 'value' is the interaction value at that point and 'dist' is its
        scalar distance from the neighborhood. This function should then return
        a float representing the aggregate value of the neighborhood, weighted
        using the distances.
    norm_function : Callable[[Tuple[int]], float]
        A function that takes in a tuple of ints representing the x- and y-axis
        distances of a point to the neighborhood and returns a scalar value
        representing the distance.
    weighted_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to ``weighted_function``.
    norm_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to ``norm_function``.
    pseudocount : float
        A pseudocount to be added to the values before applying the aggregation
        function. Useful if the aggregation function has catastrophic behavior
        when one input value is zero.
    check_function : Optional[Callable[[List[Dict[str, Any]], float], bool]]
        A function that takes in a neighborhood and a threshold value and
        performs some sort of test on the neighborhood, returning False if the
        filter function should return NaN for the neighborhood because it fails
        some critical condition.
    check_threshold : float
        The threshold to pass as the second arg to ``check_function``.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    # resolve function_kwargs and norm_kwargs
    if weighted_kwargs is None:
        weighted_kwargs = {}
    if norm_kwargs is None:
        norm_kwargs = {}

    def filter_function(neighborhood):
        # honor check API
        if check_function is not None:
            if not check_function(neighborhood, check_threshold):
                return np.nan

        # prepare value and distance for function
        values_distances = [{'value': i['value'] + pseudocount,
                             'dist' : norm_function((i['x_dist'], i['y_dist']),
                                                    **norm_kwargs)}
                            for i in neighborhood
                            if np.isfinite(i['value'])]

        # compute results based on function
        if values_distances:
            return weighted_function(values_distances, **weighted_kwargs)
        else:
            return np.nan

    return filter_function


def weighted_values_distances_function(weighting_function,
                                       aggregating_function,
                                       weighting_kwargs=None,
                                       aggregating_kwargs=None,
                                       cache=True):
    """
    Constructs a weighted aggregation function appropriate for use with
    ``norm_filter_function()``.

    Parameters
    ----------
    weighting_function : Callable[[float], float]
        A function that takes in a distance and returns a weight.
    aggregating_function : Callable[[Sequence[float], Sequence[float]], float]
        A special aggregating function that takes in the values and the weights
        as parallel vectors and returns the aggregated value.
    weighting_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to ``weighting_function``.
    aggregating_kwargs : Optional[Dict[str, Any]]
        Kwargs to be passed to ``aggregating_function``.
    cache : bool
        Pass True to make the returned function use a cache to avoid recomputing
        expensive weighting function calls.

    Returns
    -------
    Callable[[List[Dict[str, float]], float]
        A special aggregation function that takes in a list of points
        represented as dicts with the following structure::

            {
                'value': float,
                'dist': float
            }

        where 'value' is the interaction value at that point and 'dist' is its
        scalar distance from the neighborhood. This function returns a float
        representing the aggregate value of the neighborhood, weighted using the
        distances.
    """
    # resolve weighting_kwargs and aggregating_kwargs
    if weighting_kwargs is None:
        weighting_kwargs = {}
    if aggregating_kwargs is None:
        aggregating_kwargs = {}

    # create cache
    if cache:
        cached_weights = {}

    def weighted_function(values_distances):
        if cache:
            weights = []
            for i in values_distances:
                if i['dist'] in cached_weights:
                    weights.append(cached_weights[i['dist']])
                else:
                    weight = weighting_function(i['dist'], **weighting_kwargs)
                    cached_weights[i['dist']] = weight
                    weights.append(weight)
            weights = np.array(weights)
        else:
            weights = np.array([weighting_function(i['dist'],
                                                   **weighting_kwargs)
                                for i in values_distances])
        values = np.array([i['value'] for i in values_distances])
        return aggregating_function(values, weights, **aggregating_kwargs)

    return weighted_function


def inverse_weighting_function(distance, bin_width=None):
    """
    The "inverse" weighting function used in Yaffe and Tanay 2011.

    Parameters
    ----------
    distance : float
        The distance to compute a weight for, in base pairs.
    bin_width : Optional[int]
        The bin width in base pairs. Used to make results equivalent to Yaffe
        and Tanay 2011 by scaling ``distance`` to units of bins. Pass None to
        simply leave the distance in units of base pairs

    Returns
    -------
    float
        A weight appropriate for this distance.
    """
    if bin_width is not None:
        return 1 / ((distance / float(bin_width)) + 1)
    return float(1) / (distance + 1)


def amean_inverse(bin_width=4000, norm_ord=1, check_threshold=0.2):
    """
    Constructs a filter function that uses the arithmetic mean with "inverse"
    weights as the aggregating function and a p-norm as the norm function.

    Parameters
    ----------
    bin_width : int
        The bin width in base pairs.
    norm_ord : int
        The order of the p-norm to use to convert (x-dist, y-dist) vectors to
        scalar distances.
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return norm_filter_function(
        weighted_function=weighted_values_distances_function(
            weighting_function=inverse_weighting_function,
            aggregating_function=weighted_amean,
            weighting_kwargs={'bin_width': bin_width}
        ),
        norm_function=np.linalg.norm,
        norm_kwargs={'ord': norm_ord},
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def gmean_inverse(bin_width=4000, norm_ord=1, check_threshold=0.2):
    """
    Constructs a filter function that uses the geometric mean with "inverse"
    weights as the aggregating function and a p-norm as the norm function.

    Parameters
    ----------
    bin_width : int
        The bin width in base pairs.
    norm_ord : int
        The order of the p-norm to use to convert (x-dist, y-dist) vectors to
        scalar distances.
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return norm_filter_function(
        weighted_function=weighted_values_distances_function(
            weighting_function=inverse_weighting_function,
            aggregating_function=weighted_gmean,
            weighting_kwargs={'bin_width': bin_width}
        ),
        norm_function=np.linalg.norm,
        norm_kwargs={'ord': norm_ord},
        pseudocount=1,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def weighted_amean(values, weights):
    """
    Weighted version of the arithmetic mean.

    Parameters
    ----------
    values : Sequence[float]
        The values to aggregate.
    weights : Sequence[float]
        The weights for each value.

    Returns
    -------
    float
        The weighted arithmetic mean of the values given the weights.
    """
    normed_weights = weights / weights.sum()
    return np.dot(values, normed_weights)


def weighted_gmean(values, weights):
    """
    Weighted version of the geometric mean.

    Parameters
    ----------
    values : Sequence[float]
        The values to aggregate.
    weights : Sequence[float]
        The weights for each value.

    Returns
    -------
    float
        The weighted geometric mean of the values given the weights.
    """
    return np.exp(np.dot(np.log(values), weights) / np.sum(weights))


def amean_gaussian(sigma=1000.0, norm_ord=1, check_threshold=0.2):
    """
    Constructs a filter function that uses the arithmetic mean with Gaussian
    weights as the aggregating function and a p-norm as the norm function.

    Parameters
    ----------
    sigma : float
        The standard deviation to use for the Gaussian when assigning weights.
    norm_ord : int
        The order of the p-norm to use to convert (x-dist, y-dist) vectors to
        scalar distances.
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return norm_filter_function(
        weighted_function=weighted_values_distances_function(
            weighting_function=norm.pdf,
            aggregating_function=weighted_amean,
            weighting_kwargs={'scale': sigma}
        ),
        norm_function=np.linalg.norm,
        norm_kwargs={'ord': norm_ord},
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def gmean_gaussian(sigma=1000.0, norm_ord=1, check_threshold=0.2):
    """
    Constructs a filter function that uses the geometric mean with Gaussian
    weights as the aggregating function and a p-norm as the norm function.

    Parameters
    ----------
    sigma : float
        The standard deviation to use for the Gaussian when assigning weights.
    norm_ord : int
        The order of the p-norm to use to convert (x-dist, y-dist) vectors to
        scalar distances.
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return norm_filter_function(
        weighted_function=weighted_values_distances_function(
            weighting_function=norm.pdf,
            aggregating_function=weighted_gmean,
            weighting_kwargs={'scale': sigma}
        ),
        norm_function=np.linalg.norm,
        norm_kwargs={'ord': norm_ord},
        pseudocount=1,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def geometric_mean(check_threshold=0.2):
    """
    Constructs a filter function that uses the unweighted geometric mean as the
    aggregating function.

    Parameters
    ----------
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return value_filter_function(
        function=gmean,
        pseudocount=1,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def arithmetic_mean(check_threshold=0.2):
    """
    Constructs a filter function that uses the unweighted arithmetic mean as the
    aggregating function.

    Parameters
    ----------
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return value_filter_function(
        function=np.mean,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def simple_sum(check_threshold=0.2):
    """
    Constructs a filter function that uses a simple sum as the aggregating
    function.

    Parameters
    ----------
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return value_filter_function(
        function=np.sum,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )


def median(check_threshold=0.2):
    """
    Constructs a filter function that uses the median as the aggregating
    function.

    Parameters
    ----------
    check_threshold : float
        If less than this fraction of the values in a neighborhood are
        positive, the filter function will return NaN.

    Returns
    -------
    Callable[[List[Dict[str, Any]]], float]
        The constructed filter function. This function takes in a "neighborhood"
        and returns the filtered value given that neighborhood. A neighborhood
        is represented as a list of "nearby points" where each nearby point is
        represented as a dict of the following form::

            {
                'value': float,
                'x_dist': int,
                'y_dist': int
            }

        where 'value' is the value at the point and 'x_dist' and 'y_dist' are
        its distances from the center of the neighborhood along the x- and
        y-axis, respectively, in base pairs.
    """
    return value_filter_function(
        function=np.median,
        check_function=check_neighboorhood_positive,
        check_threshold=check_threshold
    )
