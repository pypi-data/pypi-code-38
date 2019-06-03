import numpy as np
from numba import njit, prange
from numpy import log, exp, logaddexp
from scipy.special import betaln

from bgbb.numba_special import nb_lbeta_vec12, nb_lbeta_vec2


def get_vals(x):
    return x.values if hasattr(x, "values") else x


@njit
def nbsum_scalar(
    x, tx, recency_T, alpha, beta, gamma, delta, J, beta_ab, beta_gd
):
    if recency_T <= -1:
        return -np.inf

    j = J[: recency_T + 1]
    return log(
        np.sum(
            exp(
                nb_lbeta_vec2(alpha + x, beta + tx - x + j)
                - beta_ab
                + nb_lbeta_vec2(gamma + 1, delta + tx + j)
                - beta_gd
            )
        )
    )


@njit
def nbsum_(x, tx, recency_T, a, b, g, d, J, ab, gd):
    N = len(x)
    res = np.empty(N)
    for i in range(N):
        res[i] = nbsum_scalar(x[i], tx[i], recency_T[i], a, b, g, d, J, ab, gd)
    return res


@njit(parallel=True)
def nbsum_p(x, tx, recency_T, a, b, g, d, J, ab, gd):
    N = len(x)
    res = np.empty(N)
    for i in prange(N):
        res[i] = nbsum_scalar(x[i], tx[i], recency_T[i], a, b, g, d, J, ab, gd)
    return res


def nbsum(x, tx, recency_T, a, b, g, d, J, ab, gd, parallel=True):
    f = nbsum_p if parallel else nbsum_
    return f(x, tx, recency_T, a, b, g, d, J, ab, gd)


def _nb_loglikelihood(alpha, beta, gamma, delta, x, tx, T, parallel=True):
    """Loglikelihood for optimizer."""
    # Constrain the params to be > 0
    if min([alpha, beta, gamma, delta]) <= 0:
        return np.full_like(x, -np.inf)

    beta_ab = betaln(alpha, beta)
    beta_gd = betaln(gamma, delta)

    recency_T = T - tx - 1
    xa, txa, Ta, recency_Ta = map(get_vals, [x, tx, T, recency_T])

    indiv_loglike = (
        nb_lbeta_vec12(alpha + xa, beta + Ta - xa)
        - beta_ab
        + nb_lbeta_vec2(gamma, delta + Ta)
        - beta_gd
    )

    J = np.arange(recency_T.max() + 1)

    s = nbsum(
        xa,
        txa,
        recency_Ta,
        alpha,
        beta,
        gamma,
        delta,
        J,
        beta_ab,
        beta_gd,
        parallel=parallel,
    )

    indiv_loglike = logaddexp(indiv_loglike, s)

    return indiv_loglike


############
# Wrappers #
############
def nb_loglikelihood(params, x, tx, T, parallel=True):
    alpha, beta, gamma, delta = params
    return _nb_loglikelihood(
        alpha, beta, gamma, delta, x, tx, T, parallel=parallel
    )


def nb_loglikelihood_df(
    params, df, rfn_names=False, parallel=True, nll=False, ncusts=None
):
    columns = ["frequency", "recency", "n"] if rfn_names else ["x", "tx", "T"]
    x, tx, T = [df[c] for c in columns]
    alpha, beta, gamma, delta = params
    ll = _nb_loglikelihood(
        alpha, beta, gamma, delta, x, tx, T, parallel=parallel
    )
    if nll:
        if ncusts is None:
            print("WARNING: ncusts not passed")
            ncusts = 1
        return -np.mean(ll * ncusts)
    return ll
