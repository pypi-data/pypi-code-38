# # # # # # # # # # # # # # # # # # # # # # # # # #
# Adaptive balancer class
# For particle filtering based on
# Kattwinkel & Reichert, EMS 2017.
#
# Strategy: move excess work to the closest available worker
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import math

import numpy

from .balancer import Balancer

class Adaptive (Balancer):
    """Derived class to establish particle routings."""

    # distribute initial particles to particle ensembles for each worker - ensembles = groups to workers
    def ensembles (self, indices, workers):
        """Initially distribute particles to ensembles according to how many 'workers' are available."""

        if workers < 1 or workers is None:
            import sys
            sys.exit ('Gotten self.workers < 1 or None in ensembles. This is a bug.')
            exit ()

        ensembles = numpy.array_split (indices, workers)

        return ensembles

    # compute routings from current particle ensembles and specified indices
    def routings (self, ensembles, indices):
        """Compute routings of particles from current particle 'ensembles' and specified 'indices'"""

        if self.verbosity:
            print ('Routings ensembles:', ensembles)

        if self.verbosity:
            print ('Routings indices:', indices)

        workers = len (ensembles)
        if self.verbosity:
            print ('Routings workers:', workers)

        # maximal number of particles per ensemble
        limit = math.ceil(float(len(indices)) / workers)
        if self.verbosity:
            print ('Routings limit:', limit)

        # construct sources dictionary based on indices from ensembles
        sources = {}

        # source indexes ensembles, tells which subset of ensembles we process
        for source, ensemble in enumerate(ensembles):
            for index in ensemble:
                sources[index] = source
        if self.verbosity:
            print ('Routings sources', sources)

        # reset ensembles
        ensembles = [[] for worker in range(workers)]

        # initialize current loads
        loads = numpy.zeros(workers)

        # process all indices (sorted, to enable caching)
        # REMARK: does not include particle removal
        routings = [[] for worker in range(workers)]

        # first traversal for particles that do NOT need to be moved
        # this is because indices contains only particles that survive
        # and we check loads, i.e, we do not move survived particles
        # up to the saturation of the worker they belonged to
        remaining = []
        # index here is id of future particles
        for reindex, index in enumerate(sorted(indices)):

            # determine particle source: worker that runned particle "index"
            source = sources[index]

            # check load of the source
            if loads[source] < limit:

                # don't move particle
                destination = source

                # append routing for this particle - reindex is new particle id
                routings[source] += [(index, source, destination, reindex)]

                # increase destination-worker load: dest = source
                loads[destination] += 1

                # update ensembles
                ensembles[destination] += [reindex]

            # otherwise, store particle index for the second traversal
            else:
                remaining += [(reindex, index)]

        if self.verbosity:
            print ('Routings intermediate loads', loads)
            print ('Routings intermediate ensembles', ensembles)
            print ('Routings intermediate routings', routings)

        # second traversal for particles that DO need to be moved
        cached_index = None
        cached_destination = None
        for reindex, index in remaining:

            # determine particle source
            source = sources[index]

            # if particle index was already proccessed and cached destination
            # is not yet full, use it - minimize moves to different workers
            if index == cached_index and loads[cached_destination] < limit:
                destination = cached_destination

            # otherwise, find a new destination for this particle, closest to the source
            else:

                for i in range(int(math.floor(workers / 2))):
                    right = (source + i + 1) % workers
                    left = (source - i - 1) % workers
                    if loads[right] < limit:
                        destination = right
                        break
                    if loads[left] < limit:
                        destination = left
                        break

                # cache particle index and destination
                cached_index = index
                cached_destination = destination

            # append routing information for the worker that is a source for this particle
            routings [source] += [(index, source, destination, reindex)]

            # append routing information for the worker that is a destination for this particle
            routings [destination] += [(index, source, destination, reindex)]

            # increase destination worker load
            loads [destination] += 1

            # update ensembles
            ensembles [destination] += [reindex]

        if self.verbosity:
            print ('Routings final loads', loads)
            print ('Routings final ensembles', ensembles)
            print ('Routings final routings', routings)

        return ensembles, routings
