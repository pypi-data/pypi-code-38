# # # # # # # # # # # # # # # # # # # # # # # # # #
# Executor class using mpi4py bindings and MPI backend for distributed memory paralellization
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch

# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import cloudpickle
MPI.pickle.__init__ (cloudpickle.dumps, cloudpickle.loads)

from copy import deepcopy as copy
import sys

from ..executor import Executor
from .ensemble_contract import INIT, CALL, RESA, DONE, EXIT, Instruction, contract

from ..balancers.adaptive import Adaptive
from .connectors.spawn import Spawn

from ...utils.timing import Timing
from ...utils import transforms

class Mpi4pyEnsemble (Executor):
    "Executor class for Ensemble tasks."

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

    def __init__ (self, workers=None, balancer=Adaptive(), connector=Spawn()):

        self.workers = workers
        self.balancer = balancer
        self.connector = connector

        self.balancer.verbosity = self.verbosity - 1 if self.verbosity > 0 else 0

    def info (self):

        thread = MPI.Query_thread()
        if thread == MPI.THREAD_MULTIPLE:
            return 'multiple threads support'
        elif thread == MPI.THREAD_SERIALIZED:
            return 'multiple threads support (serialized)'
        else:
            return 'NO support for multiple threads'

    def bootup (self, peers):
        """Return means of inter-communication along a possible hierarchy of processes."""

        # get port for later connection to an inter-communicator to worker pool
        port = self.connector.bootup (contract, self.task, self.resources () [0], self.root, self.verbosity)

        return port

    def shutdown (self):
        """Finalize executor."""

        workers = self.connector.accept (self.port, self.verbosity)
        workers.Bcast (Instruction (EXIT).list, root=MPI.ROOT)
        self.connector.disconnect (workers, self.verbosity)
        workers = None
        self.connector.shutdown (self.port, self.verbosity)

    # set task ensemble for execution
    def connect (self, ensemble, indices):
        """Establish inter-connection with the lower level along the possible hierarchy of Executors.

        Set task ensemble for execution
        """

        # warn if the length of indices is smaller than the number of workers
        if len (indices) < self.workers and self.verbosity:
            print (' :: WARNING: the length of indices in \'Ensemble.connect (...)\' is smaller than the number of workers:')
            print ('  : -> %d < %d.' % (len (indices), self.workers))

        self.workers_comm = self.connector.accept (self.port, self.verbosity)

        self.timing = Timing ()

        instruction = Instruction (INIT)
        self.workers_comm.Bcast (instruction.list, root=MPI.ROOT)

        # prepare and broadcast ensemble
        self.prepare (ensemble)
        self.workers_comm.bcast (ensemble, root=MPI.ROOT)

        # set balancer verbosity
        self.balancer.verbosity = self.verbosity - 1 if self.verbosity > 0 else 0

        # distribute task indices to workers
        self.ensembles = self.balancer.ensembles (indices, self.workers)
        if self.verbosity >= 2:
            print("connect ensembles (before scatter):", self.ensembles)

        # scatter task ensembles to workers (must make a copy, because after scatter self.ensembles is invalid!)
        if self.verbosity >= 2:
            print ("connect ensembles (before scatter):", self.ensembles)
            sys.stdout.flush()
        self.workers_comm.scatter (copy (self.ensembles), root=MPI.ROOT)
        if self.verbosity >= 2:
            print ("connect ensembles (after scatter):", self.ensembles)
            sys.stdout.flush()

        # time init sync overhead
        self.timing.start ('wait')
        self.workers_comm.Barrier ()
        self.timing.time ('wait')

    # disconnect task ensemble
    def disconnect (self):
        """Disconnect taks ensemble."""

        instruction = Instruction (DONE)
        self.workers_comm.Bcast (instruction.list, root=MPI.ROOT)

        # gather worker timings
        timings = self.workers_comm.gather (None, root=MPI.ROOT)

        self.connector.disconnect (self.workers_comm, self.verbosity)
        self.workers_comm = None

        if self.verbosity >= 2:
            print("Ensemble executor disconnect")

        return timings

    # report performance
    def report (self):
        """Return execution timings."""

        return self.timing

    # execute ensemble method with specified args and return results (if wait=1)
    def call (self, method, args=[], results=1):
        """Execute ensemble method with specified args and return results."""

        instruction = Instruction (CALL)
        self.workers_comm.Bcast (instruction.list, root=MPI.ROOT)
        self.workers_comm.bcast ({'method' : method, 'args' : args, 'results' : results}, root=MPI.ROOT)

        # if there are no results to wait for, return
        if not results:
            return None

        # else, wait for the results and process them
        self.timing.start ('wait')
        results = self.workers_comm.gather (None, root=MPI.ROOT)
        self.timing.time ('wait')

        if any (result is None for result in results):
            print (" :: ERROR: Encountered \'None\' results in \'Ensemble.call (...)\'.")
            sys.stdout.flush ()
            self.workers_comm.Abort ()

        return transforms.flatten (results)

    # resample (delete and replicate) tasks and balance ensembles
    def resample (self, indices):
        """Clone and kill (resample) tasks and balance ensembles."""

        # compute new task ensembles and their routings from current task
        # ensembles
        if self.verbosity >= 2:
            print("Resample: current ensembles:", self.ensembles)
        self.ensembles, routings = self.balancer.routings (self.ensembles, indices)
        if self.verbosity >= 2:
            print("Resample: future ensembles:", self.ensembles)
        if self.verbosity >= 2:
            print("Resample: routings", routings)

        # measure traffic
        traffic = self.balancer.traffic (routings)

        # compute sources
        sources = self.balancer.sources (routings)

        # send instruction to start the task resampling and ensemble balancing process
        instruction = Instruction (RESA)
        self.workers_comm.Bcast (instruction.list, root=MPI.ROOT)

        # scatter routings
        self.timing.start ('routings')
        self.workers_comm.scatter (routings, root=MPI.ROOT)
        self.timing.time ('routings')

        # gather timings
        self.timing.start ('wait')
        self.workers_comm.Barrier ()
        self.timing.time ('wait')

        return traffic, sources

    # abort
    def abort (self):
        """Exit from a parallel execution."""

        MPI.Abort ()
