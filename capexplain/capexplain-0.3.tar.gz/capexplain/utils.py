import datetime
import traceback
from itertools import combinations, permutations
from math import factorial
from tqdm import tqdm

def printException(ex,finfo):
    print(exceptionToString(ex,finfo))

def exceptionToString(ex,finfo):
    trace=traceback.format_stack()
    trace=trace[:-3]
    formatStr = '{}\n\nEXCEPTION:{}\n\n{}\n\nSTACK TRACE\n-----------\n{}'
    return formatStr.format(formatCurFileAndLine(finfo),
                            type(ex),
                            ex,
                            "\n".join(trace))

def formatCurFileAndLine(finfo):
    return 'FILE: {0.filename} LINE: {0.lineno}:'.format(finfo) 

def projection(t, cols):
    res = list()
    for c in cols:
        if c in t:
            res.append(t[c])
    return res
    # return list(map(lambda x: t[x], cols))

def get_F_value(F, t):
    return projection(t, F)

def get_V_value(V, t):
    return projection(t, V)

def is_float(s):
    try:
        if isinstance(s, float) or isinstance(s, int) or isinstance(s, str):
            float(s)
            return True
        else:
            return False
    except ValueError:
        return False

def is_integer(s):
    try:
        if isinstance(s, str) and s[-1] == 'L':
            int(s[0:-1])
        else:
            int(s)
        return True
    except ValueError:
        return False

def float_or_integer(s):
    if is_float(s):
        return float(s)
    elif is_integer(s):
        return int(s[0:-1]) if s[-1] == 'L' else int(s)
    else:
        return s

def tuple_column_to_str_in_where_clause(col_value):
    if is_float(col_value):
        return '=' + str(col_value)
    else:
        return "like '%" + col_value + "%'"

def normalize_numerical_distance(df=None, cur=None, table_name=''):
    '''
        get the min value, max value, and the range of each column in the data frame
    '''
    if df is not None:
        res = {}
        max_vals = df.max()
        min_vals = df.min()
        for col in df:
            if col == 'index':
                continue
            if df[col].dtype.kind != 'S' and df[col].dtype.kind != 'O':
                res[col] = {'max':{}, 'min':{}, 'range':{}}

                res[col]['max'] = float(max_vals[col])
                res[col]['min'] = float(min_vals[col])
                res[col]['range'] = res[col]['max'] - res[col]['min']
        return res
    else:
        res = {}
        column_name_query = "SELECT column_name FROM information_schema.columns where table_name='{}';".format(table_name)
        cur.execute(column_name_query)
        column_name = cur.fetchall()

        max_clause = ', '.join(map(lambda x: 'MAX(' + x + ')',
            map(lambda x: x[0] if x[0] != 'arrest' and x[0] != 'domestic' else '1', column_name)))
        max_query = "SELECT {} FROM {};".format(max_clause, table_name)
        cur.execute(max_query)
        max_vals = cur.fetchall()[0]
        min_clause = ', '.join(map(lambda x: 'MIN(' + x + ')',
            map(lambda x: x[0] if x[0] != 'arrest' and x[0] != 'domestic' else '1', column_name)))
        min_query = "SELECT {} FROM {};".format(min_clause, table_name)
        cur.execute(min_query)
        min_vals = cur.fetchall()[0]
        for idx, col_res in enumerate(column_name):
            col = col_res[0]
            res[col] = {'max':None, 'min':None, 'range':None}
            print('IN NORM', col, max_vals[idx], min_vals[idx])
            if is_float(max_vals[idx]) and is_float(min_vals[idx]):
                res[col]['max'] = float(max_vals[idx])
                res[col]['min'] = float(min_vals[idx])
                res[col]['range'] = res[col]['max'] - res[col]['min']
            else:
                if isinstance(max_vals[idx], datetime.date):
                    res[col]['max'] = max_vals[idx]
                    res[col]['min'] = min_vals[idx]
                    res[col]['range'] = res[col]['max'] - res[col]['min']
        return res

################################################################################
class CombinationsWithLen():
    """
    Wrapping a combinations generator to provide its length without having to iterate through all elements
    """

    def __init__(self,it,r):
        self._inLen = len(it)
        self._it = it
        self._r = r
        self._comb=combinations(it,r)

    def __iter__(self):
        for el in self._comb:
            yield el

    def __len__(self):
        return factorial(self._inLen) // (factorial(self._inLen - self._r)) // factorial(self._r)

def progress_iter(iter, showProgress=True, desc=None):
    if (showProgress == True):
        return tqdm(iter, desc=desc)
    else:
        return iter
    
################################################################################
class PermutationsWithLen():
    """
    Wrapping a permutations generator to provide its length without having to iterate through all elements
    """

    def __init__(self,it,r):
        self._inLen = len(it)
        self._it = it
        self._r = r
        self._perms=permutations(it,r)

    def __iter__(self):
        for el in self._perms:
            yield el

    def __len__(self):
        return factorial(self._inLen) // (factorial(self._inLen - self._r))
