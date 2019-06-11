#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import zlib

import dill
import emcee

emcee_version = int(emcee.__version__.split(".")[0])

# Copyright © 2018 Uwe Schmitt <uwe.schmitt@id.ethz.ch>


class _SamplerPersister(object):
    def __init__(self, check, path, persist_on_exceptions):
        self.check = check
        self.path = path
        self.persist_on_exceptions = persist_on_exceptions
        self._iter_track = []

    def __call__(self, sampler, i, n_iter, exception):
        do_persist = self.check(i, n_iter)
        do_persist = do_persist or (
            exception is not None and self.persist_on_exceptions
        )
        if do_persist:
            with open(self.path, "wb") as fh:
                fh.write(zlib.compress(dill.dumps(sampler)))
            self._iter_track.append(i)
        if exception:
            raise exception
        return do_persist

    @staticmethod
    def restore_sampler(file_path):
        with open(file_path, "rb") as fh:
            return dill.loads(zlib.decompress(fh.read()))


def load_samples(path):
    """loads samples for persisted sampler file"""
    sampler = _SamplerPersister.restore_sampler(path)
    if emcee_version == 3:
        return sampler.flatchain
    n_samples = sampler.iterations * sampler.n_walkers
    return sampler.flatchain[:n_samples]


def persist_every_n_iterations(n, path):
    """Return value of this function can be passed as argument `persist` to ``sample``
    function to store state during sampling. This allows later continuation of sampling,
    e.g. after crashes.

    This persister saves state every ``n`` iterations and in case of failure.

    :param n:  persist after every ``n`` iterations of the sampler
    :param path: file path to store the relevant information.
    """

    def check(i, n_iter):
        return i > 0 and i % n == 0

    return _SamplerPersister(check, path, True)


def persist_final(path):
    """Return value of this function can be passed as argument `persist` to ``sample``
    function to store state during sampling. This allows later continuation of sampling,
    e.g. after crashes.

    This persister only stores the information when sampling finishes and in case
    of failure.

    :param path: file path to store the relevant information.
    """

    def check(i, n_iter):
        return i == n_iter

    return _SamplerPersister(check, path, True)


def persist_on_error(path):
    """Return value of this function can be passed as argument `persist` to ``sample``
    function to store state during sampling. This allows later continuation of sampling,
    e.g. after crashes.

    This persister only stores the information only in case of failure.

    :param path: file path to store the relevant information.
    """

    def check(i, n_iter):
        return False

    return _SamplerPersister(check, path, True)


def dont_persist():
    def check(i, n_iter):
        return False

    return _SamplerPersister(check, None, False)
