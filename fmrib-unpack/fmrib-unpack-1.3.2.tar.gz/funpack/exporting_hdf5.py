#!/usr/bin/env python
#
# exporting_hdf5.py - Export data to HDF5 files
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions for exporting data to HDF5 files. """


import logging

import                     h5py
import numpy            as np
import pandas           as pd
import pandas.api.types as pdtypes

from . import util
from . import custom


log = logging.getLogger(__name__)


HDF5_KEY = 'funpack'
"""Default group key to use when exporting to a HDF5 file. """


HDF5_STYLES = ['pandas', 'funpack']
"""Available styles to use when saving to HDF5, specified via the ``style``
argument passed to the :func:`exportHDF5` function.
"""


HDF5_STYLE = 'pandas'
"""Default style to use when exporting to a HDF5 file. """


@custom.exporter('hdf5')
def exportHDF5(dtable,
               outfile,
               subjects,
               idcol,
               colnames,
               key=None,
               style=None,
               **kwargs):
    """Export data to a HDF5 file.

    The ``style`` argument determins the internal format of the resulting HDF5
    file. Available styles are ``'pandas'`` and ``'funpack'`` - see the
    :func:`exportPandasStyle` and :func:`exportFunpackStyle` functions
    for details.

    :arg dtable:     :class:`.DataTable` containing the data

    :arg outfile:    File to output to

    :arg subjects:   Sequence containing subjects (and order) to export.

    :arg idcol:      Name to use for the subject ID column

    :arg colnames:   Sequence containing column names

    :arg key:        Name to give the HDF5 group. Defaults to :attr:`HDF5_KEY`.

    :arg style:      HDF5 style to use (see above). Defaults to
                     :attr:`HDF5_STYLE`.
    """

    if key   is None: key   = HDF5_KEY
    if style is None: style = HDF5_STYLE

    if style not in HDF5_STYLES:
        raise ValueError('Unrecognised HDF5 style: {}'.format(style))

    if style == 'pandas':
        exportPandasStyle(dtable,
                          outfile,
                          subjects,
                          idcol,
                          colnames,
                          key=key,
                          **kwargs)

    elif style == 'funpack':
        exportFunpackStyle(dtable,
                           outfile,
                           subjects,
                           idcol,
                           colnames,
                           key=key,
                           **kwargs)


def exportPandasStyle(dtable,
                      outfile,
                      subjects,
                      idcol,
                      colnames,
                      key,
                      numRows=None,
                      **kwargs):
    """Save the data to a ``pandas``-style HDF5 file.

    The entire data frame is saved using the ``pandas.to_hdf`` function,
    under a single group named according to the ``key`` argument.

    The data can be reloaded via the ``pandas.read_hdf`` function.

    :arg dtable:     :class:`.DataTable` containing the data

    :arg outfile:    File to output to

    :arg subjects:   Sequence containing subjects (and order) to export.

    :arg idcol:      Name to use for the subject ID column

    :arg colnames:   Sequence containing column names

    :arg key:        Name to give the HDF5 group.

    :arg numRows:    Number of rows to write at time (only used for
                     ``pandas``-style files).
    """

    if numRows is None:
        numRows = len(dtable)

    with pd.HDFStore(outfile, 'w') as s:

        nchunks  = int(np.ceil(len(subjects) / numRows))
        oldcols  = [c.name for c in dtable.allColumns[1:]]
        colnames = {oc : nc for oc, nc in zip(oldcols, colnames)}

        log.info('Writing %u columns in %u chunk(s) to %s ...',
                 len(dtable.allColumns), nchunks, outfile)

        for chunki in range(nchunks):
            cstart  = chunki * numRows
            cend    = cstart + numRows
            csubjs  = subjects[cstart:cend]
            towrite = dtable[csubjs, :]

            towrite.index.name = idcol
            towrite.rename(columns=colnames, inplace=True)

            if chunki == 0: s.put(   key, towrite, format='table')
            else:           s.append(key, towrite, format='table')


def exportFunpackStyle(dtable,
                       outfile,
                       subjects,
                       idcol,
                       colnames,
                       key,
                       dateFormat=None,
                       timeFormat=None):
    """Save the data to a ``funpack``-style HDF5 file.

    Each column is saved as a separate data set, and named according to the
    column name. All columns are saved under a single group named according to
    the ``key`` argument.

    :arg dtable:     :class:`.DataTable` containing the data

    :arg outfile:    File to output to

    :arg subjects:   Sequence containing subjects (and order) to export.

    :arg idcol:      Name to use for the subject ID column

    :arg colnames:   Sequence containing column names

    :arg key:        Name to give the HDF5 group.

    :arg dateFormat: Name of formatter to use for date columns.

    :arg timeFormat: Name of formatter to use for time columns.
    """

    if dateFormat is None: dateFormat = 'default'
    if timeFormat is None: timeFormat = 'default'

    vartable = dtable.vartable

    log.info('Writing %u columns in to %s ...',
             len(dtable.allColumns), outfile)

    with h5py.File(outfile, 'w') as f:

        name = '/'.join((key, idcol))
        data = np.asarray(subjects)
        f.create_dataset(name, data=data)

        for i, col in enumerate(dtable.allColumns[1:]):

            name      = '/'.join((key, colnames[i]))
            series    = dtable[subjects, col.name]
            vid       = col.vid
            formatter = None

            if vid in vartable.index: vtype = vartable['Type'][vid]
            else:                     vtype = None

            if   vtype == util.CTYPES.date:
                formatter = dateFormat
            elif vtype == util.CTYPES.time or \
                 pdtypes.is_datetime64_any_dtype(series):
                formatter = timeFormat

            if formatter is not None:
                log.debug('Formatting column %s with %s formatter',
                          name, formatter)
                series = custom.runFormatter(
                    formatter, dtable, col, series)
            else:
                series = np.asarray(series)

            if np.issubdtype(series.dtype, np.number):
                dtype = None
            else:
                dtype = h5py.special_dtype(vlen=str)

            f.create_dataset(name, dtype=dtype, data=series)


def importFunpackStyle(infile, idcol, key=None):
    """Load a ``funpack``-style HDF5 file as a ``pandas.DataFrame``.
    See the :func:`exportFunpackStyle` function.

    :arg infile: File to load

    :arg idocol: Name of index column.

    :arg key:    HDF5 group key containing the data. If not provided, and
                 the file only has one group, that group is assumed to
                 contain the data. If not provided, and the file contains
                 more than one group, a :exc:`ValueError` is raised.

    :returns:    A ``pandas.DataFrame`` containing the data.
    """

    df = pd.DataFrame()

    with h5py.File(infile, 'r') as f:

        if key is None and len(f.keys()) != 1:
            raise ValueError('Key not provided, and file contains '
                             'multiple keys: {}'.format(infile))

        if key is None:
            key = f.keys()[0]

        cols = list(f[key].keys())

        if idcol not in cols:
            raise ValueError('Index column not in file: {}'.format(idcol))

        for colname in cols:
            df[colname] = np.asarray(f['/'.join((key, colname))])

    return df.set_index(idcol)
