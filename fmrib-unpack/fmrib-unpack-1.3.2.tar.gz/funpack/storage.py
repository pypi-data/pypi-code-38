#!/usr/bin/env python
#
# storage.py - The HDFStoreCollection class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`HDFStoreCollection` class, a simple
class which can be used to split the columns of a ``pandas.DataFrame``
across multiple HDF5 files.
"""


import multiprocessing       as mp
import multiprocessing.dummy as mpd
import functools             as ft
import itertools             as it
import os.path               as op
import                          uuid
import                          shutil
import                          logging
import                          tempfile
import                          warnings
import                          contextlib
import                          collections

import pandas  as pd
import numpy   as np


log = logging.getLogger(__name__)


COLUMNS_PER_FILE = 100
"""Default value for the ``colsPerFile`` parameter to
:class:`HDFStoreCollection`.
"""


@contextlib.contextmanager
def _silence_tables():
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', module='tables')
        yield


def is_bool_array(obj):
    ba = isinstance(obj, (np.ndarray, pd.Series))
    ba = ba and obj.dtype == np.bool
    return ba


class HDFStoreCollection(object):
    """The ``HDFStoreCollection`` class can be used to store, read and write
    one or more ``pandas.DataFrame`` objects (all with the same columns) as
    HDF5 files, where each file contains a sub-set of columns.

    If a ``multiprocessing.Manager`` is passed to :mod:`__init__`, the methods
    of the ``HDFStoreCollection`` are thread- and process-safe for reading and
    writing.
    """


    def __init__(self,
                 prefix=None,
                 workDir=None,
                 colsPerFile=None,
                 mgr=None):
        """Create a ``HDFStoreCollection``.


        :arg prefix:      Prefix to use for HDF files. Defaults to a randomly
                          generated sequence of characters.


        :arg workDir:     Directory to store the HDF files. Defaults to a
                          temporary directory, which will be deleted when this
                          ``HDFStoreCollection`` is garbage-collected.

        :arg colsPerFile: Maximum number of data columns to store in each
                          ``.h5`` file. Pytables doesn't allow more than
                          about 2000 columns to be stored in its HDF files,
                          so we have to split wide tables across multiple
                          files. Defaults to :attr:`COLUMNS_PER_FILE`.

        :arg mgr:         A ``multiprocessing.Manager`` - this must be provided
                          for concurrent write support. Not needed if
                          concurrent writing is not needed.
        """

        if prefix      is None: prefix      = uuid.uuid4().hex[:8]
        if colsPerFile is None: colsPerFile = COLUMNS_PER_FILE

        ownDir = workDir is None

        if ownDir:
            workDir = tempfile.mkdtemp()

        # __storeFiles is a list of file
        # names used to store the columns
        # of the data frame(s).
        #
        # __columns is a dict of
        # { column : file_index } mappings,
        # used to keep track of which
        # columns are stored in which file.
        #
        # __columns is a list of lists of
        # column names, used to keep track
        # of which columns are stored in
        # which file.
        #
        # __locks is a list of mgr.Lock
        # objects, used to lock files for
        # writing.
        #
        # All are initialised in the
        # append method.
        self.__mgr         = mgr
        self.__ownDir      = ownDir
        self.__prefix      = prefix
        self.__workDir     = op.abspath(workDir)
        self.__colsPerFile = colsPerFile
        self.__storeFiles  = None
        self.__fileLocks   = None
        self.__columns     = None

        # Ugly hack - columns which cannot be
        # stored in pytables (e.g. which have
        # a complicated data type) are stored
        # in-memory in the __unstorable dict.
        #
        # TODO If you need write support
        #      across multiple processes,
        #      you will need to use a more
        #      complicated (e.g. file-based)
        #      strategy for storing/sharing
        #      these columns.
        self.__unstorable = {}


    def __del__(self):
        """If this ``HDFStoreCollection`` created a temporary directory to
        store the HDF5 files, that directory is deleted.
        """
        if self.__ownDir:
            shutil.rmtree(self.__workDir)


    def __getstate__(self):
        """Returns the state of this ``HDFStoreCollection`` for pickling.
        """
        return (self.__prefix,
                self.__workDir,
                self.__colsPerFile,
                self.__storeFiles,
                self.__fileLocks,
                self.__columns,
                self.__unstorable)


    def __setstate__(self, state):
        """Set the state of this ``HDFStoreCollection`` for
        unpickling.
        """

        self.__ownDir      = False
        self.__mgr         = None
        self.__prefix      = state[0]
        self.__workDir     = state[1]
        self.__colsPerFile = state[2]
        self.__storeFiles  = state[3]
        self.__fileLocks   = state[4]
        self.__columns     = state[5]
        self.__unstorable  = state[6]


    @property
    def colsPerFile(self):
        """Returns the maximum number of columns stored in each HDF5 file. """
        return self.__colsPerFile


    @property
    def prefix(self):
        """Returns the file prefix used by this ``HDFStoreCollection``. """
        return self.__prefix


    @property
    def workDir(self):
        """Returns the directory that contains the HDF5 files. """
        return self.__workDir


    @contextlib.contextmanager
    def storeFile(self, idx, mode, *args, **kwargs):
        """Context manager which yields a ``pandas.HDFStore`` object
        for the file with the given ``idx``.
        """

        if self.__fileLocks is not None:
            lock = self.__fileLocks[idx]
        else:
            lock = mp.Lock()

        with lock:
            with pd.HDFStore(self.__storeFiles[idx],
                             mode=mode,
                             *args, **kwargs) as f:
                yield f


    def columnIndex(self, column):
        """Returns the index of the file that contains the given column. """
        for i in range(len(self.__columns)):
            if column in self.__columns[i]:
                return i
        raise ValueError('Column {} is not in store'.format(column))


    def columnBlocks(self, cols):
        """Splits the given sequence of column names into blocks for
        each underlying file.

        :returns: a ``dict`` of ``{ idx : [column] }`` mappings.
        """

        colblocks = collections.defaultdict(list)

        for col in cols:
            idx = self.columnIndex(col)
            colblocks[idx].append(col)

        return colblocks


    def columnsIn(self, idx):
        """Returns a list of all the columns stored in the specified file. """
        return self.__columns[idx]


    def _dropRows(self, rows, idx):
        """Drop the specified ``rows`` in the file at ``idx``. """

        log.debug('Dropping rows from store file %i: %s', idx, rows)

        cols = self.columnsIn(idx)
        with self.storeFile(idx, mode='a') as s:
            for col in cols:
                s.put(col, s[col][rows], format='table')


    def dropRows(self, rows, pool=None):
        """Drops the specified rows from the data set.

        :arg rows: Something which can be used to index the rows of a
                   ``pandas.Series``.
        """

        ownPool = pool is None

        if pool is None:
            pool = mpd.Pool(1)

        idxs = range(len(self.__storeFiles))
        pool.map(ft.partial(self._dropRows, rows), idxs)

        if ownPool:
            pool.close()
            pool.join()


    def _dropColumns(self, idx, cols):
        """Drop all columns from the specified file.

        Assumes that all columns in ``cols`` are present in the file at
        ``idx``.
        """

        log.debug('Dropping columns from store file %i: %s', idx, cols)

        with self.storeFile(idx, 'a') as s:
            for col in cols:
                s.remove(col)

                # self.__columns[idx] may be
                # a mp.Manager.list, so we
                # re-assign it to make sure
                # it is propagated.
                newcols = self.__columns[idx]
                newcols.remove(col)
                self.__columns[idx] = newcols


    def dropColumns(self, cols, pool=None):
        """Drops the specified columns from the data set.

        :arg cols: Sequence of columns to drop.
        """

        ownPool = pool is None

        if pool is None:
            pool = mpd.Pool(1)

        blocks = self.columnBlocks(cols)
        pool.starmap(self._dropColumns, blocks.items())

        if ownPool:
            pool.close()
            pool.join()


    def append(self, dataframe):
        """Append more rows to the store. """

        columns   = list(dataframe.columns)
        ncols     = len(columns)
        nfiles    = int(np.ceil(ncols / self.colsPerFile))
        colBlocks = []

        if self.__columns is not None:
            if self.columns != columns:
                raise ValueError('Columns do not match!')

        for i in range(nfiles):
            s = i * self.colsPerFile
            e = s + self.colsPerFile
            colBlocks.append(columns[s:e])

        if self.__storeFiles is None:

            filenames = ['{}_{:03d}.h5'.format(self.__prefix, i)
                         for i in range(nfiles)]
            filenames = [op.join(self.__workDir, f) for f in filenames]

            self.__storeFiles = filenames
            self.__columns    = collections.OrderedDict()

            if self.__mgr is not None:
                self.__fileLocks = [self.__mgr.Lock() for f in filenames]
                self.__columns   =  self.__mgr.list()
            else:
                self.__fileLocks = None
                self.__columns   = []

            self.__columns.extend([[] for i in range(nfiles)])

            for i, cb in enumerate(colBlocks):
                for col in cb:
                    # self.__columns[i] may be
                    # a mp.Manager.list, so we
                    # re-assign it to make sure
                    # it is propagated.
                    self.__columns[i] = self.__columns[i] + [col]

                log.debug('Assigning %u columns [%s, ..., %s] to file %s',
                          len(cb), cb[0], cb[-1], filenames[i])

        # TODO store index separately
        for i, block in enumerate(colBlocks):
            with self.storeFile(i, mode='a') as s, _silence_tables():

                log.debug('Appending %u columns [%s, ..., %s] to file %s',
                          len(block), block[0], block[-1], s.filename)

                for col in block:
                    s.append(col, dataframe[col], format='table')


    def __len__(self):
        """Returns the number of rows in the store. """
        return self.nrows


    @property
    def nrows(self):
        """Returns the number of rows in the store. """
        with self.storeFile(0, mode='r') as s:
            return s.get_storer(self.columns[0]).nrows


    @property
    def ncols(self):
        """Returns the number of columns in the store. """

        ncols = 0

        for i in range(len(self.__storeFiles)):
            with self.storeFile(i, mode='r') as s:
                ncols += len(s)

        return ncols


    @property
    def columns(self):
        """Returns all of the columns in the store. """
        return list(it.chain(*self.__columns))


    @property
    def index(self):
        """Returns the store index."""

        colblock = self.columnBlocks([self.columns[0]])
        idx, col = list(colblock.items())[0]

        with self.storeFile(idx, mode='r') as s:
            return s.select(col[0]).index


    @property
    def loc(self):
        """Emulates ``pandas.DataFrame.loc``. Read or write columns and
        rows from/to the store. See the :class:`StoreSlicer`.
        """
        return StoreSlicer(self, self.__unstorable)


class StoreSlicer(object):
    """The ``StoreSlicer`` provides a slice interface (``__getitem__`` and
    ``__setitem__``) to a :class:`HDFStoreCollection`.
    """

    def __init__(self, store, unstorable):
        """Create a ``StoreSlicer``.

        :arg store:      The :class:`HDFStoreCollection`.
        :arg unstorable: Dictionary which will be used to store columns
                         that cannot be stored on disk.
        """
        self.__store      = store
        self.__unstorable = unstorable


    def __normaliseSlice(self, slc):
        """Convert a slice object (as passed to :meth:`__getitem__` or
        :meth:`__setitem__`) into separate row/column indexers.
        """

        store = self.__store

        fancyTypes = (slice, list, tuple,
                      np.ndarray, pd.core.base.PandasObject)

        # some pandas indexing operations will
        # return a Series if a single column is
        # passed, or a DataFrame if list
        # containing a single column is passed.
        # So we need to differentiate between
        # these scenarios.
        onerow = False
        onecol = False

        # only rows, slice across all columns
        if not isinstance(slc, tuple):
            rows = slc
            cols = store.columns
        else:
            rows = slc[0]
            cols = slc[1]

            # single row index - make it a list
            if not (isinstance(rows, fancyTypes) or is_bool_array(rows)):
                onerow = True
                rows   = [rows]

            # column slice
            if isinstance(cols, slice):
                cols = pd.Index(store.columns)[cols]

            # single column label - make it a list
            elif not isinstance(cols, fancyTypes):
                onecol = True
                cols   = [cols]

        return rows, cols, onerow, onecol


    def __getitem__(self, slc):
        """Get the data at the given slice. """

        store                      = self.__store
        rows, cols, onerow, onecol = self.__normaliseSlice(slc)
        colblocks                  = store.columnBlocks(cols)
        results                    = []

        for idx, colblock in colblocks.items():
            with store.storeFile(idx, mode='r') as s:
                for col in colblock:
                    try:
                        series = s.select(col)
                    except Exception:
                        series = None

                    if series is None:
                        series = self.__unstorable.get(col, None)
                    results.append(series.loc[rows])

        result = pd.concat(results, axis=1, sort=False)

        if onecol: return result.iloc[:, 0]
        else:      return result
        return result


    def __setitem__(self, slc, val):
        """Set the data at the given slice. """

        store      = self.__store
        rows, cols = self.__normaliseSlice(slc)[:2]
        colblocks  = store.columnBlocks(cols)

        # If this assignment is across multiple columns,
        # does the provided value need to be indexed?
        if isinstance(val, pd.DataFrame):
            validxs = cols
        elif isinstance(val, np.ndarray) and val.shape == 2:
            validxs = range(len(cols))

        # constant/1D array/series - no indexing
        # necessary.
        else:
            validxs = [None] * len(cols)

        validxs = iter(validxs)

        for idx, colblock in colblocks.items():
            with store.storeFile(idx, mode='a') as s, _silence_tables():
                for col in colblock:

                    data   = s[col]
                    validx = next(validxs)
                    if validx is None: data[rows] = val
                    else:              data[rows] = val[validx]

                    try:
                        s.put(col, data, format='table')
                    except TypeError:
                        log.warning('Unstorable column: %s', col)
                        self.__unstorable[col] = data
