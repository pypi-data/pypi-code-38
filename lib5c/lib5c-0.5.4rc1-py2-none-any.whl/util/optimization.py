"""
Module containing utility functions for curve optimization and root finding.
"""

import warnings
from collections import namedtuple

import numpy as np


def quadratic_log_log_fit(x, y):
    """
    Fit a pure-quadratic function ``y = a * x**2`` using a loss function in
    log-log space.

    Parameters
    ----------
    x : np.ndarray
        Flat vector of ``x`` values to fit.
    y : np.ndarray
        Flat vector of ``y`` values to fit.

    Returns
    -------
    np.poly1d
        The fitted function.
    """
    a = np.exp(np.nanmean(np.log(y + 1) - 2 * np.log(x + 1)))
    return np.poly1d([a, 0, 0])


def array_newton(func, x0, fprime=None, args=(), tol=1.48e-8, maxiter=50,
                 fprime2=None, failure_idx_flag=None):
    """
    Finds roots of a scalar function ``func`` given a vector of initial guesses
    ``x0`` and parallel vectors of additional arguments to ``func`` (passed in
    ``args``) in a vectorized fashion. Similar to calling
    ``scipy.optimize.newton()`` in a for loop, but more performant and more
    legible. Bootlegged from https://github.com/scipy/scipy/pull/8357 preceeding
    its official release.

    Parameters
    ----------
    func : function
        The scalar function to minimize. Should be vectorized (when a vector of
        independent inputs is passed it should return a vector of independent
        outputs). Signature should be ``func(x, *args)`` where ``x0`` contains
        initial guesses for ``x`` and ``args`` represents the additional
        arguments.
    x0 : np.ndarray
        Initial guesses.
    fprime : function, optional
        The derivative of ``func``. If not passed, this will be estimated with
        the secant method.
    args : tuple
        Extra arguments to be passed to ``func``.
    tol : float
        The allowable error of the zero value.
    maxiter : int
        Maximal number of iterations.
    fprime2 : function, optional
        The second derivative of ``func``. If passed, Halley's method will be
        used. If not passed, the normal Newton-Raphson method or the secant
        method is used.
    failure_idx_flag : bool, optional
        Pass True to return two extra boolean arrays specifying which
        optimizations failed or encountered zero derivatives, respectively.

    Returns
    -------
    root : np.ndarray
        The identified zeros of ``func``.
    failures : np.ndarray of bool, optional
        Only returned if ``failure_idx_flag`` is True. Indicates which elements
        failed to converge.
    zero_der : np.ndarray of bool, optional
        Only returned if ``failure_idx_flag`` is True. Indicates which elements
        had a zero derivative.
    """
    try:
        p = np.asarray(x0, dtype=float)
    except TypeError:  # can't convert complex to float
        p = np.asarray(x0)
    failures = np.ones_like(p, dtype=bool)  # at start, nothing converged
    if fprime is not None:
        # Newton-Raphson method
        for iteration in range(maxiter):
            fder = np.asarray(fprime(p, *args))
            nz_der = (fder != 0)
            # stop iterating if all derivatives are zero
            if not nz_der.any():
                break
            fval = np.asarray(func(p, *args))
            # Newton step
            dp = fval[nz_der] / fder[nz_der]
            if fprime2 is not None:
                fder2 = np.asarray(fprime2(p, *args))
                dp = dp / (1.0 - 0.5 * dp * fder2[nz_der] / fder[nz_der])
            # only update nonzero derivatives
            p[nz_der] -= dp
            failures[nz_der] = np.abs(dp) >= tol  # items not yet converged
            # stop iterating if there aren't any failures, not incl zero der
            if not failures[nz_der].any():
                break
    else:
        # Secant method
        dx = np.finfo(float).eps**0.33
        p1 = p * (1 + dx) + np.where(p >= 0, dx, -dx)
        q0 = np.asarray(func(p, *args))
        q1 = np.asarray(func(p1, *args))
        active = np.ones_like(p, dtype=bool)
        for iteration in range(maxiter):
            nz_der = (q1 != q0)
            # stop iterating if all derivatives are zero
            if not nz_der.any():
                p = (p1 + p) / 2.0
                break
            # Secant Step
            dp = (q1 * (p1 - p))[nz_der] / (q1 - q0)[nz_der]
            # only update nonzero derivatives
            p[nz_der] = p1[nz_der] - dp
            active_zero_der = ~nz_der & active
            p[active_zero_der] = (p1 + p)[active_zero_der] / 2.0
            active &= nz_der  # don't assign zero derivatives again
            failures[nz_der] = np.abs(dp) >= tol  # not yet converged
            # stop iterating if there aren't any failures, not incl zero der
            if not failures[nz_der].any():
                break
            p1, p = p, p1
            q0 = q1
            q1 = np.asarray(func(p1, *args))
    zero_der = ~nz_der & failures  # don't include converged with zero-ders
    if zero_der.any():
        # secant warnings
        if fprime is None:
            nonzero_dp = (p1 != p)
            # non-zero dp, but infinite newton step
            zero_der_nz_dp = (zero_der & nonzero_dp)
            if zero_der_nz_dp.any():
                rms = np.sqrt(
                    sum((p1[zero_der_nz_dp] - p[zero_der_nz_dp]) ** 2)
                )
                warnings.warn('RMS of {:g} reached'.format(rms), RuntimeWarning)
        # netwon or halley warnings
        else:
            all_or_some = 'all' if zero_der.all() else 'some'
            msg = '{:s} derivatives were zero'.format(all_or_some)
            warnings.warn(msg, RuntimeWarning)
    elif failures.any():
        all_or_some = 'all' if failures.all() else 'some'
        msg = '{0:s} failed to converge after {1:d} iterations'.format(
            all_or_some, maxiter
        )
        if failures.all():
            raise RuntimeError(msg)
        warnings.warn(msg, RuntimeWarning)
    if failure_idx_flag:
        result = namedtuple('result', ('root', 'failures', 'zero_der'))
        p = result(p, failures, zero_der)
    return p
