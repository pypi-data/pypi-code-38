from __future__ import print_function

import os

import numpy as np

from uhammer import Parameters, persist_every_n_iterations, sample

sigma = .5

OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX")
PERSIST_PATH = os.environ.get("PERSIST_PATH")


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
    import numpy as np  # noqa
    from mpi4py import MPI  # noqa

    rank = MPI.COMM_WORLD.rank
    print(rank)
    y = p.a + p.b * x + p.c * x ** 2
    diff = (y - y_measured) / sigma
    return -np.dot(diff.T, diff) / 2


n_samples = 1500
n_walkers_per_param = 200


def main():
    samples, __ = sample(
        lnprob,
        p,
        args=gen_data(),
        n_walkers_per_param=n_walkers_per_param,
        n_samples=n_samples,
        show_progress=False,
        show_output=False,
        output_prefix=OUTPUT_PREFIX,
        parallel=True,
        verbose=True,
        persist=persist_every_n_iterations(1, PERSIST_PATH),
    )
    return samples


print("++++ START")
try:
    samples = main()
    print("++++ SAMPLES", samples.shape)
except Exception as e:
    print("+++++ ERROR")
    print(e)

print("++++ DONE")
