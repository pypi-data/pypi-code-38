#!/usr/bin/env python
#
# exporting_tsv.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import logging

import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

from . import util
from . import custom


log = logging.getLogger(__name__)


TSV_SEP = '\t'
"""Default separator string to use in TSV-style output files."""


@custom.exporter('tsv')
def exportTSV(dtable,
              outfile,
              subjects,
              idcol,
              colnames,
              sep=None,
              missingValues=None,
              dateFormat=None,
              timeFormat=None,
              formatters=None,
              numRows=None,
              nonNumericFile=None,
              **kwargs):
    """Export data to a TSV-style file.

    :arg dtable:         :class:`.DataTable` containing the data

    :arg outfile:        File to output to

    :arg subjects:       Sequence containing subjects (and order) to export.

    :arg idcol:          Name to use for the subject ID column

    :arg colnames:       Sequence containing column names

    :arg sep:            Separator character to use. Defaults to
                         :attr:`TSV_SEP`

    :arg missingValues:  String to use for missing/NA values. Defaults to the
                         empty string.

    :arg dateFormat:     Name of formatter to use for date columns.

    :arg timeFormat:     Name of formatter to use for time columns.

    :arg formatters:     Dict of ``{ [vid|column] : formatter }`` mappings,
                         specifying custom formatters to use for specific
                         variables.

    :arg numRows:        Number of rows to write at a time. Defaults to writing
                         all rows in one go.

    :arg nonNumericFile: If provided, non-numeric columns (after formatting)
                         are saved to this file instead of to ``outfile``
    """
    if sep           is None: sep           = TSV_SEP
    if missingValues is None: missingValues = ''
    if dateFormat    is None: dateFormat    = 'default'
    if timeFormat    is None: timeFormat    = 'default'
    if formatters    is None: formatters    = {}
    if numRows       is None: numRows       = len(dtable)
    if colnames      is None: colnames      = True

    nchunks   = int(np.ceil(len(subjects) / numRows))
    vartable  = dtable.vartable

    # Created during the first iteration.
    # If nonNumericFile is specified, we
    # store the names of all numeric and
    # non-numeric columns here so we can
    # figure out which columns to put
    # where.
    numericCols    = None
    nonNumericCols = None

    log.info('Writing %u columns in %u chunk(s) to %s ...',
             len(dtable.allColumns), nchunks, outfile)

    for chunki in range(nchunks):

        cstart  = chunki * numRows
        cend    = cstart + numRows
        csubjs  = subjects[cstart:cend]
        towrite = pd.DataFrame(index=csubjs)

        for col in dtable.allColumns:

            vid = col.vid

            if vid == 0:
                continue

            name      = col.name
            series    = dtable[csubjs, name]
            formatter = formatters.get(vid, None)

            if vid in vartable.index: vtype = vartable['Type'][vid]
            else:                     vtype = None

            # allow formatters to be
            # specified by column name
            # as well
            if formatter is None:
                formatter = formatters.get(name, None)

            # fall back to date/time formatting
            # if relevant for this column
            if formatter is None:
                if   vtype == util.CTYPES.date:
                    formatter = dateFormat
                elif vtype == util.CTYPES.time or \
                     pdtypes.is_datetime64_any_dtype(series):
                    formatter = timeFormat

            if formatter is not None:
                log.debug('Formatting column %s [chunk %u] with %s formatter',
                          name, chunki, formatter)
                towrite[name] = custom.runFormatter(
                    formatter, dtable, col, series)
            else:
                towrite[name] = series

        if nonNumericFile is None:
            numericCols     = colnames
            nonNumericCols  = None
            numericChunk    = towrite
            nonNumericChunk = None
        else:
            if numericCols is None:
                numericCols    = [c for c in towrite.columns
                                  if     pdtypes.is_numeric_dtype(towrite[c])]
                nonNumericCols = [c for c in towrite.columns
                                  if not pdtypes.is_numeric_dtype(towrite[c])]

                if len(nonNumericCols) > 0:
                    log.debug('Redirecting %i non-numeric columns to %s '
                              '(remaining %i columns will be written to %s)',
                              len(nonNumericCols), nonNumericFile,
                              len(numericCols),    outfile)
                else:
                    log.debug('No non-numeric columns present - not creating '
                              '%s', nonNumericFile)
                    nonNumericFile  = None
                    nonNumericCols  = None
                    nonNumericChunk = None

            numericChunk = towrite[numericCols]
            if nonNumericCols is not None:
                nonNumericChunk = towrite[nonNumericCols]

        _writeChunk(numericChunk,
                    chunki,
                    outfile,
                    sep,
                    missingValues,
                    numericCols,
                    idcol)
        if nonNumericFile is not None:
            _writeChunk(nonNumericChunk,
                        chunki,
                        nonNumericFile,
                        sep,
                        missingValues,
                        nonNumericCols,
                        idcol)


def _writeChunk(chunk, i, outfile, sep, missingValues, colnames, idcol):
    """Write a chunk of data to a file.

    :arg chunk:         ``pandas.DataFrame`` containing the data to write
    :arg i:             Chunk index - if ``0``, column headers are written
    :arg outfile:       File to write to
    :arg sep:           Separater character
    :arg missingValues: String to use for missing values
    :arg colnames:      Names for all columns
    :arg idcol:         Name for the index column
    """

    if i > 0:
        mode     = 'a'
        colnames = False
        idcol    = None
    else:
        mode = 'w'

    chunk.to_csv(outfile,
                 sep=sep,
                 na_rep=missingValues,
                 header=colnames,
                 index_label=idcol,
                 mode=mode)
