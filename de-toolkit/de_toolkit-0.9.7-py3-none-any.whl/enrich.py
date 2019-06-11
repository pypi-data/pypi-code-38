r'''
Usage:
    detk-enrich fgsea [options] <gmt_fn> <result_fn>
Options:
    -o FILE --output=FILE        Destination of normalized output in CSV format [default: stdout]
'''

todo = r'''
    detk-enrich fisher [options] <gmt_fn> <result_fn>
'''
cmd_opts = {
        'fgsea':r'''
Perform preranked Gene Set Enrichment Analysis using the fgsea bioconductor
package on the given gmt gene set file.

The GMT file must be tab delimited with set name in the first column, a
description in the second column (ignored by detk), and an individual feature
ID in each column after, one feature set per line. The result file can be any
character delimited file, and is assumed to have column names in the first row.

The feature IDs must be from the same system (e.g. gene symbols, ENSGIDs, etc)
in both GMT and result files. The user will likely have to provide:

- -i <col>: column name in the results file that contains feature IDs
- -c <col>: column name in the results file that contains the statistics to
  use when computing enrichment, e.g. log2FoldChange

fgsea: https://bioconductor.org/packages/release/bioc/html/fgsea.html

Usage:
    detk-enrich fgsea [options] <gmt_fn> <result_fn>

Options:
    -h --help                 Print out this help
    -o FILE --output=FILE     Destination of fgsea output [default: stdout]
    -p PROCS --cores=PROCS    Ask BiocParallel to use PROCS processes when
                              executing fgsea in parallel, requires the
                              BiocParallel package to be installed
    -i FIELD --idcol=FIELD    Column name or 0-based integer index to use as
                              the gene identifier [default: 0]
    -c FIELD --statcol=FIELD  Column name or 0-based integer index to use as
                              the statistic for ranking, defaults to the last
                              numeric column in the file
    -a --ascending            Sort column ascending, default is to sort
                              descending, use this if you are sorting by p-value
                              or want to reverse the directionality of the NES
                              scores
    --abs                     Take the absolute value of the column before
                              passing to fgsea
    --minSize=INT             minSize argument to fgsea [default: 15]
    --maxSize=INT             maxSize argument to fgsea [default: 500]
    --nperm=INT               nperm argument to fgsea [default: 10000]
    --rda=FILE                write out the fgsea result to the provide file
                              using saveRDS() in R
''',
}
from collections import namedtuple, OrderedDict
import csv
from docopt import docopt
import logging
import numpy as np
import os
import pandas
from pprint import pformat
import tempfile
import sys
import warnings
from .common import CountMatrixFile, DetkModule, _cli_doc, set_logging, write_output
from .util import stub
from .wrapr import require_r, wrapr, require_r_package, RPackageMissing
from .report import DetkReport

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

GeneSet = namedtuple('GeneSet',('name','desc','ids'))
class GMT(OrderedDict):
    def __init__(self,sets={}) :
        super(GMT, self).__init__(self)
        for name,ids in sets.items() :
            self[name] = ids

    def __setitem__(self,name,ids) :
        self.add(name,ids)

    def add(self,name,ids,desc=None) :
        OrderedDict.__setitem__(
                self,
                name,
                GeneSet(name,desc or name,ids)
            )

    def load_file(self,fn) :
        self.fn = fn
        with open(fn) as f :
            for r in csv.reader(f,delimiter='\t') :
                self[r[0]] = [_.strip() for _ in r[2:]]

    def write_file(self,out_fn) :
        with open(out_fn,'wt') as f :
            out_f = csv.writer(f,delimiter='\t')
            for k,v in self.items() :
                out_f.writerow([k,k]+list(v.ids))

def fgsea(
        gmt,
        stat,
        minSize=15,
        maxSize=500,
        nperm=10000,
        nproc=None,
        rda_fn=None) :
    '''
    Perform pre-ranked Gene Set Enrichment Analysis using the fgsea Bioconductor
    package

    Compute GSEA enrichment using the provided gene sets in the GMT object *gmt*
    using the statistics in the pandas.Series *stat*. The fgsea Bioconductor
    package must be installed on your system for this function to work.

    The output dataframe contains one result row per features set in the GMT
    file, in the same order. Output columns include:

    - name: name of feature set
    - ES: GSEA enrichment score
    - NES: GSEA normalized enrichment score
    - pval: nominal p-value
    - padj: Benjamini-Hochberg adjusted p-value
    - nMoreExtreme: number of permutations with a more extreme NES than true
    - size: number of features in the feature set
    - leadingEdge: the leading edge features as defined by GSEA (string with
      space-separated feature names)
    '''
    obj = FGSEARes(gmt, stat, minSize, maxSize, nperm, nproc, rda_fn)
    return obj.output

class FGSEARes(DetkModule) :
    @require_r('fgsea')
    def __init__(self,
            gmt,
            stat,
            minSize=15,
            maxSize=500,
            nperm=10000,
            nproc=None,
            rda_fn=None
        ) :
        self['params'] = {
                'minSize': minSize,
                'maxSize': maxSize,
                'nperm': nperm,
                'nproc': nproc,
                'rda_fn': rda_fn
                }
        self.gmt = gmt

        # check for NAs in the stat
        if stat.isnull().any() :
            nas = stat[stat.isnull()]
            warnings.warn('The following statistics were NaN and were filtered prior to fgsea:\n{}'.format(nas))
            logger.warn('The following statistics were NaN and were filtered prior to fgsea:\n{}'.format(nas))
            stat = stat[~stat.isnull()]

        script = '''\
        library(fgsea)
        library(data.table)

        ranks <- setNames(params$stat,params$id)
        pathways <- gmtPathways(params$gmt.fn)

        fgseaRes <- fgsea(
            pathways,
            ranks,
            minSize=params$minSize,
            maxSize=params$maxSize,
            nperm=params$nperm,
            nproc=params$nproc
        )
        if(!is.null(params$rda.fn)) {
            saveRDS(
                list(
                    fgseaRes=fgseaRes,
                    pathways=pathways,
                    ranks=ranks,
                    params=params
                ),
                file=params$rda.fn
            )
        }
        fwrite(fgseaRes,file=out.fn,sep=",",sep2=c("", " ", ""))
        '''
        logger.debug('fgsea R script:\n%s',script)

        # need to write out the gmt to file
        with tempfile.NamedTemporaryFile() as f :
            gmt.write_file(f.name)
            params = {
                'gmt.fn': os.path.realpath(f.name),
                'stat': stat.tolist(),
                'id': stat.index.tolist(),
                'minSize': minSize,
                'maxSize': maxSize,
                'nperm': nperm,
                'rda.fn': rda_fn,
                'nproc': nproc or 0
            }
            logger.debug('fgsea wrapr params:\n%s',pformat(params))
            with wrapr(script,
                    params=params,
                    raise_on_error=True) as r :
                gsea_res = r.output
        
        self.gsea_res = gsea_res
        logger.info('shape of fgsea result dataframe: %s',gsea_res.shape)

        logger.info('fgsea done')

    @property
    def properties(self):
        return {
                'num_pathways': len(self.gsea_res),
                }
    @property
    def output(self):
        return self.gsea_res

def main(argv=sys.argv) :

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    # add the common opts to the docopt strings
    cmd_opts_aug = {}
    for k,v in cmd_opts.items() :
        cmd_opts_aug[k] = _cli_doc(v)

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts) :
        docopt(__doc__)
    argv = argv[1:]
    cmd = argv[0]

    if cmd == 'fgsea' :
        args = docopt(cmd_opts_aug['fgsea'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        logger.info('reading in GMT file %s',args['<gmt_fn>'])
        gmt = GMT()
        try :
            gmt.load_file(args['<gmt_fn>'])
        except Exception as e :
            logger.error(e)
            sys.exit(1)

        logger.info('reading in results file %s',args['<result_fn>'])
        try :
            res_df = pandas.read_csv(
                    args['<result_fn>'],
                    sep=None,
                    engine='python'
            )
        except Exception as e :
            logger.error(e)
            sys.exit(1)

        logger.info('result data frame shape: %s',res_df.shape)

        cores = args['--cores']
        if cores is not None :

            logging.debug('Enabling parallelism with BiocParallel')

            try:
                require_r_package('BiocParallel')
            except Exception as e :
                logger.error(e)
                sys.exit(1)

            try :
                cores = int(cores)
            except ValueError :
                logger.error(Exception('The cores argument to fgsea '
                        'must be an integer'))
                sys.exit(1)

        def get_col_or_idcol(res_df,col) :
            if col not in res_df.columns :
                col = int(col)
                if col >= len(res_df.columns) :
                    raise ValueError()
                col = res_df.columns[col]
            return col

        col = args['--statcol']
        if col is not None :
            # check that the provided column is either in the column names
            # of the results df, or else is a valid integer index into it

                try :
                    col = get_col_or_idcol(res_df,col)
                except ValueError :
                    logger.error(Exception((
                        'Stat column {} could not be found in results result '
                        'or interpreted as an integer index, aborting'
                        ).format(col)
                    ))
                    sys.exit(1)
        else :
            # pick the last numeric column
            col = res_df.columns[res_df.dtypes.apply(lambda x: np.issubdtype(x,np.number))][-1]
        logger.info('using % as statistic column',col)

        stat = res_df[col]
        if args['--abs'] :
            logger.info('taking absolute value of statistic column due to --abs')
            stat = stat.abs()

        idcol = args['--idcol']
        if idcol is not None :
            try :
                idcol = get_col_or_idcol(res_df,idcol)
            except ValueError :
                logger.error(Exception((
                    'ID column {} could not be found in results result '
                    'or interpreted as an integer index, aborting'
                    ).format(col)
                ))
                sys.exit(1)

            stat.index = res_df[idcol]
        logger.info('using % as identifier column',col)

        if args['--ascending'] :
            logger.info('sorting statistic into ascending order due to --ascending')
            stat = -stat

        try :
            out = FGSEARes(
                    gmt,
                    stat,
                    minSize=int(args['--minSize']),
                    maxSize=int(args['--maxSize']),
                    nperm=int(args['--nperm']),
                    nproc=cores,
                    rda_fn=args['--rda']
                )
        except Exception as e :
            logger.error(e)
            sys.exit(1)

    write_output(out.output,args)

    if not args['--no-report'] :
        logging.info('writing report to %s',args['--report-dir'])
        with DetkReport(args['--report-dir']) as r :
            r.add_module(
                    out,
                    in_file_path=args['<gmt_fn>'],
                    out_file_path=args['--output'],
                    column_data_path=args.get('--column-data'),
                    workdir=os.getcwd()
                )
    else :
        logging.info('not generating report due to --no-report')

    logging.info('done')

if __name__ == '__main__':
    main()
