#!/usr/bin/env python
#
# processing_functions_core.py - Functions used by processing_functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains utility algorithms and functions used by the
:mod:`processing_functions` module.

 .. autosummary::
   :nosignatures:

   isSparse
   redundantColumns
   binariseCategorical
   expandCompound
"""


import logging
import collections
import itertools as it

import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

import funpack.util as util


log = logging.getLogger(__name__)


def isSparse(data,
             ctype=None,
             minpres=None,
             minstd=None,
             mincat=None,
             maxcat=None,
             abspres=True,
             abscat=True):
    """Returns ``True`` if the given data looks sparse, ``False`` otherwise.

    Used by :func:`removeIfSparse`.

    The check is based on the following criteria:

     - The number/proportion of non-NA values must be greater than
       or equal to ``minpres``.

     - The standard deviation of the data must be greater than ``minstd``.

     - For integer and categorical types, the number/proportion of the largest
       category must be less than ``maxcat``.

     - For integer and categorical types, the number/proportion of the largest
       category must be greater than ``mincat``.

    If any of these criteria are not met, the data is considered to be sparse.

    Each criteria can be disabled by passing in ``None`` for the relevant
    parameter.

    By default, the ``minstd`` test is only performed on numeric columns, and
    the ``mincat``/``maxcat`` tests are only performed on integer/categorical
    columns. This behaviour can be overridden by passing in a ``ctype`` of
    ``None``, in which case all speified tests will be performed.

    :arg data:     ``pandas.Series`` containing the data

    :arg ctype:    The series column type (one of the :attr:`.util.CTYPES`
                   values), or ``None`` to disable type-specific logic.

    :arg minpres:  Minimum number/proportion of values which must be present.

    :arg minstd:   Minimum standard deviation, for numeric/categorical types.

    :arg mincat:   Minimum size/proportion of largest category,
                   for integer/categorical types.

    :arg maxcat:   Maximum size/proportion of largest category,
                   for integer/categorical types.

    :arg abspres:  If ``True`` (the default), ``minpres`` is interpreted as
                   an absolute count. Otherwise ``minpres`` is interpreted
                   as a proportion.

    :arg abscat:   If ``True`` (the default), ``mincat`` and ``maxcat`` are
                   interpreted as absolute counts. Otherwise ``mincat`` and
                   ``maxcat`` are interpreted as proportions

    :returns:      A tuple containing:

                    - ``True`` if the data is sparse, ``False`` otherwise.

                    - If the data is sparse, one of ``'minpres'``,
                      ``'minstd'``, ``mincat``, or ``'maxcat'``, indicating
                      the cause of its sparsity. ``None`` if the data is not
                      sparse.

                    - If the data is sparse, the value of the criteria which
                      caused the data to fail the test.  ``None`` if the data
                      is not sparse.
    """

    presmask = data.notnull()
    present  = data[presmask]
    ntotal   = len(data)
    npresent = len(present)

    def fixabs(val, isabs, limit=ntotal, repl=npresent):

        # Turn proportion into
        # an absolute count
        if not isabs:
            val = val * limit
            if (val % 1) >= 0.5: val = np.ceil(val)
            else:                val = np.floor(val)

        # ignore the threshold if it is
        # bigger than the total data length
        if limit < val: return repl
        else:           return val

    iscategorical = ctype in (None,
                              util.CTYPES.integer,
                              util.CTYPES.categorical_single,
                              util.CTYPES.categorical_single_non_numeric,
                              util.CTYPES.categorical_multiple,
                              util.CTYPES.categorical_multiple_non_numeric)
    isnumeric     = ctype in (None,
                              util.CTYPES.continuous,
                              util.CTYPES.integer,
                              util.CTYPES.categorical_single,
                              util.CTYPES.categorical_multiple) and \
                    pdtypes.is_numeric_dtype(data)

    # not enough values
    if minpres is not None:
        if npresent < fixabs(minpres, abspres):
            return True, 'minpres', npresent

    # stddev is not large enough (for
    # numerical/categorical types
    if isnumeric and minstd is not None:
        std = (present - present.mean()).std()
        if std <= minstd:
            return True, 'minstd', std

    # for categorical types
    if iscategorical and ((maxcat is not None) or (mincat is not None)):

        if maxcat is not None:
            maxcat = fixabs(maxcat, abscat, npresent, npresent + 1)
        if mincat is not None:
            mincat = fixabs(mincat, abscat, npresent)

        # mincat - smallest category is too small
        # maxcat - one category is too dominant
        uniqvals   = pd.unique(present)
        uniqcounts = [sum(present == u) for u in uniqvals]
        nmincat    = min(uniqcounts)
        nmaxcat    = max(uniqcounts)

        if mincat is not None:
            if nmincat < mincat:
                return True, 'mincat', nmincat

        if maxcat is not None:
            if nmaxcat >= maxcat:
                return True, 'maxcat', nmaxcat

    return False, None, None


def redundantColumns(data, columns, corrthres, nathres=None):
    """Identifies redundant columns based on the correlation of present and
    missing data.

    :arg data:      ``pandas.DataFrame`` containing the data

    :arg columns:   Sequence of column names to check.

    :arg corrthres: Correlation threshold - columns with a correlation greater
                    than this are identified as redundant.

    :arg nathres:   Correlation threshold to use for missing values. If
                    provided, columns must have a correlation greater than
                    ``corrthres`` *and* a missing-value correlation greater
                    than ``nathres`` to be identified as redundant.

    :returns:       List of redundant column names.
    """

    if nathres is None:
        nathres = 0

    # If not performing na thresholding, we
    # have to test all pairs of columns
    if nathres == 0:
        colpairs = list(it.combinations(columns, 2))

    # But if we are checking the correlation of
    # missing values, we can improve performance
    # by calculating the missingness correlation
    # using a matrix product, then only testing
    # the normal correlation between pairs of
    # columns that exceed the missingness
    # threshold.
    if nathres > 0:

        namask = np.asarray(pd.isna(data[columns]), dtype=np.float16)

        # normalise each column of the namask
        # array to unit standard deviation, but
        # only for those columns which have a
        # stddev greater than 0 (those that
        # correspond to columns with either all
        # missing values, or no missing values).
        nameans              = namask.mean(axis=0)
        nastds               = namask.std( axis=0)
        nahasdev             = nastds > 0
        namask              -= nameans
        namask[:, nahasdev] /= nastds[nahasdev]
        nacorr               = np.dot(namask.T, namask) / len(data)

        # Only pairs which exceed the missing
        # threshold need to be further tested.
        # And as the matrix is symmetric, we
        # can drop column pairs where x <= y.
        colpairs = zip(*np.where(nacorr > nathres))
        colpairs = [(x, y) for x, y in colpairs if x > y]
        colpairs = [(columns[x], columns[y]) for x, y in colpairs]

    redundant = set()

    # calculate correlation between column pairs
    for coli, colj in colpairs:

        if coli in redundant or colj in redundant:
            continue

        datai = data[coli]
        dataj = data[colj]
        corr  = datai.corr(dataj)

        # i and j are highly correlated -
        # flag the one with more missing
        # values as redundant
        if corr > corrthres:
            if sum(datai.isna()) > sum(dataj.isna()): drop, keep = coli, colj
            else:                                     drop, keep = colj, coli

            log.debug('Column %s is redundant (correlation with %s: %f)',
                      drop, keep, corr)
            redundant.add(drop)

    return list(redundant)


def binariseCategorical(data, minpres=None):
    """Takes one or more columns containing categorical data,, and generates a
    newd set of binary columns, one for each unique categorical value,
    containing ``True`` in rows where the value was present, ``False``
    otherwise.

    :arg data:    A ``pandas.DataFrame``containing the input columns
    :arg minpres: Optional threshold - values with less than this number of
                  occurrences will not be included in the output

    :returns:     A tuple containing:

                   - A ``(nrows, nvalues)`` ``numpy`` array containing the
                     generated binary columns

                   - A 1D ``numpy`` array of length ``nvalues`` containing
                     the unique values that are encoded in the binary columns.
    """

    if minpres is None:
        minpres = 0

    cols    = [data[c]      for c in data.columns]
    cols    = [c[c.notna()] for c in cols]
    coluniq = [np.unique(c, return_counts=True) for c in cols]
    uniq    = collections.defaultdict(lambda : 0)

    for coluniq, colcounts in coluniq:
        for val, count in zip(coluniq, colcounts):
            uniq[val] += count

    # drop values with low occurrence
    uniq = [v for v, c in uniq.items() if c >= minpres]
    uniq = list(sorted(uniq))

    # Make a new subjects * values array,
    # where each column is True where the
    # subject had an entry equal to that
    # value, False otherwise.
    bindata = np.zeros((len(data), len(uniq)), dtype=np.uint8)
    for i, v in enumerate(uniq):
        bindata[:, i] = (data == v).any(axis=1)

    return bindata, uniq


def expandCompound(data):
    """Takes a ``pandas.Series`` containing sequence data (potentially of
    variable length), and returns a 2D ``numpy`` array containing the parsed
    data.

    The returned array has shape ``(X, Y)``, where ``X`` is the number of rows
    in the data, and ``Y`` is the maximum number of values for any of the
    entries.

    :arg data: ``pandas.Series`` containing the compound data.
    :returns:   2D ``numpy`` array containing expanded data.
    """

    nrows = len(data)
    lens  = data.apply(len).values
    ncols = max(lens)

    # Create a 2D array from
    # rows of different lengths
    #
    # https://stackoverflow.com/a/32043366
    #
    # 2D mask array of shape (nrows, max(lens))
    # which identifies positions to be filled
    mask          = np.arange(ncols) < np.atleast_2d(lens).T
    newdata       = np.full((nrows, ncols), np.nan, dtype=np.float32)
    newdata[mask] = np.concatenate(data.values)

    return newdata
