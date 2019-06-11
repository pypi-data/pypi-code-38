# encoding: utf-8
import sys

import pkg_resources

from ._parallel import runs_with_mpi as _runs_with_mpi
from .lnprob_adapters import *  # noqa
from .parameters import Parameters  # noqa
from .persisting import load_samples  # noqa
from .persisting import persist_every_n_iterations  # noqa
from .persisting import persist_final  # noqa
from .persisting import persist_on_error  # noqa
from .sampler import *  # noqa

if _runs_with_mpi():

    def handler(type_, value, tb):
        import traceback
        from mpi4py import MPI

        traceback.print_tb(tb, file=sys.stdout)
        sys.stdout.flush()

        MPI.COMM_WORLD.Abort(1)

    sys.excepthook = handler

__version__ = pkg_resources.require(__package__)[0].version
