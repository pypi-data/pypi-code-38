r'''
Usage:
    detk-transform plog [options] <counts_fn>
    detk-transform vst [options] <counts_fn>
    detk-transform rlog [options] <counts_fn> [<design> <cov_fn>]

Options:
    -h --help   This helpful helping of help
'''
TODO = '''
    detk-transform ruvseq <counts_fn>
'''

cmd_opts = {
    'vst':r'''
Usage:
    detk-transform vst [options] <counts_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    --rda=RDA              Filename passed to saveRDS() R function of the result
                           objects from the analysis
''',
    'plog':r'''
Usage:
    detk-transform plog [options] <counts_fn>

Options:
    -c N --pseudocount=N   The pseudocount to use when taking the log transform [default: 1]
    -b B --base=B          The base of the log to use [default: 10]
    -o FILE --output=FILE  Destination of primary output [default: stdout]
''',
    'rlog':r'''
Usage:
    detk-transform rlog [options] <counts_fn> [<design> <cov_fn>]

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    --rda=RDA              Filename passed to saveRDS() R function of the result
                           objects from the analysis
    --strict               Require that the sample order indicated by the column names in the
                           counts file are the same as, and in the same order as, the
                           sample order in the row names of the covariates file
    --blind N              If False, count_obj is expected to have column_data
''',
}

from docopt import docopt
import logging
import math, os
import numpy
import pandas
from pprint import pformat
import sys
from .common import CountMatrixFile, DetkModule, _cli_doc, make_cli_count_obj, set_logging, write_output
from .wrapr import (
                require_r, require_deseq2, wrapr, RExecutionError, RPackageMissing,
                require_r_package
        )
from .util import stub
from .report import DetkReport

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def plog(count_obj,pseudocount=1,base=10) :
    '''
    Logarithmic transform of a counts matrix with fixed pseudocount, i.e. $\\log(x+c)$

    Parameters
    ----------
    count_obj : CountMatrix object
        count matrix object

    Returns
    -------
    pandas.DataFrame
        log transformed counts dataframe with the same dimensionality as input
        counts

    '''
    obj = PlogCounts(count_obj, pseudocount, base)
    return obj.output

class PlogCounts(DetkModule):
    def __init__(self, count_obj, pseudocount=1, base=10):
        self['params'] = {'pseudocount': pseudocount,
                'base': base}
        logger.debug('plog params: %s',pformat(self['params']))
        self.count_obj = count_obj
        self.plog_counts = numpy.log(count_obj.counts+pseudocount)/numpy.log(base)
        logger.info('done plog transform')
    @property
    def output(self):
        return self.plog_counts
    @property
    def properties(self):
        return {'num_length': len(self.plog_counts),
                'params': self['params']}

def vst(count_obj) :
    '''
    Variance Stabilizing Transformation implemented in the DESeq2 bioconductor
    package.

    Parameters
    ----------
    count_obj : CountMatrix object
        count matrix object

    Returns
    -------
    pandas.DataFrame
        VST transformed counts dataframe with the same dimensionality as input
        counts
    '''
    obj = VstCounts(count_obj)
    return obj.output

class VstCounts(DetkModule):
    @require_r('DESeq2','SummarizedExperiment')
    def __init__(self, count_obj):
        self.count_obj = count_obj
        script = '''\
        library(DESeq2)
        library(SummarizedExperiment)

        cnts <- as.matrix(read.csv(counts.fn,row.names=1,check.names=FALSE))
        colData <- data.frame(name=seq(ncol(cnts)),check.names=FALSE)
        dds <- DESeqDataSetFromMatrix(countData = cnts,
            colData = colData,
            design = ~ 1)
        dds <- varianceStabilizingTransformation(dds)
        write.csv(assay(dds),out.fn)
        '''
        logger.debug('VST R script:\n%s',pformat(script))

        with wrapr(script,
                counts=count_obj.counts,
                raise_on_error=True) as r :
            vsd_values = r.output
            self.vsd_values = vsd_values

        logger.info('done VST transform')

    @property
    def output(self):
        return self.vsd_values
    @property
    def properties(self):
        return {'num_length': len(self.vsd_values)
            }

def rlog(count_obj, blind=True) :
    '''
    Regularized log (rlog) transformation implemented in the DESeq2 bioconductor
    package.

    Parameters
    ----------
    count_obj : CountMatrix object
        count matrix object
    blind : bool
        the `blind` parameter as passed to the `rlog` function in DESeq2. if
        False, `count_obj` is expected to have `column_data` and a valid
        design as required by the R function

    Returns
    -------
    pandas.DataFrame
        rlog transformed counts dataframe with the same dimensionality as input
        counts
    '''
    obj = RlogCounts(count_obj, blind)
    return obj.output

class RlogCounts(DetkModule):
    @require_r('DESeq2','SummarizedExperiment')
    def __init__(self, count_obj, blind=True):
        self['params'] = {'blind': blind
                }
        logger.debug('rlog params:\n%s',pformat(self['params']))

        self.count_obj = count_obj

        script = '''\
        library(DESeq2)
        library(SummarizedExperiment)

        cnts <- as.matrix(read.csv(counts.fn,row.names=1,check.names=FALSE))

        rnames <- rownames(cnts)

        # DESeq2 whines when input counts aren't integers
        # round the counts matrix
        cnts <- data.frame(apply(cnts,2,function(x) { round(as.numeric(x)) }),
            check.names=FALSE
        )
        rownames(cnts) <- rnames

        # load design matrix
        if(file.info(metadata.fn)$size != 0) {
            colData <- read.csv(metadata.fn,header=T,as.is=T,row.names=1,check.names=FALSE)
        } else {
            # just to convince DESeq2 that everything is ok when we're doing a
            # blind rlog
            n.fake.class.1 <- floor(ncol(cnts)/2)
            fake.classes <- factor(c(
                rep(0,n.fake.class.1),
                rep(1,ncol(cnts)-n.fake.class.1))
            )
            colData <- data.frame(name=fake.classes)
        }

        blind <- params$blind
        form <- params$design

        dds <- DESeqDataSetFromMatrix(countData = cnts,
            colData = colData,
            design = formula(form)
        )

        dds <- rlog(dds,blind=blind)
        write.csv(assay(dds),out.fn)
        '''
        logger.debug('VST R script:\n%s',script)
        column_data = None
        if not blind and count_obj.column_data is not None :
            column_data = count_obj.design_matrix.full_matrix

        params = {
            'design': '~ 1' if blind else count_obj.design,
            'blind': blind
        }
        logger.debug('VST R script params:\n%s',pformat(params))

        with wrapr(script,
                counts=count_obj.counts,
                metadata=column_data,
                params=params,
                raise_on_error=True) as r :
            vsd_values = r.output
            self.vsd_values = vsd_values

        logger.info('done rlog transform')
    @property
    def output(self):
        return self.vsd_values
    @property
    def properties(self):
        return {'num_length': len(self.vsd_values)
                }

@stub
def ruvseq(count_obj) :
    pass

def main(argv=sys.argv) :

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    # add the common opts to the docopt strings
    cmd_opts_aug = {}
    for k,v in cmd_opts.items() :
        cmd_opts_aug[k] = _cli_doc(v)

    args = docopt(_cli_doc(__doc__), argv=argv[1:])
    set_logging(args)
    logger.info('cmd: %s',' '.join(argv))

    count_obj = make_cli_count_obj(args)

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts) :
        docopt(_cli_doc(__doc__))
    argv = argv[1:]
    cmd = argv[0]

    if cmd == 'vst' :
        args = docopt(cmd_opts_aug['vst'],argv)

        out = VstCounts(count_obj)

    if cmd == 'plog' :
        args = docopt(cmd_opts_aug['plog'],argv)

        try :
            out = PlogCounts(
                    count_obj,
                    pseudocount=float(args['--pseudocount']),
                    base=float(args['--base'])
                    )
        except Exception as e :
            logger.error(e)
            sys.exit(1)
    
    elif cmd == 'rlog' :
        args = docopt(cmd_opts_aug['rlog'],argv)

        if args['--blind'] is None:
            args['--blind'] = True

        try :
            out = RlogCounts(count_obj,
                    blind=args['--blind'])
        except Exception as e :
            logger.error(e)
            sys.exit(1)

    write_output(out.output,args)

    if not args['--no-report'] :
        logging.info('writing report to %s',args['--report-dir'])
        with DetkReport(args['--report-dir']) as r :
            r.add_module(
                    out,
                    in_file_path=args['<counts_fn>'],
                    out_file_path=args['--output'],
                    column_data_path=args.get('--column-data'),
                    workdir=os.getcwd()
                    )

    logging.info('done')

if __name__ == '__main__' :
    main()
