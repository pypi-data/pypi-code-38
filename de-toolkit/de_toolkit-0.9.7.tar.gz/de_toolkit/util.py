r'''
Usage:
    detk-util tidy [options] <counts_fn> <cov_fn>
    detk-util tidy-counts [options] <counts_fn> <cov_fn>
    detk-util tidy-covs [options] <counts_fn> <cov_fn>
'''

cmd_opts = {
        'tidy':r'''

Subset both the counts columns and column data rows by intersection, returning
new outputs for both. Note the tidied column data is not output by default, and
the user must specify the -p argument to obtain it.

Usage:
    detk-util tidy [options] <counts_fn> <cov_fn>

Options:
    -o FILE --output=FILE  Destination of tidied counts data [default: stdout]
    -p FILE --column-data-output=FILE  Destination of tidied column data
''',

        'tidy-counts':r'''

Subset and order the provided counts file columns according to the rows of the
provided column data file. Operation will fail if there are rows in the column
data file that do not exist as columns in the counts file.

Usage:
    detk-util tidy-counts [options] <counts_fn> <cov_fn>

Options:
    -o FILE --output=FILE  Destination of tidied counts data [default: stdout]
''',
        'tidy-covs':r'''

Subset and order the provided column data file rows according to the columns of
the provided ccounts data file. Operation will fail if there are columns in the
counts file that do not exist as rows in the column data file.


Usage:
    detk-util tidy-covs [options] <counts_fn> <cov_fn>

Options:
    -o FILE --output=FILE  Destination of tidied column data [default: stdout]
'''
}

from contextlib import contextmanager
from docopt import docopt
import logging
import pandas
import sys

from .common import (CountMatrix, CountMatrixFile, _cli_doc, set_logging,
        make_cli_count_obj, write_output)
from .patsy_lite import ModelError

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ.get('PATH','').split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

class Stub(Exception): pass
def stub(f) :
  def stub(*args,**kwargs) :
    raise Stub('Not yet implemented - {}.{}'.format(f.__module__,f.__name__))
  return stub

def main(argv=sys.argv) :

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts) :
        docopt(_cli_doc(__doc__))
    argv = argv[1:]
    cmd = argv[0]

    # add the common opts to the docopt strings
    cmd_opts_aug = {}
    for k,v in cmd_opts.items() :
        cmd_opts_aug[k] = _cli_doc(v)

    args = docopt(cmd_opts_aug[cmd],argv)
    count_obj = make_cli_count_obj(args)
    set_logging(args)
    logger.info('cmd: %s',' '.join(argv))

    if cmd == 'tidy' :
        logger.info('tidying counts...')

        out = count_obj.counts

        if args['--column-data-output'] :
            logger.info('...and covs to --column-data-output=%s',args['--column-data-output'])
            count_obj.column_data.to_csv(
                    args['--column-data-output'],
                    sep=args.get('--out-delim',',')
            )

    elif cmd in ('tidy-counts','tidy-covs') :
        logger.info('performing %s',cmd)

        args = docopt(cmd_opts_aug[cmd],argv)
        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        # read in the counts and covs so we can compare
        counts = pandas.read_csv(
                args['<counts_fn>'],
                index_col=0,
                sep=None,
                engine='python'
        )
        logger.info('shape of counts: %s',counts.shape)
        covs = pandas.read_csv(
                args['<cov_fn>'],
                index_col=0,
                sep=None,
                engine='python'
        )
        logger.info('shape of covs: %s',covs.shape)

        logger.info('shape of counts after merge: %s',count_obj.counts.shape)
        logger.info('counts columns lost: %s',counts.shape[1]-count_obj.counts.shape[1])

        logger.info('shape of covs after merge: %s',count_obj.column_data.shape)
        logger.info('cov rows lost: %s',covs.shape[1]-count_obj.column_data.shape[1])

        if cmd == 'tidy-counts' :
            # check to make sure the counts columns are a subset of the column
            # data rows
            if len(covs.index.difference(counts.columns)) != 0 :
                logger.error(Exception('tidy-counts requires that all row IDs in the '
                        'column data file exist as columns in the counts file.')
                )
                sys.exit(1)
            out = count_obj.counts

        elif cmd == 'tidy-covs' :
            # check to make sure the column data rows are a subset of the counts
            # columns
            if len(counts.columns.difference(covs.index)) != 0 :
                logger.error(Exception('tidy-covs requires that all column IDs in the '
                        'counts data file exist as rows in the column data file.')
                )
                sys.exit(1)
            out = count_obj.column_data

    write_output(out,args)

    logging.info('done')

if __name__ == '__main__' :
    main()
