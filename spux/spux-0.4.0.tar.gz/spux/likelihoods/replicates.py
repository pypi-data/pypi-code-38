# # # # # # # # # # # # # # # # # # # # # # # # # #
# Replicates class for multiple independent data sets
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
from copy import deepcopy as copy

from .likelihood import Likelihood
from ..executors.serial import Serial
from ..io import dumper
from ..utils import evaluations
import sys

class Replicates (Likelihood):
    """Replicates class for multiple independent data sets."""

    @property
    def evaluations (self):

        return evaluations.construct (self, len (self.datasets))

    # constructor
    def __init__(self, log=1, sort=1):

        self.log = log
        self.sort = sort

        # initially likelihoods are not created
        self.likelihoods = None

    # feedback
    def feedback (self, likelihoods):
        """Feedback method to be executed by the sampler."""

        # compute feedbacks
        if hasattr (self.likelihood, 'feedback') and self.likelihoods is not None:
            feedbacks = {name : likelihood.feedback (likelihoods [name]) for name, likelihood in self.likelihoods.items ()}
            return feedbacks
        else:
            return {name : float ('nan') for name in self.names}

    # assign required components to likelihood
    def assign (self, likelihood, datasets, inputsets=None):
        """Assign required components to Replicate likelihood."""

        if not hasattr (likelihood, 'assigned'):
            print (' :: ERROR: likelihood needs to have components assigned before being assigned to replicates.')
            sys.exit ()

        self.likelihood = likelihood
        self.datasets = datasets
        self.inputsets = inputsets

        self.task = self.likelihood
        self.sandboxing = self.likelihood.sandboxing

        self.names = list (datasets.keys ())

        if not hasattr (self, 'executor'):
            self.attach (Serial ())

        self.assigned = True

        dumper.config (self)

    # evaluate likelihoods of the specified parameters for all replicates and combine them
    def __call__ (self, parameters):
        """Evaluate likelihoods of the specified parameters for all replicates and combine them."""

        # verbose output
        if self.verbosity:
            print ("Replicates parameters:")
            print (parameters)

        # create likelihoods by combining with each dataset in the datasets
        if self.likelihoods is None:
            self.likelihoods = {}
            for name, dataset in self.datasets.items ():
                self.likelihoods [name] = copy (self.likelihood)
                self.likelihoods [name] .dataset = dataset
                if self.inputsets is not None:
                    self.likelihoods [name] .inputset = self.inputsets [name]

        # setup likelihoods
        for index, (name, likelihood) in enumerate (self.likelihoods.items ()):
            label = 'R-%s' % name
            sandbox = self.sandbox.spawn (label) if self.sandboxing else None
            seed = self.seed.spawn (index, name=label)
            feedback = self._feedback [name] if self._feedback is not None else None
            likelihood.setup (sandbox, self.verbosity - 1, seed, self.informative, self.trace, feedback)

        # sort likelihoods according to the length of the associated dataset and the size of the likelihood
        if self.sort:
            lengths = [ len (likelihood.dataset) * likelihood.evaluations [0] ['cumulative'] for likelihood in self.likelihoods.values () ]
            ordering = numpy.argsort (lengths) [::-1]
            keys = numpy.array ([ key for key in self.likelihoods.keys () ]) [ordering]
            likelihoods = [ self.likelihoods [key] for key in keys ]
            if self.verbosity:
                print ("Using ordered likelihoods:")
                print (" -> order: ", keys)
        else:
            keys = self.likelihoods.keys ()
            likelihoods = self.likelihoods.values ()

        # schedule likelihood evaluations
        results, timings = self.executor.map (likelihoods, None, parameters)

        # append executor timing
        timing = self.executor.report()

        # get results
        evaluations = {}
        infos = {}
        for index, name in enumerate (keys):
            evaluations [name], infos [name] = results [index]

        # compute estimated (log-)likelihood as the product of estimates from all replicates
        successful = True
        evaluations_array = numpy.array (list(evaluations.values()))
        nans = numpy.isnan (evaluations_array)
        if any (nans):
            mean = numpy.nanmean (evaluations_array)
            if numpy.isnan (mean):
                successful = False
            if self.verbosity:
                print (" :: WARNING: encountered NaN estimates in the Replicates likelihood:")
                print (evaluations)
                print ("  : -> setting NaN estimates to the mean of the non-NaN estimates: %1.1e" % mean)
            evaluations_array = numpy.where (nans, mean, evaluations_array)
        if self.log:
            if not self.likelihood.log:
                evaluations_array = numpy.log (evaluations_array)
            evaluation = numpy.sum (evaluations_array)
        else:
            if self.likelihood.log:
                evaluations_array = numpy.exp (evaluations_array)
            evaluation = numpy.prod (evaluations_array)

        # clean up sandboxes
        if self.sandboxing and not self.trace:
            for likelihood in self.likelihoods.values ():
                likelihood.sandbox.remove ()

        # information
        info = {}
        info ["evaluations"] = evaluations
        info ["infos"] = infos
        info ["successful"] = successful
        if self.informative:
            info ["timing"] = timing
            info ["timings"] = timings

        # return estimated likelihood, its info
        return evaluation, info
