# # # # # # # # # # # # # # # # # # # # # # # # # #
# Executor class using serial execution (no parallelization)
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import copy
from collections.abc import Iterable
import numpy

from .executor import Executor
from ..utils.timing import Timing

class Serial (Executor):
    """Executor class for serial execution of tasks."""

    manager = 0
    workers = 1

    @staticmethod
    def address (peers):
        """Set rank of serial executor to 0 fictitiously."""

        address = 0
        return address

    @staticmethod
    def universe_address ():
        """Set address of serial executor to None as there is no hierarchy."""

        address = None
        return address

    def bootup (self, peers):
        """Return means of inter-communication along a possible hierarchy of processes."""

        # bind task
        self.taskroot = self.task.rootcall (peers)

        # init task executor
        if hasattr (self.task, 'executor'):
            self.taskport = self.task.executor.init (peers=peers, internal=1)
        else:
            self.taskport = None

        # serial executor simply forwards taskport onwards to other executors
        return self.taskport

    def shutdown (self):
        """Finalize executor."""

        if hasattr (self.task, 'executor'):
            self.task.executor.exit ()

    def map (self, functions, parameters=None, *args):
        """Request execution of tasks following a task-dependent logic, and receive results."""

        # prepare timings
        self.timing = Timing ()
        timing = Timing ()

        # determine operational mode
        if parameters is not None:
            if isinstance (functions, Iterable):
                assert len (parameters) == len (functions)
                mode = 'MFMP' # multiple functions with multiple parameters
            else:
                mode = 'SFMP' # single function with multiple parameters
        else:
            mode = 'MFNP' # multiple functions with no parameters (should be specified in 'args')

        # prepare tasks according to the operational mode
        if mode == 'SFMP':
            function = functions
            self.prepare (function)
            function.root = self.taskroot
            if hasattr (function, 'executor'):
                function.executor.bind (self.taskroot, self.taskport)
            timing.start ('task')
            results = [ None ] * len (parameters)
            for index, ps in enumerate (parameters):
                results [index] = function (ps, *args)
            timing.time ('task')
        if mode == 'MFNP':
            for function in functions:
                self.prepare (function)
                function.root = self.taskroot
                if hasattr (function, 'executor'):
                    function.executor.bind (self.taskroot, self.taskport)
            timing.start ('task')
            results = [ None ] * len (functions)
            for index, function in enumerate (functions):
                results [index] = function (*args)
            timing.time ('task')
        if mode == 'MFMP':
            for function in functions:
                self.prepare (function)
                function.root = self.taskroot
                if hasattr (function, 'executor'):
                    function.executor.bind (self.taskroot, self.taskport)
            timing.start ('task')
            results = [ None ] * len (parameters)
            for index, function in enumerate (functions):
                results [index] = function (parameters [index], *args)
            timing.time ('task')

        timings = [timing]
        return results, timings

    def connect (self, ensemble, indices):
        """Establish inter-connection with the lower level along the possible hierarchy of Executors."""

        self.timing = Timing ()
        self.worker_timing = Timing ()
        self.ensemble = ensemble

        # prepare ensemble
        self.prepare (self.ensemble)

        # bind ensemble
        self.ensemble.root = self.taskroot

        # bind ensemble task
        self.ensemble.task.root = self.taskroot

        # bind ensemble task executor
        if hasattr (self.ensemble.task, 'executor'):
           self.ensemble.task.executor.bind (self.taskroot, self.taskport)

        # init ensemble
        self.worker_timing.start ('init')
        self.ensemble.init (indices)
        self.worker_timing.time ('init')

    # disconnect task ensemble
    def disconnect (self):
        """Disconnect taks ensemble."""

        self.ensemble.exit ()
        return [self.worker_timing]

    # report performance
    def report (self):
        """Return execution timings."""

        return self.timing

    # execute ensemble method with specified args and return results
    def call (self, method, args=[], results=1):
        """Execute ensemble method with specified args and return results."""

        self.worker_timing.start (method)
        call = getattr (self.ensemble, method)
        results = call (*args)
        self.worker_timing.time (method)
        if results:
            return results
        else:
            return

    # resample (delete and clone) tasks according to the specified indices
    def resample (self, indices):
        """Init, clone and kill (resample) tasks according to specified 'indices'."""

        # 1. remove all extinct particles (not to be kept: 'kill')
        # 2. stash remaining particles
        # 3. clone particles (to be kept: 'keep'):
        #   3.1. fetch stashed particles according to 'keep_counters'
        #   3.2. copy particles according to 'keep_counters'

        self.worker_timing.start ('resample')

        # container for traffic information
        traffic = {}

        # track sources
        sources = numpy.empty (len (indices), dtype=int)

        # count keep particles for each index
        keep_counters = {}
        for reindex, index in enumerate (indices):
            if index not in keep_counters:
                keep_counters [index] = [reindex]
            else:
                keep_counters [index] .append (reindex)
            sources [reindex] = index

        # 1. remove all extinct particles according to the 'keep_counters'
        self.worker_timing.start ('kill')
        kill = set (self.ensemble.particles.keys ()) - set (keep_counters.keys ())
        for index in kill:
            self.ensemble.remove (index)
        traffic ["kill"] = len (kill) / len (indices)
        self.worker_timing.time ('kill')

        self.worker_timing.start ('clone')

        # 2. stash particles that are to be kept
        self.worker_timing.start ('stash')
        stashes = {}
        for index in keep_counters.keys ():
            stashes [index] = self.ensemble.stash (index)
        self.worker_timing.time ('stash')

        # 3. clone particles according to 'keep_counters':

        # 3.1. fetch (rename) stashed particles according to 'keep_counters'
        self.worker_timing.start ('fetch')
        for index, reindices in keep_counters.items ():
            reindex = reindices [0]
            self.ensemble.fetch (stashes [index], reindex)
            del stashes [index]
        self.worker_timing.time ('fetch')

        # 3.2. copy particles according to 'keep_counters'
        copys = 0
        for index, reindices in keep_counters.items ():
            if len (reindices) > 1:
                reindex = reindices [0]
                state = self.ensemble.particles [reindex] .save ()
                for reindex in reindices [1:]:
                    self.ensemble.particles [reindex] = copy.deepcopy (self.ensemble.task)
                    self.ensemble.isolate (reindex)
                    self.ensemble.particles [reindex] .load (state)
                    copys += 1
        traffic ["copy"] = copys / len (indices)

        self.worker_timing.time ('clone')

        self.worker_timing.time ('resample')

        return traffic, sources

    # abort - likely to hang if there are others MPI-aware executors
    def abort (self):
        """Exit from a serial execution."""

        import sys
        sys.exit ()
