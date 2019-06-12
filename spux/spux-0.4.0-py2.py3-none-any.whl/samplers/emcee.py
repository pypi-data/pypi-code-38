# # # # # # # # # # # # # # # # # # # # # # # # # #
# Markov chain Monter Carlo (affine-invariant ensemble) sampler class
# Foreman-Mackey, Hogg, Lang & Goodman
# "emcee: The MCMC Hammer"
# PASP, 2012.
#
# Code in 'stretch ()' and 'propose ()' methods was adapted from
# https://github.com/dfm/emcee (dated in 2018)
# and extended according to the needs of the SPUX framework.
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import numpy
import pandas
from copy import deepcopy as copy

from .sampler import Sampler
from ..utils.timing import Timing

numpy.seterr (invalid='ignore')

class EMCEE (Sampler):
    """Markov chain Monter Carlo (affine-invariant ensemble) sampler class."""

    def __init__(self, chains, a=2.0, attempts=100, reset=10):
        """
        Constructor: *reset* is the number of chain updates after which likelihoods of stuck chains are re-evaluated.
        """

        self.chains = chains
        self.a = a
        self.attempts = attempts
        self.reset = reset

    # init chain
    def init (self, initial=None, reinit=0, posteriors=None):
        """Init chain.

        Initial values and associated posteriors can be provided to continue the sampling process instead of starting from the beggining.
        """

        # additional routines for the first init
        if not reinit:

            # issue a warning if there are fewer chains than twice the number of workers
            if self.chains < 2 * self.executor.workers:
                print (' :: WARNING: in EMCEE sampler, number of chains is less than twice the number of workers:')
                print ('  : -> %d < 2 * %d.' % (self.chains, self.executor.workers))

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

        # if initial parameters are not specified, draw them from the prior distribution
        if initial is None:
            self.parameters = pandas.DataFrame (index=range(0), columns=self.prior.labels)
            for index in range (self.chains):
                parameters = self.prior.draw (rng=self.rng)
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
            self.parameters[c] = self.parameters[c].astype(self.prior.types[c])

        # store keys for later wrapping
        self.labels = self.parameters.keys()

        # store parameter dimensions - how many paramters to be inferred
        self.dimensions = len (self.labels)

        # initialize stuck counters
        self.stuck = numpy.zeros (self.chains, dtype=int)

        if self.verbosity >= 3:
            print("Initial samples:")
            print(self.parameters)

        if self.initialized and self.verbosity >= 3:
            print ("Initial posteriors:")
            print (self.Lps)

    def pickup (self):
        """Return sampler pickup information as a dictionary."""

        return {'parameters' : self.parameters, 'posteriors' : self.Lps}

    # evaluate likelihoods and priors of the proposed parameters
    def evaluate (self, qs):
        """Evaluate likelihoods and priors of the proposed parameters."""

        # get indices to be evaluated
        indices = qs.index.values

        # evaluate priors
        ps = numpy.array ([ self.prior.logpdf (parameters) if self.prior else 0.0 for index, parameters in qs.iterrows () ])

        # skip likelihood evaluation for parameters with zero prior
        keep = numpy.where (ps != float ('-inf')) [0] #numpy.array(numpy.where (ps != float('-inf')))
        skip = numpy.where (ps == float ('-inf')) [0] #numpy.array(numpy.where (ps == float('-inf')))

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

        # sampler info
        info = {}
        info ["index"] = self.index
        info ["parameters"] = self.parameters
        info ["proposes"] = self.proposes
        info ["priors"] = self.ps
        info ["likelihoods"] = self.Ls
        info ["posteriors"] = self.Lps
        info ["accepts"] = self.accepts
        info ["resets"] = self.resets
        info ["infos"] = self.infos

        # auxiliary informative fields
        if self.informative:
            info ["timing"] = self.timing
            info ["timings"] = self.timings

        return self.parameters, info

    # routine adapted from EMCEE
    def stretch (self, p0, p1, lnprob0):
        """Routine adapted from EMCEE."""

        s = numpy.atleast_2d(p0.values)
        Ns = len(s)
        c = numpy.atleast_2d(p1.values)
        Nc = len(c)

        zz = ((self.a - 1.) * self.rng.rand(Ns) + 1) ** 2. / self.a
        rint = self.rng.randint(Nc, size=(Ns,))
        proposes = pandas.DataFrame (c[rint] - zz[:, numpy.newaxis] * (c[rint] - s), columns=self.labels, index=p0.index)

        # check if some chains are stuck and re-evaluate their posteriors
        stuck = {index : loc for index, loc in enumerate (proposes.index) if self.stuck [loc] == self.reset}
        for index, loc in stuck.items ():
            proposes.loc [loc] = self.parameters.loc [loc]

        Lps, ps, Ls, infos, timing, timings = self.evaluate (proposes)
        try:
            lnpdiff = (self.dimensions - 1.) * numpy.log(zz) + Lps - lnprob0
        except FloatingPointError as e:
            print(":: WARNING: reject proposed parameter as two specular chains are at -inf, ",e)
            assert numpy.where(lnprob0 == -float('inf'))[0] in numpy.where(Lps == -float('inf') )[0], ":: Fatal: -inf are not located where expected. This is a bug."
            lnprob0[numpy.isinf(lnprob0)] = 0
            lnpdiff = (self.dimensions - 1.) * numpy.log(zz) + Lps - lnprob0
        except:
            raise ValueError(":: Fatal: wrong computation of lnpdiff in EMCEE. This is a bug.")

        accepts = (lnpdiff > numpy.log(self.rng.rand(len(lnpdiff))))

        # accept all proposes that were stuck and their posteriors were re-evaluated
        for index, loc in stuck.items ():
            accepts [index] = True
        self.resets += len (stuck)

        return proposes, Lps, ps, Ls, infos, accepts, timing, timings

    # routine adapted from EMCEE
    def propose (self):
        """Propose new parameters."""

        self.timing = Timing ()
        self.timings = [Timing () for worker in range (self.executor.workers)]
        self.proposes = pandas.DataFrame (index=range(self.chains), columns=self.labels)
        self.ps = numpy.zeros (self.chains)
        self.Ls = numpy.zeros (self.chains)
        self.infos = [None for chain in range(self.chains)]
        self.accepts = numpy.zeros (self.chains)
        half = self.chains // 2
        first, second = numpy.arange (0, half), numpy.arange (half, self.chains)
        for S0, S1 in [(first, second), (second, first)]:
            proposes, Lps, ps, Ls, infos, accepts, timing, timings = self.stretch (self.parameters.iloc [S0], self.parameters.iloc [S1], self.Lps [S0])
            # assign right type to proposals
            for c in proposes.columns:
                proposes[c] = proposes[c].astype(self.prior.types[c])
            self.proposes.iloc[S0] = proposes
            self.ps[S0] = ps
            self.Ls[S0] = Ls
            for index, info in enumerate (infos):
                self.infos [S0[index]] = info
            self.accepts[S0] = accepts
            self.stuck [S0[accepts]] = 0
            self.stuck [S0[numpy.logical_not (accepts)]] += 1
            self.Lps[S0[accepts]] = Lps [accepts]
            self.parameters.values[S0[accepts]] = proposes.values [accepts]
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
            likelihood.setup (chain_sandbox, self.verbosity - 2, chain_seed, self.informative, self.trace, self._feedback)

        # initialize resets counter
        self.resets = 0

        # treat 'initial' parameters as the first sample
        if not self.initialized:

            if self.verbosity >= 3:
                print ('EMCEE: draw (initialize)')

            # attempt to evaluate likelihood of the initial parameters, with a redraw if needed
            for attempt in range (self.attempts):

                # all initial samples are proposed
                self.proposes = self.parameters

                # evaluate likelihood and prior of the initial parameters
                self.Lps, self.ps, self.Ls, self.infos, self.timing, self.timings = self.evaluate (self.proposes)

                # check if at least one likelihood is valid
                if not all (self.Lps == float ("-inf")):
                    break

                # otherwise, attempt to redraw prior samples
                else:

                    # if this is the final attempt, crash
                    if attempt == self.attempts - 1:
                        print (" :: Fatal: Unable to find initial parameters with non-zero likelihoods.")
                        print ("  : -> You may try to change seed and/or give explicit initial parameters.")
                        self.executor.abort ()

                    # otherwise, attempt to redraw prior samples
                    if self.verbosity >= 2:
                        print (" :: Warning: The likelihoods of all initial parameters are zero.")
                        print ("  : -> Re-drawing initial parameters from prior (attempt: %d/%d)" % (attempt, self.attempts))
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
