# # # # # # # # # # # # # # # # # # # # # # # # # #
# Resample routine for the contract of the Mpi4pyEnsemble executor class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

from mpi4py import MPI
import cloudpickle
MPI.pickle.__init__ (cloudpickle.dumps, cloudpickle.loads)

from copy import deepcopy as copy

from ...utils.timing import Timing

def universe_address ():
    """Return rank in MPI COMM_WORLD"""

    address = MPI.COMM_WORLD.Get_rank ()
    return address

# resample (detele and replicate) particles and balance ensembles according to the specified 'routing'
# REMARK: only particles provided in 'routing' are kept - non-routed particles are removed
def resample (ensemble, routing, peers):
    """Resample (replicate and delete) particles and balance ensembles according to the specified 'routing'"""

    address = ensemble.root [-1] ['address']

    # Communication/computation overlap at the expense of memory usage:
    # 0. check if routing makes sense
    # 1. compute or initialize counters and requests according to routings
    # 2. remove all extinct particles (neither to be sent nor to be kept: 'kill')
    # 3. launch all asynchronous sends/recvs for particle exchange according to routing ('send' and 'recv')
    # 4. remove all orphan particles (already sent, but not to be kept: 'free')
    # 5. stash remaining particles (to be kept: 'keep')
    # 6. synchronize ensembles to prevent race conditions
    # 7. fetch stashed particles
    # 8. replicate local particles (to be kept: 'keep')
    # 9. store and replicate received remote particles
    # 10. wait for all local particles to be sent

    # counter of particles (for each index - index is here id particle)
    keep_counters = {} # with this ensemble as both source and destination
    send_counters = {} # with this ensemble as source
    recv_counters = {} # with this ensemble as destination

    # commnunication requests
    send_requests = {}
    recv_requests = {}

    # available task states for required indices
    states = {}

    # timer for replicate (save/copy/load) routines
    timing = Timing ()

    # 0. check if routing makes sense
    for index, source, destination, reindex in routing:
        if source == address and index not in ensemble.particles:
            values = (str ((index, source, destination, reindex)), ensemble.particles.keys (), ensemble.root)
            print (' :: ERROR: invalid routing %s in resample() with indices %s and root %s' % values)
            peers.Abort ()

    # 1. compute or initialize counters and requests according to routings
    for index, source, destination, reindex in routing:

        # if particle exists locally
        if source == address:

            # keep particles with local ensemble as destination
            if destination == address:

                if index not in keep_counters:
                    keep_counters [index] = [reindex]
                else:
                    keep_counters [index] += [reindex]
                continue

            # particles with remote ensemble as destination are to be send out
            if destination != address:

                # initialize 'send_counters'
                # format: send_counters [index] [destination]
                send_counters [index] = {}

                # initialize 'send_requests'
                # format: send_requests [index] [destination]
                send_requests [index] = {}

                continue

        # if particle already exists in a remote ensemble, request it
        if source != address and destination == address:

            # initialize 'recv_counters'
            # format: recv_counters [index]
            recv_counters [index] = []

            # initialize 'recv_requests'
            # format: recv_requests [index] [source]
            recv_requests [index] = {}

            continue

    # 2. remove all extinct particles (neither to be sent nor to be kept: 'kill')
    timing.start ('kill')
    kill = set (ensemble.particles.keys ()) - set (send_counters.keys ()) - set (keep_counters.keys ())
    for index in kill:
        ensemble.remove (index)
    timing.time ('kill')

    # 3. launch all asynchronous sends/recvs for particle exchange according to routing ('send' and 'recv')

    # in the first stride, launch asynchronous sends/recvs for particle state sizes
    for index, source, destination, reindex in routing:

        # if particle exists locally with remote ensemble as destination
        if source == address and destination != address:

            # for the first index to this destination
            if destination not in send_counters [index]:

                # save particle state
                send_counters [index][destination] = 1
                if index not in states:
                    timing.start ('clone')
                    states [index] = ensemble.particles [index] .save ()
                    timing.time ('clone')

                # send out particle state size
                size = len (states [index])
                send_requests [index][destination] = peers.isend (size, dest = destination, tag = index)

                continue

            # for all other remaining indices to this destination
            else:

                # simply increment send counter
                send_counters [index][destination] += 1

                continue

        # if particle already exists in a remote ensemble, request it
        if source != address and destination == address:

            # receive particle size only once per each particle index
            if recv_counters [index] == []:
                recv_requests [index][source] = peers.irecv (source = source, tag = index)
            recv_counters [index] += [reindex]
            continue

    # store received remote particle sizes and initiate asynchronous particle recvs
    for index, requests in recv_requests.items ():
        for source, request in requests.items ():
            size = request.wait ()
            states [index] = ensemble.task.state (size)
            recv_requests [index][source] = peers.Irecv ([states [index], size, MPI.BYTE], source = source, tag = index)

    # initiate asynchronous particle sends to all destinations
    for index, requests in send_requests.items ():
        for destination, request in requests.items ():
            request.wait ()
            size = len (states [index])
            send_requests [index][destination] = peers.Isend ([states [index], size, MPI.BYTE], dest = destination, tag = index)

    # 4. remove orphan particles (states already saved for sending, but particles are not to be kept: 'free')
    timing.start ('kill')
    free = set (send_counters.keys ()) - set (keep_counters.keys ())
    for index in free:
        ensemble.remove (index)
    timing.time ('kill')

    timing.start ('clone')

    # 5. stash remaining particles
    timing.start ('stash')
    stashes = {}
    for index in keep_counters.keys ():
        stashes [index] = ensemble.stash (index)
    timing.time ('stash')

    # 6. synchronize ensembles to prevent race conditions
    peers.Barrier ()

    # 7. fetch stashed particles
    timing.start ('fetch')
    for index, reindices in keep_counters.items ():
        reindex = reindices [0]
        ensemble.fetch (stashes [index], reindex)
        del stashes [index]
    timing.time ('fetch')

    # 8. replicate local particles according to 'keep_counters'
    for index, reindices in keep_counters.items ():
        if len (reindices) > 1:
            if index not in states:
                reindex = reindices [0]
                states [index] = ensemble.particles [reindex] .save ()
            for reindex in reindices [1:]:
                ensemble.particles [reindex] = copy (ensemble.task)
                ensemble.isolate (reindex)
                ensemble.particles [reindex] .load (states [index])

    timing.time ('clone')

    # 9. store and replicate received remote particles according to 'recv_counters'
    for index, requests in recv_requests.items():
        for source, request in requests.items():
            request.Wait ()
    timing.start ('clone')
    for index, requests in recv_requests.items():
        for source, request in requests.items():
            for reindex in recv_counters [index]:
                ensemble.particles [reindex] = copy (ensemble.task)
                ensemble.isolate (reindex)
                ensemble.particles [reindex] .load (states [index])
    timing.time ('clone')

    # 10. wait for all local particles to be sent
    for index, requests in send_requests.items():
        for request in requests.values():
            request.Wait()

    # take out trash
    states = None

    # return timing
    return timing
