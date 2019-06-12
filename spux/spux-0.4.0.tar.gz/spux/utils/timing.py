# # # # # # # # # # # # # # # # # # # # # # # # # #
# Timing class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from .timer import Timer

class Timing (object):

    def __init__ (self):

        self.timers = {}
        self.runtimes = {}
        self.timestamps = {}

    def start (self, name):

        if name not in self.timers:
            self.timers [name] = Timer ()
        self.timers [name] .start ()

    def time (self, name):

        if name not in self.runtimes:
            self.runtimes [name] = 0
            self.timestamps [name] = []

        self.runtimes [name] += self.timers [name] .current()
        self.timestamps [name] += [self.timers [name] .timestamp()]

    def __iadd__ (self, timing):

        for name in timing.runtimes.keys ():
            if name in self.runtimes.keys ():
                self.runtimes [name] += timing.runtimes [name]
                self.timestamps [name] += timing.timestamps [name]
            else:
                self.runtimes [name] = timing.runtimes [name]
                self.timestamps [name] = timing.timestamps [name]

        return self
