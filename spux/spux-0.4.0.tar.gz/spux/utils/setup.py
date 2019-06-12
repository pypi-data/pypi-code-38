# process setup
import numpy

from .sandbox import Sandbox
from ..io.report import report

def isolate (instance, sandbox, verbosity, trace):
    """An auxiliary method to provide built-in partial functionality of setup (...) regarding sanboxing and verbosity only."""

    # set verbosity
    instance.verbosity = verbosity if verbosity >= 0 else 0

    # standartized report
    report (instance, 'isolate')

    # make a default sandbox if sandboxing is required
    if instance.sandboxing and sandbox is None:
        if instance.verbosity:
            print ('  : -> WARNING: No \'sandbox\' specified for %s, but sandboxing is enabled.' % instance.name)
            print ('  : -> Setting sandbox to a default \'sandbox = Sandbox ()\' for %s.', instance.name)
        sandbox = Sandbox ()

    # set sandbox
    instance.sandbox = sandbox

    # set trace
    instance.trace = trace

    # report
    if instance.verbosity:
        print ("  : -> %s verbosity: %s" % (instance.name, instance.verbosity))
        if hasattr (instance, 'sandboxing') and instance.sandboxing:
            print ("  : -> %s sandbox: %s" % (instance.name, instance.sandbox))
        if hasattr (instance, 'trace') and instance.trace is not None:
            print ("  : -> %s trace: %s" % (instance.name, instance.trace))

def plant (instance, seed, informative):
    """Plant instance using specified 'seed' and propagate the 'informative' flag."""

    # standartized report
    report (instance, 'plant')

    # set seed and rng
    if seed is not None:
        instance.seed = seed
        instance.rng = numpy.random.RandomState (instance.seed ())

    # set informativity
    instance.informative = informative

    # report
    if instance.verbosity:
        if hasattr (instance, 'seed') and instance.seed is not None:
            print ("  : -> %s seed: %s" % (instance.name, instance.seed))
        if hasattr (instance, 'informative'):
            print ("  : -> %s informative: %s" % (instance.name, instance.informative))

def setup (instance, sandbox, verbosity, seed, informative, trace, fresh = True):
    """Do standardized setup on 'instance' by isolating to a sandbox and planting using the specified seed."""

    # isolate instance to a sandbox
    isolate (instance, sandbox, verbosity, trace)

    # plant instance using the specified seed
    plant (instance, seed, informative)