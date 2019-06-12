# # # # # # # # # # # # # # # # # # # # # # # # # #
# Ensemble class for processing of multiple models in likelihoods
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from copy import deepcopy as copy

from ..utils.setup import setup
from ..utils.seed import Seed
from ..io.formatter import compactify

class Ensemble (object):
    """Class of type ensemble operates set of particles (user models)."""

    @property
    def name (self):

        return type(self).__name__

    # constructor requires dynamical system 'model' including its 'inputset' and 'parameters', and the 'error' distribution for prediction validation
    def __init__(self, model, inputset, parameters, error, log=1):

        self.model = model
        self.inputset = inputset
        self.parameters = parameters
        self.error = error
        self.log = log

        self.sandboxing = model.sandboxing

        # label for sandboxes
        self.label = "P%04d"

        # seeds for iterations
        self.seeds = {}

        self.task = self.model

    # setup ensemble
    def setup (self, sandbox=None, verbosity=1, seed=Seed(), informative=0, trace=0):
        """Do a standardized setup."""

        # standardized setup
        setup (self, sandbox, verbosity, seed, informative, trace)

    # isolate the 'index' particle
    def isolate (self, index):
        """Isolate particle to its sandbox and propagate the 'verbosity' and 'trace' flags."""

        if not self.sandboxing:
            sandbox = None
        else:
            label = self.label % index
            sandbox = self.sandbox.spawn (label)
        self.particles [index] .isolate (sandbox, self.verbosity - 2, self.trace)

    # plant the 'index' particle
    def plant (self, index):
        """Plant particle: set 'seed' and also propagate the 'informative' flag."""

        seed = self.seeds [self.iteration] .spawn (index, name='PF index')
        self.particles [index] .plant (seed, self.informative)

    # stash 'index' particle
    def stash (self, index, suffix='-stash'):
        """ Stash (move) particle key and sandbox by appending the specified suffix."""

        if self.sandboxing:
            self.particles [index] .sandbox.stash ()

        key = str (index) + suffix

        self.particles [key] = self.particles [index]
        del self.particles [index]

        return key

    # fetch particle from 'key' stash and move it to a specified index
    def fetch (self, key, index, suffix='-stash'):
        """ Fetch (move) particle key and sandbox by removing the specified suffix and moving to a specified index."""

        self.particles [index] = self.particles [key]
        del self.particles [key]

        if self.sandboxing:
            label = self.label % index
            self.particles [index] .sandbox.fetch (tail = label)

    # remove 'index' particle (including its sandbox, if trace is not enabled)
    def remove (self, index, trace=0):
        """Remove particle for the specified index."""

        self.particles [index] .exit ()
        if self.sandboxing and not trace:
            self.particles [index] .sandbox.remove ()
        del self.particles [index]

    # initialize ensemble
    def init (self, indices):
        """Initialize ensemble."""

        if self.verbosity:
            print("Ensemble init with root", compactify (self.root))

        # set iteration
        self.iteration = 0

        # set iteration seed
        self.seeds [self.iteration] = self.seed.spawn (self.iteration, name='PF iteration')

        # construct particles and sandboxes
        self.particles = {}
        for index in indices:
            self.particles [index] = copy (self.model)
            self.isolate (index)
            self.plant (index)

        # initialize particles with specified parameters
        for index, particle in self.particles.items ():
            particle.init (self.inputset, self.parameters)

    # advance ensemble state to next iteration
    def advance (self):
        """Advance ensemble state to next iteration."""

        if self.verbosity:
            print("Ensemble advance with root", compactify (self.root))

        # set iteration
        self.iteration += 1

        # set iteration seed
        self.seeds [self.iteration] = self.seed.spawn (self.iteration, name='PF iteration')

    # run all particles in ensemble up to the specified time
    def run (self, time):
        """Run all particles in ensemble up to the specified time."""

        self.time = time

        if self.verbosity:
            print("Ensemble run with root", compactify (self.root))

        self.predictions = {}
        scalars = {}
        for index, particle in self.particles.items ():
            self.plant (index)
            self.predictions [index] = particle.run (time)
            if isinstance (self.predictions [index], dict):
                scalars [index] = self.predictions [index] ['scalars']
            else:
                scalars [index] = self.predictions [index]

        return scalars

    # compute errors for all particles in ensemble
    def errors (self, dataset):
        """Compute errors for all particles in ensemble."""

        if self.verbosity:
            print("Ensemble errors with root", compactify (self.root))

        if hasattr (self.error, 'transform') and self.verbosity:
            print (' -> Model predictions and dataset will be transformed before error computations.')

        # transform dataset if error requires so
        if hasattr (self.error, 'transform'):
            dataset = self.error.transform (dataset, self.parameters)

        errors = {}
        self._peaks = {}
        for index, particle in self.particles.items():
            prediction = self.predictions [index]
            if hasattr (self.error, 'transform'):
                prediction = self.error.transform (prediction, self.parameters)
            distribution = self.error.distribution (prediction, self.parameters)
            if self.verbosity >= 2:
                print (' -> Prediction (particle %05d): ' % index, prediction)
                print (' -> Dataset (particle %05d): ' % index, dataset)
            if self.log:
                errors [index] = distribution.logpdf (dataset)
                self._peaks [index] = distribution.logpdf (prediction [dataset.index])
            else:
                errors [index] = distribution.pdf (dataset)
                self._peaks [index] = distribution.pdf (prediction [dataset.index])

        return errors

    def peaks (self):
        """Return peaks computed in earlier in self.errors (...)."""

        return self._peaks

    # cleanup
    def exit (self):
        """Cleanup Ensemble object."""

        if self.verbosity:
            print("Ensemble exit with root", compactify (self.root))

        for index in list (self.particles.keys ()):
            self.remove (index, self.trace)

        # take out trash
        self.particles = None
