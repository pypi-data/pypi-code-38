# # # # # # # # # # # # # # # # # # # # # # # # # #
# Timer class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import timeit

class Timer(object):

    def __init__(self):

        self.total = 0.0

    def current(self, format=0):

        time = timeit.default_timer() - self.time
        if not format:
            return time
        else:
            rounded = round (time / 60)
            hours = rounded // 60
            minutes = rounded - 60 * hours
            timestamp = '%02dh%02dm' % (hours, minutes)
            return timestamp

    def pause(self):

        self.total += self.current()

    def start(self):

        self.time = timeit.default_timer()

    def timestamp(self):

        return (self.time, timeit.default_timer())
