# # # # # # # # # # # # # # # # # # # # # # # # # #
# Base sampler class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import pandas
import os
import sys
import cProfile
import gc
import numpy
import argparse

from ..utils.timer import Timer
from ..utils.setup import setup
from ..utils.seed import Seed
from ..executors.serial import Serial
from ..utils.progress import Progress
from ..utils import evaluations
from ..io.checkpointer import Checkpointer
from ..io import dumper
from ..io import loader
from ..io import formatter

class Sampler (object):
    """Base class for sampler (of parameter space)."""

    @property
    def name (self):

        return type(self).__name__

    @property
    def component (self):

        return 'Sampler'

    def evaluations (self, size):

        return evaluations.construct (self, size + self.index)

    # assign required components to sampler
    def assign (self, likelihood, prior=None):
        """Assign required components to sampler."""

        if not hasattr (likelihood, 'assigned'):
            print (' :: ERROR: likelihood needs to have components assigned before being assigned to sampler.')
            sys.exit ()

        self.likelihood = likelihood
        self.prior = prior

        self.sandboxing = self.likelihood.sandboxing
        self.task = self.likelihood

        if hasattr (self, 'executor'):
            self.executor.setup (self)
        else:
            self.attach (Serial ())

        self.assigned = True

        dumper.config (self, verbose = True)

    # attach an executor
    def attach (self, executor):
        """Attach an executor."""

        self.executor = executor
        self.executor.setup (self)
        self.executor.capabilities (['map', 'report'])

    # setup sampler
    def setup (self, sandbox=None, verbosity=1, seed=Seed(), informative=None, trace=0, lock=None, thin=1, index=None, feedback=None, outputdir='output', reportdir='report'):
        """Setup sampler."""

        # standardized setup
        setup (self, sandbox, verbosity, seed, informative, trace)

        # set thin period
        self.thin = thin

        # setup index
        self.index = index

        # store reportdir
        self.reportdir = reportdir

        # setup outputdir
        self.outputdir = outputdir
        fresh = (self.index == 0)
        dumper.mkdir (self.outputdir, fresh)

        # store preferred informativity
        self._informative = informative

        # set feedback and lock
        self._feedback = feedback
        self.lock = lock

        # report sampler setup: seed, thin, lock
        arglist = {}
        arglist ['seed'] = self.seed ()
        arglist ['thin'] = self.thin
        arglist ['lock (batch)'] = self.lock
        #arglist ['lock (sample)'] = self.lock * self.chains if self.lock is not None else None
        title = 'Setup argument list'
        headers = ['seed', 'thin', 'lock (batch)']
        #headers = ['seed', 'thin', 'lock (batch)', 'lock (sample)']
        dumper.report (self.reportdir, 'setup', arglist, title, [arglist], headers)

        # for continuation sampling, attempt to load the most recent pickup file
        self._pickup = None
        parser = argparse.ArgumentParser ()
        parser.add_argument ("--continue", dest = "cont", help = "continue sampling", action = "store_true")
        args, unknown = parser.parse_known_args ()
        if args.cont:
            if self.index is not None:
                print (' :: CONTINUE: Using index and feedback specified in setup (...).')
            else:
                self._pickup = loader.pickup ('pickup-*.dat', self.outputdir)
                if self._pickup is not None:
                    print (' :: CONTINUE: Loaded index and feedback from the pickup file.')
                    self.index = self._pickup ['setup'] ['index']
                    self._feedback = self._pickup ['setup'] ['feedback']
                else:
                    print (' :: ERROR: Can not continue sampling as requested:')
                    print ('  : -> Neither index was specified in setup (...) nor any pickup file was found.')
                    self.executor.abort ()
        elif self.index is None:
            self.index = 0

        # report index
        if self.verbosity and self.index > 0:
            print ("Sampler index:", self.index)

    # process feedback
    def feedback (self, info):

        # for replicates likelihoods, return a dictionary with associated likelihood estimates across chains
        if self.likelihood.name == 'Replicates':
            likelihoods = {}
            names = self.likelihood.names
            for name in names:
                likelihoods [name] = [chaininfo ['evaluations'] [name] if chaininfo is not None else float ('nan') for chaininfo in info ["infos"]]
            feedbacks = [likelihood.feedback (likelihoods) for likelihood in self.likelihoods]
            # args = {name : numpy.nanargmax (likelihoods [name]) for name in names}
            feedback = {name : numpy.nanmedian ([feedback [name] for feedback in feedbacks]) for name in names}
            info ["feedback"] = feedback
            if self.informative:
                info ['feedbacks'] = feedbacks
            if (self.lock is None or self.index < self.lock):
                if self._feedback is None:
                    self._feedback = {name: (int (feedback [name]) if not numpy.isnan (feedback [name]) else None) for name in names}
                else:
                    for name in names:
                        if not numpy.isnan (feedback [name]):
                            self._feedback [name] = int (feedback [name])

        # for all other likelihoods, simply return all likelihood estimates across chains
        else:
            feedbacks = numpy.array ([likelihood.feedback (info ["likelihoods"]) for likelihood in self.likelihoods])
            # arg = numpy.nanargmax (info ["likelihoods"])
            # feedback = feedbacks [arg]
            feedback = numpy.nanmedian (feedbacks)
            info ["feedback"] = feedback
            if self.informative:
                info ['feedbacks'] = feedbacks
            if (self.lock is None or self.index < self.lock) and not numpy.isnan (feedback):
                self._feedback = int (feedback)

    # online sampling (Python generator) with progress tracking and periodic saving
    # iteratively yielding results for each sample (or ensemble of samples)
    def generator (self, size=1):
        """Generate samples iteratively."""

        # initialize progress bar
        if self.verbosity == 1:
            progress = Progress (prefix="Sampling: ", steps=size, length=40)
            progress.init ()
        elif self.verbosity >= 2:
            print ("Drawing %d samples..." % size)

        # initialize sample count
        self.count = 0

        # flag for the last yield
        last = False

        # sample iteratively
        while self.count < size:

            # use informative flag only for the first and the last samples
            if self._informative is None:
                if self.index == 0 or last:
                    self.informative = 1
                else:
                    self.informative = 0
            else:
                self.informative = self._informative

            # set label for current index
            label = "S%05d" % self.index

            # spawn a sandbox for current index
            sandbox = self.sandbox.spawn (label) if self.sandboxing else None

            # spawn a seed for current index
            seed = self.seed.spawn (self.index, name=label)

            # draw a random sample from posterior
            parameters, info = self.draw (sandbox, seed)

            # increment count
            self.count += len (parameters)

            # update progress
            if self.verbosity == 1:
                progress.update (self.count)
            elif self.verbosity >= 2:
                print("Sample(s) %d/%d" % (self.count, size))

            # cleanup sample-specific sandbox
            if self.sandboxing and not self.trace:
                sandbox.remove ()

            # process feedback
            if hasattr (self.likelihood, 'feedback'):
                self.feedback (info)

            # yield results as a generator for additional external processing
            if self.index % self.thin == 0:
                yield parameters, info

            # increment index
            self.index += 1

            # return after processing the last yield
            if last:
                return

            # will the next yield be the last?
            last = (self.count + self.thin * len (parameters) >= size and self.index % self.thin == 0)

        if self.verbosity == 1:
            progress.finalize ()

    # save samples and infos and free the memory
    def flush (self, samples, infos, time):
        """Save samples and infos and free the memory."""

        # initialize timer
        timer = Timer ()
        timer.start ()

        # format time to a timestamp
        timestamp = formatter.timestamp (time)

        # format suffix
        suffix = '%05d-%s' % (self.index, timestamp)

        # CSV export of samples
        samples.to_csv (os.path.join (self.outputdir, 'samples-%s.csv' % suffix))

        # binary export of samples
        dumper.dump (samples, name='samples-%s.dat' % suffix, directory=self.outputdir)

        # binary export of infos
        # garbage collector is temprorarily disabled to increase performance
        gc.disable ()
        size = dumper.dump (infos, name='infos-%s.dat' % suffix, directory=self.outputdir)
        gc.enable ()

        # dump current index and feedback for later continuation
        pickup = {}
        pickup ['setup'] = {'index' : self.index, 'feedback' : self._feedback}
        pickup ['init'] = self.pickup ()
        dumper.dump (pickup, name='pickup-%s.dat' % suffix, directory=self.outputdir)

        # report timer
        if self.verbosity >= 2:
            print ('  : -> Checkpointer took:', timer.current ())
            print ('  : -> Infos size:', size)

        # reset samples and infos
        timer.start ()
        samples.drop (samples.index, inplace=True)
        infos.clear ()
        gc.collect ()
        if self.verbosity >= 2:
            print ('  : -> Garbage collector took:', timer.current ())

    # returns pandas dataframe with the requested number of parameter samples from
    # posterior distribution
    def __call__ (self, size=1, checkpointer=Checkpointer(600), profile=0):
        """Return pandas dataframe with the requested number of parameter samples from posterior."""

        # report the total number of foreseen model evaluations
        evaluations = self.evaluations (size)
        title = 'Number of model evaluations'
        entries = evaluations [::-1]
        headers = ['Component', 'Class', 'tasks', 'sizes', 'cumulative']
        align = ['l', 'l', 'r', 'r', 'r']
        formatters = {'tasks' : formatter.intf, 'sizes' : formatter.intf, 'cumulative' : formatter.intf}
        dumper.report (self.reportdir, 'evaluations', evaluations, title, entries, headers, align, formatters)

        # initialize profile
        if profile:
            profile = cProfile.Profile ()
            profile.enable ()

        # initialize checkpointer
        if checkpointer is not None:
            checkpointer.init (self.verbosity >= 2)

        # initialize timer and runtime
        timer = Timer ()
        timer.start ()

        # initialize samples and infos
        samples = pandas.DataFrame ()
        infos = []

        # process all generated parameters
        for (parameters, info) in self.generator (size):

            # store samples
            if len (samples) == 0:
                samples = pandas.DataFrame (columns = parameters.columns.values)
            indices = numpy.arange (self.index * len (parameters), (self.index + 1) * len (parameters))
            for i, index in enumerate (indices):
                samples.loc [index] = parameters.iloc [i]
            infos += [info]

            # save samples and infos at periodical checkpoints
            if checkpointer is not None:
                time = checkpointer.check ()
                if time is not None:
                    self.flush (samples, infos, time)

        # final checkpoint
        if checkpointer is not None and len (samples) > 0 and len (infos) > 0:
            time = checkpointer.check (force=1)
            self.flush (samples, infos, time)

        # report runtimes
        runtime = timer.current ()
        runtimes = {}
        runtimes ['total'] = runtime
        runtimes ['average'] = runtime / self.count
        runtimes ['serial'] = runtime * self.executor.resources () [0] ['cumulative']
        descriptions = {'total' : 'Total runtime (excl. checkpointer)', 'average' : 'Average runtime per sample', 'serial' : 'Equivalent serial runtime'}
        order = ['total', 'average', 'serial']
        headers = ['Timer', 'Value']
        entries = [{'Timer' : descriptions [key], 'Value' : formatter.timestamp (runtimes [key], precise=True, expand=True)} for key in order]
        title = 'Runtimes (excl. checkpointer)'
        dumper.report (self.reportdir, 'runtimes', runtimes, title, entries, headers)

        # dump profile
        if profile:
            timer.start ()
            profile.disable ()
            profile.create_stats ()
            profile.dump_stats (os.path.join (self.outputdir, 'profile.pstats'))
            if self.verbosity >= 2:
                print ('  : -> Profile dump took: ', timer.current (format=1))

        if checkpointer is None:
            return samples, infos
