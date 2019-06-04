#!/usr/bin/env python
#
# processing_functions.py - Processing functions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains definitions of processing functions - functions which
may be specifeid in the processing table.


A processing function may perform any sort of processing on one or more
variables. A processing function may add, remove, or manipulate the columns of
the :class:`DataTable`.


All processing functions must accept the following as their first two
positional arguments:


 - The :class:`.DataTable` object, containing references to the data, variable,
   and processing table.
 - A list of integer ID of the variables to process.


Furthermore, all processing functions must return one of the following:

 - ``None``, indicating that no columns are to be added or removed.

 - A ``list`` of :class:`.Column` objects describing the columns that should
   be removed from the data.

 - A ``tuple`` of length 2, containing:

    - A list of ``pandas.Series`` that should be added to the data.

    - A list of variable IDs to use for each new ``Series``. This list must
      have the same length as the list of new ``Series``, but if they are not
      associated with any specific variable, ``None`` may be used.

 - A ``tuple`` of length 3, containing:

    - List of columns to be removed
    - List of ``Series`` to be added
    - List of variable IDs for each new ``Series``.

 - A ``tuple`` of length 3, containing the above, and:

    - List of metadata associated with each of the new ``Series``. This will
      be added to the :class:`.Column` objects that represent each of the new
      ``Series``.

The following processing functions are defined:

 .. autosummary::
   :nosignatures:

   removeIfSparse
   removeIfRedundant
   binariseCategorical
   expandCompound
"""


import itertools as it
import              logging
import              collections

import pandas           as pd
import pandas.api.types as pdtypes

from . import processing_functions_core as core
from . import                              custom


log = logging.getLogger(__name__)


@custom.processor()
def removeIfSparse(dtable,
                   vids,
                   minpres=None,
                   minstd=None,
                   mincat=None,
                   maxcat=None,
                   abspres=True,
                   abscat=True,
                   ignoreType=False):
    """removeIfSparse([minpres], [minstd], [mincat], [maxcat], [abspres], [abscat])
    Removes columns deemed to be sparse.

    Removes columns for the variables in ``vids`` if they are sparse.

    :arg ignoreType: Defaults to ``False``. If ``True``, all specified tests are
                     run regardless of the types of the ``vids``.

    See the :func:`.isSparse` function for details on the other arguments.
    """  # noqa

    remove = []

    for vid in vids:

        if ignoreType: vtype = None
        else:          vtype = dtable.vartable.loc[vid, 'Type']

        for col in dtable.columns(vid):

            log.debug('Checking column %s for sparsity', col.name)

            isSparse, test, val = core.isSparse(dtable[:, col.name],
                                                vtype,
                                                minpres=minpres,
                                                minstd=minstd,
                                                mincat=mincat,
                                                maxcat=maxcat,
                                                abspres=abspres,
                                                abscat=abscat)

            if isSparse:
                log.debug('Dropping sparse column %s (%s: %f)',
                          col.name, test, val)
                remove.append(col)

    return remove


@custom.processor()
def removeIfRedundant(dtable, vids, corrthres, nathres=None):
    """removeIfRedundant(corrthres, [nathres])
    Removes columns deemed to be redundant.

    Removes columns from the variables in ``vids`` if they are redundant.

    Redundancy is determined by calculating the correlation between pairs
    of columns - see the :func:`.isRedundant` function.
    """

    # Ignore non-numeric columns
    columns = list(it.chain(*[dtable.columns(v) for v in vids]))
    columns = [c for c in columns
               if pdtypes.is_numeric_dtype(dtable[:, c.name])]

    log.debug('Checking %u columns for redundancy', len(columns))

    columns  = collections.OrderedDict([(c.name, c) for c in columns])
    toremove = core.redundantColumns(
        dtable[:, :], list(columns.keys()), corrthres, nathres)

    if len(toremove) > 0:
        log.debug('Dropping %u redundant columns: %s ...',
                  len(toremove), toremove[:5])

    return [columns[tr] for tr in toremove]


@custom.processor()
def binariseCategorical(dtable,
                        vids,
                        acrossVisits=False,
                        acrossInstances=True,
                        minpres=None,
                        nameFormat=None,
                        replace=True):
    """binariseCategorical([acrossVisits], [acrossInstances], [minpres], [nameFormat], [replace])
    Replace a categorical column with one binary column per category.

    Binarises categorical variables - replaces their columns with
    one new column for each value, containing ``True`` for subjects
    with that value, and ``False`` otherwise.

    :arg dtable:          The :class:`.DataTable`

    :arg vids:            Sequence of variable IDs to (independently) apply the
                          binarisation to.

    :arg acrossVisits:    If ``True``, the binarisation is applied across
                          visits for each variable.

    :arg acrossInstances: If ``True``, the binarisation is applied across
                          instances for each variable.

    :arg minpres:         Optional threshold - categorical values with less
                          than this many occurrences will not be added as
                          columns.

    :arg nameFormat:      Format string defining how the new columns should
                          be named - see below.

    :arg replace:         If ``True`` (the default), the original columns are
                          flagged for removal.

    The ``nameFormat`` argument controls how the new data columns should be
    named - it must be a format string using named replacement fields
    ``'vid'``, ``'visit'``, ``'instance'``, and ``'value'``. The ``'visit'``
    and ``'instance'`` fields may or may not be necessary, depending on the
    value of the ``acrossVisits`` and ``acrossInstances`` arguments.

    The default value for the ``nameFormat`` string is as follows:

    ================ =================== ======================================
    ``acrossVisits`` ``acrossInstances`` ``nameFormat``
    ================ =================== ======================================
    ``False``        ``False``           ``'{vid}-{visit}.{instance}_{value}'``
    ``False``        ``True``            ``'{vid}-{visit}.{value}'``
    ``True``         ``False``           ``'{vid}-{value}.{instance}'``
    ``True``         ``True``            ``'{vid}-0.{value}'``
    ================ =================== ======================================
    """  # noqa

    defaultNameFormat = {
        (False, False) : '{vid}-{visit}.{instance}_{value}',
        (False, True)  : '{vid}-{visit}.{value}',
        (True,  False) : '{vid}-{value}.{instance}',
        (True,  True)  : '{vid}-0.{value}',
    }

    if nameFormat is None:
        nameFormat = defaultNameFormat[acrossVisits, acrossInstances]

    toremove  = []
    newseries = []
    newvids   = []
    newmeta   = []

    for vid in vids:

        visits    = dtable.visits(   vid)
        instances = dtable.instances(vid)
        colgroups = []

        if not (acrossVisits or acrossInstances):
            for visit, instance in it.product(visits, instances):
                colgroups.append(dtable.columns(vid, visit, instance))
        elif acrossInstances and (not acrossVisits):
            for visit in visits:
                colgroups.append(dtable.columns(vid, visit))
        elif (not acrossInstances) and acrossVisits:
            for instance in instances:
                colgroups.append(dtable.columns(vid, instance=instance))
        else:
            colgroups = [dtable.columns(vid)]

        for columns in colgroups:

            data              = dtable[:, [c.name for c in columns]]
            binarised, values = core.binariseCategorical(data, minpres=minpres)

            toremove.extend(columns)

            for col, val in zip(binarised.T, values):

                # make sure no periods appear
                # in the resulting column name.
                # We're assuming here that all
                # categoricals are integers,
                # which has not been verified.
                try:               val = int(val)
                except ValueError: pass

                fmtargs = {
                    'vid'      : str(int(columns[0].vid)),
                    'visit'    : str(int(columns[0].visit)),
                    'instance' : str(int(columns[0].instance)),
                    'value'    : str(val)
                }

                newvids  .append(vid)
                newmeta  .append(val)
                newseries.append(pd.Series(
                    col,
                    index=dtable.index,
                    name=nameFormat.format(**fmtargs)))

    if replace: return toremove, newseries, newvids, newmeta
    else:       return [],       newseries, newvids, newmeta


@custom.processor()
def expandCompound(dtable, vids, nameFormat=None, replace=True):
    """expandCompound([nameFormat], [replace])
    Expand a compound column into a set of columns, one for each value.

    Expands compound variables into a set of columns, one for each value.
    Rows with different number of values are padded with ``np.nan``.

    :arg dtable:     The :class:`.DataTable`

    :arg vids:       Sequence of variable IDs to (independently) apply the
                     expansion to.

    :arg nameFormat: Format string defining how the new columns should be named
                     - see below.

    :arg replace:    If ``True`` (the default), the original columns are
                     flagged for removal.
    """

    if nameFormat is None:
        nameFormat = '{vid}-{visit}.{instance}_{index}'

    columns   = list(it.chain(*[dtable.columns(v) for v in vids]))
    newseries = []
    newvids   = []

    for column in columns:

        data    = dtable[:, column.name]
        newdata = core.expandCompound(data)

        for i in range(newdata.shape[1]):

            coldata = newdata[:, i]
            name    = nameFormat.format(vid=column.vid,
                                        visit=column.visit,
                                        instance=column.instance,
                                        index=i)

            newvids  .append(column.vid)
            newseries.append(pd.Series(coldata,
                                       index=dtable.index,
                                       name=name))

    if replace: return columns, newseries, newvids
    else:       return          newseries, newvids
