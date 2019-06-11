import logging
import numpy
import pandas
from patsy import EvalFactor, ModelDesc, design_matrix_builders, dmatrices, PatsyError
from ply import lex
from pprint import pprint
import re

# setup logging, null on the library level
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class PatsyLiteParseError(Exception): pass

tokens = ('CONSTANT','FACTORTERM','RELATION','OP','COUNT')

t_COUNT = r'count'
t_CONSTANT = r'-?\d+(?:\.\d*)?'
#t_SIMPLETERM = r'\w[\w:*.()]*'
t_RELATION = r'~'
t_OP = r'[-+*/]'
t_ignore = ' '

#def t_BINARYTERM(t) :
#    r'(\w[^[]*)\[([^]]+)\]$'
#    t.term, t.args = t.lexer.lexmatch.groups()[1:3]
#    return t

def t_FACTORTERM(t) :
    r'([\w](?:[\w.():]+)?)(?:\[([^]]+)\])?'
    # this regex returns a bunch of empty groups for some reason
    # filter out the None valued groups and just operate on what
    # is left
    groups = [_ for _ in t.lexer.lexmatch.groups() if _][1:]
    if len(groups) == 1 :
        t.term = groups[0]
    elif len(groups) == 2 :
        args = groups[1]
        if ',' in args :
            t.term, t.levels = groups[0], args
            t.levels = t.levels.split(',')
        else :
            t.term, t.ref = groups[0], args
    return t

def t_error(t) :
    #print(t)
    return t

lexer = lex.lex()

def quote_var(v) :
    if any(_ in v for _ in '#.()[]@') :
        return 'Q("{}")'.format(v)
    return v

def repr_val(v) :
    try :
        return int(v)
    except :
        pass
    try :
        return float(v)
    except :
        pass
    return v

def patsy_lite_to_patsy(formula) :

    # I guess we assume there is always a lhs and a rhs?
    if '~' not in formula :
        raise PatsyLiteParseError('A ~ must be specified, so that there is a left '
            'and right hand side')

    lexer.input(formula)

    patsy_formula = []
    # the name map is attached to the model description and used later to
    # replace the patsy DesignInfo column names to the originals specified
    # in the formula
    name_map = {}

    while True:

        try :
            tok = lexer.token()
        except lex.LexError as e :
            raise PatsyLiteParseError('Error parsing formula:\n{}\n{}'.format(
                formula,e.args)
            )

        if not tok : break

        if tok.type in ('CONSTANT','RELATION','OP','COUNT') :
            patsy_formula.append(tok.value)

        # term
        # term[ref] -> C(term, Treatment("ref"))
        # term[lev1,lev2,lev3] -> C(term, levels=["lev1","lev2","lev3"])
        if tok.type == 'FACTORTERM' :
            if hasattr(tok,'ref') :
                term = 'C({}, Treatment({}))'.format(
                        quote_var(tok.term),
                        repr(repr_val(tok.ref))
                )
                name_map[term] = tok.term
                patsy_formula.append(term)
            elif hasattr(tok,'levels') :
                term = 'C({}, levels={})'.format(
                        quote_var(tok.term),
                        [repr_val(_) for _ in tok.levels]
                )
                name_map[term] = tok.term
                patsy_formula.append(term)
            else :
                term = quote_var(tok.value)
                patsy_formula.append(term)
                name_map[term] = tok.value

    patsy_formula = ' '.join(patsy_formula)
    model = ModelDesc.from_formula(patsy_formula)
    model.name_map = name_map
    return model

class ModelError(Exception): pass

class DesignMatrix(object) :

    def __init__(self,formula,model_data) :

        self._formula = formula
        logger.debug('DesignMatrix formula: %s',formula)
        self._model_data = model_data

        # when there is a categorical veriable on the lhs, the vector
        # space of all levels is included where, for example, we're only
        # interested in the vector space of the reference level for
        # logistic regression (i.e., one column with zero for reference
        # samples and one for the other)
        # with patsy we can control this by adding an intercept to the
        # lhs, which will acheive the desired result and has no effect
        # when including, e.g. continuous variables
        # we remove the Intercept term from the lhs before returning
        # the design matrix
        if not formula.strip().startswith('~') :
            formula = '1 + {}'.format(formula)

        model = patsy_lite_to_patsy(formula)
        logger.debug('transpiled patsy formula: %s',model.describe())

        try :
            self.lhs, self.rhs = dmatrices(
                model.describe()
                ,model_data
                ,return_type='dataframe'
            )
        except PatsyError as e :
            raise PatsyLiteParseError('Misspecified column in design, check term '
                'names. {}'.format(e.args))

        # patsy reorders the terms after calling dmatrices for some reason
        # rearrange them back again to what was specified in the design
        new_order = []
        for term in model.rhs_termlist :
            for col in self.rhs.columns:
                if col.startswith(term.name()) :
                    new_order.append(col)

        self.rhs = self.rhs[new_order]

        # the patsy formula names are ugly and not very machine (or human)
        # readable
        # replace the patsy names with the patsy lite names
        def rename_model_cols(c) :
            for k,v in model.name_map.items() :
                if k in c :
                    c = c.replace(k,v)
            # categorical variables sometimes look like
            # C(term, Treatment('cont'))[T.cont]
            # replace [T.cont] -> __cont
            cat_match = r'\[(?:T\.)?(\w*)\]'
            if re.search(cat_match,c) :
                c = re.sub(cat_match,r'__\1',c)
            return c

        self.lhs.rename(columns=rename_model_cols,inplace=True)
        self.rhs.rename(columns=rename_model_cols,inplace=True)

        # remove the Intercept term from the lhs that we added at the beginning
        self.drop_from_lhs('Intercept')

        logger.debug('final design: %s', self.design)

    @property
    def design(self) :
        lhs = ' + '.join(self.lhs.columns)
        rhs = ' + '.join(self.rhs.columns)
        # it is sometimes useful to have a trivial model, e.g. counts ~ 1
        if len(rhs) == 0 :
            rhs = '1'
        return ' '.join([
            lhs
            ,'~'
            ,rhs
        ])

    def drop_from_lhs(self,column,quiet=False) :
        try :
            self.lhs.drop(column,axis=1,inplace=True)
        except KeyError as e :
            if not quiet :
                raise ModelError('Cannot drop {} from lhs, does not exist'.format(column))

    def drop_from_rhs(self,column,quiet=False) :
        try :
            self.rhs.drop(column,axis=1,inplace=True)
        except KeyError as e :
            if not quiet :
                raise ModelError('Cannot drop {} from rhs, does not exist'.format(column))

    def head(self) :
        return self.full_matrix.head()

    @property
    def full_matrix(self) :
        return pandas.concat([self.lhs,self.rhs],axis=1)

    def augment(self,df,side) :
        '''Return a new DesignMatrix with the columns (or keys) of *df* appended to
        the left or right hand side

        '''
        if side == 'lhs' :
            new_design = '{} + {}'.format('+'.join(df.columns),self._formula)
        else :
            new_design = '{} + {}'.format(self._formula,'+'.join(df.columns))
        model_data = pandas.concat([self._model_data,df],axis=1)
        return DesignMatrix(new_design,model_data)

    def augment_lhs(self,df) :
        '''Return a new DesignMatrix with the columns (or keys) of *df* appended to
        the left hand side

        '''
        return self.augment(df,'lhs')

    def augment_rhs(self,df) :
        '''Return a new DesignMatrix with the columns (or keys) of *df* appended to
        the right hand side

        '''
        return self.augment(df,'rhs')

    def update_design(self,column,values) :
        '''Update the DesignMatrix *column* with *values*

        '''
        if column in self.lhs :
            self.lhs[column] = values
        elif column in self.rhs :
            self.rhs[column] = values
        else :
            raise ModelError(('Cannot replace values for column {}, '
                'column does not exist').format(column))
