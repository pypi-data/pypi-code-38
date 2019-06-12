# # # # # # # # # # # # # # # # # # # # # # # # # #
# Balancer base class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import math
import numpy

class Balancer (object):
    """Base class for balancing network traffic due to killing and cloning (resampling) of particles."""

    verbosity = 0

    # compute sources from routings
    def sources (self, routings):
        """Compute sources for the particles to be resampled according to the specified routings."""

        # determine the total number of particles
        ceiling = numpy.max ( [ numpy.max ( [ reindex for index, source, destination, reindex in routing ] ) for routing in routings ] )
        count = ceiling + 1

        sources = numpy.empty (count, dtype=int)
        for routing in routings:
            for index, source, destination, reindex in routing:
                sources [reindex] = index

        return sources

    # compute traffic from routings
    def traffic (self, routings):
        """Compute network traffic (moves, copies, etc.) from routing of particles."""

        # determine the total number of particles
        ceiling = numpy.max ( [ numpy.max ( [ reindex for index, source, destination, reindex in routing ] ) for routing in routings ] ) + 1
        count = ceiling + 1

        moves = [{} for address, routing in enumerate (routings)]
        costs = [{} for address, routing in enumerate (routings)]
        copys = [{} for address, routing in enumerate (routings)]

        inits = [0 for address, routing in enumerate (routings)]
        kills = [0 for address, routing in enumerate (routings)]

        for address, routing in enumerate (routings):
            for index, source, destination, reindex in routing:
                moves [address][index] = 0
                costs [address][index] = 0
                copys [address][index] = 0

        for address, routing in enumerate (routings):

            for index, source, destination, reindex in routing:

                if source is None:
                    inits [address] += 1
                    continue

                if destination is None:
                    kills [address] += 1
                    continue

                if destination == address:

                    if source == address:
                        copys [address][index] += 1
                        continue

                    if source != address:

                        # if particle has not been moved yet, move it
                        if moves [address][index] == 0:
                            moves [address][index] = 1
                            costs [address][index] += math.fabs (source - destination)
                            continue

                        # particles are moved only once, then always copied
                        if moves [address][index] == 1:
                            copys [address][index] += 1
                            continue

        # first copy is not performed
        for address, copy in enumerate (copys):
            for index in copy:
                if copy [index] > 0:
                    copy [index] -= 1

        moves_total = numpy.sum ( [ numpy.sum (list (moves[address].values())) for address, routing in enumerate (routings) ] )
        costs_total = numpy.sum ( [ numpy.sum (list (costs[address].values())) for address, routing in enumerate (routings) ] )
        copys_total = numpy.sum ( [ numpy.sum (list (copys[address].values())) for address, routing in enumerate (routings) ] )

        traffic = {}
        traffic ["init"] = numpy.sum (inits) / float(count)
        traffic ["move"] = moves_total / float(count)
        traffic ["cost"] = costs_total / float(count)
        traffic ["copy"] = copys_total / float(count)
        traffic ["kill"] = numpy.sum (kills) / float(count)

        return traffic