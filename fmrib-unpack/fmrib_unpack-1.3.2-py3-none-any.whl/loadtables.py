#!/usr/bin/env python
#
# loadtables.py - Functions which load the variable, data coding, processing,
#                 and category tables used by funpack.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides functions and logic to load the variable, data coding,
type, processing, and category tables used by funpack.

The variable table is a ``pandas.DataFrame`` which contains metadata about all
UK Biobank variables in the input data files, along with cleaning rules. The
data coding and type tables contain the same information about all UK Biobank
data codings and types - these are merged into the variable table after
being loaded. All of these tables are loaded by the :func:`loadVariableTable`
function.

The processing table contains an ordered list of processing functions to be
applied to the input data.

The category table contains collections of variable groupings; it is used to
allow the user to select these groups by name, rather than having to
use variable IDs.

.. autosummary::
   :nosignatures:

   loadTables
   loadVariableTable
   addNewVariable
   loadProcessingTable
   loadCategoryTable
   categoryVariables
   columnTypes
"""


import itertools as it
import functools as ft
import os.path   as op
import              re
import              logging
import              warnings
import              functools
import              collections

import numpy  as np
import pandas as pd

from . import util
from . import fileinfo
from . import processing
from . import expression


log = logging.getLogger(__name__)


def convert_type(val):
    """Convert a string containing a type into a numerical identifier for that
    type.
    """
    valmap = {
        'sequence' :
        util.CTYPES.sequence,
        'integer' :
        util.CTYPES.integer,
        'continuous' :
        util.CTYPES.continuous,
        'categorical (single)' :
        util.CTYPES.categorical_single,
        'categorical (single non-numeric)' :
        util.CTYPES.categorical_single_non_numeric,
        'categorical (multiple)' :
        util.CTYPES.categorical_multiple,
        'categorical (multiple non-numeric)' :
        util.CTYPES.categorical_multiple_non_numeric,
        'time' : util.CTYPES.time,
        'date' :
        util.CTYPES.date,
        'text' :
        util.CTYPES.text,
        'compound' :
        util.CTYPES.compound,
        'unknown' :
        util.CTYPES.unknown,
    }
    return valmap.get(val.lower(), util.CTYPES.unknown)


def convert_comma_sep_text(val):
    """Convert a string containing comma-separated text into a list. """
    if val.strip() == '':
        return np.nan
    words = val.split(',')
    return [w.strip() for w in words]


def convert_comma_sep_numbers(val):
    """Convert a string containing comma-separated numbers into a ``numpy``
    array.
    """
    if val.strip() == '':
        return np.nan
    return np.fromstring(val, sep=',', dtype=np.float)


def convert_ParentValues(val):
    """Convert a string containing a sequence of comma-separated
    ``ParentValue`` expressions into a sequence of :class:`.Expression`
    objects.
    """
    if val.strip() == '':
        return np.nan
    return [expression.Expression(e) for e in val.split(',')]


def convert_Process_Variable(val):
    """Convert a string containing a process variable specification - one of:

      - One or more comma-separated MATLAB-style ``start:stop:step`` ranges.

      - ``'all'``, indicating that the process is to be applied to all
        variables simultaneously

      - ``'all_independent'``, indicating that the process is to be applied
        to all variables independently

      - ``'all_except,'``, followed by one or more comma-separated MATLAB-style
        ranges, indicating that the process is to be applied to all variables
        simultaneously, except for the specified variables.

      - ``'all_independent_except,'``, followed by one or more comma-separated
        MATLAB-style ranges, indicating that the process is to be applied to
        all variables independently, except for the specified variables.

    :returns: A tuple containing:

               - The process variable type - one of ``'all'``,
                 ``'all_independent'``, ``'all_except'``,
                 ``'all_independent_except'``, or ``'vids'``

               - A list of variable IDs (empty if the process variable type
                 is ``'all'`` or ``'all_independent'``).
    """
    tokens = convert_comma_sep_text(val)
    if len(tokens) == 1 and \
       tokens[0] in ('all', 'all_independent',
                     'all_except', 'all_independent_except'):
        return tokens[0], []

    if tokens[0] in ('all_except', 'all_independent_except'):
        ptype  = tokens[0]
        tokens = tokens[1:]
    else:
        ptype = 'vids'

    return ptype, list(it.chain(*[util.parseMatlabRange(t) for t in tokens]))


def convert_Process(ptype, val):
    """Convert a string containing a sequence of comma-separated ``Process`` or
    ``Clean`` expressions into an ``OrderedDict`` of :class:`.Process`
    objects (with the process names used as dictionary keys).
    """
    if val.strip() == '':
        return np.nan

    procs = processing.parseProcesses(val, ptype)

    return collections.OrderedDict([(p.name, p)  for p in procs])


def convert_category_variables(val):
    """Convert a string containing a sequence of comma-separated variable IDs
    or ranges into a list of variable IDs. Variables may be specified as
    integer IDs, or via a MATLAB-style ``start:step:stop`` range. See
    :func:`.util.parseMatlabRange`.
    """

    ranges    = convert_comma_sep_text(val)
    variables = list(it.chain(*[util.parseMatlabRange(r) for r in ranges]))

    return variables


VARTABLE_COLUMNS = [
    'ID',
    'Type',
    'Description',
    'DataCoding',
    'Instancing',
    'NAValues',
    'RawLevels',
    'NewLevels',
    'ParentValues',
    'ChildValues',
    'Clean']
"""The columns that must be in a variable table file. """


DCTABLE_COLUMNS = [
    'ID',
    'NAValues',
    'RawLevels',
    'NewLevels']
"""The columns that must be in a datacoding table file. """


TYPETABLE_COLUMNS = [
    'Type',
    'Clean']
"""The columns that must be in a type table file. """


PROCTABLE_COLUMNS = [
    'Variable',
    'Process']
"""The columns that must be in a processing table file. """


CATTABLE_COLUMNS = [
    'ID',
    'Category',
    'Variables']
"""The columns that must be in a category table file. """


VARTABLE_DTYPES = {
    'ID'           : np.uint32,
    'Description'  : object,

    # We can't use an integer for the data
    # coding, because not all variables
    # have a data coding, and pandas uses
    # np.nan to represent missing data.
    'DataCoding'   : np.float32,
    'Instancing'   : np.float32,
    'NAValues'     : object,
    'RawLevels'    : object,
    'NewLevels'    : object,
    'ParentValues' : object,
    'ChildValues'  : object,
    'Clean'        : object,

}
"""Types to use for some columns in the variable table. """


VARTABLE_CONVERTERS = {
    'Type'         : convert_type,
    'NAValues'     : convert_comma_sep_numbers,
    'RawLevels'    : convert_comma_sep_numbers,
    'NewLevels'    : convert_comma_sep_numbers,
    'ParentValues' : convert_ParentValues,
    'ChildValues'  : convert_comma_sep_numbers,
    'Clean'        : functools.partial(convert_Process, 'cleaner'),
}
"""Custom converter functinos to use for some columns in the variable
table.
"""


DCTABLE_DTYPES = {
    'ID'         : np.uint32,
    'NAValues'   : object,
    'RawLevels'  : object,
    'NewLevels'  : object,
}
"""Types to use for some columns in the data coding table. """


DCTABLE_CONVERTERS = {
    'NAValues'  : convert_comma_sep_numbers,
    'RawLevels' : convert_comma_sep_numbers,
    'NewLevels' : convert_comma_sep_numbers,
}
"""Custom converter functinos to use for some columns in the data coding
table.
"""


TYPETABLE_DTYPES = {
    'Type'  : object,
    'Clean' : object,
}
"""Types to use for some columns in the types table. """


TYPETABLE_CONVERTERS = {
    'Type'  : convert_type,
    'Clean' : functools.partial(convert_Process, 'cleaner'),
}
"""Custom converter functinos to use for some columns in the type trable. """



PROCTABLE_CONVERTERS = {
    'Variable' : convert_Process_Variable,
    'Process'  : functools.partial(convert_Process, 'processor'),
}
"""Custom converter functinos to use for some columns in the processing
table.
"""


CATTABLE_DTYPES = {
    'ID' : np.int32,
}
"""Types to use for some columns in the category table. """


CATTABLE_CONVERTERS = {
    'Variables' : convert_category_variables
}
"""Custom converter functinos to use for some columns in the category
table.
"""

UNKNOWN_CATEGORY_ID = -1
"""Category table ID to use for the automatically added unknown variable
category.
"""



def loadTables(datafiles,
               varfiles=None,
               dcfiles=None,
               typefile=None,
               procfile=None,
               catfile=None,
               **kw):
    """Loads the data tables used to run ``funpack``.

    :arg datafiles: Path(s) to the data files
    :arg varfiles:  Path to one or more partial variable table files
    :arg dcfiles:   Path to one or more partial data coding table files
    :arg typefile:  Path to the type table file
    :arg procfile:  Path to the processing table file
    :arg catfile:   Path to the category table file

    All other arguments are passed throughh to the :func:`loadVariableTable`
    and :func:`loadProcessingTable` functions.

    :returns:      A tuple containing:
                    - The variable table
                    - The processing table
                    - The category table
                    - List of :class:`.Column` objects representing columns
                      which were in the data file(s), but not in the variable
                      table
                    - List of :class:`.Column` objects representing columns
                      which are uncategorised, and do not have any cleaning or
                      processing explicitly applied for them.
    """

    vartable, unk, unc = loadVariableTable(datafiles,
                                           varfiles,
                                           dcfiles,
                                           typefile,
                                           **kw)
    proctable          = loadProcessingTable(procfile, **kw)
    cattable           = loadCategoryTable(catfile, unk)
    unc                = identifyUnprocessedVariables(vartable,
                                                      proctable,
                                                      cattable,
                                                      unc)

    return vartable, proctable, cattable, unk, unc


@util.deprecated('Use loadTables instead')
def loadDefaultTables(datafiles, **kw):
    """Deprecated - equivalent to :func:`loadTables`. """
    return loadTables(datafiles, **kw)


def loadVariableTable(datafiles,
                      varfiles=None,
                      dcfiles=None,
                      typefile=None,
                      noBuiltins=False,
                      naValues=None,
                      childValues=None,
                      recoding=None,
                      clean=None,
                      typeClean=None,
                      globalClean=None,
                      indexes=None,
                      sniffers=None,
                      dropAbsent=True,
                      **kwargs):
    """Given variable table and datacoding table file names, builds and returns
    the variable table.

    :arg datafiles:   Path(s) to the data files

    :arg varfiles:    Path(s) to one or more variable files

    :arg dcfiles:     Path(s) to one or more data coding files

    :arg typefile:    Path to the type file

    :arg noBuiltins:  If provided, the built-in variable and datacoding base
                      tables are not loaded.

    :arg naValues:    Dictionary of ``{vid : [values]}`` mappings, specifying
                      values which should be replaced with NA.

    :arg childValues: Dictionary of ``{vid : [exprs], [values]}`` mappings,
                      specifying parent value expressions, and corresponding
                      child values.

    :arg recoding:    Dictionary of ``{vid : [rawlevel], [newlevel]}``
                      mappings

    :arg clean:       Dictionary of ``{vid : expr}`` mappings containing
                      cleaning functions to apply - this will override
                      any cleaning specified in the variable file, and
                      any cleaning specified in ``typeClean``.

    :arg typeClean:   Dictionary of ``{type : expr}`` mappings containing
                      cleaning functions to apply to all variables of a
                      specific type - this will override any cleaning
                      specified in the type file.

    :arg globalClean: Expression containing cleaning functions to
                      apply to every variable - this will be performed after
                      variable-specific cleaning in the variable table,
                      or specified via ``clean`` or ``typeClean``.

    :arg indexes:     Dict of ``{filename : index}`` mappings, specifying
                      the number of the column to use as the index.
                      Defaults to 0 (the first column).

    :arg sniffers:    Dict of ``{ file : snifferName }`` mappings containing
                      custom sniffers to be used for specific files. See the
                      :mod:`.custom` module.

    :arg dropAbsent:  If ``True`` (the default), remove all variables from the
                      variable table which are not present in the data
                      file(s).

    All other keyword arguments are ignored.

    :returns: A tuple containing:

                - A ``pandas.DataFrame`` containing the variable table

                - A sequence of :class:`.Column` objects representing variables
                  which were present in the data files, but not in the variable
                  table, but were added to the variable table.

                - A sequence of :class:`.Column` objects representing variables
                  which were present in the data files and in the variable
                  table, but which did not have any cleaning rules specified.
    """

    if sniffers is None: sniffers = {}
    if indexes  is None: indexes  = {}

    if noBuiltins: varbase, dcbase = None, None
    else:          varbase, dcbase = loadTableBases()

    vartable = mergeTableFiles(varbase,
                               varfiles,
                               'variable',
                               VARTABLE_DTYPES,
                               VARTABLE_CONVERTERS,
                               VARTABLE_COLUMNS)
    dctable  = mergeTableFiles(dcbase,
                               dcfiles,
                               'data coding',
                               DCTABLE_DTYPES,
                               DCTABLE_CONVERTERS,
                               DCTABLE_COLUMNS)
    tytable  = mergeTableFiles(None,
                               [typefile],
                               'type',
                               TYPETABLE_DTYPES,
                               TYPETABLE_CONVERTERS,
                               TYPETABLE_COLUMNS)

    # Make sure data types are aligned,
    # otherwise we may run into problems
    # when merging them together.
    vartable = vartable.astype(
        {c : t for c, t in VARTABLE_DTYPES .items() if c != 'ID'})
    dctable  = dctable .astype(
        {c : t for c, t in DCTABLE_DTYPES  .items() if c != 'ID'})
    tytable  = tytable .astype(
        {c : t for c, t in TYPETABLE_DTYPES.items() if c != 'Type'})

    vartable.index = vartable.index.astype(VARTABLE_DTYPES[ 'ID'])
    dctable .index = dctable .index.astype(DCTABLE_DTYPES[  'ID'])
    tytable .index = tytable .index.astype(TYPETABLE_DTYPES['Type'])

    # All column names and variable
    # IDs in the input data files
    finfo = fileinfo.fileinfo(datafiles,
                              indexes=indexes,
                              sniffers=sniffers)

    # with the index column from
    # each file dropped
    cols = list(finfo[2])
    for i, df in enumerate(datafiles):
        idxcol  = indexes.get(df, 0)
        cols[i] = cols[i][:idxcol] + cols[i][idxcol + 1:]
    cols = list(it.chain(*cols))

    # Make sure the variable table
    # contains an entry for every
    # variable in the input data.
    unknownVars = sanitiseVariableTable(vartable, cols, dropAbsent)

    # Merge data coding specific NAValues,
    # RawLevels, and NewLevels from the data
    # coding table into the variable table.
    mergeDataCodingTable(vartable, dctable)

    # Merge provided naValues, recodings,
    # and childValues into the variable
    # table (overriding whatever was specified
    # in the datacoding/variable tables)
    if naValues is not None:
        naValues = {vid : np.array(vals) for vid, vals in naValues.items()}
        mergeIntoVariableTable(
            vartable,
            'NAValues',
            naValues)

    if recoding is not None:
        recoding = {vid : (np.array(raw), np.array(new))
                    for vid, (raw, new) in recoding.items()}
        mergeIntoVariableTable(
            vartable,
            ['RawLevels', 'NewLevels'],
            recoding)

    if childValues is not None:
        childValues = {vid : (convert_ParentValues(expr),
                              np.array(values))
                       for vid, (expr, values) in childValues.items()}
        mergeIntoVariableTable(
            vartable,
            ['ParentValues', 'ChildValues'],
            childValues)

    # Before merging the cleaning functions
    # in, we generate a list of variables
    # which are "uncleaned", i.e. have not
    # had any cleaning specified, as this
    # may indicate that a variable has been
    # overlooked.
    #
    # If a variable has indirectly had NA
    # value insertion or recoding applied
    # via its data coding, it is not included
    # in this list.
    if clean is not None: ucmask = ~vartable.index.isin(clean.keys())
    else:                 ucmask =  vartable.index.notna()

    ucmask      = (ucmask                          &
                   vartable['NAValues']    .isna() &
                   vartable['RawLevels']   .isna() &
                   vartable['ParentValues'].isna() &
                   vartable['Clean']       .isna())
    ucmask      = ucmask[ucmask]
    uncleanVars = [c for c in cols
                   if (c.vid in ucmask.index and
                       c not in unknownVars)]

    # Merge clean options into variable table
    mergeCleanFunctions(vartable, tytable, clean, typeClean, globalClean)

    # Check where we can that the
    # vartable contains valid rules
    def checkLengths(col1, col2, row):
        val1  = row[col1]
        val2  = row[col2]
        isna1 = pd.isna(val1)
        isna2 = pd.isna(val2)

        # ugh. if the value is a sequence, isna
        # will return a sequence of bools
        if not isinstance(isna1, bool): isna1 = False
        if not isinstance(isna2, bool): isna2 = False

        if isna1 and isna2:
            return
        if isna1 or isna2 or (len(val1) != len(val2)):
            raise ValueError('Columns don\'t match [len({}) != '
                             'len({})]: {}'.format(val1, val2, row.name))

    checkRecoding     = ft.partial(checkLengths, 'RawLevels', 'NewLevels')
    checkParentValues = ft.partial(checkLengths, 'RawLevels', 'NewLevels')

    vartable.apply(checkRecoding,     axis=1)
    vartable.apply(checkParentValues, axis=1)

    return vartable, unknownVars, uncleanVars


def loadTableBases():
    """Loads the UK Biobank variable and data coding schema files.

    This function is called by :func:`loadVariableTable`. It loads the UK
    Biobank variable and data coding schema files (available from the UK
    Biobank data showcase web site), and returns the information contained
    within as two ``pandas.Dataframe`` objects. These dataframes are then
    used as bases for the ``funpack`` variable table.

    :returns: A tuple containing:
               - a ``pandas.DataFrame`` to be used as the base for the
                 variable table
               - a ``pandas.DataFrame`` to be used as the base for the
                 datacoding table
    """

    # Here we load these files, both obtained
    # from the UK Biobank showcase website:
    #
    #  - field.txt    - describes all UK biobank variables
    #  - encoding.txt - describes all data codings
    #

    # This dict contains all possible combinations
    # of (value_type, base_type) from field.txt
    typecodes = {
        (11,  0)  : util.CTYPES.integer,
        (31,  0)  : util.CTYPES.continuous,
        (21,  11) : util.CTYPES.categorical_single,
        (21,  41) : util.CTYPES.categorical_single_non_numeric,
        (22,  11) : util.CTYPES.categorical_multiple,
        (22,  41) : util.CTYPES.categorical_multiple_non_numeric,
        (61,  0)  : util.CTYPES.time,
        (51,  0)  : util.CTYPES.date,
        (41,  0)  : util.CTYPES.text,
        (101, 0)  : util.CTYPES.compound,
    }

    def settype(valtype, basetype):
        return typecodes[valtype, basetype]

    datadir   = op.join(op.dirname(__file__), 'data')
    fields    = op.join(datadir, 'field.txt')
    encodings = op.join(datadir, 'encoding.txt')

    fields    = pd.read_csv(fields,    delimiter='\t')
    encodings = pd.read_csv(encodings, delimiter='\t')

    dcbase  = pd.DataFrame({'ID' : encodings['encoding_id']}).set_index('ID')
    varbase = pd.DataFrame({
        'ID'          : fields['field_id'],
        'Type'        : fields['value_type'].combine(fields['base_type'],
                                                     settype),
        'Description' : fields['title'],
        'DataCoding'  : fields['encoding_id'],
        'Instancing'  : fields['instance_id'],
    }).set_index('ID')

    return varbase, dcbase


def mergeTableFiles(base, fnames, what, dtypes, converters, columns):
    """Load and merge one or more table files.

    This function is called by :func:`loadVariableTable` to load the variable,
    data coding, and type table files.

    The variable and datacoding tables can be loaded from multiple files, with
    each file containing part of the full table. All provided files are merged
    into one table. The final table for a given set of files is the outer join
    on the index column (assumed to be the first column in each file), where
    non-na values in overlapping columns from later files will overwrite the
    values in earlier files.

    :arg base:       Table containing base information - used for the variable
                     and datacoding tables (see :func:`_loadTableBases`).

    :arg fnames:     List of files to load. If ``None``, the ``base`` table
                     is returned (or an empty table if a ``base`` is not
                     given).

    :arg what:       Name of the table files being loaded - used solely for log
                     messages

    :arg dtypes:     Dict containing ``{column : datatype}`` mappings

    :arg converters: Dict containing ``{column : convertfunc}`` mappings

    :arg columns:    Expected column names
    """

    idcol   = columns[0]
    columns = columns[1:]

    if fnames is None:
        fnames = []

    fnames = [f for f in fnames if f is not None]

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=pd.errors.ParserWarning)

        for f in fnames:

            log.debug('Loading %s table from %s', what, f)

            table = pd.read_csv(f, '\t',
                                index_col=0,
                                dtype=dtypes,
                                converters=converters)

            if base is None:
                base = table
                continue

            # Merge each file with an outer
            # join, so we retain all IDs and
            # columns defined across the
            # entire set of files.
            merged = base.merge(table,
                                how='outer',
                                on=idcol,
                                sort=True,
                                suffixes=('_x', '_y'))

            # Now we merge overlapping columns -
            # non-na values in later files take
            # precedence.
            for c in [c[:-2] for c in merged.columns if c.endswith('_x')]:
                bcolname        = c + '_x'
                tcolname        = c + '_y'
                bcol            = merged[bcolname]
                tcol            = merged[tcolname]
                notna           = tcol.notna()
                bcol.loc[notna] = tcol[notna]
                merged[c]       = bcol
                merged          = merged.drop(columns=[bcolname, tcolname])
            base = merged

    # no base, and no files
    if base is None:
        base = pd.DataFrame()

    # error if we have any
    # unrecognised columns
    for col in base.columns:
        if col not in columns:
            raise ValueError('Unrecognised column in table file {} - '
                             'should be {}, but file contained {}.'.format(
                                 fnames, columns, base.columns))

    # in-fill any columns that
    # were not provided
    for col in columns:
        if col not in base.columns:
            base[col] = pd.Series()

    return base


def sanitiseVariableTable(vartable, cols, dropAbsent):
    """Ensures that the variable table contains an entry for every
    variable in the input data.

    Called by :func:`loadVariableTable`.

    :arg vartable:   ``pandas.DataFrame`` containing the variable table.

    :arg cols:       Sequence of :class:`.Column` objects representing
                     the columns in the input data.

    :arg dropAbsent: If ``True``, entries in the table for variables which are
                     not in ``cols`` will be removed.

    :return:         A list of unknown :class:`.Column` objects, i.e.
                     representing variables which were not in the variable
                     table.
    """

    unknownVars = []

    # Make sure a placeholder entry is
    # present for any variables which are
    # not in the variable table, but which
    # are in the data file(s).
    for i, col in enumerate(cols):

        vid  = col.vid
        name = col.name

        if vid in vartable.index:
            continue

        unknownVars.append(col)
        addNewVariable(vartable, vid, name)

    # And the inverse - we can drop any
    # variables from the variable table
    # that are not in the data.
    if dropAbsent:
        vids = [c.vid for c in cols]
        vartable.drop([v for v in vartable.index if v not in vids],
                      inplace=True)
    return unknownVars


def mergeIntoVariableTable(vartable, cols, mapping):
    """Merge data from ``mapping`` into the variable table.

    Called by :func:`loadVariableTable`.

    :arg vartable: The variable table

    :arg cols:     Names of columns in the variable table

    :arg mapping:  Dict of ``{vid : values}`` mappings containing the
                   data to copy in.
    """

    onecol = isinstance(cols, str)
    if onecol:
        cols = [cols]

    # Ignore any variables that
    # are not in variable table
    vids   = list(mapping.keys())
    vin    = pd.Series(vids).isin(vartable.index)
    vids   = [v for i, v in enumerate(vids) if vin[i]]

    for vid in vids:
        vals = mapping[vid]

        if onecol:
            vals = [vals]

        for col, val in zip(cols, vals):
            vartable.at[vid, col] = val


def mergeDataCodingTable(vartable, dctable):
    """Merges information from the data coding table into the variable
    table.

    Called by :func:`loadVariableTable`.

    :arg vartable: The variable table.
    :arg dctable:  The data coding table.
    """

    with_datacoding = vartable['DataCoding'].notna()

    for field in ['NAValues', 'RawLevels', 'NewLevels']:
        mask    = vartable[field].isna() & with_datacoding
        newvals = vartable.loc[mask].merge(dctable,
                                           left_on='DataCoding',
                                           right_index=True,
                                           suffixes=('_v', '_dc'),
                                           copy=False)['{}_dc'.format(field)]
        vartable.loc[mask, field] = newvals


def mergeCleanFunctions(vartable, tytable, clean, typeClean, globalClean):
    """Merges custom clean functions into the variable table.

    Called by :func:`loadVariableTable`.

    :arg vartable:    The variable table.

    :arg tytable:     The type table

    :arg clean:       Dictionary of ``{vid : expr}`` mappings containing
                      cleaning functions to apply - this will override
                      any cleaning specified in the variable file, and
                      any cleaning specified in ``typeClean``.

    :arg typeClean:   Dictionary of ``{type : expr}`` mappings containing
                      cleaning functions to apply to all variables of a
                      specific type - this will override any cleaning
                      specified in the type file.

    :arg globalClean: Expression containing cleaning functions to
                      apply to every variable - this will be performed after
                      variable-specific cleaning in the variable table,
                      or specified via ``clean`` or ``typeClean``.
    """

    # Merge type-specific Clean
    # from the type table into
    # the variable table.
    for vid in vartable.index:

        if vid == 0:
            continue

        vtype = vartable.loc[vid, 'Type']
        pp    = vartable.loc[vid, 'Clean']

        # Override with typeClean if necessary
        if typeClean is not None and vtype in typeClean:
            tpp = convert_Process('cleaner', typeClean[vtype])
        elif vtype in tytable.index:
            tpp = collections.OrderedDict((tytable.loc[vtype, 'Clean']))
        else:
            continue

        # type cleaning is applied after
        # variable-specific cleaning
        if pd.isnull(pp): vartable.loc[[vid], 'Clean'] = [tpp]
        else:             vartable.loc[ vid,  'Clean'].update(tpp)

    # Override cleaning with expressions
    # that have been passed on the command line
    if clean is not None:
        clean = {vid : convert_Process('cleaner', expr)
                 for vid, expr in clean.items()}
        mergeIntoVariableTable(vartable, 'Clean', clean)

    # Add global cleaning to all variables
    if globalClean is not None:

        for vid in vartable.index:

            if vid == 0:
                continue

            pp  = vartable.loc[vid, 'Clean']
            gpp = convert_Process('cleaner', globalClean)

            # global cleaning is applied
            # after all other cleaning
            if pd.isnull(pp): vartable.loc[[vid], 'Clean'] = [gpp]
            else:             vartable.loc[ vid,  'Clean'].update(gpp)


def addNewVariable(vartable, vid, name, dtype=None, instancing=None):
    """Add a new row to the variable table.

    The ``instancing`` argument defines the meaning of the
    :attr:`.Column.visit` field for columns associated with this variable.
    The default value is ``2``, meaning that this variable may be associated
    with columns corresponding to measurements acquired at different UK
    BioBank assessments and imaging visits.  See
    https://biobank.ctsu.ox.ac.uk/crystal/schema.cgi?id=9 and
    https://biobank.ctsu.ox.ac.uk/crystal/schema.cgi?id=10 for more details.

    .. note:: If an entry for the specified ``vid`` already exists in
              ``vartable``, the ``name``, ``dtype`` and ``instancing``
              arguments are ignored and the existing information in
              ``vartable`` will take precedence.

    :arg vartable:   The variable table

    :arg vid:        Integer variable ID

    :arg name:       Variable name - used as the description

    :arg dtype:      ``numpy`` data type. If ``None``, the variable type
                     is set to :attr:`.util.CTYPES.unknown`.

    :arg instancing: Instancing code for the new variable - defaults to ``2``
    """

    # If an entry already exists
    # in the variable table, it
    # takes precedence
    if vid in vartable.index:
        dtype      = vartable.at[vid, 'Type']
        name       = vartable.at[vid, 'Description']
        instancing = vartable.at[vid, 'Instancing']

    else:
        # set dtype to something which
        # will cause the conditionals
        # to fall through
        if dtype is None: dtype = object
        else:             dtype = dtype.type

        # Assume that new variables
        # are associated with visits
        if instancing is None:
            instancing = 2

        if   issubclass(dtype, np.integer): dtype = util.CTYPES.integer
        elif issubclass(dtype, np.float):   dtype = util.CTYPES.continuous
        else:                               dtype = util.CTYPES.unknown

    vartable.loc[vid, 'Description'] = name
    vartable.loc[vid, 'Type']        = dtype
    vartable.loc[vid, 'Instancing']  = instancing


def loadProcessingTable(procfile=None,
                        skipProcessing=False,
                        prependProcess=None,
                        appendProcess=None,
                        **kwargs):
    """Loads the processing table from the given file.

    :arg procfile:       Path to the processing table file.

    :arg skipProcessing: If ``True``, the processing table is not loaded from
                         ``procfile``. The ``prependProcess`` and
                         ``appendProcess`` arguments are still applied.

    :arg prependProcess: Sequence of ``(varids, procstr)`` mappings specifying
                         processes to prepend to the beginning of the
                         processing table.

    :arg appendProcess:  Sequence of ``(varids, procstr)`` mappings specifying
                         processes to append to the end of the processing
                         table.

    All other keyword arguments are ignored.
    """

    if prependProcess is None: prependProcess = []
    if appendProcess  is None: appendProcess  = []

    if (procfile is not None) and (not skipProcessing):
        log.debug('Loading processing table from %s', procfile)
        proctable = pd.read_csv(procfile, '\t',
                                index_col=False,
                                skip_blank_lines=True,
                                comment='#',
                                converters=PROCTABLE_CONVERTERS)

    else:
        proctable = pd.DataFrame(columns=PROCTABLE_COLUMNS)

    # prepend/append custom
    # processes to the table
    proctable.index += len(prependProcess)
    for i, (vids, procs) in enumerate(prependProcess):
        vids  = convert_Process_Variable(vids)
        procs = convert_Process('processor', procs)
        proctable.loc[i, ['Variable', 'Process']] = [vids, procs]

    for i, (vids, procs) in enumerate(appendProcess, len(proctable.index)):
        vids  = convert_Process_Variable(vids)
        procs = convert_Process('processor', procs)
        proctable.loc[i, ['Variable', 'Process']] = [vids, procs]

    proctable.sort_index(inplace=True)

    return proctable


def loadCategoryTable(catfile=None, unknownVars=None):
    """Loads the category table from the given file.

    :arg catfile:     Path to the category file.
    :arg unknownVars: Sequence of :class:`.Column` objects representing
                      variables to add to an "unknown" category.
    """
    if catfile is not None:
        log.debug('Loading category table from %s', catfile)
        cattable = pd.read_csv(catfile,
                               '\t',
                               index_col=0,
                               dtype=CATTABLE_DTYPES,
                               converters=CATTABLE_CONVERTERS)
    else:
        cattable            = pd.DataFrame(columns=CATTABLE_COLUMNS[1:])
        cattable.index.name = CATTABLE_COLUMNS[0]

    # add an implicit "unknown" category
    # for any columns in the data file
    # which are unknown
    if unknownVars is not None:

        unknownVids = list(sorted(set([c.vid for c in unknownVars])))

        # unknown column already in table?
        umask = cattable['Category'] == 'unknown'

        if np.any(umask):
            idx         = np.where(umask)[0][0]
            idx         = cattable.index[idx]
            unknownVids = cattable.loc[idx, 'Variables'] + unknownVids
        else:
            idx = UNKNOWN_CATEGORY_ID

        cattable.loc[idx, 'Category']  = 'unknown'
        cattable.loc[idx, 'Variables'] = list(unknownVids)

    return cattable


def categoryVariables(cattable, categories):
    """Returns a list of variable IDs from ``cattable`` which correspond to
    the strings in ``categories``.

    :arg cattable:   The category table.
    :arg categories: Sequence of integer category IDs or label sub-strings
                     specifying the categories to return.
    :returns:        A list of variable IDs as strings.
    """

    allvars = []

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for cat in categories:

            catpat  = re.compile('({})'.format(cat), re.IGNORECASE)
            idmask  = cattable.index.isin([cat])
            lblmask = cattable['Category'].str.contains(catpat)
            catvars = cattable.loc[idmask | lblmask, 'Variables']

            if len(catvars) == 0:
                continue

            for c in catvars.iloc[0]:
                if c not in allvars:
                    allvars.append(c)

    return allvars


def columnTypes(vartable, columns):
    """Retrieves the type of each column in ``cols`` as listed in ``vartable``.
    Also identifies a suitable internal data type to use for each column where
    possible.

    :arg vartable: The variable table.

    :arg columnss: List of :class:`.Column` objects.

    :returns:      A tuple containing:

                    - A list containing the type for each column in ``cols`` -
                      an identifier from the :attr:`.util.CTYPES` enum.
                      Columns corresponding to a variable which is not in
                      the variable table is given a type of ``None``.

                    - A dict of ``{ column_name : dtype }`` mappings containing
                      a suitable internal data type to use for some columns.
    """

    vttypes = []
    dtypes  = {}

    for col in columns:

        vid  = col.vid
        name = col.name

        if vid not in vartable.index:
            vttypes.append(None)
            continue

        vttype = vartable.loc[vid, 'Type']
        dtype  = util.DATA_TYPES.get(vttype, None)

        vttypes.append(vttype)
        if dtype is not None:
            dtypes[name] = dtype

    return vttypes, dtypes


def identifyUnprocessedVariables(vartable,
                                 proctable,
                                 cattable,
                                 unclean):
    """Called by :func:`loadTables`. Identifies all variables which are in the
    data file(s), but which:

     - are uncategorised (not present in any categories in the category table),
       or
     - did not have any cleaning/processing specifically applied to them or to
       their data coding.

    Such variables might have been overlooked, so the user may need to be
    warned about them.

    :arg vartable:  Variable table
    :arg proctable: Processing table
    :arg cattable:  Category table
    :arg unclean:   List of :class:`.Column` objects represennting columns for
                    which there were no cleaning rules specified. Generated by
                    :func:`loadVariableTable`.
    :returns:       A list of variables which are not in any category, and do
                    not have any cleaning or processing rules applied.
    """

    unprocessed = []

    def isCategorised(col):
        def inCategory(catvars):
            return col.vid in catvars
        return cattable['Variables'].apply(inCategory).any()

    def isProcessed(col):
        def inProcess(procvars):
            return isinstance(procvars, list) and col.vid in procvars
        return proctable['Variable'].apply(inProcess).any()

    for c in unclean:
        if not (isCategorised(c) or isProcessed(c)):
            unprocessed.append(c)

    return unprocessed
