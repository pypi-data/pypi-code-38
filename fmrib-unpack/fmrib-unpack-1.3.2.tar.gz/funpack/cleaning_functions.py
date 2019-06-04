#!/usr/bin/env python
#
# cleaning_functions.py - Cleaning functions.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains definitions of cleaning functions - functions
which may be specified in the ``Clean`` column of the variable table,
and which are appiled during the data import stage.

The following cleaning functions are available:

.. autosummary::
   :nosignatures:

   remove
   keepVisits
   fillVisits
   fillMissing
   convertICD10Codes
   makeNa


All cleaning functions (with two exceptions - :func:`remove` and
:func:`keepVisits`, explained below) will be passed the following as their
first positional arguments, followed by any arguments specified in the
variable table:

 - The :class:`.DataTable` object, containing references to the data, variable,
   and processing table.
 - The integer ID of the variable to process

These functions are expected to perform in-place pre-processing on the data.


The :func:`remove` and :func:`keepVisits` functions are called before the data
is loaded, as they are used to determine which columns should be loaded
in. They therefore have a different function signature to the other cleaning
functions, which are called after the data has been loaded. These functions
are passed the following positional arguments, followed by arguments specified
in the variable table:

 - The variable table, containing metadata about all known variables

 - The integer ID of the variable to be checked

 - A list of :class:`.Column` objects denoting all columns
   associated with this variable that are present in the data

These functions are expected to return a modified list containing the columns
that should be loaded.
"""


import logging

import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

from . import util
from . import icd10
from . import custom
from . import hierarchy
from . import expression


log = logging.getLogger(__name__)


@custom.cleaner()
def remove(vartable, vid, columns):
    """remove()
    Remove (do not load) all columns associated with ``vid``.

    :arg vartable: Variable table
    :arg vid:      Integer variable ID.
    :arg columns:  List of all :class:`.Column` objects associated with
                   ``vid``.
    :returns:      An empty list.
    """
    return []


@custom.cleaner()
def keepVisits(vartable, vid, columns, *tokeep):
    """keepVisits(visit, [visit, ...])
    Only load columns for ``vid`` which correspond to the specified visits.

    This test is only applied to variables which have an *instancing* equal to
    2:

    https://biobank.ctsu.ox.ac.uk/crystal/instance.cgi?id=2

    Such variables are not associated with a specific visit, so it makes no
    sense to apply this test to them. See the
    :func:`.loadtables.addNewVariable` function for more information on
    variable instancing.

    :arg vartable: Variable table

    :arg vid:      Integer variable ID.

    :arg columns:  List of all :class:`.Column` objects that are associated
                   with ``vid``.

    :arg tokeep:   Visit IDs (integers), or ``'first'``, or ``'last'``,
                   indicating that the first or last visit should be loaded.

    :returns:      List of columns that should be loaded.
    """

    # variables which don't follow instancing
    # 2 do not have columns that correspond
    # to specific visits.
    instancing = vartable.loc[vid, 'Instancing']
    if instancing != 2:
        return columns

    keep      = []
    minVisit  = min([c.visit for c in columns])
    maxVisit  = max([c.visit for c in columns])

    for col in columns:

        test = [col.visit]

        if col.visit == minVisit: test.append('first')
        if col.visit == maxVisit: test.append('last')

        if col not in keep and any([v in tokeep for v in test]):
            keep.append(col)

    return keep


@custom.cleaner()
def fillVisits(dtable, vid, method='mode'):
    """fillVisits([method=(mode|mean)])
    Fill missing visits from available visits.

    For a variable with multiple visits, fills missing values from the visits
    that do contain data.
    """

    if method not in ('mode', 'mean'):
        raise ValueError('Unknown method: {}'.format(method))

    instances = dtable.instances(vid)

    for instance in instances:
        columns = [c.name for c in dtable.columns(vid, instance=instance)]
        view    = dtable[:, columns]

        if   method == 'mode': repvals = view.mode('columns')[0]
        elif method == 'mean': repvals = view.mean('columns')

        log.debug('Filling NA values in columns %s across visits', columns)

        for col in columns:
            dtable[:, col] = dtable[:, col].fillna(repvals)


@custom.cleaner()
def fillMissing(dtable, vid, value):
    """fillMissing(fill_value)
    Fill missing values with a constant.

    Fills all missing values in columns for the given variable with
    ``value``.
    """
    columns = [c.name for c in dtable.columns(vid)]
    log.debug('Filling NA values in columns %s with %i', columns, value)
    for col in columns:
        dtable[:, col] = dtable[:, col].fillna(value)


@custom.cleaner()
def flattenHierarchical(dtable, vid, level=None, name=None):
    """flattenHierarchical([level], [name])
    Replace leaf values with parent values in hierarchical variables.

    For hierarchical variables such as the ICD10 disease categorisations,
    this function replaces leaf values with a parent value.

    The ``name`` argument allows the hierarchy data type to be specified.

    The ``level`` argument allows the depth of the parent value to be selected
    - ``0`` (the default) replaces a value with the top-level (i.e. its most
    distant) parent value, ``1`` the second-level parent value, etc.

    If, for a particular value, the ``level`` argument is greater than the
    number of ancestors of the value, the value is unchanged.
    """

    if level is None:
        level = 0

    columns = [c.name for c in dtable.columns(vid)]
    vhier   = hierarchy.getHierarchyFilePath(dtable, vid, name)
    vhier   = hierarchy.loadHierarchyFile(vhier)

    def index_parent(parents, coding):

        # the list returned by Hierarchy.parents
        # is ordered from closest to most distant
        # parent, so we index from the end.
        if pdtypes.is_number(parents) and pd.isna(parents):
            return coding

        idx = len(parents) - 1 - level

        # If the specified level is out of
        # bounds, we return the original value
        if idx < 0: return coding
        else:       return parents[idx]

    log.debug('Flattening hierarchical data in columns %s (level %i)',
              columns, level)
    for col in columns:
        data           = dtable[:, col]
        parents        = data.map(vhier.parents, na_action='ignore')
        parents        = parents.combine(data, index_parent)
        dtable[:, col] = parents


@custom.cleaner()
def codeToNumeric(dtable, vid, name):
    """codeToNumeric([name])
    Convert hierarchical alpha-numeric codes to numeric equivalents.

    Given a hierarchical variable which contains alpha-numeric codings, this
    function will replace the codings with numeric equivalents.

    :arg name: Hierarchy data type name
    """

    log.debug('Converting hierarchy codes to numeric for variable %i', vid)

    hier = hierarchy.getHierarchyFilePath(dtable, vid, name)
    hier = hierarchy.loadHierarchyFile(hier)

    def convert(code):
        return hierarchy.codeToNumeric(code, name)

    cols  = [c.name for c in dtable.columns(vid)]
    codes = dtable[:, cols]

    for col in cols:
        dtable[:, col] = codes[col].map(convert)

    if name == 'icd10':
        for col in cols:
            icd10.storeCodes(codes[col].tolist())


@custom.cleaner()
@util.deprecated('Use codeToNumeric(\'icd10\') instead')
def convertICD10Codes(dtable, vid):
    """convertICD10Codes()
    Convert ICD10 codes to numeric values. Deprecated - use codeToNumeric.

    Converts values which are assumed to contain ICD10 codes into numeric
    values.
    """
    codeToNumeric(dtable, vid, 'icd10')


@custom.cleaner()
def parseSpirometryData(dtable, vid):
    """parseSpirometryData()
    Parse spirometry (lung volume measurement) data.

    Parses values which contain spirometry (lung volume measurement) test
    data.

    Columns for UK Biobank variable 3066 and 10697 contain comma-separated
    time series data. This function converts the text values into ``numpy``
    arrays, and potentially re-orders instances of the variable within each
    visit - subjects potentially underwent a series of tests, with each test
    stored as a separate instance within one visit. However, the instance
    order does not necessarily correspond to the test order.

    See the following links for more information:

     - https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=3066
     - https://biobank.ctsu.ox.ac.uk/crystal/field.cgi?id=10697
    """
    visits = dtable.visits(vid)

    # applied to each row
    def fixOrder(vals):

        def parseBlow(val):
            # the first entry is "blowN",
            # where N is the blow number
            try:
                tkn = val[:10].split(',', maxsplit=1)[0]
                return int(tkn[4:])
            except Exception:
                return np.nan
        bnumvals = [(parseBlow(v), v) for v in vals]
        bnumvals = sorted(bnumvals)
        return pd.Series([bv[1] for bv in bnumvals],
                          index=vals.index)

    def parseValue(val):
        # first entry is "blowN", second
        # entry is number of samples.
        # Ignore them both, turn the
        # remainder into a numpy array
        try:
            val = val.split(',', maxsplit=2)[2]
            return np.fromstring(val, sep=',')
        except Exception:
            return np.nan

    for visit in visits:
        cols = dtable.columns(vid, visit=visit)
        cols = [c.name for c in cols]

        data = dtable[:, cols]
        data = data.apply(fixOrder,   axis=1)
        for col in cols:
            data.loc[:, col] = data.loc[:, col].apply(parseValue)

        dtable[:, cols] = data


@custom.cleaner()
def makeNa(dtable, vid, expr):
    """makeNa(expression)
    Replace values which pass the expression with NA.

    Replaces all values in ``vid`` for which ``func`` evaluates to ``True``
    with ``nan``.
    """

    expr = expression.Expression('v{} {}'.format(vid, expr))
    cols = dtable.columns(vid)

    for col in cols:
        col               = col.name
        mask              = expr.evaluate(dtable, {vid : col})
        dtable[mask, col] = np.nan
