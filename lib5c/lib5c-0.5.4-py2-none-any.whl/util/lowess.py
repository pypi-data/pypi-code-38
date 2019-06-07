"""
Module for performing lowess fitting. Consists mostly of a convenience wrapper
around ``statsmodels.nonparametric.smoothers_lowess.lowess()``.
"""

import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess


def lowess_fit(x, y, logx=False, logy=False, left_boundary=0,
               right_boundary=None, frac=0.3, delta=0.01):
    """
    Opinionated convenience wrapper for lowess smoothing.

    Parameters
    ----------
    x, y : np.ndarray
        The x and y values to fit, respectively.
    logx, logy : bool
        Pass True to perform the fit on the scale of ``log(x)`` and/or
        ``log(y)``, respectively.
    left_boundary, right_boundary : float, optional
        Allows specifying boundaries for the fit, in the original ``x`` space.
        If a float is passed, the returned fit will return the farthest left or
        farthest right lowess-estimated ``y_hat`` (from the original fitting
        set) for all points which are left or right of the specified left or
        right boundary point, respectively.
    frac : float
        The lowess smoothing fraction to use.
    delta : float
        Distance (on the scale of ``x`` or ``log(x)``) within which to use
        linear interpolation when constructing the initial fit, expressed as a
        fraction of the range of ``x`` or ``log(x)``.

    Returns
    -------
    function
        This function takes in ``x`` values on the original ``x`` scale and
        returns estimated ``y`` values on the original ``y`` scale (regardless
        of what is passed for ``logx`` and ``logy``). This function will still
        return sane estimates for ``y`` even at points not in the original
        fitting set by performing linear interpolation in the space the fit was
        performed in.

    Notes
    -----
    No filtering of input values is performed; clients are expected to handle
    this if desired. NaN values should not break the function, but ``x`` points
    with zero values passed when ``logx`` is True are expected to break the
    function.

    Linear interpolation between x-values in the original fitting set is used to
    provide a familiar functional interface to the fitted function.

    The default value of the ``delta`` parameter is set to be non-zero, matching
    the behavior of lowess smoothing in R and improving performance.

    Boundary conditions on the fitted function are exposed, mostly as a
    convenience for points where ``x == 0`` when fitting was performed on the
    scale of ``log(x)``.
    """
    if logx:
        x = np.log(x)
    if logy:
        y = np.log(y)

    res = lowess(y, x, frac=frac, delta=(np.nanmax(x) - np.nanmin(x)) * delta)
    sorted_x = res[:, 0]
    sorted_y_hat = res[:, 1]

    def fit(x_star):
        if logx:
            new_x = np.log(x_star)
        else:
            new_x = x_star
        y_hat = np.interp(new_x, sorted_x, sorted_y_hat)
        if left_boundary is not None:
            y_hat[x_star <= left_boundary] = sorted_y_hat[0]
        if right_boundary is not None:
            y_hat[x_star >= right_boundary] = sorted_y_hat[-1]
        if logy:
            y_hat = np.exp(y_hat)
        return y_hat

    return fit


def group_fit(x, y, logx=False, logy=False, agg='median', left_boundary=0,
              right_boundary=None, n_windows=100, window_width=0.2):
    """
    Simpler alternative to lowess fitting using a sliding window mean.

    Parameters
    ----------
    x, y : np.ndarray
        The x and y values to fit, respectively.
    logx, logy : bool
        Pass True to perform the fit on the scale of ``log(x)`` and/or
        ``log(y)``, respectively.
    agg : {'median', 'mean', 'lowess'}
        The function to use to aggregate within groups.
    left_boundary, right_boundary : float, optional
        Allows specifying boundaries for the fit, in the original ``x`` space.
        If a float is passed, the returned fit will return the farthest left or
        farthest right lowess-estimated ``y_hat`` (from the original fitting
        set) for all points which are left or right of the specified left or
        right boundary point, respectively.
    n_windows : int
        The number of windows to use (spaced uniformly across the range of
        ``x``).
    window_width : float
        The width of each window, defined as a fraction of its x-value.

    Returns
    -------
    function
        This function takes in ``x`` values on the original ``x`` scale and
        returns estimated ``y`` values on the original ``y`` scale (regardless
        of what is passed for ``logx`` and ``logy``). This function will still
        return sane estimates for ``y`` even at points not in the original
        fitting set by performing linear interpolation in the space the fit was
        performed in.
    """
    if logx:
        x = np.log(x)
    if logy:
        y = np.log(y)

    fn = {'median': np.median, 'mean': np.mean, 'lowess': lowess_agg}[agg]
    centers = np.linspace(x.min(), x.max(), n_windows)
    windows = [y[np.abs((center - x) / x) < window_width] for center in centers]
    y_hat = np.array([fn(window) for window in windows])

    def fit(x_star):
        if logx:
            new_x = np.log(x_star)
        else:
            new_x = x_star
        y_hat_star = np.interp(new_x, centers, y_hat)
        if left_boundary is not None:
            y_hat_star[x_star <= left_boundary] = y_hat[0]
        if right_boundary is not None:
            y_hat_star[x_star >= right_boundary] = y_hat[-1]
        if logy:
            y_hat_star = np.exp(y_hat_star)
        return y_hat_star

    return fit


def constant_fit(x, y, logx=False, logy=False, agg='median'):
    """
    Same signature as ``lowess_fit()`` and ``group_fit()``, but instead of
    fitting ``y`` against ``x``, simply applies an aggregating function to
    ``y``.

    Parameters
    ----------
    x : Any
        Ignored, present only for signature parity with other fitters.
    y : np.ndarray
        The y values to fit.
    logx : Any
        Ignored, present only for signature parity with other fitters.
    logy : bool
        Pass True to perform the fit on the scale of ``log(y)``.
    agg : {'median', 'mean', 'lowess'}
        The function to use to aggregate y-values.

    Returns
    -------
    function
        This function takes in ``x`` values, ignores them completely, and simply
        returns the constant estimated ``y`` value on the original ``y`` scale
        (regardless of what is passed for ``logy``).
    """
    if logy:
        y = np.log(y)

    fn = {'median': np.median, 'mean': np.mean, 'lowess': lowess_agg}[agg]
    constant = fn(y)

    def fit(x_star):
        y_hat_star = constant
        if logy:
            y_hat_star = np.exp(y_hat_star)
        return y_hat_star

    return fit


def lowess_agg(y, it=3):
    """
    Performs an aggregation operation equivalent to lowess. Should behave like
    an outlier-resistant mean.

    Parameters
    ----------
    y : np.ndarray
        The values to aggregate.
    it : int
        The number of residual-based reweightings to perform.

    Returns
    -------
    float
        The lowess-implemented outlier-resistant mean.
    """
    w = np.ones_like(y, dtype=float)
    yest = None
    if it < 0:
        raise ValueError('iteration number cannot be negative')
    for _ in range(it+1):
        yest = np.average(y, weights=w)
        residuals = y - yest
        s = np.median(np.abs(residuals))
        w = np.clip(residuals / (6.0 * s), -1, 1)
        w = (1 - w ** 2) ** 2
    return yest
