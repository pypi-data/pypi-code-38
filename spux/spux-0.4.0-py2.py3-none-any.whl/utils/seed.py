# # # # # # # # # # # # # # # # # # # # # # # # # #
# Seed class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from copy import deepcopy as copy
import numpy

def inc (a):
  a += 1
  return a

# pair two seeds into one [Szudzik]
def pair (a, b):
    """Construct (pair) two seeds from one [Szudzik]."""

    return inc(a) ** 2 + inc(a) + inc(b) if a >= b else inc(a) + inc(b) ** 2

class Seed (object):
    """Class to generate independent seeds for random number generators."""

    # constructor
    def __init__ (self, seed=0, name='root'):

        self.seeds = [numpy.uint32 (seed)]
        self.names = [name]
        self.paired = []

    # get list of seeds
    def __call__ (self):
        """Get list of seeds."""

        return numpy.array (self.seeds, dtype=numpy.uint32)

    # get cumulative seed
    def cumulative (self):
        """Get cumulative seed."""

        if len (self.seeds) == 0:
            return None

        while len (self.paired) < len (self.seeds):
            loc = len (self.paired)
            if loc == 0:
                self.paired += [self.seeds [0]]
            else:
                self.paired += [pair (self.paired [loc - 1], self.seeds [loc])]

        return self.paired [-1]

    # spawn new seed based on current state (append lists)
    def spawn (self, seed, name='noname'):
        """Spawn new seed based on current state (append lists)."""

        child = copy (self)
        child.seeds += [numpy.uint32 (seed)]
        child.names += [name]
        return child

    # get seed description
    def __str__ (self):
        """Get seed description."""

        names_seeds = [ '%s - %s' % (self.names [i], self.seeds [i]) for i in range (len (self.names)) ]
        return ', '.join (names_seeds) + (' | cumulative: %d' % self.cumulative ())
