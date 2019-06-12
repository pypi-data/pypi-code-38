# # # # # # # # # # # # # # # # # # # # # # # # # #
# Direct likelihood class for a determistic model
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy

from ..utils.timing import Timing
from ..utils import evaluations
from .likelihood import Likelihood
from .ensemble import Ensemble

class Direct (Likelihood):
    """Likelihood class for a deterministic model, where likelihood is computed directly from the specified error model."""

    # constructor
    def __init__ (self, log=1):

        self.log = log

    @property
    def evaluations (self):

        return evaluations.construct (self, 1)

    # attach an executor
    def attach (self, executor):
        """Attach an executor."""

        self.executor = executor
        self.executor.setup (self)
        methods = ['connect', 'call', 'resample', 'disconnect']
        self.executor.capabilities (methods)

    # evaluate likelihood of the specified parameters
    def __call__ (self, parameters):
        """Evaluate likelihood for the specified parameters."""

        # verbose output
        if self.verbosity >= 2:
            print ("Direct likelihood parameters:")
            print (parameters)

        # start global timer
        timing = Timing ()
        timing.start ('evaluate')

        # ensemble consists only of a single model
        ensemble = Ensemble (self.model, self.inputset, parameters, self.error)
        ensemble.setup (self.sandbox, self.verbosity - 1, self.seed, self.informative, self.trace)

        # initialize task ensemble in executor
        self.executor.connect (ensemble, indices=[0])

        # initialize predictions container
        predictions = {}

        # initialize estimates container
        estimates = {}

        # initial estimate is assumed to be successful
        successful = True

        # iterate over all dataset snapshots (times)
        for snapshot in self.dataset.index:

            if self.verbosity:
                print("Snapshot", snapshot)

            # model
            if self.verbosity >= 2:
                print("Running %s model..." % self.task.name)
            predictions [snapshot] = self.executor.call ('run', args = [snapshot]) [0]

            # compute estimate
            if self.verbosity >= 2:
                print("Computing estimate...")
            estimates [snapshot] = self.executor.call ('errors', args = [self.dataset.loc [snapshot]]) [0]

            if self.verbosity:
                print ("Estimated %slikelihood: %1.1e" % ('log-' if self.log else '', estimates [snapshot]))

            # if estimator failed - no further simulation makes sense
            if numpy.isnan (estimates [snapshot]):
                successful = False
                if self.verbosity:
                    print (" :: WARNING: NaN estimate in the Direct likelihood.")
                    print ("  : -> stopping here and returning the infos as they are.")
                break

            # if estimator failed - no further simulation makes sense
            if estimates [snapshot] == 0:
                successful = False
                if self.verbosity:
                    print (" :: WARNING: 0 estimate in the Direct likelihood.")
                    print ("  : -> stopping here and returning the infos as they are.")
                break

            # advance ensemble state to next iteration (do not gather results)
            self.executor.call ('advance', results=0)

        # finalize task ensemble in executor
        timings = self.executor.disconnect ()

        # append executor timing
        timing += self.executor.report ()

        # compute estimated (log-)likelihood as the product of estimates from all snapshots
        if self.log:
            estimate = numpy.sum (list (estimates.values()))
        else:
            estimate = numpy.prod (list (estimates.values()))

        if self.verbosity:
            print ("Estimated %slikelihood: %1.1e" % ('log-' if self.log else '', estimate))

        # measure evaluation runtime and timestamp
        timing.time ('evaluate')

        # information includes predictions, errors, estimates, and timings
        info = {}
        info ["predictions"] = predictions
        info ["estimates"] = estimates
        info ["successful"] = successful
        if self.informative:
            info ["timing"] = timing
            info ['timings'] = timings

        # return estimated likelihood and its info
        return estimate, info
