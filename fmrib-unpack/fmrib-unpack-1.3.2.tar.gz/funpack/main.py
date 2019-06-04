#!/usr/bin/env python
#
# main.py - funpack entry point
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains the ``funpack`` entry point. """


import multiprocessing     as mp
import                        sys
import                        shutil
import                        logging
import                        fnmatch
import                        tempfile
import                        warnings
import                        datetime
import                        calendar

import pandas              as pd

import funpack
import funpack.util        as util
import funpack.icd10       as icd10
import funpack.config      as config
import funpack.custom      as custom
import funpack.dryrun      as dryrun
import funpack.cleaning    as cleaning
import funpack.importing   as importing
import funpack.exporting   as exporting
import funpack.hierarchy   as hierarchy
import funpack.processing  as processing
import funpack.loadtables  as loadtables


log = logging.getLogger(__name__)


def main(argv=None):
    """``funpack`` entry point. """

    # Make sure built in plugins are
    # registered, as they are queried
    # in the command-line help. Set
    # logging to critical until we've
    # parsed command-line args.
    logging.getLogger().setLevel(logging.CRITICAL)
    custom.registerBuiltIns()

    args, argv = config.parseArgsWithConfigFile(argv)
    date = datetime.date.today()

    # Now that args are passed,
    # we can set up logging properly.
    configLogging(args)

    log.info('funpack %s', funpack.__version__)
    log.info('Date: %s (%s)', date.today(), calendar.day_name[date.weekday()])
    log.info('Command-line arguments %s', ' '.join(argv))
    log.debug('Running with the following options')
    for name, val in args.__dict__.items():
        if val is not None:
            val = str(val)
            if len(val) <= 30: log.debug('  %s: %s',    name, val)
            else:              log.debug('  %s: %s...', name, val[:30])

    # Re-load any custom plugins
    # that have been specified.
    custom.registerBuiltIns()

    if args.plugin_file is not None:
        for p in args.plugin_file:
            custom.loadPluginFile(p)

    # error if any loaders/formats are
    # invalid (we can only perform this
    # check after plugins have been
    # loaded)
    if args.loader is not None:
        for f, l in args.loader.items():
            if not custom.exists('loader', l):
                raise ValueError('Unknown loader {} [{}]'.format(l, f))
    if not custom.exists('exporter', args.format):
        raise ValueError('Unknown output format {}'.format(args.format))
    if args.date_format is not None and \
       not custom.exists('formatter', args.date_format):
        raise ValueError('Unknown date format {}'.format(args.date_format))
    if args.time_format is not None and \
       not custom.exists('formatter', args.time_format):
        raise ValueError('Unknown time format {}'.format(args.time_format))
    if args.tsv_var_format is not None:
        for v, f in args.tsv_var_format.items():
            if not custom.exists('formatter', f):
                raise ValueError('Unknown formatter {} [{}]'.format(f, v))

    if args.num_jobs > 1:
        log.debug('Running up to %i jobs in parallel', args.num_jobs)
        pool = mp.Pool(args.num_jobs)
        mgr  = mp.Manager()
    else:
        pool = None
        mgr  = None

    if args.work_dir is None: workdir = tempfile.mkdtemp(prefix='funpack')
    else:                     workdir = args.work_dir

    try:
        with util.timed(None, log, fmt='Total time: %s (%+iMB)'):

            dtable, unknowns, unprocessed, drop = doImport(args, pool, mgr)

            if args.dry_run:
                dryrun.doDryRun(dtable, unknowns, unprocessed, drop, args)
            else:
                doCleanAndProcess(  dtable, args)
                finaliseColumns(    dtable, args, unknowns, unprocessed)
                doExport(           dtable, args)
                doICD10Export(              args)
                doDescriptionExport(dtable, args)
                doSummaryExport(    dtable, args)

    finally:
        # shutdown the pool gracefully
        if pool is not None:
            pool.close()
            pool.join()
            pool = None

        if args.work_dir is None:
            shutil.rmtree(workdir)
    return 0


def doImport(args, pool, mgr):
    """Data import stage.

    :arg args: :class:`argparse.Namespace` object containing command line
               arguments
    :arg pool: :class:`multiprocessing.Pool` object for parallelisation (may
               be ``None``)
    :arg mgr:  :class:`multiprocessing.Manager` object for parallelisation (may
               be ``None``)

    :returns:  A tuple containing:

                - A :class:`.DataTable` containing the data
                - A sequence of :class:`.Column` objects representing the
                  unknown columns.
                - A sequence of :class:`.Column` objects representing columns
                  which are uncategorised, and have no processing or cleaning
                  rules specified on them.
    """

    with util.timed('Table import', log):
        vartable, proctable, cattable, unknowns, unprocessed = \
            loadtables.loadTables(
                args.infile,
                args.variable_file,
                args.datacoding_file,
                args.type_file,
                args.processing_file,
                args.category_file,
                noBuiltins=args.no_builtins,
                naValues=args.na_values,
                childValues=args.child_values,
                recoding=args.recoding,
                clean=args.clean,
                typeClean=args.type_clean,
                globalClean=args.global_clean,
                skipProcessing=args.skip_processing,
                prependProcess=args.prepend_process,
                appendProcess=args.append_process,
                sniffers=args.loader,
                indexes=args.index)

        for u in unknowns:
            log.warning('Variable %s [file %s, column %s, assigned variable '
                        'ID %s] is unknown - consider adding it to your '
                        'variable table.',
                        u.name, u.datafile, u.index, u.vid)
        for u in unprocessed:
            log.warning('Variable %s [file %s, column %s, assigned variable '
                        'ID %s] is uncategorised and does not have any '
                        'cleaning or processing rules set.',
                        u.name, u.datafile, u.index, u.vid)

    subjects, exprs = args.subject

    if not args.dry_run and args.import_all:
        variables     = None
        categories    = None
        columns       = None
        removeUnknown = None
    else:
        variables     = args.variable
        categories    = args.category
        columns       = args.column
        removeUnknown = args.remove_unknown

    # Import data
    with util.timed('Data import', log):
        dtable, drop = importing.importData(
            datafiles=args.infile,
            vartable=vartable,
            proctable=proctable,
            cattable=cattable,
            variables=variables,
            colnames=columns,
            categories=categories,
            subjects=subjects,
            encoding=args.encoding,
            indexes=args.index,
            unknownVars=unknowns,
            removeUnknown=removeUnknown,
            mergeAxis=args.merge_axis,
            mergeStrategy=args.merge_strategy,
            loaders=args.loader,
            lowMemory=args.low_memory,
            workDir=args.work_dir,
            pool=pool,
            mgr=mgr,
            dryrun=args.dry_run)

    # Exclude subjects
    if (not args.dry_run) and (exprs is not None or args.exclude is not None):
        with util.timed('Subject exclusion', log):
            importing.removeSubjects(
                dtable,
                exclude=args.exclude,
                exprs=exprs)

    return dtable, unknowns, unprocessed, drop


def doCleanAndProcess(dtable, args):
    """Data cleaning and processing stage.

    :arg dtable: :class:`.DataTable` containing the data
    :arg args:   :class:`argparse.Namespace` object containing command line
                 arguments
    :arg pool:   :class:`multiprocessing.Pool` object for parallelisation (may
                 be ``None``)
    """

    # Clean data (it times each step individually)
    cleaning.cleanData(
        dtable,
        skipNAInsertion=args.skip_insertna,
        skipCleanFuncs=args.skip_clean_funcs,
        skipChildValues=args.skip_childvalues,
        skipRecoding=args.skip_recoding)

    # Process data
    with util.timed('Data processing', log):
        processing.processData(dtable)


def finaliseColumns(dtable, args, unknowns, unprocessed):
    """Called after processing and before export.

    If the ``--import_all`` argument was used (which forces all columns
    to be loaded and processed), this function applies the ``--variable``,
    ``--category`` and ``--remove_unknown`` arguments. to the processed
    data.

    If the ``--unknown_vars_file`` argument was used, the unknown/unprocessed
    columns are saved out to a file.

    :arg dtable:      :class:`.DataTable` containing the data
    :arg args:        :class:`argparse.Namespace` object containing command
                      line arguments
    :arg unknowns:    List of :class:`.Column` objects representing the
                      unknown columns.
    :arg unprocessed: A sequence of :class:`.Column` objects representing
                      columns which are uncategorised, and have no processing
                      or cleaning rules specified on them.
    """

    if not args.import_all:
        return

    # get a list of variables requested
    # via --variable or --category (will
    # be None if no requests)
    vids = importing.restrictVariables(
        dtable.cattable, args.variable, args.category)

    # args.remove_unknown is only applied
    # if variables/columns were not already
    # restricted by args.variable,
    # args.category, and or args.column
    removeUnknown = all((vids is None,
                         args.remove_unknown,
                         args.column is None,
                         len(unknowns) > 0))

    # apply removeUnknown
    if removeUnknown:
        vids  = dtable.variables
        uvids = set([c.vid for c in unknowns])
        for vid in list(vids):
            if vid in uvids:
                vids.remove(vid)

    # apply column patterns
    if args.column is not None:
        remove = []
        for col in list(dtable.allColumns[1:]):
            hits = [fnmatch.fnmatch(col.name, pat) for pat in args.column]
            if not any(hits):
                remove.append(col)
        dtable.removeColumns(remove)

    # remove/reorder variables
    allcols = set([c.name for c in dtable.allColumns])
    if vids is None:
        finalcols = allcols
    else:
        vids = [vid for vid in vids if dtable.present(vid)]
        dtable.order(vids)
        finalcols = set([c.name for c in dtable.allColumns])

    # Save unknown/unprocessed vars list to file
    # columns:
    #  - name      - column name
    #  - file      - originating input file
    #  - class     - unknown or uncategorised/unprocessed
    #  - processed - whether column passed processing
    #  - exported  - whether column was exported
    if args.unknown_vars_file is not None:
        allunknowns = list(unknowns + unprocessed)
        names       = [    u.name               for u in allunknowns]
        files       = [    u.datafile           for u in allunknowns]
        classes     = ['unknown'     for u in unknowns] + \
                      ['unprocessed' for u in unprocessed]
        processed   = [int(u.name in allcols)   for u in allunknowns]
        exported    = [int(u.name in finalcols) for u in allunknowns]
        rows        = ['{}\t{}\t{}\t{}\t{}'.format(n, f, c, p, e)
                       for n, f, c, p, e
                       in zip(names, files, classes, processed, exported)]

        log.debug('Saving unknown/unprocessed variables to %s',
                  args.unknown_vars_file)

        try:
            with open(args.unknown_vars_file, 'wt') as f:
                f.write('name\tfile\tclass\tprocessed\texported\n')
                f.write('\n'.join(rows))

        except Exception as e:
            log.warning('Error saving unknown variables to {}: '
                        '{}'.format(args.unknown_vars_file, e),
                        exc_info=True)


def doExport(dtable, args):
    """Data export stage.

    :arg dtable: :class:`.DataTable` containing the data
    :arg args:   :class:`argparse.Namespace` object containing command line
                 arguments
    """

    # Output data. Re-order subjects,
    # but only if no subject inclusion
    # expressions were used.
    subjects, exprs = args.subject

    if exprs is not None:
        subjects = None

    with util.timed('Data export', log):
        exporting.exportData(
            dtable,
            args.outfile,

            # General export options
            colpat=args.column_pattern,
            colmap=args.rename_column,
            idcol=args.output_id_column,
            fileFormat=args.format,
            dateFormat=args.date_format,
            timeFormat=args.time_format,
            numRows=args.num_rows,
            subjects=subjects,

            # TSV options
            sep=args.tsv_sep,
            missingValues=args.tsv_missing_values,
            formatters=args.tsv_var_format,
            nonNumericFile=args.non_numeric_file,

            # HDF5 options
            key=args.hdf5_key,
            style=args.hdf5_style)


def doICD10Export(args):
    """If a ``--icd10_map_file`` has been specified, the ICD10 codes present
    in the data (and their converted values) are saved out to the file.
    """
    if args.icd10_map_file is None:
        return

    with util.timed('ICD10 mapping export', log):
        try:
            ihier = hierarchy.getHierarchyFilePath(name='icd10')
            ihier = hierarchy.loadHierarchyFile(ihier)
            icd10.saveCodes(args.icd10_map_file, ihier)

        except Exception as e:
            log.warning('Failed to export ICD10 mappings: {}'.format(e),
                        exc_info=True)


def doDescriptionExport(dtable, args):
    """If a ``--description_file`` has been specified, a description for every
    column is saved out to the file.
    """
    if args.description_file is None:
        return

    with util.timed('Description export', log):
        cols = dtable.allColumns[1:]

        try:
            with open(args.description_file, 'wt') as f:
                for col in cols:
                    desc = generateDescription(dtable, col)
                    f.write('{}\t{}\n'.format(col.name, desc))

        except Exception as e:
            log.warning('Failed to export descriptions: {}'.format(e),
                        exc_info=True)


def generateDescription(dtable, col):
    """Called by :func:`doDescriptionExport`. Generates and returns a
    suitable description for the given column.

    :arg dtable: :class:`.Datatable` instance
    :arg col:    :class:`.Column` instance
    """
    vartable = dtable.vartable
    desc     = vartable.loc[col.vid, 'Description']

    if pd.isna(desc) or (desc == col.name):
        desc = 'n/a'

    # If metadata has been added to the column,
    # we add it to the description. See the
    # binariseCategorical processing function
    # for an example of this.
    if col.metadata is not None:
        suffix = ' ({})'.format(col.metadata)
    else:
        suffix = ' ({}.{})'.format(col.visit, col.instance)

    return '{}{}'.format(desc, suffix)


def doSummaryExport(dtable, args):
    """If a ``--summary_file`` has been specified, a summary of the cleaning
    steps that have been applied to each variable are saved out to the file.
    """
    if args.summary_file is None:
        return

    vartable = dtable.vartable
    vids     = sorted(dtable.variables)[1:]
    sum     = pd.DataFrame(columns=['ID', 'NAValues',
                                     'RawLevels', 'NewLevels',
                                     'ParentValues', 'ChildValues',
                                     'Clean', 'Flags']).set_index('ID')

    with util.timed('Summary export', log):
        for vid in vids:
            sum.at[vid, 'NAValues']     = vartable.at[vid, 'NAValues']
            sum.at[vid, 'RawLevels']    = vartable.at[vid, 'RawLevels']
            sum.at[vid, 'NewLevels']    = vartable.at[vid, 'NewLevels']
            sum.at[vid, 'ParentValues'] = vartable.at[vid, 'ParentValues']
            sum.at[vid, 'ChildValues']  = vartable.at[vid, 'ChildValues']

            clean = vartable.at[vid, 'Clean']
            if pd.notna(clean):
                sum.at[vid, 'Clean'] = list(clean.values())

            flagstr  = []
            cols     = dtable.columns(vid)
            colflags = {c : dtable.getFlags(c) for c in cols}
            flags    = set.union(*colflags.values())

            for flag in flags:
                if all([flag in colflags[c] for c in cols]):
                    flagstr.append(flag)
                else:
                    names = [c.name for c in cols if flag in colflags[c]]
                    flagstr.append('{} [{}]'.format(flag, ', '.join(names)))

            sum.at[vid, 'Flags'] = ';'.join(flagstr)

        sum.to_csv(args.summary_file, sep='\t')


def configLogging(args):
    """Configures ``funpack`` logging.

    :arg args: ``argparse.Namespace`` object containing parsed command line
               arguments.
    """

    # Custom log handler which
    # colours messages
    class LogHandler(logging.StreamHandler):

        def emit(self, record):

            levelno = record.levelno

            if   levelno >= logging.WARNING:  colour = '\x1b[31;1m'
            elif levelno >= logging.INFO:     colour = '\x1b[39;1m'
            elif levelno >= logging.DEBUG:    colour = '\x1b[90;1m'
            else:                             colour = ''

            # Reset terminal attributes
            # after each message.
            record.msg = '{}{}\x1b[0m'.format(colour, record.msg)

            return super(LogHandler, self).emit(record)

    logger = logging.getLogger('funpack')
    fmt    = logging.Formatter('%(asctime)s '
                               '%(levelname)8.8s '
                               '%(filename)20.20s '
                               '%(lineno)4d: '
                               '%(funcName)-15.15s - '
                               '%(message)s',
                               '%H:%M:%S')

    if args.log_file is None: handler = LogHandler()
    else:                     handler = logging.FileHandler(args.log_file)

    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # configure verbosity
    if   args.quiet:      loglevel = logging.CRITICAL
    elif args.noisy == 0: loglevel = logging.INFO
    else:                 loglevel = logging.DEBUG

    logging.getLogger('funpack').setLevel(loglevel)

    if args.quiet or args.noisy < 3:
        warnings.filterwarnings('ignore',  module='pandas')
        warnings.filterwarnings('ignore',  module='numpy')
        warnings.filterwarnings('ignore',  module='tables')

    if args.noisy == 1:
        makequiet = ['funpack.expression',
                     'funpack.custom',
                     'funpack.cleaning_functions',
                     'funpack.processing_functions']
    elif args.noisy == 2:
        makequiet = ['funpack.expression',
                     'funpack.custom']
    else:
        makequiet = []

    for mod in makequiet:
        logging.getLogger(mod).setLevel(logging.INFO)


if __name__ == '__main__':
    sys.exit(main())
