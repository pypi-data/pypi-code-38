#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import emcee
import numpy as np
import pytest

from uhammer import Parameters, distribution, gaussian, model, sample

emcee_version = emcee.__version__.split(".")[0]


@pytest.mark.parametrize("wrong_range", [0, (), (1, 2, 3), ("a", 1), (2, 1), (1, 1)])
def test_param(regtest, wrong_range):

    p = Parameters()
    with pytest.raises(ValueError) as e:
        p.add("a", wrong_range)

    print(e.value, file=regtest)


def test_double_param(regtest):
    p = Parameters()
    p.add("a", (1, 2))
    with pytest.raises(ValueError) as e:
        p.add("a", (1, 2))
    print(e.value, file=regtest)


def test_invalid_prob_density(regtest):

    p = Parameters()
    p.add("a", (0, 1))

    def lnprob(p):
        return 1

    with pytest.raises(AssertionError) as e:
        sample(
            lnprob,
            p,
            args=None,
            n_walkers_per_param=10,
            seed=42,
            n_samples=100,
            show_progress=False,
        )

    print(e.value, file=regtest)


def test_empty_parameters(regtest):

    p = Parameters()

    def lnprob(p):
        return 1

    with pytest.raises(AssertionError) as e:
        sample(
            lnprob,
            p,
            args=None,
            n_walkers_per_param=10,
            seed=42,
            n_samples=100,
            show_progress=False,
        )

    print(e.value, file=regtest)


def test_sample_from_distribution(regtest):

    regtest.identifier = "emcee_" + emcee_version

    seed = 42

    lnprob, p = distribution(gaussian(5), 1, (0, 3))

    samples, lnprobs = sample(
        lnprob,
        p,
        args=None,
        n_walkers_per_param=10,
        seed=seed,
        n_samples=1000,
        show_progress=False,
    )

    print("min:", np.min(samples), file=regtest)
    print("max:", np.max(samples), file=regtest)

    assert samples.shape == (1000, 1)
    assert lnprobs.shape == (1000,)

    # dimensions do not fit, should raise AssertionError:
    icov = np.array(((1, 0.2), (0.2, 1)))
    lnprob, p = distribution(gaussian(icov), 1, (0, 3))

    with pytest.raises(AssertionError) as e:
        samples, __ = sample(
            lnprob,
            p,
            args=None,
            n_walkers_per_param=10,
            seed=seed,
            n_samples=1000,
            show_progress=False,
        )

    print(e.value, file=regtest)

    np.random.seed(seed)
    N = 5

    cov = np.random.random((N, N))
    cov = np.dot(cov.T, cov)
    cov += 5 * np.eye(N)

    lnprob, p = distribution(gaussian(cov), N, (0, 2))

    samples, __ = sample(
        lnprob,
        p,
        args=None,
        n_walkers_per_param=10,
        seed=seed,
        n_samples=5000,
        show_progress=False,
    )

    assert samples.shape == (5000, N)
    print(samples[1000:, :].mean(axis=0), file=regtest)

    lnprob, p = distribution(gaussian(cov), N, N * [(-1, 1)])

    samples, __ = sample(
        lnprob,
        p,
        args=None,
        n_walkers_per_param=10,
        seed=seed,
        n_samples=5000,
        show_progress=False,
    )

    assert samples.shape == (5000, N)
    print(samples[1000:, :].mean(axis=0), file=regtest)


def test_line_fit(regtest, tmpdir):

    regtest.identifier = "emcee_" + emcee_version

    np.random.seed(42)

    a0 = 0.5
    b0 = 0.5
    c0 = 0.1
    sigma = 0.5

    x = np.linspace(-1, 1, 100)
    y_measured = a0 + b0 * x + c0 * x ** 2 + sigma * np.random.randn(*x.shape)

    p = Parameters()
    p.add("a", (-1, 1))
    p.add("b", (-1, 1))
    p.add("c", (-1, 1))

    def line(p, x):
        print(p)
        y = p.a + p.b * x + p.c * x ** 2
        return y

    def lnprob(p, x, y_measured):
        y = line(p, x)
        diff = y - y_measured
        return -np.dot(diff.T, diff) / sigma / 2.0

    n_samples = 3000
    n_walkers_per_param = 10

    log_file_prefix = tmpdir.join("out").strpath

    samples, lnprobs = sample(
        lnprob,
        p,
        args=[x, y_measured],
        n_walkers_per_param=n_walkers_per_param,
        seed=42,
        n_samples=n_samples,
        show_progress=False,
        show_output=False,
        output_prefix=log_file_prefix,
    )

    assert samples.shape == (n_samples, len(p))
    assert lnprobs.shape == (n_samples,)

    log_file = log_file_prefix + "_run_0000.txt"
    assert os.path.exists(log_file), log_file

    lines = open(log_file, "r").readlines()
    assert 0 < len(lines) <= n_samples
    assert all("Parameters" in line for line in lines)

    is_ = samples[::100, :]

    lnprob_via_model = model(line, gaussian(sigma), x, y_measured)

    samples, __ = sample(
        lnprob_via_model,
        p,
        args=[x, y_measured],
        n_walkers_per_param=n_walkers_per_param,
        n_samples=n_samples,
        show_progress=True,
        seed=42,
    )
    assert np.all(is_ == samples[::100, :])

    print(samples[::100], file=regtest)


def test_parameter_with_start_value():
    p = Parameters()
    p.add("a", (1, 2), 1.5)

    def lnprob(p):
        return -1

    samples, lnprobs = sample(
        lnprob,
        p,
        args=None,
        n_walkers_per_param=10,
        seed=42,
        n_samples=10,
        show_progress=False,
    )

    assert samples.shape == (10, 1)
    assert lnprobs.shape == (10,)
    assert set(samples.flatten()) == set((1.5,))
    assert set(lnprobs) == set((-1,))
