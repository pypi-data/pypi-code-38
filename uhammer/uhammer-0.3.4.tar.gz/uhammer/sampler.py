# encoding: utf-8
from __future__ import absolute_import, division, print_function

import functools
import glob
import itertools
import os
import random
import sys
import warnings

import dill
import numpy as np

from ._parallel import (check_parallel, get_pool_for, get_rank,
                        runs_on_euler_node, runs_with_mpi)
from ._utils import (capture, mute_stderr, os_write_works, with_progressbar,
                     with_simple_progress_report)
from .parameters import Parameters
from .persisting import _SamplerPersister, dont_persist

with mute_stderr():
    # might cause MPI related error message if run on one single node, even
    # without mpirun:
    import emcee

    emcee_version = int(emcee.__version__.split(".")[0])


RUNS_WITH_MPI = runs_with_mpi()


class _ParameterAdapter(object):
    """
    Addapts parameters argument of emcee lnprob function to parameters of uhammer
    lnprob function.
    """

    def __init__(self, names, values):
        self.names = names
        self.values = values
        # this sets every parameter as an attribute:
        self.__dict__.update(dict(zip(names, values)))

    def __str__(self):
        assignments = [
            "{}={:e}".format(name, value)
            for name, value in zip(self.names, self.values)
        ]
        return "Parameters({})".format(", ".join(assignments))


class _LnProbAdapter(object):
    """
    Adapts API of uhammer lnprob function to emcee hammer API.
    """

    def __init__(self, lnprob_uhammer, p, show_output, output_path_pattern):
        self.lnprob_uhammer = lnprob_uhammer
        self.p = p
        self.show_output = show_output
        self.output_path_pattern = output_path_pattern

    def __call__(self, parameters, *args):
        if self.output_path_pattern is not None:
            rank = get_rank()
            if rank is not None:
                output_path = self.output_path_pattern.format(worker_id=rank)
            else:
                output_path = self.output_path_pattern
        else:
            output_path = None

        with capture(output_path, self.show_output):
            return self.lnprob(parameters, args)

    def lnprob(self, parameters, args):

        p = self.p
        names = p.names

        lnprob_prior = 0
        for name, value in zip(names, parameters):
            if not p._is_in_bounds(name, value):
                return -np.inf
            lnprob_prior -= np.log(p._range_length(name))

        parameters_for_lnprob = _ParameterAdapter(names, parameters)

        computed_lnprob = self.lnprob_uhammer(parameters_for_lnprob, *args)

        if computed_lnprob > 0:
            client_function_name = self.lnprob_uhammer.__name__
            raise AssertionError(
                "{} computed positive value {} for parameters {}".format(
                    client_function_name, computed_lnprob, parameters_for_lnprob
                )
            )

        return computed_lnprob + lnprob_prior

    def __getstate__(self):
        # distributed computation requires pickling of the posterior
        # function using pickle module from the python standard library.
        # this can fail e.g. if nested functions or classes with
        # classmethods are infolved.
        # to fix that we implement here how to pickle this class using
        # dill which is more versatile than pickle from the standard
        # library:
        return dill.dumps(self.__dict__)

    def __setstate__(self, state):
        # see __getstate__
        # this method implements the unpickling part.
        self.__dict__.update(dill.loads(state))


class PickableEmceeSampler(emcee.EnsembleSampler):
    def __getstate__(self):
        dd = self.__dict__.copy()
        if "pool" in dd:
            del dd["pool"]
        return dd

    def __setstate__(self, dd):
        self.pool = None
        self.__dict__.update(dd)


def _setup_random_state(seed, sampler):
    rstate0 = sampler._random
    rstate0.seed(seed)
    random.seed(seed)
    np.random.seed(seed)


def sample(
    lnprob,
    p,
    args=None,
    n_walkers_per_param=10,
    seed=None,
    n_samples=1000,
    parallel=False,
    show_progress=False,
    show_output=True,
    output_prefix=None,
    persist=dont_persist(),
    verbose=True,
):
    """
    Runs emcee sampler to generate samples from the declared
    distribution.

    :param lnprob: Function for computing the natural logarithm of the
                   distribution to sample from. Fist argument is a
                   object with the current values of the declared
                   parameters as attributes.  The function may accept
                   additioanal arguments for auxiliary data.

    :param p:      Instance of the ``Parameters`` class.

    :param args:   List with auxiliary values. Can also be ``None`` or
                   ``[]``.

    :param n_walkers_per_param: Number of walkers per parameter.
                                Results in ``len(p) *
                                n_walkers_per_param`` walkers in total.

    :param seed:  Used random seed in case you want reproducible
                  samples. Skip this argument or use ``None`` else.

    :param n_samples: Number of samples to generate. So the return value
                      is a ``numpy`` array of shape ``(n_samples, len(p))``.

    :param parallel: Run in sequention or parallel mode? Automatically
                     detects number of cores, also detects if code is
                     run using ``mpirun``.

    :param show_progress: Show progress of sampling.

    :param show_output: set to ``True`` if you want to see the output
                        from the workers on the terminal, else set it to
                        ``False``.

    :param output_prefix: prefix for file path to record output from the
                          workers.  Default is ``None`` which means no
                          recording of output.

    :param persist:  persisting strategy, on of the functions in
                     :py:mod:`~uhammer.persisting`.

    :param verbose:  boolean value. If set to ``True``
                     :py:func:`~uhammer.sampler.sample` prints extra information.

    This function returns two values:

    - computed samples as a ``numpy`` array of shape ``(n_samples, len(p)``
    - computed log probabilites as ``numpy`` array of shape ``(n_samples,)``.

    Samples are arranged as follows, log probbilites in similar order:

    .. table::

       +----------------------------------------+
       | samples                                |
       +========================================+
       | p-dimensional sample from walker 0     |
       +----------------------------------------+
       | p-dimensional sample from walker 1     |
       +----------------------------------------+
       | ...                                    |
       +----------------------------------------+
       | p-dimensional sample from walker n - 1 |
       +----------------------------------------+
       | p-dimensional sample from walker 0     |
       +----------------------------------------+
       | p-dimensional sample from walker 1     |
       +----------------------------------------+
       | ...                                    |
       +----------------------------------------+

    """

    if args is None:
        args = []

    assert isinstance(p, Parameters), p
    assert len(p) > 0, "need parameters"

    assert isinstance(args, (list, tuple)), args
    assert isinstance(n_walkers_per_param, int), n_walkers_per_param
    assert n_walkers_per_param > 1, "need at least 2 walkers per parameter"
    if seed is not None:
        assert isinstance(seed, int)
    assert isinstance(n_samples, int), n_samples
    assert isinstance(parallel, bool)
    assert isinstance(show_progress, bool), show_progress
    assert isinstance(verbose, bool), verbose
    assert isinstance(show_output, bool), show_output

    if output_prefix is not None:
        assert isinstance(output_prefix, str), output_prefix

    check_parallel(parallel)

    if output_prefix is not None:
        output_path_pattern = capture_output_path(output_prefix, parallel)
    else:
        output_path_pattern = None

    show_progress = _check_and_fix_progress_settings(show_output, show_progress)

    # holds paramters passed to lnprob:
    _lnprob = _LnProbAdapter(lnprob, p, show_output, output_path_pattern)
    n_walkers = n_walkers_per_param * len(p)

    # might be global including startup of workers, workers hang there:
    # workers are stopped at exit:
    pool = get_pool_for(n_walkers) if parallel else None

    if pool is not None and verbose:
        print("uhammer: started {} with {} workers".format(pool, pool.size))

    sampler = PickableEmceeSampler(n_walkers, len(p), _lnprob, args=args, pool=pool)

    sampler.n_walkers = n_walkers

    _setup_random_state(seed, sampler) if seed is not None else np.random.RandomState()
    p0 = [[p.start_value(name) for name in p.names] for _ in range(n_walkers)]

    result = _sample(p0, sampler, n_samples, show_progress, persist, verbose=verbose)
    return result


def continue_sampling(
    persistence_file_path,
    n_samples,
    parallel=False,
    show_progress=False,
    show_output=True,
    output_prefix=None,
    persist=dont_persist(),
    verbose=True,
):
    """
    Continues sampling from a persisted sampler.

    Original arguments of  :py:func:`~uhammer.sampler.sample` like
    ``lnprob``, `n_walkers_per_param``, ``seed``, etc. are reused from
    the persisted sampler and can not be modified anymore.

    :param persistence_file_path: Path to a perviously persisted
                                  sampler. This includes `lnprob`,
                                  parameters and number of walkers.

    :param n_samples: Number of samples to generate. So the return value
                      is a ``numpy`` array of shape ``(n_samples, len(p))``.

    :param parallel: Run in sequention or parallel mode ? Automatic
                     dection of number of cores, also auto detects if
                     code is run using ``mpirun``.

    :param show_progress: Show progress of sampling.

    :param show_output: set to ``True`` if you want to see the output
                        from the workers on the terminal, else set it to
                        ``False``.

    :param output_prefix: prefix for file path to record output from the
                          workers.  Default is ``None`` which means no
                          recording of output.

    :param persist:  persisting strategy, on of the functions in
                     :py:mod:`~uhammer.persisting`.

    :param verbose:  boolean value, if ``True``
                     :py:func:`~uhammer.sampler.continue_sampling`
                     prints some information.

    This function returns two values:

    - computed samples as a ``numpy`` array of shape ``(n_samples, len(p)``
    - computed log probabilites as ``numpy`` array of shape ``(n_samples,)``.

    Samples are arranged as follows, log probbilites in similar order:

    .. table::

       +----------------------------------------+
       | samples                                |
       +========================================+
       | p-dimensional sample from walker 0     |
       +----------------------------------------+
       | p-dimensional sample from walker 1     |
       +----------------------------------------+
       | ...                                    |
       +----------------------------------------+
       | p-dimensional sample from walker n - 1 |
       +----------------------------------------+
       | p-dimensional sample from walker 0     |
       +----------------------------------------+
       | p-dimensional sample from walker 1     |
       +----------------------------------------+
       | ...                                    |
       +----------------------------------------+
    """
    assert isinstance(persistence_file_path, str)
    assert os.path.exists(persistence_file_path), "file {} does not exist".format(
        persistence_file_path
    )
    assert isinstance(n_samples, int), n_samples
    assert isinstance(parallel, bool)
    assert isinstance(show_progress, bool), show_progress

    assert isinstance(show_output, bool), show_output

    if output_prefix is not None:
        assert isinstance(output_prefix, str), output_prefix

    check_parallel(parallel)

    show_progress = _check_and_fix_progress_settings(show_output, show_progress)

    if output_prefix is not None:
        output_path_pattern = capture_output_path(output_prefix, parallel)
    else:
        output_path_pattern = None

    sampler = _SamplerPersister.restore_sampler(persistence_file_path)
    sampler.pool = get_pool_for(sampler.n_walkers) if parallel else None

    if emcee_version < 3:
        sampler.lnprobfn.f.show_output = show_output
        sampler.lnprobfn.f.output_path_pattern = output_path_pattern
    else:
        sampler.log_prob_fn.f.show_output = show_output
        sampler.log_prob_fn.f.output_path_pattern = output_path_pattern

    p0, lnprob0, rstate0 = sampler._last_run_mcmc_result
    return _sample(
        p0, sampler, n_samples, show_progress, persist, lnprob0, rstate0, verbose
    )


def capture_output_path(prefix, parallel):

    existing = glob.glob(prefix + "_run_*_*.txt")
    run_ids = [int(os.path.basename(p).split("_")[2]) for p in existing]
    if run_ids:
        next_run_id = max(run_ids) + 1
    else:
        next_run_id = 0

    if not parallel:
        return "{prefix}_run_{run_id:04d}.txt".format(prefix=prefix, run_id=next_run_id)

    return "{prefix}_run_{run_id:04d}_worker_{{worker_id}}.txt".format(
        prefix=prefix, run_id=next_run_id
    )


def _check_and_fix_progress_settings(show_output, show_progress):

    if show_output and show_progress:
        warnings.warn(
            "not supressing output might corrupt the progressbar. "
            "Better set show_output to False and set an appropriabe "
            "value for output_prefix."
        )

    if show_progress and not os_write_works() and not runs_on_euler_node():
        show_progress = False
        warnings.warn("disabled progressbar, can not write to fid 1")

    return show_progress


def _sample(
    p0,
    sampler,
    n_samples,
    show_progress,
    persist,
    lnprob0=None,
    rstate0=None,
    verbose=True,
):
    print_ = functools.partial(print, file=sys.__stdout__)

    n_steps = int(np.ceil(n_samples / sampler.n_walkers))
    if verbose:
        print_("uhammer: perform {} steps of emcee sampler".format(n_steps))

    # eemcee sampler.sample
    sample_iter = sampler.sample(p0, iterations=n_steps)

    if show_progress:
        if runs_on_euler_node():
            sample_iter = with_simple_progress_report(n_steps, sample_iter)
        else:
            sample_iter = with_progressbar(n_steps, sample_iter)

    for step in itertools.count(1):
        try:
            state = next(sample_iter)
            if emcee_version < 3:
                state = state[:3]
            sampler._last_run_mcmc_result = state
        except StopIteration:
            break
        except Exception as e:
            persisted = persist(sampler, step, n_steps, e)
            if verbose and persisted:
                print_("uhammer: persist sampler due to exception")
            raise e
        persisted = persist(sampler, step, n_steps, None)
        if verbose and persisted:
            print_("uhammer: persisted sampler after iteration {}".format(step))

    n_param = sampler.chain.shape[2]
    samples = sampler.chain.swapaxes(0, 1).reshape(-1, n_param)[:n_samples, :]
    lnprobs = sampler.lnprobability.swapaxes(0, 1)[:n_samples].flatten()
    return samples, lnprobs
