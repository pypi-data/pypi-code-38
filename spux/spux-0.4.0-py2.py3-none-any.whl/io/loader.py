# # # # # # # # # # # # # # # # # # # # # # # # # #
# Cloudpickle-based loader class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import cloudpickle
import os
import glob
import numpy
import pandas
#import itertools

def tail (samples = None, infos = None, batch = 0):
    """Return only the tail of the samples and infos after the batch cutoff."""

    if samples is not None and len (samples) > batch:
        samples = samples.loc [batch:]
    if infos is not None and len (infos) > batch:
        infos = infos [batch:]
    return samples, infos

def load (name="dump.dat", directory="report", verbosity=1):
    """Load the specified binary file."""

    path = name
    if directory is not None:
        path = os.path.join (directory, path)
    with open (path, "rb") as f:
        obj = cloudpickle.load (f)
    if verbosity:
        print ('  : -> Loaded %s with size: %.1f GB' % (path, os.path.getsize (path) / (1024 ** 3)))
    return obj

def loadall (name="samples-*.dat", directory="output", verbosity=1, interactive=True, burnin=0, legacy=False, chains=None, last=False):
    """Load SPUX binary output files as generator."""

    path = os.path.join (directory, name)
    paths = sorted (glob.glob (path))
    previous = 0
    if burnin > 0:
        for checkpoint, p in enumerate (paths):
            lastindex = int (p.split ('-') [1])
            count = lastindex - previous
            previous = lastindex
            if lastindex >= burnin:
                paths = paths [checkpoint:]
                break
    if last:
        paths = [paths [-1]]
    sizes = [ os.path.getsize (p) / (1024 ** 3) for p in paths ]
    size = numpy.sum (sizes)
    print ('  : -> Size of all \'%s\' files to be loaded (minimum requirement for RAM): %.1f GB' % (path, size))

    if size > 4 and interactive:
        print ('  : -> Proceed? [press ENTER if yes, and enter \'n\' if not]')
        reply = input ('  : -> ')
        if reply == 'n':
            print ('  : -> Canceling.' % size)
            yield None
        else:
            print ('  : -> Proceeding.' % size)

    for checkpoint, path in enumerate (paths):
        result = load (path, directory=None, verbosity=verbosity)
        if burnin > 0 and chains is None:
            chains = len (result) // count
        if verbosity:
            print ('  : -> Loaded %s with length %d%s and size: %.1f GB' % (path, len (result), (' (%d chains)' % chains) if burnin > 0 else '', sizes [checkpoint]))
        if burnin > 0 and checkpoint == 0:
            tail = - 1 - (lastindex - burnin)
            if hasattr (result, 'iloc'):
                result = result.iloc [tail * chains:]
            else:
                result = result [tail:]
        if legacy and burnin > 0 and checkpoint == 0:
            result = result.reindex (index = range (burnin * chains, burnin * chains + len (result)))
        yield result

def reconstruct (samplesfiles='samples-*.dat', infosfiles='infos-*.dat', directory='output', verbosity=1, interactive=True, burnin=0, legacy=False, chains=None):
    """Recostruct samples and infos from the specified checkpoint files, taking into account a possible burnin cutoff."""

    if samplesfiles is not None:
        samples = pandas.concat (loadall (samplesfiles, directory, verbosity, interactive, burnin, legacy, chains), sort=False, ignore_index=legacy)
    else:
        samples = None

    if infosfiles is not None:
        infos = [info for infos in loadall (infosfiles, directory, verbosity, interactive, burnin) for info in infos]
        #infos = [info for info in itertools.chain (loadall (infosfiles, directory, verbosity, interactive, burnin))]
    else:
        infos = None

    return samples, infos

def last (name="infos-*.dat", directory="output", verbosity=1, interactive=True):
    """Load the last sample batch from the SPUX binary output files."""

    return [info for info in loadall (name, directory, verbosity, interactive, last=1)] [0] [-1]

def pickup (name="pickup-*.dat", directory="output"):
    """Loads the most recent pickup file."""

    path = os.path.join (directory, name)
    paths = sorted (glob.glob (path))
    if len (paths) > 1:
        return load (os.path.basename (paths [-1]), directory)
    else:
        return None

def read_types_of_keys (infl=None):
    """Read file with keys and types"""

    if infl is None or not os.path.exists (infl):
        return None

    if infl is not None:
        types_of_keys = {}
        with open(infl) as fl:
            for line in fl:
                (key, val) = line.split()
                types_of_keys[key] = val

    return types_of_keys
