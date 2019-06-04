#!/usr/bin/env python

import numpy as np

from funpack import cleaner

# Cleaner functions are passed:
#
#   - dtable: An object which provides access to the data set.
#   - vid:    The variable ID of the column(s) to be cleaned.
#
# Cleaner functions should modify the data in-place.
@cleaner()
def drop_odd_values(dtable, vid):

    # Remember that a variable may be
    # associated with multiple columns
    cols = dtable.columns(vid)

    # the columns() method returns a list of
    # Column objects,  each of which contains
    # information about one column in the data.
    for col in cols:
        col = col.name
        mask = dtable[:, col] % 2 != 0
        dtable[mask, col] = np.nan
