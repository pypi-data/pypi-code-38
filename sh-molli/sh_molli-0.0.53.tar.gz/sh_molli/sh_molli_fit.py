# python module to fit (sh)MOLLI data
#
# exp_fit function based on pull request to scipy
# https://github.com/scipy/scipy/pull/9158/files
# Added return of sum-squared error with the fitted parameters

import numpy as np
from numpy import (
    argsort, asfarray, cumsum, diff, empty, empty_like, exp, log,
    square,
)
from numpy.linalg import inv

import math
from scipy.optimize import curve_fit
from scipy import array
    
# Define fit function
# This will fit the T1 curve to the data
def fit_shmolli(x, a, b, t):
    return ( a - b*pow(math.e, -x/t) )

def my_fit(x,y,ff=fit_shmolli):
    guess = [1000, 1000, 1000]
    params = curve_fit(ff, x, y , p0=guess, method='trf', bounds=(0, 10000), maxfev=10000)
    [a,b,t] = params[0]
    sse = (sum(pow(array(y) - [ff(xi,a,b,t) for xi in array(x)], 2)))
    return [a,b,t,sse]

def exp_fit(x, y, sorted=True):
    """
    Fit an exponential curve to raveled 1D data.

    This algorithm does not require any a-priori knowledge of the data,
    such as the intercept. The fitting parameters are comptued for:

    .. math::

       y = A + Be^{Cx}

    Parameters
    ----------
    x : array-like
        The x-values of the data points. The fit will be performed on a
        raveled version of this array.
    y : array-like
        The y-values of the data points corresponding to `x`. Must be
        the same size as `x`. The fit will be performed on a raveled
        version of this array.
    sorted : bool
        Set to True if `x` is already monotonically increasing or
        decreasing. If False, x will be sorted into increasing order,
        and y will be sorted along with it.

    Return
    ------
    a, b, c : array
        A 3-element array of optimized fitting parameters. The first
        element is the additive bias, the second the multiplicative, and
        the third the exponential.

    Notes
    -----
    The fit is computed non-iteratively in a single pass. It can be used
    to initialize other regression methods based on different
    optimization criteria. The algorithm and the theory behind it is
    presented in the paper below.

    References
    ----------
    Jacquelin, Jean. REGRESSIONS Et EQUATIONS INTEGRALES 14 Jan. 2009, pp. 1518., https://www.scribd.com/doc/14674814/Regressions-et-equations-integrales
    """
    x = asfarray(x).ravel()
    y = asfarray(y).ravel()
    if x.size != y.size:
        raise ValueError('x and y must be the same size')
    if not sorted:
        # Is there a better way to do this in scipy?
        ind = argsort(x)
        x = x[ind]
        y = y[ind]

    s = empty_like(y)
    s[0] = 0
    s[1:] = cumsum(0.5 * (y[1:] + y[:-1]) * diff(x))
    # This might be better: Needs a benchmark
    #s[1:] = y[:-1]
    #s[1:] += y[1:]
    #s[1:] *= np.diff(x)
    #s *= 0.5
    #s = np.cumsum(s)

    xn = x - x[0]
    yn = y - y[0]

    sx2 = square(xn).sum()
    sxs = (xn * s).sum()
    sys = (yn * s).sum()
    ss2 = square(s).sum()
    sxy = (xn * yn).sum()

    out = empty(3, dtype=float)

    _, out[2] = inv([[sx2, sxs], [sxs, ss2]]).dot([[sxy], [sys]])

    ex = exp(out[2] * x)

    se1 = ex.sum()
    se2 = square(ex).sum()
    sy0 = y.sum()
    sye = (y * ex).sum()

    out[0], out[1] = inv([[x.size, se1], [se1, se2]]).dot([[sy0], [sye]])
    
    sse = sum(square(out[0] + out[1]*exp(out[2]*x) - y))

    #return out, sse
    return [out[0],-1*out[1],-1/out[2],sse]