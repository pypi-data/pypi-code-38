
__copyright__ = "Copyright 2013-2014, http://radical.rutgers.edu"
__license__   = "MIT"


import radical.utils as ru


# ------------------------------------------------------------------------------
#
def get_backfill(partition=None, max_cores=None, max_walltime=None):
    '''
    Return a set of [partition, cores walltime] tuples which fit into the
    current backfill.  By default we split the backfillable cores into chunks of
    10 nodes (where one node is used for the agent), and in walltimes of at most
    60 min.
    '''

    if max_cores    is None: max_cores    = 160
    if max_walltime is None: max_walltime =  60


    # --------------------------------------------------------------------------
    def _duration_to_walltime(timestr):
        '''
        convert a timestring of the forms:

            00:00:00:00  days:hours:min:sec
               00:00:00       hours:min:sec
                  00:00             min:sec
                     00                 sec
               INFINITY

        into a number of minutes. 

        Any result larger than `max_walltime` is truncated to `max_walltime`.
        `INFINITY` is also mapped to `max_walltime`.
        '''
        if timestr == 'INFINITY':
            return max_walltime

        walltime = 0.0
        elems    = timestr.split(':')
        if len(elems) >= 4:  walltime += 24 * 60 * int(elems[-4])
        if len(elems) >= 3:  walltime +=      60 * int(elems[-3])
        if len(elems) >= 2:  walltime +=           int(elems[-2])
        if len(elems) >= 1:  walltime +=           int(elems[-1]) / 60

        return min(walltime, max_walltime)
    # --------------------------------------------------------------------------


    if partition:
        part = '-p %s' % partition
    else:
        part = ''

    out, err, ret = ru.sh_callout('showbf --blocking %s' % part)

    if err:
        raise RuntimeError('showbf failed [%s]: %s' % (ret, err))

    ret = list()
    for line in out.splitlines():
        part, cores, nodes, duration, start_offset, start_date = line.split()

        if  part.startswith('-') or \
            part == 'Partition':
            continue

        cores    = int(cores)
        walltime = int(_duration_to_walltime(duration))

        while cores > max_cores:
            cores -= max_cores
            ret.append([part, max_cores, walltime])

        if cores:
            ret.append([part, cores, walltime])

    return ret


# ------------------------------------------------------------------------------

