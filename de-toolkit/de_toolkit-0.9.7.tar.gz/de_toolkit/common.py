r'''
Usage:
    detk norm [options] <args>...
    detk de [options] <args>...
    detk transform [options] <args>...
    detk filter [options] <args>...
    detk stats [options] <args>...
    detk outlier [options] <args>...
    detk wrapr [options] <args>...
    detk report [options] <args>...
    detk util [options] <args>...
'''
from collections import OrderedDict
from copy import deepcopy
from docopt import docopt
import logging
import pandas
from pprint import pformat
import re
import sys
import warnings
from .patsy_lite import DesignMatrix, PatsyLiteParseError
from .version import __version__

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_cli_version = '''\
detk version: {}\n
'''.format(__version__)

_cli_common_opts = '''\

Common options:
    -d CHAR --out-delim=CHAR  Delimiter to use for output file [default: ,]
    --report-dir=DIR          Specify the report directory [default: ./detk_report]
    --no-report               Do not generate the HTML report
    --version                 Print out detk version and exit
    -v --verbose              Make log output verbose
    -q --quiet                Turn off all logging except warnings and errors
    --shut-up                 Turn off ALL logging
'''

def _cli_doc(src) :
    'Add the common command line arguments to the given *src* docopt string'
    return _cli_version+src+_cli_common_opts

banner = r'''
===========================
        _      _   _    
       | |    | | | |   
     __| | ___| |_| | __
    / _` |/ _ \ __| |/ /
   | (_| |  __/ |_|   < 
    \__,_|\___|\__|_|\_\
                        
 de-toolkit.readthedocs.io
 Version: {}
==========================='''.format(__version__)
def set_logging(opts) :
    if not opts['--shut-up'] :
        if opts['--quiet'] :
            level = logging.WARNING
        elif opts['--verbose'] :
            level = logging.DEBUG
        else :
            level = logging.INFO

        logging.basicConfig(
                format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
                level=level
        )

        logger.debug('Set logging level to %d',level)
        logger.info(banner)
        logger.info('detk version: %s',__version__)

def make_cli_count_obj(args) :
    logger.info('constructing counts matrix from %s and %s',
            args.get('<counts_fn>'),args.get('<cov_fn>'))
    logger.info('design is %s',args.get('<design>'))
    try :
        count_obj = CountMatrixFile(
            args.get('<counts_fn>'),
            args.get('<cov_fn>'),
            design=args.get('<design>'),
            strict=args.get('--strict',False)
        )
    except Exception as e :
        logger.error(e)
        sys.exit(1)

    logger.info('counts matrix created successfully')

    return count_obj

def write_output(df,args) :

    if args['--output'] == 'stdout' :
        f = sys.stdout
        logging.info('writing result to stdout')
    else :
        f = args['--output']
        logging.info('writing result to %s',f)

    df.to_csv(f,sep=args.get('--out-delim',','))

    logging.info('finished writing output')

class InvalidDesignException(Exception): pass
class SampleMismatchException(Exception): pass

class CountMatrix(object) :
    def __init__(self
            ,counts
            ,column_data=None
            ,design=None
            ,strict=False
         ) :

        self.strict = strict

        if column_data is not None :
            # line up the sample names from the column_data and counts matrices
            if strict and (
                len(column_data.index) != len(counts.columns) or
                not all(column_data.index == counts.columns)
            ) :
                raise SampleMismatchException('When *strict* is supplied, the columns '
                    'of the counts file must correspond exactly to the row names in the '
                    'column_data matrix')
            else :
                common_names = counts.columns.intersection(column_data.index)

                logger.debug('common names between counts and column data:\n %s', pformat(common_names))

                # fix to "no memory available" bitbucket issue #4 when matrices are
                # empty
                if len(common_names) < 2 :
                    raise SampleMismatchException('No sample names were found to be in '
                        'common between the counts and column data or specified sample '
                        'names. Check that the first column of the column_data matrix '
                        'and the first row of the counts matrix contain at least 2 values '
                        'in common')

                counts = counts[common_names]
                column_data = column_data.loc[common_names]

        # if the design is provided, it must have a 'counts' term somewhere
        if design is not None and 'counts' not in design :
            raise InvalidDesignException('The term "counts" must exist on at least one '
                'side of the CountsMatrix design')

        # set the things
        self.counts = counts
        logger.info('counts matrix has shape: %s',self.counts.shape)

        self.column_data = column_data
        if column_data is not None:
            logger.info('column data matrix has shape: %s',self.column_data.shape)
        else :
            logger.info('column data was not provided')

        # set the design no matta wat
        self._design_matrix = None
        self.design = self._original_design = design
        logger.info('design: %s',design)
        logger.debug('full design:\n %s',pformat(self.design_matrix))

        #TODO this is not yet implemented or thought out
        # members to keep track of count mutations
        self.transformed = {}
        self.normalized = {}

    @property
    def column_data(self) :
        return self._column_data

    @column_data.setter
    def column_data(self,column_data) :
        # if column_data does not have a counts column, add one with trivial values
        # so things work
        if column_data is not None and 'counts' not in column_data :
            column_data['counts'] = 0

        self._column_data = column_data

        # update the design matrix by setting the design to itself
        self.design = self.design

    @property
    def design(self) :
        if hasattr(self,'design_matrix') and self.design_matrix is not None :
            return self.design_matrix.design
        if hasattr(self,'_design') :
            return self._design
        return None

    @design.setter
    def design(self,design) :
        self._design = design
        if design is not None and self.column_data is not None :
            try :
                self.design_matrix = DesignMatrix(design,self.column_data)
            except PatsyLiteParseError as e :
                raise InvalidDesignException('Invalid design, patsy lite could not parse '
                    '{}'.format(e.args))

            # check if the full design matrix has lost any rows due to
            # missing data
            if self.design_matrix.full_matrix.index.size != self.column_data.index.size :
                msg = ('The full design matrix rows do not match the input column '
                       'data matrix, likely due to some missing fields. '
                       '# design matrix rows: {}, # column data rows: {}. '.format(
                           self.design_matrix.full_matrix.index.size,
                           self.column_data.shape[0]
                       ))

                if self.strict :
                    raise SampleMismatchException(msg+'Aborting.')
                else :
                    warnings.warn(msg+'Adjusting the counts matrix and column '
                                      'data to fit.')
                    logger.warn(msg+'Adjusting the counts matrix and column '
                                      'data to fit.')
                    logger.warn('counts shape prior to fit: %s', self.counts.shape)
                    logger.warn('column data prior to fit: %s', self.column_data.shape)
                    self.counts = self.counts[self.design_matrix.full_matrix.index]
                    self._column_data = self.column_data.loc[self.design_matrix.full_matrix.index]

                    logger.warn('counts shape after fit: %s', self.counts.shape)
                    logger.warn('column data after fit: %s', self._column_data.shape)

        elif design is not None and self.column_data is None :
            raise InvalidDesignException('There must be column data associated with a '
            'CountMatrix object before specifying a design')

    @property
    def design_matrix(self) :
        return self._design_matrix

    @design_matrix.setter
    def design_matrix(self,design_matrix) :
        self._design_matrix = design_matrix

    @property
    def sample_names(self) :
        return self.counts.columns

    @sample_names.setter
    def sample_names(self,value):
        try :
            self.counts = self.counts[value]
        except Exception as e :
            raise Exception('Sample names provided that are not contained in the '
                'counts matrix')

    @property
    def feature_names(self) :
        return self.counts.index

    @feature_names.setter
    def feature_names(self,value):
        try :
            self.counts = self.counts.loc[value]
        except Exception as e :
            raise Exception('Feaure names provided that are not contained in the '
                'counts matrix')

    def copy(self) :
        return deepcopy(self)

    def transform(self,transf) :
        self.transformed[transf.__name__] = transf(self)

    def add_normalized(self,method='deseq2') :
        pass

class CountMatrixFile(CountMatrix) :

    def __init__(self
        ,count_f
        ,column_data_f=None
        ,design=None
        ,**kwargs
     ) :

        counts = pandas.read_csv(
            count_f
            ,sep=None # sniff the format automatically
            ,engine='python'
            ,index_col=0
        )

        column_data = None
        if column_data_f is not None :
            column_data = pandas.read_csv(
                column_data_f
                ,sep=None
                ,engine='python'
                ,index_col=0
            )

        CountMatrix.__init__(self
            ,counts
            ,column_data=column_data
            ,design=design
            ,**kwargs
        )

class DetkModule(OrderedDict) :
    '''
    Base class for all detk methods.

    Each function in detk is a subclass of this class.
    A module has the following properties:
    - ``name``: name of the module
    - ``params``: the module-dependent params passed to the module
    - ``output``: the output of the module in tabular form
    - ``properties``: properties and statistics about the module, used for
        formatting the results into a report

    All of these properties are JSON serializable, i.e. basic python
    types (int, float, str, bool, array, dict).
    '''
    @property
    def json(self) :
        '''
        Format the module object into a form amenable to serializing with JSON
        for report creation. By default this returns all of the module-level
        fields except output. Override if additional serialization is needed.
        '''
        return {
                   'name': self.name
                   ,'params': self.params
                   ,'properties': self.properties
               }
    @property
    def params(self) :
        '''
        Override this method to return a dictionary with relevant parameters
        for the method.
        '''
        return self.get('params',{})
    @property
    def output(self) :
        '''
        Override this method to return a tabular form of the output. Can be
        any rectangular-shaped object (i.e. list of lists, pandas.DataFrame,
        numpy array, etc)
        '''
        return []
    @property
    def properties(self) :
        '''
        Override this method to return a dictionary with relevant properties
        for the method. These might include metadata or summary statistics of
        the output that would not otherwise be included. Primarily used in the
        construction of report sections.
        '''
        return self.get('properties',{})
    @property
    def name(self) :
        'Name of this stats object, by default the class name in all lower case'
        return self.__class__.__name__.lower()


def main(argv=sys.argv) :

    if '--version' in argv :
        print(__version__)
        return

    cmds = 'norm','de','transform','filter','stats','outlier','wrapr','help'

    if len(argv) < 2 or (len(argv) > 1 and argv[1] not in cmds) :
        docopt(_cli_doc(__doc__))
    cmd = argv[1]

    # the individual main methods expect an executable of the form
    # detk-<mode>, but here the detk and mode come as separate arguments
    # concatenate them together and pass them on
    cli_args = ['-'.join(argv[:2])]+argv[2:]

    if cmd == 'norm' :
        from .norm import main
        main(cli_args)
    elif cmd == 'de' :
        from .de import main
        main(cli_args)
    elif cmd == 'enrich' :
        from .enrich import main
        main(cli_args)
    elif cmd == 'transform' :
        from .transform import main
        main(cli_args)
    elif cmd == 'filter' :
        from .filter import main
        main(cli_args)
    elif cmd == 'stats' :
        from .stats import main
        main(cli_args)
    elif cmd == 'outlier' :
        from .outlier import main
        main(cli_args)
    elif cmd == 'wrapr' :
        from .wrapr import main
        main(cli_args)
    elif cmd == 'help' :
        docopt(__doc__,['-h'])


if __name__ == '__main__' :
    main()
