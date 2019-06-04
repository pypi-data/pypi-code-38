#!/usr/bin/env python
#
# config.py - Parses command line arguments and configuration files.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains functions for parsing ``funpack`` command line
arguments and configuration files.
"""


import os.path         as op
import functools       as ft
import itertools       as it
import multiprocessing as mp
import                    sys
import                    shlex
import                    logging
import                    argparse
import                    collections
import numpy           as np

import funpack
import funpack.util           as util
import funpack.custom         as custom
import funpack.importing      as importing
import funpack.exporting      as exporting
import funpack.exporting_hdf5 as exporting_hdf5
import funpack.exporting_tsv  as exporting_tsv


log = logging.getLogger(__name__)


VERSION                    = funpack.__version__
DEFAULT_MERGE_AXIS         = importing.MERGE_AXIS
DEFAULT_MERGE_STRATEGY     = importing.MERGE_STRATEGY
DEFAULT_EXPORT_FORMAT      = exporting.EXPORT_FORMAT
AVAILABLE_MERGE_AXES       = importing.MERGE_AXIS_OPTIONS
AVAILABLE_MERGE_STRATEGIES = importing.MERGE_STRATEGY_OPTIONS
DEFAULT_COLUMN_PATTERN     = exporting.COLUMN_PATTERN
DEFAULT_TSV_SEP            = exporting_tsv.TSV_SEP
DEFAULT_HDF5_KEY           = exporting_hdf5.HDF5_KEY
DEFAULT_HDF5_STYLE         = exporting_hdf5.HDF5_STYLE
AVAILABLE_HDF5_STYLES      = exporting_hdf5.HDF5_STYLES
CLI_ARGUMENTS              = collections.OrderedDict((

    ('Inputs', [
        ((       'outfile',),        {}),
        ((       'infile',),         {'nargs'   : '+'}),
        (('e',   'encoding'),        {'action'  : 'append'}),
        (('l',   'loader'),          {'nargs'   : 2,
                                      'metavar' : ('FILE', 'LOADER'),
                                      'action'  : 'append'}),
        (('i',   'index'),           {'nargs'   : 2,
                                      'metavar' : ('FILE', 'INDEX'),
                                      'action'  : 'append'}),
        (('ma',  'merge_axis'),      {'choices' : AVAILABLE_MERGE_AXES,
                                      'default' : DEFAULT_MERGE_AXIS}),
        (('ms',  'merge_strategy'),  {'choices' : AVAILABLE_MERGE_STRATEGIES,
                                      'default' : DEFAULT_MERGE_STRATEGY}),
        (('cfg', 'config_file'),     {}),
        (('vf',  'variable_file'),   {'action'  : 'append'}),
        (('df',  'datacoding_file'), {'action'  : 'append'}),
        (('tf',  'type_file'),       {}),
        (('pf',  'processing_file'), {}),
        (('cf',  'category_file'),   {})]),

    ('Import options', [
        (('ia', 'import_all'),     {'action' : 'store_true'}),
        (('r',  'remove_unknown'), {'action' : 'store_true'}),
        (('s',  'subject'),        {'action' : 'append'}),
        (('v',  'variable'),       {'action' : 'append'}),
        (('co', 'column'),         {'action' : 'append'}),
        (('c',  'category'),       {'action' : 'append'}),
        (('vi', 'visit'),          {'action' : 'append'}),
        (('ex', 'exclude'),        {'action' : 'append'})]),

    ('Cleaning options', [
        (('sn',  'skip_insertna'),      {'action'  : 'store_true'}),
        (('scv', 'skip_childvalues'),   {'action'  : 'store_true'}),
        (('scf', 'skip_clean_funcs'),   {'action'  : 'store_true'}),
        (('sr',  'skip_recoding'),      {'action'  : 'store_true'}),
        (('nv',  'na_values'),          {'nargs'   : 2,
                                         'action'  : 'append',
                                         'metavar' : ('VID', 'NAVALUES')}),
        (('re',  'recoding'),           {'nargs'   : 3,
                                         'action'  : 'append',
                                         'metavar' : ('VID',
                                                      'RAWLEVELS',
                                                      'NEWLEVELS')}),
        (('cv',  'child_values'),       {'nargs'   : 3,
                                         'action'  : 'append',
                                         'metavar' : ('VID',
                                                      'EXPRS',
                                                      'VALUES')}),
        (('cl',  'clean'),              {'nargs'   : 2,
                                         'action'  : 'append',
                                         'metavar' : ('VID', 'EXPR')}),
        (('tc',  'type_clean'),         {'nargs'   : 2,
                                         'action'  : 'append',
                                         'metavar' : ('TYPE', 'EXPR')}),
        (('gc',  'global_clean'),       {'metavar' : 'EXPR'})]),

    ('Processing options', [
        (('sp',  'skip_processing'), {'action'  : 'store_true'}),
        (('ppr', 'prepend_process'), {'action'  : 'append',
                                      'nargs'   : 2,
                                      'metavar' : ('VARS', 'PROCS')}),
        (('apr', 'append_process'),  {'action'  : 'append',
                                      'nargs'   : 2,
                                      'metavar' : ('VARS', 'PROCS')})]),

    ('Export options', [
        (('f',    'format'),            {'default' : DEFAULT_EXPORT_FORMAT}),
        (('cp',   'column_pattern'),    {'default' : DEFAULT_COLUMN_PATTERN}),
        (('rc',   'rename_column'),     {'action'  : 'append',
                                         'nargs'   : 2,
                                         'metavar' : ('OLD_NAME', 'NEW_NAME')}),  # noqa
        (('oi',   'output_id_column'),  {}),
        (('edf',  'date_format'),       {'default' : 'default'}),
        (('etf',  'time_format'),       {'default' : 'default'}),
        (('nr',   'num_rows'),          {'type'    : int}),
        (('uf',   'unknown_vars_file'), {}),
        (('imf',  'icd10_map_file'),    {}),
        (('def',  'description_file'),  {}),
        (('sf',   'summary_file'),      {})]),

    ('TSV export options', [
        (('ts',  'tsv_sep'),            {'default' : DEFAULT_TSV_SEP}),
        (('tm',  'tsv_missing_values'), {'default' : ''}),
        (('nn',  'non_numeric_file'),   {}),
        (('tvf', 'tsv_var_format'),     {'nargs'   : 2,
                                         'metavar' : ('VID', 'FORMATTER'),
                                         'action'  : 'append'})]),

    ('HDF5 export options', [

        (('hk', 'hdf5_key'),   {'default' : DEFAULT_HDF5_KEY}),
        (('hs', 'hdf5_style'), {'default' : DEFAULT_HDF5_STYLE,
                                'choices' : AVAILABLE_HDF5_STYLES})]),

    ('Miscellaneous options', [
        (('V',  'version'),      {'action'  : 'version',
                                  'version' :
                                  '%(prog)s {}'.format(VERSION)}),
        (('d',  'dry_run'),      {'action' : 'store_true'}),
        (('nb', 'no_builtins'),  {'action' : 'store_true'}),
        (('lm', 'low_memory'),   {'action' : 'store_true'}),
        (('wd', 'work_dir'),     {}),
        (('lf', 'log_file'),     {}),
        (('nj', 'num_jobs'),     {'type'    : int,
                                  'default' : mp.cpu_count()}),
        (('pt', 'pass_through'), {'action'  : 'store_true'}),
        (('p',  'plugin_file'),  {'action'  : 'append',
                                  'metavar' : 'FILE'}),
        (('ow', 'overwrite'),    {'action'  : 'store_true'}),
        (('n',  'noisy'),        {'action'  : 'count'}),
        (('q',  'quiet'),        {'action'  : 'store_true'})])))


CLI_DESCRIPTIONS = {

    'Inputs' :
    'The --variable_file and --datacoding_file options can be used multiple\n'
    'times - all provided files will be merged into a single table using the\n'
    'variable/data coding IDs.',

    'Import options' :
    'Using the --import_all option will increase RAM and CPU requirements,\n'
    'as it forces every column to be loaded and processed. The purpose of\n'
    'this option is to allow the user to identify previously unknown\n'
    'columns that passed the processing steps (e.g. the sparsity test), and\n'
    'therefore may need to be looked at more closely. Intended to be used\n'
    'with the --unknown_vars_file export option.',

    'Export options' :
    'The --unknown_vars_file (only active if --import_all is also active)\n'
    'allows a file to be saved containing information about columns which\n'
    'were in the input data, but were either not in the variable table, or\n'
    'were uncategorised and did not have any cleaning/processing rules\n'
    'specified. It contains five columns - the column name, the originating\n'
    'input file, the reason the column is being included (either unknown\n'
    'or uncategorised/unprocessed), whether the column passed the processing\n'
    'stage (e.g. sparsity/redundancy checks), and whether the column was\n'
    'exported.',
}


CLI_ARGUMENT_HELP = {

    # Input options
    'outfile' : 'Location to store output data.',
    'infile'  : 'File(s) containing input data.',

    'encoding' :
    'Character encoding. A single encoding can be specified, or this option '
    'can be used multiple times, one for each input file.',

    'loader' :
    'Use custom loader for file. Can be used multiple times.',

    'index' :
    'Position of index column for file (starting from 0). Can be used '
    'multiple times. Defaults to 0.',

    'merge_axis' :
    'Axis to concatenate multiple input files along (default: "{}"). '
    'Options are "subjects"/"rows"/"0" or "variables"/"columns"/'
    '"1".'.format(DEFAULT_MERGE_AXIS),

    'merge_strategy' :
    'Strategy for merging multiple input files (default: "{}"). '
    'Options are "naive", "intersection"/"inner", or "union"/'
    '"outer".'.format(DEFAULT_MERGE_STRATEGY),

    'config_file' :
    'File containing default command line arguments.',

    'variable_file' :
    'File(s) containing rules for handling variables',

    'datacoding_file' :
    'File(s) containing rules for handling data codings.',

    'type_file' :
    'File containing rules for handling types.',

    'processing_file' :
    'File containing variable processing rules.',

    'category_file' :
    'File containing variable categories.',

    # Import options
    'import_all' :
    'Import and process all columns, and apply --variable/--category/'
    '--remove_unknown options after processing.',

    'remove_unknown' :
    'Remove variables which are not listed in variable table. Implied if '
    'variables are specified using --variable or --category.',

    'subject' :
    'Subject ID, range, comma-separated list, or file containing a list of '
    'subject IDs, or variable expression, denoting subjects to include. Can '
    'be used multiple times.',

    'variable' :
    'Variable ID, range, comma-separated list, or file containing a list of '
    'variable IDs, to import. Can be used multiple times. Implies '
    '--remove_unknown.',

    'column' :
    'Name of column to import, or file containing a list of column names. Can '
    'also be a glob-style wildcard pattern - columns with a name matching the '
    'pattern will be imported. Can be used multiple times. Implies '
    '--remove_unknown.',

    'category' :
    'Category ID or label to import. Can be used multiple times. Implies '
    '--remove_unknown.',

    'visit' :
    'Import this visit. Can be used multiple times. Allowable values are '
    '\'first\', \'last\', or a visit number.',

    'exclude' :
    'Subject ID, range, comma-separated list, or file containing a list of '
    'subject IDs specifying subjects to exclude. Can be used multiple times.',

    # Clean options
    'skip_insertna' :
    'Skip NA insertion.',
    'skip_childvalues' :
    'Skip child value replacement.',
    'skip_clean_funcs' :
    'Skip cleaning functions defined in variable table.',
    'skip_recoding' :
    'Skip raw->new level recoding.',

    'na_values' :
    'Replace these values with NA (overrides any NA values specified in '
    'variable table). Can be used multiple times. Values must be specified as '
    'a comma-separated list.',

    'recoding' :
    'Recode categorical variables (overrides any raw/new level recodings '
    'specified in variable table). Can be used multiple times. Raw and new '
    'level values must be specified as comma-separated lists.',

    'child_values' :
    'Replace NA with the given values where the given expressions evaluate '
    'to true (overrides any parent/child values specified in variable table). '
    'Can be used multiple times. Parent value expressions and corresponding '
    'child values must be specified as comma-separated lists.',

    'clean' :
    'Apply cleaning function(s) to variable (overrides any cleaning '
    'specified in variable table).',

    'type_clean' :
    'Apply clean function(s) to all variables of the specified type '
    '(overrides any cleaning specified in type table).',

    'global_clean' :
    'Apply cleaning function(s) to every variable (after variable-'
    'specific cleaning specified in variable table or via --clean).',

    # Processing options
    'skip_processing' :
    'Skip processing functions defined in processing table (but not '
    'those specified via --prepend_process and --append_process).',
    'prepend_process' :
    'Apply processing function(s) before processing defined in processing '
    'table.',
    'append_process' :
    'Apply processing function(s) after processing defined in processing '
    'table.',

    # Export options
    'format' :
    'Output file format (default: "{}").'.format(DEFAULT_EXPORT_FORMAT),

    'column_pattern' :
    'Pattern defining output column names (default: "{}").'.format(
        DEFAULT_COLUMN_PATTERN),

    'rename_column' :
    'Rename the given column instead of applying --column_pattern. Can '
    'be used multiple times',

    'output_id_column' :
    'Name of ID column in output file.',

    'date_format' :
    'Formatter to use for date variables (default: "default").',

    'time_format' :
    'Formatter to use for time variables (default: "default").',

    'num_rows' :
    'Number of rows to write at a time.',

    'unknown_vars_file' :
    'Save list of unknown variables/columns to file. Only applicable if '
    '--import_all is enabled.',

    'icd10_map_file' :
    'Save converted ICD10 code mappings to file',

    'description_file' :
    'Save descriptions of each column to file',

    'summary_file' :
    'Save summary of cleaning applied to each column to file',

    # TSV export options
    'tsv_sep'    :
    'Column separator string to use in output file (default: "{}")'.format(
        DEFAULT_TSV_SEP.replace('\t', '\\t')),
    'tsv_missing_values' :
    'String to use for missing values in output file (default: empty '
    'string).' ,
    'non_numeric_file' :
    'Export all non-numeric columns (after formatting) to this file instead '
    'of the primary output file.',
    'tsv_var_format' :
    'Apply custom formatter to the specified variable.',

    # HDF5 export options
    'hdf5_key'    :
    'Key/name to use for the HDF5 group (default: '
    '"{}").'.format(DEFAULT_HDF5_KEY),
    'hdf5_style'  :
    'HDF5 style to save as (default: "{}").'.format(DEFAULT_HDF5_STYLE),

    # Miscellaneous options
    'version'      : 'Print version and exit.',
    'dry_run'      : 'Print a summary of what would happen and exit.',
    'no_builtins'  : 'Do not use the built in variable or data coding tables.',
    'low_memory'   : 'Store intermediate results on disk, rather than in RAM. '
                     'Use this flag on systems which cannot store the full '
                     'data set in RAM. ',
    'work_dir'     : 'Directory to store intermediate files (default: '
                     'temporary directory). Only relevant when using '
                     '--low_memory.',
    'log_file'     : 'Save log messages to file.',
    'num_jobs'     : 'Maximum number of jobs to run in parallel. '
                     '(default: {}).'.format(mp.cpu_count()),
    'pass_through' : 'Do not perform any cleaning or processing on the data - '
                     'implies --skip_insertna, --skip_childvalues, '
                     '--skip_clean_funcs, --skip_recoding, and '
                     '--skip_processing.',
    'plugin_file'  : 'Path to file containing custom funpack plugins. Can be '
                     'used multiple times.',
    'overwrite'    : 'Overwrite output file if it already exists',
    'noisy'        : 'Print debug statements. Can be used up to three times.',
    'quiet'        : 'Be quiet.',
}


def makeEpilog():
    """Generates an epilog for the command line help.

    The epilog contains an overview of available plugin functions.
    """

    def genTable(pluginType):
        plugins = custom.listPlugins(pluginType)
        descs   = []

        # The first two lines of all plugin function
        # docstrings are assumed to be:
        #   - function signature
        #   - one line description
        for p in plugins:
            try:
                desc = custom.get(pluginType, p).__doc__.split('\n')
                sig  = desc[0]
                desc = desc[1]
                descs.append((sig, desc))
            except Exception:
                descs.append(('n\a', None))

        maxpluginlen = max([len(p) for p in plugins])

        lines = []
        fmt   = '  - {{:{}s}}  {{}}'.format(maxpluginlen)

        for p, d in zip(plugins, descs):
            sig, desc = d
            lines.append(fmt.format(p, sig))
            if desc is not None:
                lines.append('{}  {}'.format(' ' * maxpluginlen, desc))

        return '\n'.join(lines)

    epilog = 'Available cleaning routines:'   + '\n'   + \
             genTable('cleaner')              + '\n\n' + \
             'Available processing routines:' + '\n'   + \
             genTable('processor')            + '\n'

    return epilog


@ft.lru_cache()
def makeParser(include=None, exclude=None):
    """Creates and returns an ``argparse.ArgumentParser`` for parsing
    ``funpack`` command line arguments.

    :arg include: Configure the parser so it only includes the specified
                  arguments.

    :arg exclude: Configure the parser so it excludes the specified
                  arguments - this overrides ``include``.
    """

    parser = argparse.ArgumentParser(
        'funpack',
        allow_abbrev=False,
        epilog=makeEpilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    helps  = CLI_ARGUMENT_HELP
    descs  = CLI_DESCRIPTIONS

    for group, args in CLI_ARGUMENTS.items():

        desc  = descs.get(group, None)
        group = parser.add_argument_group(group, description=desc)

        for arg, kwargs in args:

            name = arg[-1]

            if exclude is not None and name     in exclude: continue
            if include is not None and name not in include: continue

            if len(arg) == 2:
                arg = ('-{}'.format(arg[0]), '--{}'.format(arg[1]))

            group.add_argument(*arg, help=helps[name], **kwargs)

    return parser


def sanitiseArgs(argv):
    """Sanitises command-line arguments to work around a bug in ``argparse``.

    The ``argparse`` module does not work with non-numeric optional argument
    values that begin with a hyphen, as it thinks that they are argument names
    (see https://bugs.python.org/issue9334).

    This function searches for relevant optional argument names, and prepends
    a space to their values to make sure that ``argparse`` doesn't fall over.

    :arg argv: Command-line arguments
    :returns:  Sanitised command-line arguments
    """
    argv       = list(argv)
    toSanitise = [( '-nv',           [1]),
                  ('--na_values',    [1]),
                  ( '-re',           [1, 2]),
                  ('--recoding',     [1, 2]),
                  ( '-cv',           [2]),
                  ('--child_values', [2])]

    for arg, idxs in toSanitise:

        try:               argidx = argv.index(arg)
        except ValueError: continue

        for i in idxs:

            i   = i + 1 + argidx
            val = argv[i]

            if val.startswith('-'):
                argv[i] = ' ' + val

    return argv


def parseArgsWithConfigFile(argv=None):
    """Checks the command line arguments to see if a configuration file has
    been specified. If so, loads the arguments in the configuration file,
    and then parses the rest of the command line arguments.

    :returns: see :func:`parseArgs`.
    """

    if argv is None:
        argv = sys.argv[1:]

    argv    = sanitiseArgs(argv)
    cfgfile = None

    if '-cfg' in argv or '--config_file' in argv:
        cfgparser = makeParser('config_file')
        cfgfile   = cfgparser.parse_known_args(argv)[0].config_file

    if cfgfile is not None: namespace = loadConfigFile(cfgfile)
    else:                   namespace = None

    return parseArgs(argv, namespace)


def parseArgs(argv=None, namespace=None):
    """Parses ``funpack`` command line arguments.

    :arg argv:      List of arguments to parse.
    :arg namespace: Existing ``argparse.Namespace`` - if not provided, an
                    empty one will be created.
    :returns:       A tuple containing:
                     - an ``argparse.Namespace`` object containing the parsed
                       command-line arguments.
                     - A list of the original arguments that were parsed.
    """

    if argv is None:
        argv = sys.argv[1:]

    argv = sanitiseArgs(argv)
    args = makeParser().parse_args(argv, namespace)

    # error if output file exists
    if (not args.dry_run) and (not args.overwrite) and op.exists(args.outfile):
        print('Output file already exists, and --overwrite was not '
              'specified!')
        sys.exit(1)

    # make input files absolute
    args.infile = [op.realpath(f) for f in args.infile]

    if args.pass_through:
        args.skip_insertna    = True
        args.skip_childvalues = True
        args.skip_clean_funcs = True
        args.skip_recoding    = True
        args.skip_processing  = True

    # the importing.loadData function accepts
    # either a single encoding, or one encoding
    # for each data file.
    if args.encoding is not None:
        if len(args.encoding) == 1:
            args.encoding = args.encoding[0]
        elif len(args.encoding) != len(args.infile):
            raise ValueError('Wrong number of encodings specified - specify '
                             'either one encoding, or one encoding for each '
                             'input file.')

    # parallelisation only allowed
    # in low_memory mode
    if not args.low_memory:
        args.num_jobs = 0

    # turn loaders into dict of { absfile : name } mappings
    if args.loader is not None:
        args.loader = {op.realpath(f) : n for f, n in args.loader}

    # turn index indices into dict of { file : index } mappings
    if args.index is not None:
        args.index = {op.realpath(f) : int(i) for f, i in args.index}

    # turn formatters into dict of { vid : name } mappings
    if args.tsv_var_format is not None:

        tsv_var_format = {}

        for i, (v, n) in enumerate(args.tsv_var_format):

            # Formatters should be set on integer
            # variable IDs. But we allow non-integers
            # to pass through, as the exportData
            # function will also check against column
            # names.
            try:               v = int(v)
            except ValueError: pass

            tsv_var_format[v] = n

        args.tsv_var_format = tsv_var_format

    # turn --subject/--variable/--exclude
    # arguments into lists of IDs. If
    # error is True, an error is raised on
    # unparseable arguments.
    def replaceIDs(things, error=True):
        newthings = []
        failed    = []
        for i, thing in enumerate(things):

            # --subject/--variable/--exclude args
            # may be may be a file name containing
            # a list of IDs
            if op.exists(thing):
                with open(thing, 'rt') as f:
                    parsed = f.read().split()
                    parsed = [int(t.strip()) for t in parsed]

            else:
                # Or they may be an ID or matlab-style
                # start[:step[:stop]] range, both handled
                # by the parseMatlabRange function.
                try:               parsed = util.parseMatlabRange(thing)
                except ValueError: parsed = None

                # Or they may be a comma-separated
                # list of IDs
                if parsed is None:
                    try:
                        parsed = [int(v) for v in thing.split(',')]

                    # --subject may also be an expression,
                    # so if error is False, and the range/
                    # list parses fail, we pass the argument
                    # through. Otherwise we propagate the
                    # error.
                    except ValueError:
                        if error:
                            raise

                if parsed is None:
                    failed.append(thing)
                    continue

            for t in parsed:
                if t not in newthings:
                    newthings.append(t)

        if len(newthings) == 0: newthings = None
        if len(failed)    == 0: failed    = None

        return newthings, failed

    # variable/exclude is transformed into
    # a list of integer IDs, but subject is
    # transformed into a tuple containing
    # ([ID], [exprStr])
    if args.noisy    is     None: args.noisy    = 0
    if args.quiet:                args.noisy    = 0
    if args.subject  is not None: args.subject  = replaceIDs(args.subject,
                                                             False)
    else:                         args.subject  = None, None
    if args.variable is not None: args.variable = replaceIDs(args.variable)[0]
    if args.exclude  is not None: args.exclude  = replaceIDs(args.exclude)[0]

    # The column option accepts
    # column names, or a file
    # containing column names
    def loadIfExists(path):
        if op.exists(path):
            with open(path, 'rt') as f:
                items = f.readlines()
        else:
            items = [path]
        return [i.strip() for i in items]

    if args.column is not None:
        args.column = list(it.chain(*[loadIfExists(c) for c in args.column]))

    # visits are restricted using the
    # keepVisits cleaning function
    if args.visit is not None:
        visit = []
        for v in args.visit:
            if v in ('first', 'last'): visit.append('"{}"'.format(v))
            else:                      visit.append(str(v))

        visit = 'keepVisits({})'.format(','.join(visit))

        if args.global_clean is None: args.global_clean  =       visit
        else:                         args.global_clean += ',' + visit

    # If variables/categories/columns are
    # explicitly specified, remove_unknown
    # is implied.
    if any((args.variable is not None,
            args.category is not None,
            args.column   is not None)):
        args.remove_unknown = True

    # categories can be specified
    # either by name or by ID -
    # convert the latter to integers.
    if args.category is not None:
        for i, c in enumerate(args.category):
            try:               args.category[i] = int(c)
            except ValueError: continue

    # convert rename_column from a sequence of
    # [(oldname, newname)] pairs into a dict of
    # { oldname : newname } mappings.
    if args.rename_column is not None:
        args.rename_column = dict(args.rename_column)

    def numlist(s):
        return np.fromstring(s, sep=',', dtype=np.float)

    # convert na_values from a sequence of [(varid, str)]
    # pairs into a dict of {varid : [value]} mappings
    if args.na_values is not None:
        args.na_values = {int(vid) : numlist(values)
                          for vid, values in args.na_values}

    # Convert recoding from a sequence of [(varid, rawlevels, newlevels)]
    # tuples to a dict of {varid : (rawlevels, newlevels)} mappings
    if args.recoding is not None:
        args.recoding = {int(vid) : (numlist(rawlevels), numlist(newlevels))
                         for vid, rawlevels, newlevels in args.recoding}

    # Convert child_values from a sequence of
    # [(varid, exprs, values)] tuples to a dict of
    # {varid : ([exprs], [values])} mappings
    if args.child_values is not None:
        args.child_values = {int(vid) : (exprs, numlist(values))
                             for vid, exprs, values in args.child_values}

    # convert clean from a sequence of [(varid, expr)]
    # pairs into a dict of {varid : expr} mappings.
    if args.clean is not None:
        args.clean = {int(vid) : expr for vid, expr in args.clean}

    # convert type_clean from a sequence of [(type, expr)]
    # pairs into a dict of {type : expr} mappings.
    if args.type_clean is not None:
        args.type_clean = {util.CTYPES[t] : e for t, e in args.type_clean}

    # The variable_file, datacoding_file, type_file,
    # processing_file, and category_file options
    # can be specified relative to funpackdir
    configdir = op.join(op.dirname(__file__), 'configs')

    def fixPath(f):

        if f is None:
            return f

        options = [
            f,
            op.join(configdir, f),
            op.join(configdir, f.replace('.', op.sep) + '.tsv')
        ]

        for o in options:
            if op.exists(o):
                return o

        # if the fixed version does not
        # exist, allow processing to
        # continue - it will fail later on.
        return f

    if args.variable_file is not None:
        args.variable_file = [fixPath(f) for f in args.variable_file]
    if args.datacoding_file is not None:
        args.datacoding_file = [fixPath(f) for f in args.datacoding_file]

    args.type_file       = fixPath(args.type_file)
    args.processing_file = fixPath(args.processing_file)
    args.category_file   = fixPath(args.category_file)

    return args, argv


def loadConfigFile(cfgfile):
    """Loads arguments from the given configuration file, returning an
    ``argparse.Namespace`` object.
    """

    argv = []

    # If the specified config file does
    # not exist, assume it is a reference
    # to a built-in config file
    if not op.exists(cfgfile):
        if not cfgfile.endswith('.cfg'):
            cfgfile = cfgfile + '.cfg'
        moddir   = op.dirname(op.abspath(__file__))
        cfgfile = op.join(moddir, 'configs', cfgfile)

    log.debug('Loading arguments from configuration file %s', cfgfile)

    with open(cfgfile, 'rt') as f:
        lines = [line.strip() for line in f.readlines()]
        lines = [line         for line in lines if line != '']
        lines = [line         for line in lines if not line.startswith('#')]

    for line in lines:
        words        = list(shlex.split(line))
        name, values = words[0], words[1:]

        argv.append('--{}'.format(name))
        argv.extend(values)

    argv = sanitiseArgs(argv)

    return makeParser(exclude=('outfile', 'infile')).parse_args(argv)
