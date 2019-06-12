# # # # # # # # # # # # # # # # # # # # # # # # # #
# Markov chain Monter Carlo (affine-invariant ensemble) sampler class
# Foreman-Mackey, Hogg, Lang & Goodman
# "emcee: The MCMC Hammer"
# PASP, 2012.
#
# Code in 'stretch ()' and 'propose ()' methods was adapted from
# https://github.com/dfm/emcee
# and extended according to the needs of the SPUX framework.
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #
from __future__ import absolute_import  # Fixes emcee modules names conflict

import numpy
import pandas
from copy import deepcopy as copy

from .sampler import Sampler
from ..utils.timing import Timing
from ..executors.serial import Serial

numpy.seterr (invalid='ignore')

class FORECAST (Sampler):
    """Markov chain Monter Carlo (affine-invariant ensemble) sampler class."""

    def __init__(self, chains, a=2.0, attempts=100):

        self.chains = chains
        self.a = a
        self.attempts = attempts

    def assign (self, likelihood, proposal=None):
        """Assign required components to forecast sampler."""

        if proposal is None:
            raise ValueError("Fatal. It is mandatory to specify a proposal distribution for the forecast sampler.")

        self.likelihood = likelihood
        self.proposal = proposal

        self.sandboxing = self.likelihood.sandboxing
        self.task = self.likelihood

        if hasattr (self, 'executor'):
            self.executor.setup (self)
        else:
            self.attach (Serial ())

    # init chain
    def init (self, initial=None, reinit=0, posteriors=None):
        """Init chain.

        Initial values and associated posteriors can be provided to continue the sampling process instead of starting from the begining.
        """

        # additional routines for the first init
        if not reinit:

            # setup likelihoods for each chain
            self.likelihoods = [ copy (self.likelihood) for index in range (self.chains) ]

            # for continuation sampling, attempt to load the most recent pickup file
            if self._pickup is not None:
                if initial is None:
                    initial = self._pickup ['init'] ['parameters']
                if posteriors is None:
                    posteriors = self._pickup ['init'] ['posteriors']

        # reset status
        self.initialized = 0

        # if initial parameters are not specified, draw them from the proposal distribution
        if initial is None:
          self.parameters = pandas.DataFrame (index=range(0), columns=self.proposal.labels)
          for index in range (self.chains):
            parameters = self.proposal.draw (rng=self.rng)
            self.parameters = self.parameters.append (parameters, ignore_index=1, sort=True)

        # else, if only one set of parameters is specified, replicate it
        elif not isinstance (initial, pandas.DataFrame):
            self.parameters = pandas.DataFrame (initial, index=range(1))
            self.parameters = pandas.DataFrame (numpy.repeat (self.parameters.values, self.chains, axis=0), index=range(self.chains), columns=self.parameters.keys())

        # else, if all parameteres are specified, use them
        else:
            self.parameters = initial
            if posteriors is not None:
                self.Lps = posteriors
                self.initialized = 1

        # assign right type to parameters
        for c in self.parameters.columns:
            self.parameters[c] = self.parameters[c].astype(self.proposal.types[c])

        # store keys for later wrapping
        self.labels = self.parameters.keys()

        # store parameter dimensions - how many paramters to be inferred
        self.dimensions = len (self.labels)

        if self.verbosity >= 3:
            print("Initial samples:")
            print(self.parameters)

        if self.initialized and self.verbosity >= 3:
            print ("Initial posteriors:")
            print (self.Lps)

    def pickup (self):
        """Return sampler pickup information as a dictionary."""

        return {'parameters' : self.parameters, 'posteriors' : self.Lps}

    # evaluate likelihoods and proposals of the proposed parameters
    def evaluate (self, qs):
        """Evaluate likelihoods and proposals of the proposed parameters."""

        # get indices to be evaluated
        indices = qs.index.values

        # evaluate proposals
        ps = numpy.array ([ self.proposal.logpdf (parameters) if self.proposal else 0.0 for index, parameters in qs.iterrows () ])

        # skip likelihood evaluation for parameters with zero proposal
        keep = numpy.where (ps != float ('-inf')) [0]
        skip = numpy.where (ps == float ('-inf')) [0]

        # evaluate the respective likelihoods (according to the specified indices)
        Ls = numpy.full (len(qs), float ('-inf'))
        likelihoods = [ self.likelihoods [ indices [index] ] for index in keep ]
        parameters = [ parameters for index, parameters in qs.iloc[keep].iterrows () ]
        results, timings = self.executor.map (likelihoods, parameters)

        # extract estimates and infos
        infos = [ None ] * len(qs)
        for i, result in enumerate (results):
            Ls [keep[i]], infos [keep[i]] = result

        # get executor timing
        timing = self.executor.report ()

        # compute Ls + ps
        Lps = Ls + ps

        # set skipped likelihoods to 'NaN's (after computing Lps)
        Ls [skip] = float ('nan')

        return Lps, ps, Ls, infos, timing, timings

    # returned packed results
    def results (self):
        """Returned packed results."""

        info = {}
        info ["index"] = self.index
        info ["parameters"] = self.parameters
        info ["proposes"] = self.proposes
        info ["proposals"] = self.ps
        info ["likelihoods"] = self.Ls
        info ["posteriors"] = self.Lps
        info ["accepts"] = self.accepts
        info ["infos"] = self.infos
        if self.informative:
            info ["timing"] = self.timing
            info ["timings"] = self.timings

        return self.parameters, info

    def propose (self):
        """Propose new parameters."""

        self.timing = Timing ()
        self.timings = [Timing () for worker in range (self.executor.workers)]

        self.ps = numpy.zeros (self.chains)
        self.Ls = numpy.zeros (self.chains)
        self.infos = [None for chain in range(self.chains)]

        self.proposes = pandas.DataFrame (index=range(self.chains), columns=self.labels)
        for index in range (self.chains):
            self.proposes.iloc[index] = self.proposal.draw (rng=self.rng)

        # assign right type to proposals
        for c in self.proposes.columns:
            self.proposes[c] = self.proposes[c].astype(self.proposal.types[c])

        Lps, ps, Ls, infos, timing, timings = self.evaluate (self.proposes)

        self.accepts = numpy.ones (self.chains)
        self.ps = ps
        self.Ls = Ls
        self.infos = infos
        self.Lps = Lps
        self.parameters = self.proposes
        self.timing += timing
        for worker, timing in enumerate (self.timings):
            timing += timings [worker]

    # draw samples from posterior distribution
    def draw (self, sandbox, seed):
        """Draw samples from posterior distribution."""

        # setup likelihoods
        for chain, likelihood in enumerate (self.likelihoods):
            label = 'C%05d' % chain
            chain_sandbox = sandbox.spawn (label) if self.sandboxing else None
            chain_seed = seed.spawn (chain, name=label)
            likelihood.setup (chain_sandbox, self.verbosity - 2, chain_seed, self.informative, self.trace)

        # treat 'initial' parameters as the first sample
        if not self.initialized:

            if self.verbosity >= 3:
                print ('EMCEE: draw (initialize)')

            # attempt to evaluate likelihood of the initial parameters, with a redraw if needed
            for attempt in range (self.attempts):

                # all initial samples are proposed
                self.proposes = self.parameters

                # evaluate likelihood and proposal of the initial parameters
                self.Lps, self.ps, self.Ls, self.infos, self.timing, self.timings = self.evaluate (self.proposes)

                # check if at least one likelihood is valid
                if not all (self.Lps == float ("-inf")):
                    break

                # otherwise, attempt to redraw proposal samples
                else:

                    # if this is the final attempt, crash
                    if attempt == self.attempts - 1:
                        print (" :: Fatal: Unable to find initial parameters with non-zero likelihoods.")
                        print ("  : -> You may try to change seed and/or give explicit initial parameters.")
                        self.executor.abort ()

                    # otherwise, attempt to redraw proposal samples
                    if self.verbosity >= 2:
                        print (" :: Warning: The likelihoods of all initial parameters are zero.")
                        print ("  : -> Re-drawing initial parameters from proposal (attempt: %d/%d)" % (attempt, self.attempts))
                    self.init (initial=None, reinit=1)

            # all initial samples are accepted
            self.accepts = numpy.ones ((self.chains,))

            # all initial parameters are accepted
            self.parameters = self.proposes

            # update status
            self.initialized = 1

            return self.results ()

        if self.verbosity >= 3:
            print ('EMCEE: draw (sample)')

        # get new parameters
        self.propose ()

        return self.results ()
