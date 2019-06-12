# # # # # # # # # # # # # # # # # # # # # # # # # #
# Checkpointer class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import timeit
from . import formatter

class Checkpointer (object):

    def __init__ (self, period):

        self.period = period

    def init (self, verbosity):

        self.verbosity = verbosity
        self.start = timeit.default_timer ()
        self.checkpoint = 0

    def check (self, force=0):
        """Return timestamp."""

        time = timeit.default_timer () - self.start
        if time > self.checkpoint + self.period or force:
            self.checkpoint = time
            if self.verbosity:
                print (' :: Checkpoint at: ', formatter.timestamp (time))
            return time
        else:
            return None
