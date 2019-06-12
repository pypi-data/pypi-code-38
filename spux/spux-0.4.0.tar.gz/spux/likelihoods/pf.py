# # # # # # # # # # # # # # # # # # # # # # # # # #
# Particle Filter likelihood class for a stochastic model
# Particle filtering based on
# Kattwinkel & Reichert, EMS 2017.
# Implementation described in
# Sukys & Kattwinkel, Proceedings of ParCo 2017,
# Advanced Parallel Computing, IOS Press, 2018.
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import scipy
import numpy

from ..utils.timing import Timing
from ..utils import transforms
from ..utils import evaluations
from .likelihood import Likelihood
from .ensemble import Ensemble

numpy.seterr (divide = 'ignore')

class PF (Likelihood):
    """Particle Filter likelihood class for a stochastic model.

    Operates ensemble of particles.
    """

    # constructor
    def __init__ (self, particles=10, threshold=-2, accuracy=0.1, margin=0.05, noresample=0):

        self.particles = particles
        try:
            self.particles_min = particles [0]
            self.particles_max = particles [1]
            self.adaptive = True
        except:
            self.particles_min = particles
            self.particles_max = particles
            self.adaptive = False
        self.particles_set = self.particles_min
        self.threshold = threshold
        self.accuracy = accuracy
        self.margin = margin
        self.factor = 2
        self.log = 1
        self.noresample = noresample

        # initialize variance to NaN
        self.variance = float ('nan')

    @property
    def evaluations (self):

        return evaluations.construct (self, self.particles_max)

    # attach an executor
    def attach (self, executor):
        """Attach an executor."""

        self.executor = executor
        self.executor.setup (self)
        methods = ['connect', 'call', 'resample', 'disconnect']
        self.executor.capabilities (methods)

        if self.particles_min < self.executor.workers:
            print (' :: WARNING: The minimum number of particles should NOT be smaller than the number of workers in the attached executor.')
            print (' :-> Correcting the value for the minimum number of particles.')
            self.particles_min = self.executor.workers
        if self.particles_max < self.executor.workers:
            print (' :: WARNING: The maximum number of particles should NOT be smaller than the number of workers in the attached executor.')
            print (' :-> Correcting the value for the maximum number of particles.')
            self.particles_max = self.executor.workers

    # feedback
    def feedback (self, likelihoods):
        """Feedback method to be executed by the sampler."""

        particles = float ('nan')
        if hasattr (self, 'avg_deviation') and not numpy.isnan (self.avg_deviation):
            if self.fitscore > self.threshold:
                particles = self.particles_set
                if self.avg_deviation > min (numpy.log (1 + self.accuracy + self.margin), - numpy.log (1 - self.accuracy - self.margin)):
                    particles = self.particles_set * self.factor
                if self.avg_deviation < min (numpy.log (1 + self.accuracy - self.margin), - numpy.log (1 - self.accuracy + self.margin)):
                    particles = max (2, int ( numpy.ceil (self.particles_set / self.factor)))
        return particles

    # redraw particles based on errors
    def redraw (self, indices, logerrors, logscaling, particles):
        """Redraw particles based on errors."""

        # compute probabilities for discrete distribution
        nans = numpy.isnan (logerrors)
        if logscaling == float ('-inf'):
            if self.verbosity:
                print(" :: WARNING: The sum of all particle errors is 0 (i.e., exp (-inf)).")
                print("  : -> This issue should have been mitigated already earlier.")
                print("  : -> Assigning equal probabilities to all particles with non-NaN error.")
            probabilities = numpy.where (nans, 0, 1.0 / numpy.sum (~nans))
        else:
            probabilities = numpy.where (nans, 0, numpy.exp (logerrors - logscaling))

        # sample from discrete distribution
        choice = self.rng.choice (indices, size=particles, p=probabilities)

        # compute redraw rate
        redraw = len(set(choice)) / float(len(indices))

        return choice, redraw

    # evaluate/approximate likelihood of the specified parameters
    def __call__ (self, parameters):
        """Evaluate estimate of the likelihood for the specified parameters."""

        # verbose output
        if self.verbosity >= 2:
            print ("PF likelihood parameters:")
            print (parameters)
            print ("PF likelihood feedback:")
            print (self._feedback)

        # report a warning if resampling is disabled
        if self.noresample:
            print (" :: WARNING: \'noresample\' is specified in PF - use ONLY FOR DEVELOPMENT.")

        # start global timer
        timing = Timing ()
        timing.start ('evaluate')

        # adaptive number of particles
        if not self.adaptive or self._feedback is None or numpy.isnan (self._feedback):
            particles = self.particles_min
        else:
            particles = int (self._feedback)
            if particles > self.particles_max:
                particles = self.particles_max
            if particles < self.particles_min:
                particles = self.particles_min
        if self.verbosity >= 2:
            print ("PF likelihood particles:")
            print (particles)

        # construct ensemble task
        ensemble = Ensemble (self.model, self.inputset, parameters, self.error)

        # setup ensemble
        ensemble.setup (self.sandbox, self.verbosity - 2, self.seed, self.informative, self.trace)

        # initialize task ensemble in executor
        self.executor.connect (ensemble, indices = numpy.arange (particles))

        # initialize indices container
        indices = { 'prior' : {}, 'posterior' : {} }

        # initialize predictions container
        predictions = { 'prior' : {}, 'posterior' : {}, 'unique' : {} }

        # initialize weights container
        weights = {}

        # initialize errors containter
        errors = { 'prior' : {}, 'posterior' : {} }

        # initialize peaks container
        peaks = {}

        # initialize estimates container
        estimates = {}

        # initialize quality control container
        variances = {}

        # initialize container for source indices
        sources = {}

        # initialize traffic measurements container
        traffic = {}

        # initialize particle redraw rate measurements container
        redraw = {}

        # iterate over all dataset snapshots (times)
        for snapshot in self.dataset.index:

            if self.verbosity:
                print("Snapshot", snapshot)

            # reset indices
            indices ['prior'] [snapshot] = numpy.arange (particles)

            # run particles (models)
            if self.verbosity >= 2:
                print("Running particles (%s models)..." % self.task.name)

            predictions ['prior'] [snapshot] = transforms.pandify (self.executor.call ('run', args = [snapshot]))
            if self.verbosity >= 2:
                print ("Prior (non-resampled) predictions:")
                print (predictions ['prior'] [snapshot])

            # compute errors
            if self.verbosity >= 2:
                print("Computing errors...")
            errors ['prior'] [snapshot] = transforms.numpify (self.executor.call ('errors', args = [self.dataset.loc [snapshot]]))
            if self.verbosity >= 2:
                print("Prior (non-resampled) errors", errors ['prior'] [snapshot])

            # retrieve peaks of errors
            peaks [snapshot] = transforms.numpify (self.executor.call ('peaks'))

            # if all errors are NaNs - no further filtering is possible
            if all (numpy.isnan (errors ['prior'] [snapshot])):
                estimates [snapshot] = float ('nan')
                variances [snapshot] = float ('nan')
                if self.verbosity:
                    print (" :: WARNING: NaN estimate in the PF likelihood.")
                    print ("  : -> All error model distribution densities are NaN.")
                    print ("  : -> Stopping here and returning the infos as they are.")
                successful = False
                break

            # if all errors are '-inf's - no further filtering is possible
            if all (errors ['prior'] [snapshot] == float ('-inf')):
                estimates [snapshot] = float ('-inf') if self.log else 0
                variances [snapshot] = float ('nan')
                if self.verbosity:
                    print (" :: WARNING: '-inf' (i.e., log (0)) estimate in the PF likelihood.")
                    print ("  : -> All error model distribution densities are '-inf' (i.e., log (0)).")
                    print ("  : -> Stopping here and returning the infos as they are.")
                successful = False
                break

            # compute (log-)error estimates for the current snapshot
            nonnan = errors ['prior'] [snapshot] [~ numpy.isnan (errors ['prior'] [snapshot])]
            M = len (nonnan)
            logmean = scipy.special.logsumexp (nonnan) - numpy.log (M)
            mean = numpy.exp (logmean)
            estimates [snapshot] = logmean if self.log else mean
            if self.verbosity:
                print ("Estimated %slikelihood at snapshot %s: %1.1e" % ('log-' if self.log else '', str (snapshot), estimates [snapshot]))

            # if estimate is '-inf' (or 0 for self.log = 0) - no further filtering is possible
            if (self.log and estimates [snapshot] == float ('-inf')) or (not self.log and estimates [snapshot] == 0):
                variances [snapshot] = float ('nan')
                if self.verbosity:
                    print (" :: WARNING: '-inf' (i.e., log (0)) estimate in the PF likelihood.")
                    print ("  : -> Stopping here and returning the infos as they are.")
                successful = False
                break

            # estimate variance of the log-likelihood estimate for the current snapshot,
            # using 1st order Taylor approximation for the log-likelihood case:
            # https://stats.stackexchange.com/questions/57715/expected-value-and-variance-of-loga#57766
            if M == 1 or mean == 0:
                variances [snapshot] = float ('nan')
            else:
                logscaling = numpy.max (nonnan)
                if not numpy.isfinite (logscaling):
                    logscaling = 0
                variance = numpy.var (numpy.exp (nonnan - logscaling), ddof=1)
                deviation = numpy.exp (0.5 * (numpy.log (variance) + 2 * logscaling - numpy.log (M)))
                variances [snapshot] = (deviation / mean) ** 2
            if self.verbosity:
                print ("Estimated variance of log-likelihood at snapshot %s: %1.1e" % (str (snapshot), variances [snapshot]))

            # redraw particles based on errors
            if self.noresample:
                indices ['posterior'] [snapshot] = indices ['prior'] [snapshot]
                redraw [snapshot] = None
            else:
                indices ['posterior'] [snapshot], redraw [snapshot] = self.redraw (indices ['prior'] [snapshot], errors ['prior'] [snapshot], logmean + numpy.log (M), particles)
            if self.verbosity >= 2:
                print ("Posterior (redrawn) indices (arbitrary order, particles not yet resampled):")
                print (indices ['posterior'] [snapshot])

            # advance ensemble state to next iteration (do not gather results)
            self.executor.call ('advance', results=0)

            # resample (delete and clone) particles and balance ensembles in the executor and record resulting traffic
            if self.noresample:
                traffic [snapshot] = {}
                sources [snapshot] = indices ['posterior'] [snapshot]
            else:
                traffic [snapshot], sources [snapshot] = self.executor.resample (indices ['posterior'] [snapshot])
            if self.verbosity >= 2:
                print ("Posterior (resampled) particles sources:")
                print (sources [snapshot])
                print ("Traffic:")
                print (traffic [snapshot])

            # construct posterior predictions indexed according to sources
            predictions ['posterior'] [snapshot] = predictions ['prior'] [snapshot] .loc [sources [snapshot]]

            # unique indices and counts for posterior predictions (compression to reduce 'info' size)
            isunique = ~(predictions ['posterior'] [snapshot] .index.duplicated (keep = 'first'))
            predictions ['unique'] [snapshot] = predictions ['posterior'] [snapshot] .loc [isunique]
            counts = [numpy.sum (predictions ['posterior'] [snapshot] .index == index) for index in predictions ['posterior'] [snapshot] .index]
            weights [snapshot] = numpy.array (counts)

            if self.verbosity >= 2:
                print ("Posterior (resampled) predictions:")
                print (predictions ['posterior'] [snapshot])
                print ("Posterior (resampled) unique predictions:")
                print (predictions ['unique'] [snapshot])
                print ("Posterior (resampled) unique predictions weights:")
                print (weights [snapshot])

            # construct posterior errors indexed according to sources
            errors ['posterior'] [snapshot] = errors ['prior'] [snapshot] [sources [snapshot]]
            if self.verbosity >= 2:
                print("Posterior (resampled) errors", errors ['posterior'] [snapshot])

            # all steps were successful
            successful = True

        # finalize task ensemble in executor
        timings = self.executor.disconnect ()

        # append executor timing
        timing += self.executor.report ()

        # compute estimated (log-)likelihood as the product of estimates from all snapshots
        if self.log:
            estimate = numpy.sum (list (estimates.values()))
        else:
            estimate = numpy.prod (list (estimates.values()))

        # compute estimated variance of the estimated log-likelihood
        variance = numpy.sum (list (variances.values()))

        # compute estimated average std. deviation across estimated log-errors
        avg_deviation = numpy.mean (numpy.sqrt (list (variances.values())))

        # compute fitscore: the log of the
        # average (over snapshots and particles)
        # normalized (with respect to maximum pdf and the dimensions of the observations)
        # posterior errors
        observation_dimensions = self.error.dimensions if hasattr (self.error, 'dimensions') else len (self.dataset.columns)
        fitscores = {}
        for snapshot in self.dataset.index:
            normalized_errors = errors ['posterior'] [snapshot] - peaks [snapshot] [sources [snapshot]]
            # TODO: use scipy.special.logsumexp () to average in the linear domain
            fitscores [snapshot] = numpy.nanmean (normalized_errors / observation_dimensions)
        # TODO: use scipy.special.logsumexp () to average in the linear domain
        fitscore = numpy.nanmean (list (fitscores.values ()))

        if self.verbosity:
            print ("Estimated %slikelihood: %1.1e" % ('log-' if self.log else '', estimate))
            print ("Estimated variance of log-likelihood: %1.1e" % variance)

        # compute MAP estimate
        if not successful:
            MAP = None
        else:
            cumulative = errors ['posterior'] [self.dataset.index [0]] [:]
            for snapshot in self.dataset.index [1:]:
                if self.verbosity >= 2:
                    print ('Cumulative posterior errors (tracked by sources) for snapshot %s:' % str (snapshot))
                    print (cumulative [sources [snapshot]])
                cumulative = errors ['posterior'] [snapshot] + cumulative [sources [snapshot]]
            MAP_indices = {}
            MAP_predictions = {}
            last = self.dataset.index [-1]
            MAP_indices [last] = sources [last] [numpy.argmax (cumulative)]
            MAP_predictions [last] = predictions ['unique'] [last] .loc [MAP_indices [last]]
            for snapshot in reversed (self.dataset.index [:-1]):
                MAP_indices [snapshot] = sources [snapshot] [MAP_indices [last]]
                MAP_predictions [snapshot] = predictions ['unique'] [snapshot] .loc [MAP_indices [snapshot]]
                last = snapshot
            MAP = { 'indices' : MAP_indices, 'predictions' : MAP_predictions, 'error' : numpy.max (cumulative) }

        # measure evaluation runtime and timestamp
        timing.time ('evaluate')

        # information includes predictions, errors, estimates and their variances, MAP trajectory
        # resampling sources, redraw rate, used up communication traffic, and timings
        info = {}
        info ["particles"] = particles
        info ["predictions"] = predictions ['unique']
        info ["weights"] = weights
        info ["MAP"] = MAP
        info ["variance"] = variance
        info ["fitscore"] = fitscore
        info ["avg_deviation"] = avg_deviation
        info ["redraw"] = redraw
        info ["successful"] = successful
        info ["sources"] = sources
        if self.informative >= 1:
            info ["predictions_prior"] = predictions ['prior']
            info ["errors_prior"] = errors ['prior']
            info ["estimates"] = estimates
            info ["variances"] = variances
            info ["indices"] = indices ['posterior']
        if self.informative >= 2:
            info ["predictions_posterior"] = predictions ['posterior']
            info ["errors_posterior"] = errors ['posterior']
        if self.informative >= 3:
            info ["traffic"] = traffic
            info ["timing"] = timing
            info ["timings"] = timings

        # store variance, avg_deviation, fitscore and particles for later feedback
        self.variance = variance
        self.avg_deviation = avg_deviation
        self.fitscore = fitscore
        self.particles_set = particles

        # return estimated likelihood and its info
        return estimate, info
