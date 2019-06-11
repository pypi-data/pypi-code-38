r'''
Usage:
    detk-wrapr check [options]
    detk-wrapr run [options] <rscript> [<counts_in>] [<out>]

Options:
    --rpath=PATH        Path to Rscript executable, inferred from the environment
                        by default
    --routput-dir=PATH  A directory name to write all of the relevant files to
                        when running this wrapr, useful for debugging an R
                        script if things go wrong, by default the directory
                        and files created are temporary and deleted after
                        execution
    --meta-in=PATH      Path to metadata file corresponding to columns in counts,
                        same as is passed to other detk functions
    --meta-out=PATH     Path to metadata file corresponding to columns in counts,
                        same as is passed to other detk functions
    --params-in=PATH    Path to JSON formatted file containing parameters needed
                        by R script
    --params-out=PATH   Path to JSON formatted file to be created with output
                        from the R script
    --strict            Ensure counts column names and the first row of the
                        metadata file provided (if any) match, otherwise fail
'''
from collections import defaultdict
from docopt import docopt
import json
import logging
import os
import pandas as pd
import pathlib
from pprint import pformat
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory
from .common import CountMatrixFile, _cli_doc, set_logging
from .util import which

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class RscriptExecutableNotFound(Exception) : pass
class RPackageMissing(Exception) : pass
class RExecutionError(Exception) : pass

def get_r_path():
    'Return the path to Rscript found in the shell environment.'
    return which('Rscript')

def check_r() :
    'Tests whether the Rscript executable can be found.'
    return get_r_path() is not None

def check_r_package(pkg) :
    'Tests whether the R package *pkg* is installed.'
    cmd = ' '.join([
        get_r_path(),
        '-e',
        '"library({})"'.format(pkg)
        ])
    logger.debug('check_r_package cmd: %s',cmd)
    p = subprocess.run(cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    logger.debug('check_r_package stdout:\n%s',pformat(p.stdout.decode('utf-8')))
    logger.debug('check_r_package stderr:\n%s',pformat(p.stderr.decode('utf-8')))

    return p.returncode == 0

def require_r_package(pkg) :
    'Check whether pkg is installed in R, and raise if not.'
    if not check_r_package(pkg) :
        raise RPackageMissing(('R package {pkg} is needed for this '
                'functionality. In R, try installing with:\n\n'
                'install.packages("{pkg}")').format(pkg=pkg))

def require_r(*pkgs):
    '''Decorator for functions that require using R. Raises exception if
    either Rscript or jsonlite or other packages provided cannot be found.
    Can be called with or without arguments. When arguments are supplied,
    the arguments should be strings of names of R packages required by the
    decorated function.

    **Examples**

    @require_r
    def call_requiring_only_Rscript_and_jsonlite() :
        ...

    @require_r('logistf',...)
    def call_requiring_Rscript_jsonlite_and_logistf_and_others() :
        ...
    '''
    # when decorated without arguments
    if callable(pkgs[0]) :
        f = pkgs[0]
        def decorator(*args,**kwargs):
            if not check_r():
                raise RscriptExecutableNotFound('Rscript executable could not be '
                        'found on PATH. Rscript is needed for this functionality')
            require_r_package('jsonlite')
            return f(*args,**kwargs)
    # when decorated with arguments
    else :
        def decorator(f) :
            def wrapped(*args,**kwargs):
                if not check_r():
                    raise RscriptExecutableNotFound('Rscript executable could not be '
                            'found on PATH. Rscript is needed for this functionality')
                else :
                    require_r_package('jsonlite')
                    for pkg in pkgs :
                        require_r_package(pkg)
                return f(*args,**kwargs)
            return wrapped
    return decorator

def check_deseq2():
    'Tests whether the DESeq2 bioconductor package is installed.'
    wr = wrapr('library(DESeq2)')
    return wr.success

@require_r
def require_deseq2(f):
    '''Decorator for functions that require using DESeq2. Raises exception if
    the package cannot be found.'''
    def _f(*args,**kwargs):
        if not check_deseq2():
            raise RPackageMissing('R package DESeq2 is needed for this '
                    'functionality. In R, try installing with:\n\n'
                    'source("http://bioconductor.org/biocLite.R")\n'
                    'biocLite("DESeq2")')
        else :
            return f(*args,**kwargs)
    return _f
   

_script_tmpl = '''\
args <- commandArgs(trailingOnly=TRUE)
counts.fn <- args[1]; metadata.fn <- args[2]; params.fn <- args[3];
out.fn <- args[4]; metadata.out.fn <- args[5]; params.out.fn <- args[6];
library(jsonlite)
json <- readChar(params.fn, file.info(params.fn)$size)
params <- if(nchar(json) > 0) {{
    read_json(params.fn,simplifyVector=TRUE)
}} else {{
    list()
}}

{script}
'''
class WrapR(object) :
    '''
    Wrapper object for calling R code with Rscript.

    .. note::
        The attributes are only populated after the execute() method has
        been run

    Parameters
    ----------

    rscript_path : str
        path to the R script to run

    counts : pandas.DataFrame, optional
        dataframe containing counts to be passed to R

    metadata : pandas.DataFrame, optional
        dataframe containing metadata to be passed to R

    params : dict, optional
        dict of parameters to be passed to R

    output_fn : str, optional
        path to file where R should write output, if not provided the output
        is written to a temporary file and deleted upon WrapR object deletion

    metadata_out_fn : str, optional
        path to file where R should write metadata output

    rpath : str
        path to the Rscript executable, taken from the PATH environment
        variable if None

    raise_on_error : bool
        raise an exception if R encounters an error, other wise fail silently
        and deadly

    Attributes
    ----------

    output : pandas.DataFrame
        dataframe of the tabular output created by R script

    metadata_out : pandas.DataFrame
        dataframe of the tabular metadata output created by R script

    params_out : dict
        dict of the output parameters list created by R script

    stdout : str
        string capturing the standard output of the R script

    stderr : str
        string capturing the standard error of the R script

    retcode : int
        return code of the R process

    success : bool
        True if retcode == 0

    Raises
    ------

    de_toolkit.wrapr.RExecutionError
        when *raise_on_error* is True, raise whenever R encounters an error

    Examples
    --------

    Basic usage accepts a path to an R script and loads the content of
    the file pointed to by *out.fn* in the R script into the *output*
    attribute:

    >>> with open('script.R','wt') as f :
            # note reference to implicitly defined *out.fn*
            # R variable
            f.write('write.csv(c(1,2,3,4),out.fn)')
    >>> r = WrapR('script.R',output_fn='test.csv')
    >>> r.execute()
    >>> r.output
       x
    1  1
    2  2
    3  3
    4  4
    >>> pandas.read_csv('test.csv',index_col=0)
       x
    1  1
    2  2
    3  3
    4  4

    Can also use a context manager when the output doesn't need to be
    written to a named file:

    >>> with WrapR('script.R') as r :
            r.execute()
            print(r.output)
       x
    1  1
    2  2
    3  3
    4  4

    The standard output of the R script can be accessed with the *stdout*
    attribute:

    >>> with open('euler.R','wt') as f :
            f.write('exp(complex(real=0,imag=pi))+1')
    >>> with WrapR('euler.R','wt') as r :
            r.execute()
            print(r.stdout)
    [1] 0+1.224647e-16i


    '''

    def __init__(self,
            rscript_path,
            counts=None,
            metadata=None,
            params=None,
            output_fn=None,
            metadata_out_fn=None,
            params_out_fn=None,
            rpath=None,
            raise_on_error=True,
            routput_dir=None
            ) :

        self._files = {}
        self._paths = defaultdict(str)

        # custom rpath
        self._paths['rpath'] = rpath or get_r_path()

        logger.debug('rpath: %s',self._paths['rpath'])

        # if routput_dir is specified, create the directory if necessary and
        # write all of the temporary files to it
        self.routput_dir = routput_dir
        self._tempdir = None
        if routput_dir is not None :
            pathlib.Path(routput_dir).mkdir(parents=True,exist_ok=True)
        else :
            self._tempdir = TemporaryDirectory()
            self.routput_dir = self._tempdir.name
        logger.debug('R output dir: %s',self.routput_dir)

        # load script code and put into the template that defines convenience
        # in/out filename variables
        with open(os.path.join(self.routput_dir,'script.R'),'wt') as f :
            self._files['rscript'] = f
            self._paths['rscript'] = f.name
            with open(os.path.realpath(rscript_path),'rt') as f_in :
                f.write(_script_tmpl.format(script=f_in.read()))
            f.flush()

        # write counts to tempfile
        with open(os.path.join(self.routput_dir,'counts.csv'),'wt') as f :
            self._files['counts_in'] = f
            self._paths['counts_in'] = f.name
            if counts is not None :
                counts.to_csv(self._files['counts_in'])
                f.flush()

        # set counts output file if provided, otherwise create temp file
        self._paths['output'] = output_fn
        if output_fn is None :
            self._files['output'] = open(
                    os.path.join(self.routput_dir,'counts_out.csv'),
                    'wt'
            )
            self._paths['output'] = self._files['output'].name

        # write metadata to tempfile if provided
        with open(os.path.join(self.routput_dir,'meta_in.csv'),'wt') as f :
            self._files['meta_in'] = f
            self._paths['meta_in'] = f.name
            if metadata is not None :
                metadata.to_csv(self._files['meta_in'])
                f.flush()

        # set metadata output file if provided, otherwise create temp file
        self._paths['meta_out'] = metadata_out_fn
        if metadata_out_fn is None :

            self._files['meta_out'] = open(
                    os.path.join(self.routput_dir,'meta_out.csv'),
                    'wt'
            )
            self._paths['meta_out'] = self._files['meta_out'].name

        # write out params json if provided
        with open(os.path.join(self.routput_dir,'params_in.json'),'wt') as f :
            self._files['params_in'] = f
            self._paths['params_in'] = f.name
            if params is not None :
                json.dump(params,f)
                f.flush()

        self._paths['params_out'] = params_out_fn
        if params_out_fn is None :
            self._files['params_out'] = open(os.path.join(self.routput_dir,'params_out.json'),'wt')
            self._paths['params_out'] = self._files['params_out'].name

        logger.debug('wrapr paths:\n %s',pformat(self._paths))

        # initialize output members
        self.output = None
        self.metadata_out = None
        self.params_out = None

        self.raise_on_error = raise_on_error

    @require_r
    def execute(self) :
        '''
        Execute the R script and load in the resulting output files, if any.
        '''

        # construct Rscript command
        cmd = ('{rpath} --vanilla {rscript} {counts_in} {meta_in} {params_in} '
               '{output} {meta_out} {params_out}').format(
                    **self._paths
               ).split(' ')
        logger.info('executing Rscript: %s', self._paths['rscript'])
        logger.debug(cmd)

        # run the R script
        p = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
        )

        self.process = p
        self.stdout = p.stdout.decode()
        logger.debug('R script stdout:\n %s',pformat(self.stdout))
        self.stderr = p.stderr.decode()
        logger.debug('R script stderr:\n %s',pformat(self.stderr))
        self.returncode = p.returncode
        logger.debug('R script return code: %d',self.returncode)
        self.success = p.returncode == 0

        if self.raise_on_error and not self.success :
            raise RExecutionError('R encountered an error:\n\n' +
                    'stdout:\n{}\n\n'.format(self.stdout) +
                    'stderr:\n{}\n'.format(self.stderr)
                )

        # read in the outputs
        if os.path.exists(self._paths['output']) :
            try :
                self.output = pd.read_csv(
                    self._paths['output'],
                    index_col=0
                )
            except pd.errors.EmptyDataError :
                logger.debug('No output was found, continuing')
                pass

        if os.path.exists(self._paths['meta_out']) :
            try :
                self.metadata_out = pd.read_csv(
                    self._paths['meta_out'],
                    index_col=0
                )
            except pd.errors.EmptyDataError :
                logger.debug('No metadata output was found, continuing')
                pass

        if os.path.exists(self._paths['params_out']) :
            logger.info('writing out R script params json to %s', self._paths['params_out'])
            with open(self._paths['params_out'],'rt') as f :
                json_str = f.read()
                if len(json_str) > 0 :
                    self.params_out = json.loads(json_str)

                    # jsonlite puts all elements of lists into arrays,
                    # recurse through params and replace length 1 lists
                    # with the value
                    def flat(e) :
                        if isinstance(e, dict) :
                            return {k:flat(v) for k,v in e.items()}
                        elif isinstance(e, list) :
                            if len(e) == 1 :
                                return flat(e[0])
                            else :
                                return [flat(_) for _ in e]
                        else :
                            return e
                    self.params_out = flat(self.params_out)

        logger.info('R script done executing')

    def __enter__(self) :
        logger.debug('entered WrapR context manager')
        return self
    def __exit__(self,*args)  :
        logger.debug('exitred WrapR context manager')
        # clean up the temp files if no r output directory was supplied
        if self._tempdir is not None :
            self._tempdir.cleanup()

def wrapr(Rcode,**kwargs) :
    '''Convenience wrapper for WrapR object. Writes *Rcode* to a temporary file
    and executes it as it would if it were provided.

    Parameters
    ----------

    Rcode : str
        string containing valid R code to be executed

    Returns
    -------

    obj
        A WrapR object executed with the code in input string

    Examples
    --------

    >>> with wrapr('write.csv(c(1,2,3,4),out.fn)') as r :
            print(r.output)
       x
    1  1
    2  2
    3  3
    4  4

    '''

    logger.info('wrapr() executing')
    with NamedTemporaryFile('wt') as f :
        logger.debug('writing R code to %s',f.name)
        logger.debug('R code:\n%s',pformat(Rcode))
        f.write(Rcode)
        f.flush()
        wr = WrapR(
            f.name,
            **kwargs
        )
        wr.execute()
        return wr

def main(argv=sys.argv) :

    if '--version' in argv :
        from .version import __version__
        print(__version__)
        return

    doc = _cli_doc(__doc__)

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in ('check','run')) :
        docopt(doc,argv=argv)
    argv = argv[1:]
    cmd = argv[0]

    args = docopt(doc,argv=argv)

    set_logging(args)
    logger.info('cmd: %s',' '.join(argv))

    if args['run'] :

        logger.info('Executing standalone R script')

        counts = None
        column_data = None

        if args['<counts_in>'] is not None :
            
            try :
                counts_obj = CountMatrixFile(
                      args['<counts_in>'],
                      args['--meta-in'],
                      strict=args.get('--strict',False)
                )
            except Exception as e :
                logger.error(e)
                sys.exit(1)

            logger.info('counts matrix created successfully')

            counts = counts_obj.counts
            column_data = counts_obj.column_data

        params = None
        if args['--params-in'] is not None and os.path.exists(args['--params-in']) :
            with open(args['--params-in'],'rt') as f :
                params = json.load(f)

        with WrapR(
            args['<rscript>'],
            counts,
            column_data,
            params=params,
            output_fn=args['<out>'],
            metadata_out_fn=args['--meta-out'],
            params_out_fn=args['--params-out'],
            rpath=args['--rpath'],
            routput_dir=args['--routput-dir']
            ) as wr :
            wr.execute()

    elif args['check'] :

        r = check_r()

        if not r :
            logger.error(RscriptExecutableNotFound(
                    'Rscript executable not found, wrapr interface and '
                    'functions will not work'
                ))
            sys.exit(1)

        logger.info('R found: %s',r)
        logger.info('R path: %s',get_r_path())

        jsonlite = check_r_package('jsonlite')
        logger.info('jsonlite found: %s',jsonlite)

        if not jsonlite :
            logger.error(RPackageMissing('ERROR: R package jsonlite must be installed, '
                  'wrapr interface and functions will not work'
            ))
            sys.exit(1)


if __name__ == '__main__' :

  main()
