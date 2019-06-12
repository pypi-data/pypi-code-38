# # # # # # # # # # # # # # # # # # # # # # # # # #
# Mpi4pyModel executor class using mpi4py bindings and MPI backend for parallel models
#
# Marco Bacci
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

# WORK IN PROGRESS
# most probably needs functionality analogous to Mpi4pyEnsemble executor

from mpi4py import MPI
import cloudpickle
MPI.pickle.__init__ (cloudpickle.dumps, cloudpickle.loads)

from ..executor import Executor

from .connectors.spawn import Spawn

#from ...utils.timing import Timing

class Mpi4pyModel (Executor):
    """Class to execute tasks in compliance with legacy MPI implementations."""

    manager = 1

    @staticmethod
    def address (peers):
        """Return rank in peers communicator"""

        return peers.Get_rank ()

    @staticmethod
    def universe_address ():
        """Return rank in MPI COMM_WORLD"""

        address = MPI.COMM_WORLD.Get_rank ()
        return address

    def __init__ (self, workers, connector=Spawn()):

        self.workers = workers
        self.connector = connector

    def info (self):

        thread = MPI.Query_thread()
        if thread == MPI.THREAD_MULTIPLE:
            return 'multiple threads support'
        elif thread == MPI.THREAD_SERIALIZED:
            return 'multiple threads support (serialized)'
        else:
            return 'NO support for multiple threads'

    # abort
    def abort (self):
        """Exit from a parallel execution."""

        MPI.Abort ()
