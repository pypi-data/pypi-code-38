# import pytest
import numpy as np
from scipy.special import betaln, logsumexp
from bgbb.numba_special import nb_lbeta, nb_lbeta_vec2, nb_logsumexp


def test_nb_lbeta(niter=1000):
    for _ in range(niter):
        d, g = np.random.rand(2) * 1000
        a = nb_lbeta(d, g)
        b = betaln(d, g)
        assert np.allclose(a, b), "{} != {} ({}, {})".format(a, b, d, g)


def test_nb_lbeta_vec2():
    assert np.allclose(nb_lbeta_vec2(1, np.arange(7)), betaln(1, np.arange(7)))


def test_nb_logsumexp(n_iter=100):
    np.random.seed(0)
    for _ in range(n_iter):
        a = 10 ** (np.random.rand(100) * 10)
        assert np.allclose(nb_logsumexp(a), logsumexp(a))
