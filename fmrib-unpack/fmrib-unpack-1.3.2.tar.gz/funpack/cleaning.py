#!/usr/bin/env python
#
# cleaning.py - Cleaning functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :func:`cleanData` function, which performs
a set of cleaning steps on the data.
"""


import itertools as it
import functools as ft
import              logging
import              functools

import numpy as np

import funpack.util       as util
import funpack.expression as expression


log = logging.getLogger(__name__)


def cleanData(dtable,
              skipNAInsertion=False,
              skipCleanFuncs=False,
              skipChildValues=False,
              skipRecoding=False):
    """Perform data cleaning steps.

    This function does the following:

    1. Re-encodes missing values (the ``NAValues`` column in the variable
       table)
    2. Applies cleaning (the ``Clean`` column in the processing table)
    3. Fills missing values in child variables (the ``ParentValues``
       and ``ChildValues`` columns in the variable table)
    4. Re-encodes categorical variable values (the ``RawLevels`` and
       ``NewLevels`` columns in the variable table)

    :arg dtable:            The :class:`.DataTable`.
    :arg skipNAInsertion:   If ``True``, NA value recoding is skipped.
    :arg skipCleanFuncs:    If ``True``, cleaning functions defined
                            in the variable table are not applied.
    :arg skipChildValues:   If ``True``, child value filling is skipped.
    :arg skipRecoding:      If ``True``, raw-to-new level recoding is skipped.
    :returns:               The :class:`.DataTable`, with cleaned data.
    """

    if not skipNAInsertion:
        with util.timed('NA insertion', log):
            applyNAInsertion(dtable)

    if not skipCleanFuncs:
        with util.timed('Cleaning functions', log):
            applyCleaningFunctions(dtable)

    if not skipChildValues:
        with util.timed('Child value replacement', log):
            applyChildValues(dtable)

    if not skipRecoding:
        with util.timed('Recoding replacement', log):
            applyNewLevels(dtable)

    return dtable


def _runNAInsertion(dtable, col, navals):
    """Performs NA insertion on one column. """
    dtable[:, col] = dtable[:, col].replace(navals)


def applyNAInsertion(dtable):
    """Re-codes data which should be interpreted as missing/not available.

    Certain variables can take values which should be interpreted as missing -
    these are defined in the ``NAValues`` columns of the variable and data
    coding tables.

    This function replaces all of those values with ``np.nan``.  The
    replacement is performed in-place.
    """

    # get all variables where
    # NAValues are defined
    vtable = dtable.vartable
    vids   = vtable.index[vtable['NAValues'].notna()]

    log.debug('Recoding missing values as NA for %u variables ...',
              len(vids))

    allcols   = []
    allnavals = []

    for vid in vids:

        if not dtable.present(vid):
            continue

        navals = {v : np.nan for v in vtable['NAValues'][vid]}

        for col in dtable.columns(vid):
            allcols  .append(col.name)
            allnavals.append(navals)

    job = ft.partial(_runNAInsertion, dtable)

    with dtable.pool() as pool:
        pool.starmap(job, zip(allcols, allnavals))


def _runCleaningFunctions(dtable, procs, vid):
    """Runs cleaning processes for one variable. """

    log.debug('Applying cleaning function to variable %u: %s',
              vid, ','.join([str(p) for p in procs.values()]))

    for proc in procs.values():
        proc.run(dtable, vid)


def applyCleaningFunctions(dtable):
    """Applies cleaning steps specified in the ``Clean`` column of
    the variable table.
    """

    vtable = dtable.vartable
    vids   = vtable.index[vtable['Clean'].notna()]

    allprocs = []
    allvids  = []

    for vid in vids:

        if not dtable.present(vid):
            continue

        procs = vtable.loc[vid, 'Clean']

        allprocs.append(procs)
        allvids .append(vid)

    with dtable.pool() as pool:
        pool.starmap(ft.partial(_runCleaningFunctions, dtable),
                     zip(allprocs, allvids))


def _runChildValues(dtable, exprs, cvals, vid):
    """Applies child value replacement for the given variable. """

    if not dtable.present(vid):
        return

    # NOTE I'm currently evaluating expressions
    #      *within visit* and *within instance*, i.e.
    #      for a variable at a given visit/instance,
    #      i am evaluating the expression on the
    #      parent variables at the same visit/instance.
    #
    #      Of course this means that I am assuming
    #      the same number of visits/instances are
    #      present for dependent and parent variables.
    #      Replacement on child variables for which
    #      this assumption does not hold is skipped.
    expr      = exprs[           vid]
    cval      = cvals[           vid]
    visits    = dtable.visits(   vid)
    instances = dtable.instances(vid)

    for visit, instance in it.product(visits, instances):

        # get the column names for this
        # variable, and for each parent
        # variable that correspond to
        # this variable+visit+instance
        colname = dtable.columns(vid, visit, instance)[0].name
        pvars   = list(set(it.chain(*[e.variables for e in expr])))

        # get the true column names
        # for all parent variables
        # used in the expression
        try:
            pcols = [dtable.columns(v, visit, instance) for v in pvars]

            # if a parent variable is missing,
            # (KeyError or len(pc) == 0) the
            # expression cannot be evaluated.
            # And there should only be one
            # variable for a given
            # (vid, visit, instance)
            if any([len(pc) != 1 for pc in pcols]):
                continue

        except KeyError:
            continue

        # Turn this into a dictionary of
        # { vid : column } mappings to
        # pass into the expressions.
        pcols = {pv : pc[0].name for pv, pc in zip(pvars, pcols)}

        log.debug('Evaluating dependency expression for %s...',
                  colname)

        # Evaluate each expression independently.
        masks = [e.evaluate(dtable, pcols) for e in expr]

        # The *last* expression that evalutes to
        # True is the one which defines the
        # replacement child value to use. Here
        # we build a set of indices into the
        # child values, so we use the correct
        # child value for each row. We're
        # limiting to max 255 expressions here.
        idxs = np.zeros(len(dtable), dtype=np.uint8)
        for i, mask in enumerate(masks):
            idxs[mask] = i

        # Now we can combine all expressions
        # to get the final result, and restrict
        # the mask to only affect missing values.
        mask = functools.reduce(lambda a, b: a | b, masks)
        mask = mask & dtable[:, colname].isna()

        # Finally we apply it to the data.
        dtable[mask, colname] = cval[idxs[mask]]


def applyChildValues(dtable):
    """Fills missing values in variables which have `ParentValues` expressions
    defined.
    """

    # get all variables which have
    # a ParentValues expression
    vtable = dtable.vartable
    mask   = vtable['ParentValues'].notna()
    exprs  = vtable['ParentValues'][mask]
    cvals  = vtable['ChildValues'][ mask]
    vids   = vtable.index[          mask]

    # calculate the order in which the
    # expressions need to be evaluated
    evalOrder = expression.calculateExpressionEvaluationOrder(vids, exprs)

    log.debug('Recoding missing values on %u dependent variables '
              'from parents (%u hierarchy levels) ...',
              len(vids), len(evalOrder))

    # evaluate and apply the expressions
    # one level at a time, starting from
    # child variables (and those with no
    # dependencies), and finishing with
    # parent variables
    evalOrder = [eo[1] for eo in evalOrder]
    for vidlevel in evalOrder:
        job = ft.partial(_runChildValues, dtable, exprs, cvals)
        with dtable.pool() as pool:
            pool.map(job, vidlevel)


def _runNewLevels(dtable, col, valmap):
    """Recodes categoricals for the given column. """

    name            = col.name
    old             = dtable[:, name]
    new             = old.replace(valmap)
    corr            = old.corr(new)
    dtable[:, name] = new

    if corr < 0:
        dtable.addFlag(col, 'inverted')


def applyNewLevels(dtable):
    """Applies recoding of categorical variables as specified by the
    ``RawLevels`` and ``NewLevels`` columns in the variable table.

    For each column, if the new data (after recoding) is negatively correlated
    with the old data (before recoding), an ``'inverted'`` flag is added
    to the column (via :meth:`.DataTable.addFlag`).
    """

    # get all variables where
    # RawLevels and NewLevels
    # are defined
    vtable    = dtable.vartable
    mask      = vtable['RawLevels'].notna() & vtable['NewLevels'].notna()
    vids      = vtable.index[mask]
    rawlevels = vtable.loc[mask, 'RawLevels']
    newlevels = vtable.loc[mask, 'NewLevels']

    log.debug('Recoding categoricals for %u variables ...',
              len(vids))

    cols    = []
    valmaps = []

    for vid in vids:

        if not dtable.present(vid):
            continue

        valmap = {r : n for r, n in zip(rawlevels[vid], newlevels[vid])}

        for col in dtable.columns(vid):
            cols   .append(col)
            valmaps.append(valmap)

    with dtable.pool() as pool:
        pool.starmap(ft.partial(_runNewLevels, dtable), zip(cols, valmaps))
