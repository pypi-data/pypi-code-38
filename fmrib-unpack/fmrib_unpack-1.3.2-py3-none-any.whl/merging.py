#!/usr/bin/env python
#
# merging.py - Merging data from multiple input files.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions which can merge data from multiple input
files.


.. autosummary::
   :nosignatures:

   mergeDataFrames

"""


import itertools as it
import              logging
import              collections

import numpy     as np
import pandas    as pd


log = logging.getLogger(__name__)


def mergeDataFrames(data, cols, axis, strategy, dryrun=False):
    """Merges one or more ``pandas.DataFrames`` according to the given
    ``axis`` and ``strategy``.

    :arg data:     List of ``DataFrame`` objects to merge.

    :arg cols:     List of lists - :class:`.Column` objects representing the
                   columns in each data set in ``data``.

    :arg axis:     Axis to merge on - either ``subjects`` or ``variables``.

    :arg strategy: Strategy to use for merging ``data``, either ``union`` (an
                   outer join), ``intersection`` (inner join), or ``naive``
                   (naive concatenation along ``axis``).

    :arg dryrun:   If ``True``, only ``cols`` is merged.

    :returns:  A tuple containing:

                 - a new ``DataFrame`` containing the merged ``data``, or
                   ``None`` if ``dryrun is True``.

                 - A list of :class:`.Column` objects representing the columns
                   that were kept. The index column is at the beginning of the
                   list.

    .. warning:: A dry run may produce different results with the naive merge
                 strategy.
    """

    if axis not in (0, '0', 'rows', 'subjects',
                    1, '1', 'cols', 'columns', 'variables'):
        raise ValueError('Invalid axis: {}'.format(axis))

    if strategy not in ('naive', 'union', 'intersection', 'inner', 'outer'):
        raise ValueError('Invalid merge strategy: {}'.format(strategy))

    axis     = {0              : 0,
                '0'            : 0,
                'rows'         : 0,
                'subjects'     : 0,
                1              : 1,
                '1'            : 1,
                'cols'         : 1,
                'columns'      : 1,
                'variables'    : 1}[axis]
    strategy = {'naive'        : 'naive',
                'inner'        : 'inner',
                'intersection' : 'inner',
                'outer'        : 'outer',
                'union'        : 'outer'}[strategy]

    if len(data) == 0:
        raise ValueError('No data!')

    naive = strategy == 'naive'

    if strategy == 'inner': join = 'inner'
    else:                   join = 'outer'

    # Separate out the index and non-
    # index columns for each data frame
    idxcols  = []
    datacols = [[] for _ in cols]
    for dfi, dfcols in enumerate(cols):
        for col in dfcols:
            if col.vid == 0: idxcols.append(col)
            else:            datacols[dfi].append(col)

    # Only one file - no merging required
    if len(data) == 1:
        return data[0], [idxcols[0]] + datacols[0]

    # Build a list of Column objects
    # which describe what the merged
    # data frame will look like.
    # This list will be assigned
    # back to the cols variable.

    # naive concatenation.
    if naive:

        # if performing a dry run, we can't look
        # at the data dimensions, so we take the
        # first file as the definitive one.
        if dryrun:
            if axis == 0: cols = cols[0]
            else:         cols = cols[0] + list(it.chain(*datacols[1:]))

        # If concatenating rows, we assume that
        # the columns are aligned in each file.
        # We take the column names from the file
        # with the most columns.
        elif axis == 0:
            lens = [len(d.columns) for d in data]
            rows = list(it.chain(*[d.index for d in data]))
            cols = cols[lens.index(max(lens))]

        # If concatenating columns, we assume
        # that the subjects are aligned in each
        # file. We take the subject IDs from the
        # file with the largest number of rows.
        #
        # We re-generate the list of expected
        # rows and columns in the data, dropping
        # the index column
        else:
            lens   = [len(d.index) for d in data]
            maxi   = lens.index(max(lens))
            idxcol = idxcols[maxi]
            rows   = data[maxi].index
            cols   = [idxcol] + list(it.chain(*datacols))

    # concatenate rows with inner join - only
    # retain the columns that are present in
    # every dataframe. Identify the Column
    # objectsd which represent these retained
    # columns.
    elif axis == 0 and strategy == 'inner':
        idxcol    = idxcols[0]
        allcols   = list(it.chain(*datacols))
        colnames  = [[c.name for c in dc] for dc in datacols]
        innercols = set.intersection(*[set(cn) for cn in colnames])
        colnames  = list(it.chain(*colnames))
        colidxs   = [colnames.index(ic) for ic in innercols]
        cols      = [idxcol] + [allcols[i] for i in sorted(colidxs)]

    # concatenate rows with outer join - all
    # unique column names will be retained.
    elif axis == 0 and strategy == 'outer':
        idxcol    = idxcols[0]
        uniqnames = []
        uniqcols  = []

        for col in it.chain(*datacols):
            if col.name not in uniqnames:
                uniqnames.append(col.name)
                uniqcols .append(col)

        cols = [idxcol] + uniqcols

    # concatenate columns (horizontally) -
    # all columns are retained even if
    # there are duplicate column names
    else:
        idxcol = idxcols[0]
        cols   = [idxcol] + list(it.chain(*datacols))

    if dryrun:
        return None, cols

    log.debug('Merging %u data sets (axis: %s, strategy: %s)',
              len(data), axis, strategy)

    # We have to reset row/column labels,
    # otherwise pandas will try to do a
    # real join.
    if naive:
        for d in data:
            d.columns = range(len(d.columns))
            d.reset_index(drop=True, inplace=True)

    merged = pd.concat(data,
                       axis=axis,
                       join=join,
                       ignore_index=naive,
                       sort=True,
                       copy=False)

    if len(merged) == 0:
        log.warning('Merged dataframe is empty! Are '
                    'index column positions correct?')

    # Re-label subjects and variables,
    # make sure that dataframe column
    # order matches cols list order.
    if naive:
        merged.index   = rows
        merged.columns = [c.name for c in cols[1:]]

    # If the input data frames
    # have different index names,
    # the merged index will not
    # have a name. So make sure
    # it has a name.
    merged.index.name = cols[0].name

    # Warn if we concatenated rows, and
    # there are duplicate subject IDs.
    if axis == 0:
        idxs, counts = np.unique(merged.index, return_counts=True)
        notuniq      = counts > 1
        if np.any(notuniq):
            log.warning('Duplicate subject IDs in data: %s',
                        idxs[notuniq][:5])

    # Or if we concatenated columns, and
    # there are duplicate column names
    # or VIDs
    else:
        # names
        counts = collections.Counter(merged.columns)
        if any([c > 1 for c in counts.values()]):
            log.warning('Duplicate column names in data: %s',
                        [n for n, c in counts.items() if c > 1])

        # vids
        allcols = [(c.vid, c.visit, c.instance) for c in cols]
        counts  = collections.Counter(allcols)
        if any([c > 1 for c in counts.values()]):
            log.warning('Duplicate column VIDs in data: %s',
                        [n for n, c in counts.items() if c > 1])

    return merged, cols
