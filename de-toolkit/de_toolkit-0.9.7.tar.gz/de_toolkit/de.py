r'''
Usage:
    detk-de deseq2 [options] <design> <counts_fn> <cov_fn>
    detk-de firth [options] <design> <counts_fn> <cov_fn>
'''

TODO = r'''
    detk-de t-test ( help | [options] <counts_fn> <cov_fn> )
'''

cmd_opts = {
        'deseq2':r'''
Usage:
    detk-de deseq2 [options] <design> <counts_fn> <cov_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    --routput-dir=DIR      Path to output directory for R stuffs, useful for
                           debuggin out
    --rda=RDA              Filename passed to saveRDS() R function of the result
                           objects from the analysis
    --strict               Require that the sample order indicated by the column names in the
                           counts file are the same as, and in the same order as, the
                           sample order in the row names of the covariates file
    --norm-counts          Prevent DESeq2 from normalizing counts prior to
                           running differential expression, default behavior
                           assumes that provided counts are raw
    --last-term-only       Use the default DESeq2 behavior of returning DE parameters
                           for the last term in the model, default behavior is to
                           report parameters for all variables in the model
    --gene-wise-disp       Use estimateDispersionsGeneEst instead of estimateDispersions
    --cores=N              Tell DESeq2 to use N cores when running, requires the
                           BiocParallel Bioconductor package to be installed [default: none]
''',
        'firth':r'''
Usage:
    detk-de firth [options] <design> <counts_fn> <cov_fn>

Options:
    -o FILE --output=FILE  Destination of primary output [default: stdout]
    --routput-dir=DIR      Path to output directory for R stuffs, useful for
                           debuggin out
    --rda=RDA              Filename passed to saveRDS() R function of the result
                           objects from the analysis
    --strict               Require that the sample order indicated by the column names in the
                           counts file are the same as, and in the same order as, the
                           sample order in the row names of the covariates file
    --standardize          Standardize counts prior to running logistic regression
                           as to obtain standardized (i.e. directly comparable)
                           beta coefficients
    --cores=N              Tell R to use N cores when running, requires the
                           parallel R package to be installed [default: none]
'''
}

from docopt import docopt
import logging
import pandas
from pprint import pformat
import sys, os
from .common import (CountMatrixFile, InvalidDesignException, DetkModule,
        _cli_doc, set_logging, make_cli_count_obj, write_output
    )
from .wrapr import (
        require_r, require_deseq2, wrapr, RExecutionError, RPackageMissing,
        require_r_package
    )
from .util import stub
from .report import DetkReport

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def deseq2(count_obj,
        normalized=True,
        rda=None,
        all_coeff_results=True,
        gene_wise_disp_est=False,
        cores=None,
        routput_dir=None):
    obj = DESeq2Counts(
            count_obj,
            normalized,
            rda,
            all_coeff_results,
            gene_wise_disp_est,
            cores,
            routput_dir=routput_dir
    )
    return obj.output

class DESeq2Counts(DetkModule):
    @require_r('DESeq2')
    def __init__(self, count_obj,
            normalized=True,
            rda=None,
            all_coeff_results=True,
            gene_wise_disp_est=False,
            cores=None,
            routput_dir=None):
        self.count_obj = count_obj
        self['params'] = {'normalized': normalized,
                'rda': rda,
                'all_coeff_results': all_coeff_results,
                'gene_wise_disp_est': gene_wise_disp_est,
                'cores': cores
                }

        # make a copy of count_obj, since we mutate it
        count_obj = count_obj.copy()

        # validate the design matrix
        if count_obj.design is None or count_obj.design_matrix is None :
            raise InvalidDesignException('count_obj must have a design matrix to use'
                ' DESeq2')

        if 'counts' not in count_obj.design_matrix.lhs :
            raise InvalidDesignException('The term "counts" must exist on the left '
                ' hand side of the model in DESeq2')

        # drop the counts from the left hand side since DESeq2 doesn't use it
        count_obj.design_matrix.drop_from_lhs('counts',quiet=True)

        # make sure the rhs of the design matrix doesn't have an intercept
        count_obj.design_matrix.drop_from_rhs('Intercept',quiet=True)

        if cores is not None :
            logging.debug('Enabling parallelism with BiocParallel')
            require_r_package('BiocParallel')
            try :
                cores = int(cores)
            except ValueError :
                raise Exception('The cores argument to DESeq2 '
                        'must be an integer')

        params = {
            'design': count_obj.design,
            'normalized': normalized,
            'rda': rda,
            'cores': cores,
            'all.coeff.results': all_coeff_results,
            'gene.wise.disp.est': gene_wise_disp_est
        }
        logger.debug('DESeq2 wrapr params:\n %s', pformat(params))
        script = '''\
            library(DESeq2)
            cnts <- read.csv(counts.fn,header=T,as.is=T,check.names=FALSE)
            index.name <- names(cnts)[1]

            # first column name is blank
            orig.index.name <- index.name
            if(index.name == '') {
                index.name <- 'feature'
                colnames(cnts)[1] <- index.name
            }
            rownames(cnts) <- cnts[[1]]
            cnts <- cnts[c(-1)]

            rnames <- rownames(cnts)

            # DESeq2 whines when input counts aren't integers
            # round the counts matrix
            cnts <- data.frame(lapply(cnts,function(x) { round(as.numeric(x)) }),
                check.names=FALSE
            )
            rownames(cnts) <- rnames

            # use parallelism if params$cores > 0
            cores <- if(is.null(params$cores)) { 0 } else { as.numeric(params$cores) }
            parallel <- FALSE
            if(cores>0) {
                library(BiocParallel)
                register(MulticoreParam(cores))
                parallel <- TRUE
            }

            # design formula
            form <- params$design

            # load design matrix
            design.mat <- read.csv(
                metadata.fn,
                header=T,
                as.is=T,
                row.names=1,
                check.names=FALSE
            )

            # make sure the counts and design matrix samples line up
            stopifnot(colnames(cnts) == rownames(design.mat))

            dds <- DESeqDataSetFromMatrix(
                countData = cnts,
                colData = design.mat,
                design = formula(form)
            )

            # if counts are already normalized, don't normalize them
            if(params$normalized) {
                sizeFactors(dds) <- rep(1,nrow(design.mat))
            } else {
                dds <- estimateSizeFactors(dds)
            }

            # in some cases R can throw this error:
            if(params$gene.wise.disp.est) {
                dds <- estimateDispersionsGeneEst(dds)
                dispersions(dds) <- mcols(dds)$dispGeneEst
            } else {
                dds <- estimateDispersions(dds)
            }

            # turn off cooks distance outlier replacement
            #dds <- DESeq(dds,minReplicatesForReplace=Inf,parallel=parallel)

            dds <- nbinomWaldTest(dds)

            result_from_dds <- function(name) {
                res.df <- data.frame(
                    log2FoldChange=mcols(dds)[[name]],
                    lfcSE=mcols(dds)[[paste0('SE_',name)]],
                    stat=mcols(dds)[[paste0('WaldStatistic_',name)]],
                    pvalue=mcols(dds)[[paste0('WaldPvalue_',name)]],
                    padj=p.adjust(mcols(dds)[[paste0('WaldPvalue_',name)]],method='fdr')
                )
                colnames(res.df) <- paste(name,colnames(res.df),sep='__')
                res.df
            }

            # organize output results
            res.df <- if(params$all.coeff.results==TRUE) {
                # report statistics and p-values on all model variables
                # output columns are:
                #   basemean
                #   for each model variable:
                #     <varname>__log2FoldChange (mcols(dds)[['<varname>']])
                #     <varname>__lfcSE (mcols(dds)[['SE_<varname>']])
                #     <varname>__stat (mcols(dds)[['WaldStatistic_<varname>']])
                #     <varname>__pvalue (mcols(dds)[['WaldPvalue_<varname>']])
                #     <varname>__padj (p.adjust(mcols(dds)[['WaldPvalue_<varname>']],method='fdr')

                # example mcols(dds) names:
                # Intercept
                # category__case
                # SE_Intercept
                # SE_category__case
                # WaldStatistic_Intercept
                # WaldStatistic_category__case
                # WaldPvalue_Intercept
                # WaldPvalue_category__case
                do.call(
                    cbind,
                    lapply(
                        colnames(design.mat),
                        result_from_dds
                    )
                )
            } else {
                # just report the last column as is the DESeq2 default
                result_from_dds(tail(colnames(design.mat),n=1))
            }

            # add on the basemean
            res.df <- cbind(mcols(dds)[['baseMean']],res.df)
            colnames(res.df)[1] <- 'baseMean'

            if(!is.null(params$rda)) {
                saveRDS(dds,params$rda)
            }

            # because R is stupid and can't easily write out a column name for
            # a row name
            res.df.cols <- colnames(res.df)
            res.df[[index.name]] <- rnames
            res.df <- res.df[c(index.name,res.df.cols)]

            # put the original first column name back
            colnames(res.df)[1] <- orig.index.name

            write.csv(res.df,out.fn,row.names=F)
        '''
        logging.info('Executing DESeq2 in wrapr')
        with wrapr(script,
                counts=count_obj.counts,
                metadata=count_obj.design_matrix.full_matrix,
                params=params,
                routput_dir=routput_dir) as wr :
            self.wr_output = wr.output

        logging.info('Done executing DESeq2 in wrapr')
    @property
    def output(self):
        return self.wr_output
    @property
    def properties(self):
        return {'num_length': len(self.wr_output)
                }

def firth_logistic_regression(
        count_obj,
        standardize=False,
        rda=None,
        cores=None,
        routput_dir=None) :
    obj = FLGCounts(count_obj, standardize, rda, cores)
    return obj.output

class FLGCounts(DetkModule):
    @require_r('logistf')
    def __init__(self, count_obj,
            standardize=False,
            rda=None,
            cores=None,
            routput_dir=None):
        self.count_obj = count_obj

        # make a copy of count_obj, since we mutate it
        count_obj = count_obj.copy()

        # validate the design matrix
        if count_obj.design is None or count_obj.design_matrix is None :
            raise InvalidDesignException('count_obj must have a design matrix in Firth'
                ' logistic regression')

        if 'counts' not in count_obj.design_matrix.rhs :
            raise InvalidDesignException('The term "counts" must exist on the right hand'
                'side of the model in Firth logistic regression')

        # make sure the rhs of the design matrix doesn't have an intercept
        count_obj.design_matrix.drop_from_rhs('Intercept',quiet=True)

        if cores is not None :
            require_r_package('parallel')
            try :
                cores = int(cores)
            except ValueError :
                raise Exception('The cores argument to firth_logistic_regression '
                        'must be an integer')

        params = {
            'design': count_obj.design,
            'standardize': standardize,
            'rda': rda,
            'cores': cores
        }
        logger.debug('logistf wrapr params:\n %s', pformat(params))
        script = '''\
            library(logistf)
            cnts <- read.csv(counts.fn,header=T,as.is=T,check.names=FALSE)
            index.name <- names(cnts)[1]

            # first column name is blank
            orig.index.name <- index.name
            if(index.name == '') {
                index.name <- 'feature'
                colnames(cnts)[1] <- index.name
            }

            rownames(cnts) <- cnts[[1]]
            cnts <- cnts[c(-1)]

            rnames <- rownames(cnts)
            cnts <- data.frame(lapply(cnts,as.numeric),check.names=FALSE)
            rownames(cnts) <- rnames

            # scale counts to obtain standardized beta estimates
            if(params$standardize) {
                cnts <- data.frame(t(scale(t(cnts))),check.names=FALSE)
            }

            # design formula
            form <- params$design

            # load design matrix
            design.mat <- read.csv(metadata.fn,header=T,as.is=T,row.names=1,check.names=FALSE)

            fit <- NULL

            applyf <- lapply
            if(!is.null(params$cores)) {
                library(parallel)
                applyf <- function(l,f) { mclapply(l,f,mc.cores=params$cores) }
            }
            res.orig <- applyf(rownames(cnts),
                function(gene) {
                  x <- data.frame(design.mat,check.names=FALSE)
                  x$counts <- unlist(cnts[gene,])
                  log.fit <- logistf(formula(form),data=x,pl=F)
                  fit <<- log.fit
                  out <- c(gene, 'OK')
                  names(out) <- c(index.name,'status')
                  coeffs <- log.fit$coeff
                  names(coeffs) <- paste0(names(coeffs),'__beta')
                  probs <- log.fit$prob
                  names(probs) <- paste0(names(probs),'__p')
                  padj <- rep(NA,length(probs))
                  names(padj) <- paste0(names(log.fit$prob),'__padj')
                  cp <- c(rbind(coeffs,probs,padj))
                  cp.names <- c(rbind(names(coeffs),names(probs),names(padj)))
                  cp.names <- gsub(".Intercept.","int",cp.names)
                  names(cp) <- cp.names
                  c(out,cp)
                }
            )

            if(!is.null(params$rda)) {
                saveRDS(fit,params$rda)
            }
            res <- do.call(rbind,res.orig)
            res.df <- as.data.frame(res,stringsAsFactors=F,check.names=FALSE)
            for(c in colnames(res.df)[c(-1,-2)]) {
                res.df[c] <- as.numeric(res.df[c][[1]])
            }
            # calculate p.adjust for each pvalue col
            for(c in Filter(function(x) endsWith(x,'__p'),colnames(res.df))) {
                res.df[paste0(c,'adj')] <- p.adjust(res.df[[c]],"fdr")
            }

            # put the original first column name back
            colnames(res.df)[1] <- orig.index.name

            write.csv(res.df,out.fn,row.names=F)
        '''
        logging.info('Executing logistf in wrapr')
        with wrapr(script,
                counts=count_obj.counts,
                metadata=count_obj.design_matrix.full_matrix,
                params=params,
                routput_dir=routput_dir) as wr :
            self.wr_output = wr.output

        logging.info('Done executing logistf in wrapr')
    @property
    def output(self):
        return self.wr_output
    @property
    def properties(self):
        return {'num_length': len(self.wr_output)
                }

@stub
def t_test(count_obj) :
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

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmd_opts_aug) :
        docopt(_cli_doc(__doc__))
    argv = argv[1:]
    cmd = argv[0]

    if cmd == 'deseq2' :
        args = docopt(cmd_opts_aug['deseq2'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        count_obj = make_cli_count_obj(args)

        try :
            logger.info('running DESeq2')
            out = DESeq2Counts(count_obj,
                    normalized=args.get('--norm-counts',False),
                    rda=args.get('--rda'),
                    all_coeff_results=not args.get('--last-term-only',False),
                    gene_wise_disp_est=args.get('--gene-wise-disp',False),
                    cores=int(args['--cores']) if args['--cores'] != 'none' else None,
                    routput_dir=args['--routput-dir']
            )
        except Exception as e :
            logger.error(e)
            sys.exit(1)

    elif cmd == 'firth' :
        args = docopt(cmd_opts_aug['firth'],argv)

        set_logging(args)
        logger.info('cmd: %s',' '.join(argv))

        count_obj = make_cli_count_obj(args)

        try :
            logger.info('running Firth logistic regression')
            out = FLGCounts(count_obj,
                    rda=args['--rda'],
                    standardize=args.get('--standardize',False),
                    cores=int(args['--cores']) if args['--cores'] != 'none' else None,
                    routput_dir=args['--routput-dir']
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
                    in_file_path=args['<counts_fn>'],
                    out_file_path=args['--output'],
                    column_data_path=args.get('--column-data'),
                    workdir=os.getcwd()
                    )
    else :
        logging.info('not generating report due to --no-report')

    logging.info('done')

if __name__ == '__main__' :
    main()
