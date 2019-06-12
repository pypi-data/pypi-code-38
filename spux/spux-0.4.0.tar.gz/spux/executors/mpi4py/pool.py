# # # # # # # # # # # # # # # # # # # # # # # # # #
# Mpi4pyPool executor class using mpi4py bindings and MPI backend for distributed memory paralellization
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import cloudpickle
MPI.pickle.__init__ (cloudpickle.dumps, cloudpickle.loads)
from collections import Iterable

from ..executor import Executor
from .pool_contract import INIT, TASK, DONE, EXIT, Instruction, contract

from .connectors.spawn import Spawn

from ...utils.timing import Timing

class Mpi4pyPool (Executor):
    "Executor class for Pool tasks."

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

    def bootup (self, peers):
        """Return means of inter-communication along a possible hierarchy of processes."""

        # get port for later connection to an inter-communicator to worker pool
        port = self.connector.bootup (contract, self.task, self.resources () [0], self.root, self.verbosity)

        return port

    def shutdown (self):
        """Finalize executor."""

        workers = self.connector.accept (self.port, self.verbosity)
        workers.Bcast (Instruction(EXIT).list, root=MPI.ROOT)
        self.connector.disconnect (workers, self.verbosity)
        workers = None
        self.connector.shutdown (self.port, self.verbosity)

    # report performance
    def report (self):
        """Return execution timings."""

        return self.timing

    def map (self, functions, parameters=None, *args):
        """Request execution of tasks following a task-dependent logic, and receive results."""

        # determine operational mode
        if parameters is not None:
            if isinstance (functions, Iterable):
                assert len (parameters) == len (functions)
                mode = b'MFMP' # multiple functions with multiple parameters
            else:
                mode = b'SFMP' # single function with multiple parameters
        else:
            mode = b'MFNP' # multiple functions with no parameters (should be specified in 'args')

        # setup timing
        self.timing = Timing ()

        # connect to workers and initialize them
        workers = self.connector.accept (self.port, self.verbosity)
        workers.Bcast (Instruction(INIT).list, root=MPI.ROOT)
        workers.Bcast ([mode, 4, MPI.CHAR], root=MPI.ROOT)

        # prepare tasks according to the operational mode
        if mode == b'SFMP':
            function = functions
            self.prepare (function)
            tasks = list (parameters)
        if mode == b'MFNP':
            for function in functions:
                self.prepare (function)
            function = None
            tasks = list (functions)
        if mode == b'MFMP':
            for function in functions:
                self.prepare (function)
            tasks = [ { 'function' : function, 'parameters' : parameters [index] } for index, function in enumerate (functions) ]
            function = None

        # warn if the number of tasks is smaller than the number of workers
        if len (tasks) < self.workers and self.verbosity:
            print (' :: WARNING: the nunber of received tasks in \'Pool.map (...)\' is smaller than the number of workers:')
            print ('  : -> %d < %d.' % (len (tasks), self.workers))

        # broadcast function with args
        workers.bcast ((function, args), root=MPI.ROOT)

        requested = 0
        indexes = {}

        startup = min (self.workers, len (tasks))
        for destination in range (startup):
            workers.Send (Instruction(TASK).list, dest=destination)
            workers.send (tasks [destination], dest=destination)
            indexes [destination] = destination
        requested = startup

        for destination in range (startup, self.workers):
            workers.Send (Instruction(DONE).list, dest=destination)

        results = [ None for task in tasks ]

        for i in range (len (tasks)):
            status = MPI.Status ()
            self.timing.start ('wait')
            result = workers.recv (source=MPI.ANY_SOURCE, status=status)
            self.timing.time ('wait')
            destination = status.source
            results [indexes [destination]] = result
            if requested < len (tasks):
                workers.Send (Instruction(TASK).list, dest=destination)
                workers.send (tasks [requested], dest=destination)
                indexes [destination] = requested
                requested += 1
            else:
                workers.Send (Instruction(DONE).list, dest=destination)

        self.timing.start ('wait')
        workers.Barrier ()
        self.timing.time ('wait')
        timings = workers.gather (None, root=MPI.ROOT)
        self.connector.disconnect (workers, self.verbosity)

        return results, timings

    # abort
    def abort (self):
        """Exit from a parallel execution."""

        MPI.Abort ()
