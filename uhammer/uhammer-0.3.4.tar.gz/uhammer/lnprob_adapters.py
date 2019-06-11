#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import numpy as np

from ._utils import check_range, is_float
from .parameters import Parameters

# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


def gaussian(cov):
    """Returns logarithmic probability density function for gaussian with mean 0 and
    given covariance `cov`.

    :param cov: Covariance as a single number (real case) or square invertible
                matrix (multivariate case).
    """

    class ComputeProb(object):
        def __init__(self, cov):
            self.icov = None
            self.cov = cov

        def _setup_icov(self, n):
            cov = np.atleast_1d(self.cov)
            if cov.shape == (1,):
                icov = 1.0 / cov * np.eye(n)
            else:
                icov = np.linalg.inv(cov)
            assert icov.shape == (
                n,
                n,
            ), "'cov' must be a square matrix of size {} but has shape {} x {}".format(
                n, icov.shape[0], icov.shape[1]
            )
            self.icov = icov

        def __call__(self, x):
            if self.icov is None:
                self._setup_icov(len(x))
            return -np.dot(x.T, np.dot(self.icov, x)) / 2.0

    return ComputeProb(cov)


def model(forward, probability, input_data, measured_data):
    """
    Creates a function used as `lnprob` argument for ``uhammer.sample`` function..

    :param forward: models forward computation. Takes two arguments: `p`
                    which must be an instance of ``Parameters`` and the given
                    ``input_data``.

    :param probability: A function which computes to probability of difference
                        of the computed forward model and the given
                        ``measured_data``.

    :param input_data: Input data passed as second argument to ``forward``.

    :param measured_data: Measured data. Must be compatible with the return
                          value of ``forward``.
    """

    def likelihood(p, *args):
        diff = forward(p, input_data) - measured_data
        return probability(diff)

    return likelihood


def distribution(prob_density_function, ndim, ranges):
    """
    Helper to sample from a distribution.

    Returns ``lnprob`` function and ``Parameters`` object to be used in sample.

    :param prob_density_function: Function taking vector of length ``ndim``,
                                  must return logarithm of a probability density.

    :param ndim: Dimension of input to ``prob_density_function``.

    :param ranges: Either tuple or list of tuples of numbers to restrict coordinates
                   when sampling.
    """

    tl = (tuple, list)

    assert isinstance(ranges, tl)
    assert len(ranges) > 0

    if len(ranges) == 2:
        check_range(ranges)
        min_, max_ = ranges
        if is_float(min_) and is_float(max_):
            assert min_ < max_, ranges
            ranges = [ranges] * ndim

    for range_ in ranges:
        check_range(range_)

    p = Parameters()
    for i, range_ in enumerate(ranges):
        p.add("x{i}".format(i=i), range_)

    def lnprob(p):
        return prob_density_function(np.array(p.values))

    return lnprob, p
