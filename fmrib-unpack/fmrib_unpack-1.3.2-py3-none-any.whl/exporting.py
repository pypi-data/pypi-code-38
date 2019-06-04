#!/usr/bin/env python
#
# exporting.py - Functions for exporting data
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides functions for exporting data to a file. """


import itertools        as it
import                     logging
import                     collections

import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

from . import util
from . import custom


log = logging.getLogger(__name__)


COLUMN_PATTERN = '{name}'
"""Default output column naming pattern. A python-style formatting string
which may refer to:

  - ``'{variable}'``
  - ``'{name}'``
  - ``'{description}'``
  - ``'{visit}'``
  - ``'{instance}'``
"""


EXPORT_FORMAT = 'tsv'
"""Default export format."""


def genColumnNames(dtable, colpat=None, colmap=None):
    """Generate column names to use in the output file.

    :arg dtable: :class:`.DataTable` containing the data to export.

    :arg colpat: Output column name pattern. If not provided, defaults to
                 :attr:`COLUMN_PATTERN`.

    :arg colmap: Dictionary containing ``{variable : name}`` mappings.

    :returns:    A dictionary containing ``{incolumn : outcolumn}`` mappings.
    """

    if colpat is None: colpat = COLUMN_PATTERN
    if colmap is None: colmap = {}

    variables = dtable.variables
    newcols   = {}

    for var in variables:

        # ID column
        if var == 0:
            continue

        desc      = dtable.vartable.loc[var, 'Description']
        visits    = dtable.visits(var)
        instances = dtable.instances(var)

        if pd.isna(desc):
            desc = ''

        for visit, instance in it.product(visits, instances):
            for oldcol in dtable.columns(var, visit, instance):

                newcol = colmap.get(oldcol.name, None)

                if newcol is None:
                    newcol = colpat.format(variable=var,
                                           visit=visit,
                                           name=oldcol.name,
                                           description=desc,
                                           instance=instance)

                newcols[oldcol.name] = newcol

    return newcols


def exportData(dtable,
               outfile,
               subjects=None,
               colpat=None,
               colmap=None,
               idcol=None,
               fileFormat=None,
               **kwargs):
    """Export the data contained in ``dtable`` to ``outfile`` using the
    specified ``fileFormat``.

    :arg dtable:        :class:`.DataTable` containing the data to export.

    :arg outfile:       File to export data to.

    :arg subjects:      Sequence containing subjects (and order) to export.
                        *Only* these subjects will be exported. Default is
                        to export all subjects.

    :arg colpat:        Output column name pattern - see
                        :func:`.genColumnNames`.

    :arg colmap:        Dictionary containing ``{variable : name}`` mappings,
                        to be used as the ``variable`` in ``colpat`` when
                        generating output column names.

    :arg idcol:         Name to use for ID column. Defaults to the original
                        index column name (``pandas.DataFrame.index.name``).

    :arg fileFormat:    File format to export to - the name of a ``@exporter``
                        plugin. If not provided, defaults to
                        :attr:`EXPORT_FORMAT`

    All other arguments are passed through to the exporter plugin.
    """

    if fileFormat is None: fileFormat = EXPORT_FORMAT
    if idcol      is None: idcol      = dtable.index.name

    if subjects is None:
        subjects = dtable.index
    else:
        subjects = [s for s in subjects if s in dtable.index]

    colnames = genColumnNames(dtable, colpat, colmap)
    colnames = [colnames[c.name] for c in dtable.allColumns[1:]]

    custom.runExporter(
        fileFormat, dtable, outfile, subjects, idcol, colnames, **kwargs)


@custom.formatter('default')
def defaultDateTimeFormat(dtable, column, series):
    """Default format converter for date and time columns. """

    if pdtypes.is_datetime64_any_dtype(series):

        # pandas uses the same data type
        # (pandas.Timestamp) for all date/time
        # types. So to distinguish between
        # dates, and full time stamps, we
        # need to look at the biobank type
        vttype = dtable.vartable.loc[column.vid, 'Type']

        # The biobank "Date" type is just a date
        if vttype == util.CTYPES.date: fmt = '%Y-%m-%d'
        else:                          fmt = '%Y-%m-%dT%H:%M:%S%z'

        def format(val):
            try:
                return val.strftime(fmt)
            except Exception:
                return np.nan

        return series.apply(format)

    else:
        return series


@custom.formatter('compound')
def formatCompound(dtable, column, series, delim=','):
    """Format a compound (multi-valued) column which is stored in-memory
    as a list or ``numpy`` array.
    """

    if len(series) == 0:
        return series

    sample = series.iloc[0]

    if isinstance(sample, str):
        return series
    if not isinstance(sample, (np.ndarray, collections.Sequence)):
        return series

    def format(val):
        return delim.join([str(v) for v in val])

    return series.apply(format)
