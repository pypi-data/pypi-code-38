#! /usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os
import socket
import subprocess
import sys
import time
import warnings
from distutils.spawn import find_executable
from multiprocessing import cpu_count, current_process

import numpy as np
import pytest
from schwimmbad import MultiPool

from uhammer import (Parameters, continue_sampling, persist_every_n_iterations,
                     sample)
from uhammer._parallel import (check_if_walkers_number_of_cores_fit,
                               check_pool, core_count, runs_on_euler_node,
                               runs_on_single_euler_node)


def test_check_euler(monkeypatch):

    assert not runs_on_euler_node()

    for ip in ("10.205.0.10", "10.205.1.10", "10.205.96.0", "10.205.97.0"):

        monkeypatch.setattr(socket, "gethostbyname", lambda name: ip)
        assert runs_on_euler_node()


def test_runs_on_single_euler_node(monkeypatch):
    assert not runs_on_single_euler_node()
    monkeypatch.setenv("LSB_EFFECTIVE_RSRCREQ", "span[hosts=1]")
    assert runs_on_single_euler_node()


def test_core_count(monkeypatch):
    assert core_count() == cpu_count()
    monkeypatch.setenv("LSB_MAX_NUM_PROCESSORS", "124")
    assert core_count() == 124


def test_warning_for_oversubscription(record_warnings, regtest, monkeypatch):
    monkeypatch.setenv("OMP_NUM_THREADS", "124")
    with record_warnings() as messages:
        check_pool(MultiPool(2), 10)
        assert len(messages) == 1, messages
        print("expect warning about oversubscription:".upper(), file=regtest)
        print(messages[0], file=regtest)


def test_check_if_walkers_number_of_cores_fit(record_warnings, regtest):

    with record_warnings() as messages:
        assert not check_if_walkers_number_of_cores_fit(10, 1)
        assert len(messages) == 1, messages
        print(messages[0], file=regtest)

    with record_warnings() as messages:
        check_if_walkers_number_of_cores_fit(10, 20)
        assert len(messages) == 1, messages
        print("expect warning about less walkers than cores:".upper(), file=regtest)
        print(messages[0], file=regtest)

    print(file=regtest)

    with record_warnings() as messages:
        check_if_walkers_number_of_cores_fit(81, 20)
        assert len(messages) == 1, messages
        print(
            "expectwarning about walkers beig multiples of num workers:".upper(),
            file=regtest,
        )
        print(messages[0], file=regtest)

    print(file=regtest)

    with record_warnings() as messages:
        check_if_walkers_number_of_cores_fit(80, 20)
        assert not messages


class PoolMock(object):
    def __init__(self, size):
        self.size = size


def test_check_pool_1(record_warnings, monkeypatch, regtest):
    class PoolMock(object):
        def __init__(self, size):
            self.size = size

    with record_warnings() as messages:
        monkeypatch.setattr(socket, "gethostbyname", lambda name: "10.205.0.10")
        check_pool(PoolMock(36), 72)
        assert len(messages) == 2
        for warning in messages:
            print(warning, file=regtest)


def test_check_pool_2(record_warnings, monkeypatch, regtest):

    with record_warnings() as messages:

        # setup single node on euler:
        monkeypatch.setattr(socket, "gethostbyname", lambda name: "10.205.0.10")
        monkeypatch.setenv("LSB_EFFECTIVE_RSRCREQ", "span[hosts=1]")

        check_pool(PoolMock(36), 72)
        assert len(messages) == 1
        for warning in messages:
            print(warning, file=regtest)


def test_check_pool_3(record_warnings):

    with record_warnings() as messages:
        check_pool(PoolMock(35), 70)
        assert not messages


def lnprob(p):
    # this function must be outside the test functions to be pickable, as
    # multiprocessing pool fails for non-pickable functions.

    time.sleep(0.02)  # make it slow to increase speedup.
    return -p.a ** 2


def test_parallel_sampling(record_warnings, regtest, tmpdir):
    p = Parameters()
    p.add("a", (-1, 1))

    n_samples = 50
    n_walkers_per_parm = 14

    started = time.time()

    samples_serial, __ = sample(
        lnprob, p, [], n_walkers_per_parm, seed=42, n_samples=n_samples, parallel=False
    )

    needed_serial = time.time() - started

    started = time.time()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)

        samples_parallel, __ = sample(
            lnprob,
            p,
            [],
            n_walkers_per_parm,
            seed=42,
            n_samples=n_samples,
            parallel=True,
            persist=persist_every_n_iterations(1, tmpdir.join("sampler.pkl").strpath),
        )
        needed_parallel = time.time() - started

    assert np.all(samples_serial == samples_parallel), (
        samples_serial,
        samples_parallel,
    )

    # we dont check scalablity for less than four cores as my develpment machine has
    # four. For less than four cores it is enough that the assert above did not fail.
    if cpu_count() >= 4:
        assert needed_parallel < 0.6 * needed_serial, (needed_parallel, needed_serial)


def test_mpi_tasks(record_warnings, regtest, monkeypatch):

    from uhammer._parallel import mpi_tasks  # avoids UnboundLocalError

    assert mpi_tasks() is None

    if "mpi4py" in sys.modules:
        del sys.modules["mpi4py"]

    from uhammer._parallel import mpi_tasks

    assert "mpi4py" not in sys.modules, "this test is not working any more"

    class Fake(object):
        @property
        def MPI(self):
            raise ImportError("import fails on purpose.")

    try:
        sys.modules["mpi4py"] = Fake()
        # simulate mpirun:
        os.environ["MPIEXEC_FAKE"] = "LOOKSLIKEMPI"
        with record_warnings() as messages:
            assert mpi_tasks() == 1
    finally:
        del os.environ["MPIEXEC_FAKE"]
        del sys.modules["mpi4py"]

    assert len(messages) == 1, messages
    print(messages[0], file=regtest)


def test_sample_from_lambda():

    seed = 42

    p = Parameters()
    p.add("a", (-1, 1))

    lnprob = lambda s: -abs(s.a)  # noqa

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        sample(
            lnprob,
            p,
            args=None,
            n_walkers_per_param=10,
            seed=seed,
            n_samples=1000,
            show_progress=False,
            parallel=True,
        )


MPI_EXE = find_executable("mpirun")
try:
    import mpipool  # noqa
except ImportError:
    HAS_MPIPOOL = False
else:
    HAS_MPIPOOL = True


@pytest.mark.skipif(HAS_MPIPOOL is False, reason="mpipool not installed")
@pytest.mark.skipif(MPI_EXE is None, reason="mpirun not found")
@pytest.mark.skipif(sys.version_info.major == 2, reason="fails with python")
def test_mpi(tmpdir):

    output_prefix = tmpdir.join("out").strpath
    output_prefix_continue = tmpdir.join("out_continue").strpath
    persist_path = tmpdir.join("sampler.pkl").strpath

    env = os.environ.copy()
    env.update({"OUTPUT_PREFIX": output_prefix, "PERSIST_PATH": persist_path})

    here = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(here, "files", "sample_line_fit_parallel.py")
    line = [MPI_EXE, "-n", "4", sys.executable, script]

    p = subprocess.Popen(
        line, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env  # shell=True
    )
    found_error = False
    found_shape = False
    for line in iter(p.stdout.readline, b""):
        line = line.rstrip()
        print(str(line, "utf-8"))
        if line.startswith(b"++++ ERROR"):
            found_error = True
        if line.startswith(b"++++ SAMPLES"):
            found_shape = b" ".join(line.split(b" ")[2:])

    assert not found_error
    assert found_shape == b"(1500, 3)"

    pathes = set(os.path.relpath(p.strpath, tmpdir.strpath) for p in tmpdir.listdir())
    expected = [
        os.path.basename(output_prefix) + "_run_0000_worker_{}.txt".format(i)
        for i in range(1, 4)
    ] + [os.path.basename(persist_path)]

    assert pathes == set(expected)

    for worker_id, p in enumerate(expected[:-1], 1):
        full_p = tmpdir.join(p).strpath
        content = set(open(full_p))
        assert content == set((str(worker_id) + "\n",))

    samples, __ = continue_sampling(
        persist_path,
        10,
        parallel=False,
        output_prefix=output_prefix_continue,
        show_output=False,
    )
    assert samples.shape == (10, 3)
    assert os.path.exists(output_prefix_continue + "_run_0000.txt")


def test_multiprocessing(tmpdir):

    output_prefix = tmpdir.join("out").strpath
    output_prefix_continue = tmpdir.join("out_continue").strpath
    persist_path = tmpdir.join("sampler.pkl").strpath

    sigma = .5

    def gen_data():
        a0 = .5
        b0 = .5
        c0 = 1

        x = np.linspace(-2, 2, 100)
        y_measured = a0 + b0 * x + c0 * x ** 2 + sigma * np.random.randn(*x.shape)
        return x, y_measured

    p = Parameters()
    p.add("a", (0, 1))
    p.add("b", (0, 1))
    p.add("c", (0, 2))

    def lnprob(p, x, y_measured, sigma=sigma):
        print(current_process().rank)
        y = p.a + p.b * x + p.c * x ** 2
        diff = (y - y_measured) / sigma
        return -np.dot(diff.T, diff) / 2

    n_samples = 1500
    n_walkers_per_param = 200

    samples, __ = sample(
        lnprob,
        p,
        args=gen_data(),
        n_walkers_per_param=n_walkers_per_param,
        n_samples=n_samples,
        show_progress=False,
        show_output=False,
        output_prefix=output_prefix,
        parallel=True,
        verbose=True,
        persist=persist_every_n_iterations(1, persist_path),
    )

    pathes = set(os.path.relpath(p.strpath, tmpdir.strpath) for p in tmpdir.listdir())
    expected = [
        os.path.basename(output_prefix) + "_run_0000_worker_{}.txt".format(i)
        for i in range(1, cpu_count())
    ] + [os.path.basename(persist_path)]

    assert pathes == set(expected)

    for worker_id, p in enumerate(expected[:-1], 1):
        full_p = tmpdir.join(p).strpath
        content = set(open(full_p))
        assert content == set((str(worker_id) + "\n",))

    samples, __ = continue_sampling(
        persist_path,
        10,
        parallel=False,
        output_prefix=output_prefix_continue,
        show_output=False,
    )
    assert samples.shape == (10, 3)

    assert os.path.exists(output_prefix_continue + "_run_0000.txt")
