#!/usr/bin/env python

import itertools as it

from funpack import processor

# Processor functions are passed:
#
#   - dtable: An object which provides access to the data set.
#   - vid:    The variable ID of the column(s) to be cleaned.
#
# Processor functions can do any of the following:
#
#   - modify existing columns in place,
#   - return a list of columns that should be removed
#   - return a list of columns that should be added
@processor()
def sum_squares(dtable, vids):

    cols    = it.chain(*[dtable.columns(v) for v in vids])
    series  = [dtable[:, c.name] for c in cols]
    squares = [s * s for s in series]
    sumsq   = sum(squares)

    sumsq.name = 'sum_square({})'.format(','.join([str(v) for v in vids]))

    # The value returned by a processor function differs
    # depending on what it wishes to do. In this case,
    # we are returning a list of new pandas.Series to be
    # added as columns, and a list of integer variable
    # IDs, one for each new column. The variable IDs are
    # optional, so we are just returning None instead.
    return [sumsq], None
