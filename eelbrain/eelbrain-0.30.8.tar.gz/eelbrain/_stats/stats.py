# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Statistics functions that work on numpy arrays."""
import re

import numpy as np
import scipy.stats
from scipy.linalg import inv

from .._data_obj import asfactor, asmodel, Model
from . import opt
from . import vector


FLOAT64 = np.dtype('float64')


def _as_float64(x):
    if x.dtype is FLOAT64:
        return x
    else:
        return x.astype(FLOAT64)


def betas(y, x):
    """Regression coefficients

    Parameters
    ----------
    y : array  [n_cases, ...]
        Dependent measure.
    x : Model
        Predictors

    Returns
    -------
    betas : array  [n_predictors, ...]
        Beta coefficients for the regression. The first beta is always the
        intercept (see Model).
    """
    n = len(y)
    x = asmodel(x)
    p = x._parametrize()
    shape = (x.df,) + y.shape[1:]
    y_ = _as_float64(y).reshape((n, -1))
    out = np.empty(shape)
    out_ = out.reshape((x.df, -1))
    opt.lm_betas(y_, p.x, p.projector, out_)
    return out


def corr(y, x, out=None, perm=None):
    """Correlation parameter map

    Parameters
    ----------
    y : array_like, shape = (n_cases, ...)
        Dependent variable with case in the first axis and case mean zero.
    x : array_like, shape = (n_cases, )
        Covariate.

    Returns
    -------
    r : array, shape = (...)
        The correlation. Occurrence of NaN due to 0 variance in either y or x
        are replaced with 0.
    """
    if out is None and y.ndim > 1:
        out = np.empty(y.shape[1:])
    if perm is not None:
        x = x[perm]

    z_x = scipy.stats.zscore(x, ddof=1)
    z_x.shape = (len(x),) + (1,) * (y.ndim - 1)
    z_y = scipy.stats.zscore(y, ddof=1)
    z_y *= z_x
    out = z_y.sum(0, out=out)
    out /= len(x) - 1

    # replace NaN values
    isnan = np.isnan(out)
    if np.any(isnan):
        if np.isscalar(out):
            out = 0
        else:
            out.place(isnan, 0)
    return out


def lm_betas_se_1d(y, b, p):
    """Regression coefficient standard errors

    Parameters
    ----------
    y : array  [n_cases, n_tests]
        Dependent measure.
    b : array  [n_predictors, n_tests]
        Regression coefficients.
    p : Parametrization
        Parametrized model.
    """
    v = np.einsum('i...,i...', y, y)
    y_hat = b.T.dot(p.x.T).T
    v -= np.einsum('i...,i...', y_hat, y)
    v /= len(y) - p.x.shape[1]  # Var(e)
    var_b = v * p.g.diagonal()[:, None]
    return np.sqrt(var_b, var_b)


def lm_t(y, p):
    """Calculate t-values for regression coefficients

    Parameters
    ----------
    y : array  [n_cases, ...]
        Dependent measure.
    p : Parametrization
        Parametrized model.
    """
    y_ = y.reshape((len(y), -1))
    b = p.projector.dot(y_)
    b /= lm_betas_se_1d(y_, b, p)
    return b.reshape((len(b), ) + y.shape[1:])


def residual_mean_square(y, x=None):
    """Mean square of the residuals

    Parameters
    ----------
    y : array [n, ...]
        Dependent measure.
    x : Model
        Model to account for a part of the variance.

    Returns
    -------
    mean_square : array [...]
        Estimate of the mean square within x.
    """
    n = len(y)
    assert n > 1, "Can't compute dispersion from a single measurement"
    out = np.empty(y.shape[1:])
    out_ = out.ravel()
    y_ = y.reshape((n, -1))
    if x is None:
        opt.ss(y_, out_)
        out_ /= n - 1
    else:
        x = asmodel(x)
        res = residuals(y_, x)
        opt.sum_square(res, out_)
        out_ /= x.df_error
    return out


def residuals(y, x):
    """Calculate residuals of y regressed on x (over the first axis)

    Parameters
    ----------
    y : array (n, ...)
        Data.
    x : Model
        Predictors.

    Returns
    -------
    residuals : array (...)
        Residuals.
    """
    n = len(y)
    x = asmodel(x)
    p = x._parametrize()
    res = np.empty(y.shape)
    y_ = y.reshape((n, -1))
    res_ = res.reshape((n, -1))
    opt.lm_res(y_, p.x, p.projector, res_)
    return res


def rms(a, axis=None):
    """Root mean square

    Parameters
    ----------
    a : array_like
        Data.
    axis : None | int | tuple of ints
        Axis or axes over which to calculate the RMS.
        The default (`axis` = `None`) is the RMS over all the dimensions of
        the input array.
    """
    square = np.square(a)
    out = square.mean(axis)
    if np.isscalar(out):
        return np.sqrt(out)
    else:
        return np.sqrt(out, out)


def rmssd(y):
    """Root mean square of successive differences

    Used for heart rate variance analysis.
    """
    assert np.ndim(y) == 1
    N = len(y)
    assert N > 1
    dy = np.diff(y)
    x = N / (N - 1) * np.sum(dy ** 2)
    return np.sqrt(x)


class SEM:

    def __init__(self, y, x=None, match=None):
        """Standard error of the mean (SEM)

        Parameters
        ----------
        y : array (n, ...)
            Data, first dimension reflecting cases.
        x : Categorial
            Categorial predictor for using pooled variance.
        match : Categorial
            Within-subject SEM.

        Notes
        -----
        See Loftus and Masson (1994).
        """
        if x is None:
            n = len(y)
            model = match
        else:
            x = asfactor(x)
            n = x._cellsize()
            if isinstance(n, dict):
                raise NotImplementedError("SEM for unequal cell sizes")
            model = x if match is None else x + match
        sem = residual_mean_square(y, model)
        sem /= n
        np.sqrt(sem, sem)
        self.n = n
        self.model = model
        self.sem = sem

    def ci(self, confidence):
        """Confidence interval based on the inverse t-test

        Parameters
        ----------
        confidence : scalar
            Confidence in the interval (i.e., .95 for 95% CI).

        Returns
        -------
        ci : array [...]
            Confidence interval (i.e., the mean of y lies within m +- ci with the
            specified confidence).

        Notes
        -----
        See `<http://en.wikipedia.org/wiki/Confidence_interval#Statistical_hypothesis_testing>`_
        """
        if self.model is None:
            df = self.n - 1
        elif isinstance(self.model, Model):
            df = self.model.df_error
        else:
            df = Model(self.model).df_error
        return self.sem * scipy.stats.t.isf((1 - confidence) / 2, df)


def t_1samp(y, out=None):
    "T-value for 1-sample t-test"
    n_cases = len(y)
    if out is None:
        out = np.empty(y.shape[1:])

    if out.ndim == 1:
        y_flat = y
        out_flat = out
    else:
        y_flat = y.reshape((n_cases, -1))
        out_flat = out.ravel()

    opt.t_1samp(y_flat, out_flat)
    return out


def t2_1samp(y, rotation=None, out=None):
    """T**2-value for 1-sample T**2-test

    Parameters
    ----------
    y : ndarray
        Vector field, shape ``(n_case, n_dims [, ...])``.
    rotation : ndarray
        Rotation matrix (for permutation).
    out : ndarray
        Container for result. Needs shape ``...``.
    """
    if y.ndim <= 1:
        raise ValueError(f'y with shape {y.shape}: T**2 statistic needs vector valued samples.')
    n_cases = y.shape[0]
    n_dims = y.shape[1]
    if out is None:
        out = np.empty(y.shape[2:])
    else:
        assert out.shape == y.shape[2:]

    if out.ndim == 1:
        y_flat = y
        out_flat = out
    else:
        y_flat = y.reshape((n_cases, n_dims, -1))
        out_flat = out.ravel()

    if rotation is None:
        vector.t2_stat(y_flat, out_flat)
    else:
        assert rotation.shape == (n_cases, 3, 3)
        vector.t2_stat_rotated(y_flat, rotation, out_flat)
    return out


def t_ind(y, group, out=None, perm=None):
    "T-value for independent samples t-test, assuming equal variance"
    n_cases = len(y)
    if out is None:
        out = np.empty(y.shape[1:])

    if perm is not None:
        group = group[perm]

    if out.ndim == 1:
        y_flat = y
        out_flat = out
    else:
        y_flat = y.reshape((n_cases, -1))
        out_flat = out.ravel()

    opt.t_ind(y_flat, out_flat, group)
    return out


def ftest_f(p, df_num, df_den):
    "F values for given probabilities."
    p = np.asanyarray(p)
    f = scipy.stats.f.isf(p, df_num, df_den)
    return f


def ftest_p(f, df_num, df_den):
    "P values for given f values."
    f = np.asanyarray(f)
    p = scipy.stats.f.sf(f, df_num, df_den)
    return p


def rtest_p(r, df):
    # http://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient#Inference
    r = np.asanyarray(r)
    t = r * np.sqrt(df / (1 - r ** 2))
    p = ttest_p(t, df)
    return p


def rtest_r(p, df):
    # http://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient#Inference
    p = np.asanyarray(p)
    t = ttest_t(p, df)
    r = t / np.sqrt(df + t ** 2)
    return r


def ttest_p(t, df, tail=0):
    """Two tailed probability

    Parameters
    ----------
    t : array_like
        T values.
    df : int
        Degrees of freedom.
    tail : 0 | 1 | -1
        Which tail of the t-distribution to consider:
        0: both (two-tailed);
        1: upper tail (one-tailed);
        -1: lower tail (one-tailed).
    """
    t = np.asanyarray(t)
    if tail == 0:
        t = np.abs(t)
    elif tail == -1:
        t = -t
    elif tail != 1:
        raise ValueError("tail=%r" % tail)
    p = scipy.stats.t.sf(t, df)
    if tail == 0:
        p *= 2
    return p


def ttest_t(p, df, tail=0):
    """Positive t value for a given probability

    Parameters
    ----------
    p : array_like
        Probability.
    df : int
        Degrees of freedom.
    tail : 0 | 1 | -1
        One- or two-tailed t-distribution (the return value is always positive):
        0: two-tailed;
        1 or -1: one-tailed).
    """
    p = np.asanyarray(p)
    if tail == 0:
        p = p / 2
    t = scipy.stats.t.isf(p, df)
    return t


def variability(y, x, match, spec, pool, cells=None):
    """Calculate data variability

    Parameters
    ----------
    y : array
        Dependent measure.
    x : None | Categorial
        Cells for pooling variance.
    match : Factor
        Calculate variability for related measures (Loftus & Masson 1994).
    spec : str
        Specification of the kind of variability estimate. Contains an optional
        number, an optional percent-sign, and a kind ('ci' or 'sem'). Examples:
        'ci': 95% confidence interval;
        '99%ci': 99% confidence interval (default);
        '2sem': 2 standard error of the mean.
    pool : bool
        Pool the variability to create a single estimate (as opposed to one for
        each cell in x).
    cells : list of cells
        Estimate variance in these cells of ``x`` (default ``x.cells``).

    Returns
    -------
    var : scalar | array
        Variability estimate. A single estimate if errors are pooled, otherwise
        an estimate for every cell in x.
    """
    m = re.match("^([.\d]*)(\%?)(ci|sem)$", spec.lower())
    if m is None:
        raise ValueError("error=%r" % (spec,))
    scale, perc, kind = m.groups()
    if scale:
        scale = float(scale)
        if perc:
            scale /= 100
    elif kind == 'ci':
        scale = .95
    else:
        scale = 1

    if x is None:
        if match is not None and match.df == len(match) - 1:
            raise ValueError("Can't calculate within-subject error because the "
                             "match predictor explains all variability")
    elif not pool and cells is None:
        cells = x.cells

    y = np.asarray(y, np.float64)
    if kind == 'ci':
        if pool or x is None:
            out = SEM(y, x, match).ci(scale)
        else:
            out = np.array([SEM(y[x == cell]).ci(scale) for cell in cells])
    elif kind == 'sem':
        if pool or x is None:
            out = SEM(y, x, match).sem
        else:
            out = np.array([SEM(y[x == cell]).sem for cell in cells])

        if scale != 1:
            out *= scale
    else:
        raise RuntimeError("kind=%r" % (kind,))

    # return scalars for 1d-arrays
    if out.ndim == 0:
        return out.item()
    else:
        return out


def xsinv(x):
    xt = x.T
    return inv(xt.dot(x)).dot(xt)
