#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os
from contextlib import contextmanager
from functools import partial

import emcee
import pytest

from uhammer import (Parameters, continue_sampling, load_samples,
                     persist_every_n_iterations, persist_final,
                     persist_on_error, sample)

emcee_version = int(emcee.__version__.split(".")[0])


@pytest.fixture(scope="function")
def sampler_with_persister(tmpdir):
    def dummy(p):

        return -abs(3 * p.a)

    @contextmanager
    def create_sampler(expected_shape_of_samples, persister, lnprob=dummy):

        p = Parameters()
        p.add("a", (-4, 4))

        assert len(tmpdir.listdir()) == 0

        persist_file = tmpdir.join("sampler.bin").strpath
        persist = persister(path=persist_file)
        sample_ = partial(
            sample,
            lnprob,
            p,
            None,
            n_walkers_per_param=20,
            seed=42,
            n_samples=100,
            persist=persist,
            show_output=False,
        )
        yield sample_, persist

        assert os.path.exists(persist_file)

        # TODO:
        # emcee 3 only returns successful samples, wheras
        # emcee 2 seems to return zeros filled in:
        samples = load_samples(persist_file)
        assert samples.shape == expected_shape_of_samples
        os.remove(persist_file)

    return create_sampler


def test_persist_on_error(sampler_with_persister):
    def error_ln_prob(p, count=[0]):

        count[0] += 1
        if count[0] > 40:
            # we do this to bypass the exception handler during the first iteration.  we
            # have 20 walkers so one iteration involves calling this function 20
            # times.
            1 / 0
        return -abs(3 * p.a)

    # emcee 3 makes some extra function calls before actual sampling starts:
    expected_shape = (40, 1) if emcee_version == 2 else (20, 1)

    with sampler_with_persister(expected_shape, persist_on_error, error_ln_prob) as (
        sample_,
        persister,
    ):

        with pytest.raises(ZeroDivisionError):
            sample_()


def test_persist_every_n_iterations(sampler_with_persister):

    with sampler_with_persister((100, 1), partial(persist_every_n_iterations, 1)) as (
        sample_,
        persister,
    ):
        sample_()
    assert persister._iter_track == [1, 2, 3, 4, 5]

    with sampler_with_persister((80, 1), partial(persist_every_n_iterations, 2)) as (
        sample_,
        persister,
    ):
        sample_()

    assert persister._iter_track == [2, 4]


def test_persist_final(sampler_with_persister):

    with sampler_with_persister((100, 1), persist_final) as (sample_, persister):
        sample_()

    assert persister._iter_track == [5]


def test_restore_sampler(sampler_with_persister, regtest):

    regtest.identifier = "emcee_" + str(emcee_version)

    with sampler_with_persister((100, 1), persist_final) as (sample_, persister):

        samples, __ = sample_()
        print(samples[-10:, :], file=regtest)

        samples, __ = continue_sampling(persister.path, 10)
        assert samples.shape == (10, 1)
        print(samples, file=regtest)
