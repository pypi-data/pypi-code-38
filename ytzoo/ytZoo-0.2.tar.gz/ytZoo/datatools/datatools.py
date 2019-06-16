'''
A collection of data science utilities.
Most of the class and functions are Pandas related.
'''
from __future__ import print_function

from .pandas_api import register_dataframe_booster

from functools import wraps
from ytZoo import xenumerate
import os
import sys, math
import numpy as np
import pandas as pd
import sqlite3

class SQL:
    "An database interface that integrated Dataframe and SQL."
    def __init__(self, database):
        self._conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
        self._conn.row_factory = sqlite3.Row

    def read_query(self, sql, index_col=None, coerce_float=True, params=None, parse_dates=None, chunksize=None):
        """Ported API from pd.read_sql_query."""
        return pd.read_sql_query(sql=sql,
                                con=self._conn,
                                index_col=index_col,
                                coerce_float=coerce_float,
                                params=params,
                                parse_dates=parse_dates,
                                chunksize=chunksize)
    def execute(self, sql, parameters=None):
        "Ported from sqlite3.Connection.execute()."
        return self._conn.execute(sql)
    
    def commit(self):
        "Commit changes."
        self._conn.commit()

    def executemany(self, sql, parameters, commit=True):
        """Ported from sqlite3.Connection.executemany().

        Parameters
        ==========
        commit : bool, default True
            Commit changes after executing the command.
        """
        status = self._conn.executemany(sql, parameters)
        if commit:
            self.commit()
        return status

    def close(self):
        self._conn.close()
    def tables(self):
        "Return a list of table names in the database."
        return self.read_query("""SELECT tbl_name FROM sqlite_master
                                WHERE type=='table'""")['tbl_name'].tolist()
    def columns(self, tbl_name):
        "Return a list of column names in a table."
        assert ' ' not in tbl_name, "Invalid table name '{}'".format(tbl_name)
        cursor = con.execute("select * from {} limit 1".format(tbl_name))
        names = list(map(lambda x: x[0], cursor.description))
        return names
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.close()

@register_dataframe_booster('merge')
@wraps(pd.merge)
def check_merge(left, *args, **kwargs):
    """Merge datasets and show statistics."""
    kwargs['indicator'] = True
    mg = left.merge(*args, **kwargs)
    # report stats
    stats = mg['_merge'].value_counts()
    stats.name = 'obs.'
    stats = stats.pipe(cum_freq)
    try:
        from IPython.core.display import display, HTML
        display(HTML(stats.to_html()))
    except ImportError:
        print(stats)
    return mg.drop('_merge', axis=1)

@register_dataframe_booster('update')
def check_update(master, withdf, match, columns):
    """Update columns in the master table with the updating table.
    Match records using 'match' as the key.
    """
    assert isinstance(
        columns, list), "columns must be a list, got {}.".format(columns)
    assert isinstance(
        match,   str), "match must be a string, got {}.".format(match)
    mastercols = master.columns
    withdfcols = withdf.columns
    for col in columns+[match]:
        assert col in mastercols, "Column '{}' not in master table.".format(col)
        assert col in withdfcols, "Column '{}' not in updating table.".format(col)

    # discard irrelevant columns in the updating table
    withdf = withdf[columns+[match]]
    # suffixes to distinguish master table columns from updating table columns
    sfx, sfy = suffixes = ('_x', '_y')
    mg = check_merge(master, withdf, 'left', '1:1',
                     on=match, suffixes=suffixes)

    # update values
    for col in columns:
        mask = mg[col+sfy].notnull()
        mg.loc[mask, col+sfx] = mg.loc[mask, col+sfy]
        mg.drop(col+sfy, 1, inplace=True)
        mg.rename(columns={col+sfx: col}, inplace=True)
    return mg

@register_dataframe_booster('viewpct')
def pct(dataframe, axis=0):
    """Transform values in each cell to percentages repecting to
    the axis selected.

    Example:
    df = 
        Row1 1 2 3
        Row2 1 2 3
    >>> df.pipe(pct, 1)
    Out:
        Row1 50% 50% 50%
        Row2 50% 50% 50%
        Total 100% 100% 100%
    """
    if axis == 0:
        prepare = dataframe.pipe(sumup, 0, 1)
        prepare = prepare.div(prepare['Total'], axis=0)
    if axis == 1:
        prepare = dataframe.pipe(sumup, 1, 0)
        prepare = prepare.div(prepare.loc['Total', :], axis=1)
    prepare = prepare.applymap(lambda x: "{:.0%}".format(x))
    return prepare


def format_percentage(n, precision='auto'):
    """Display a decimal number in percentage.
    
    Parameters
    =========
    n : float
        The number to format.
    percision: int, str, default 'auto'
        The precision of outcome. Default 'auto' to automatically
        choose the least precision on which the outcome is not zero.

    Examples
    ========
    format_percentage(0.001) ==> '0.1%'
    format_percentage(-0.0000010009) ==> '-0.0001%'
    format_percentage(0.001, 4) ==> '0.1000%'
    """
    if precision == 'auto':
        if n != 0:
            k = abs(n)*100
            cnt = 0
            while k < 1:
                k = k * 10
                cnt += 1
            precision = cnt
        else:
            precision = 0
    fmt = '{:.'+str(precision)+'%}'
    return fmt.format(n)

@register_dataframe_booster('fmt')
def format_dataframe(dataframe, big=0, pct='auto'):
    """Automatically format a dataframe with business readings and percentages.
    
    Parameters
    ==========
    dataframe : pd.DataFrame
    big : int, default 0
        Precision for big numbers.
    pct : int, default 'auto'
        Precision for percentage numbers.
    """
    df = dataframe.copy()

    def is_pct(srs):
        if ('pct' in srs.name.lower()) or ('%' in srs.name) \
            or ('percent' in srs.name.lower()):
            return True
        return False
    allcols = set(df.columns)
    pctcols = {col for col in allcols if is_pct(df[col])}
    numcols = allcols - pctcols
    pctcols = list(pctcols)
    numcols = list(numcols)
    df[pctcols] = df[pctcols].applymap(lambda x: format_percentage(x, pct))
    df[numcols] = df[numcols].applymap(lambda x: bignum(x, big))
    return df

@register_dataframe_booster('markup')
def markup(dataframe, precision=0):
    """ Apply human readble formats and add total column and row """
    if isinstance(dataframe, pd.Series):
        dataframe = dataframe.to_frame()
    return dataframe.pipe(sumup, 1, 1).applymap(lambda x: bignum(x, precision))

@register_dataframe_booster('sumup')
def sumup(dataframe, row=True, column=False):
    """ Add a total row and/or a total column"""
    if row:
        rowtot = dataframe.sum(0).T
        if isinstance(dataframe.index, pd.core.index.MultiIndex):
            row_idx_lvls = len(dataframe.index.levels)
            tot_row_name = [''] * row_idx_lvls
            tot_row_name[0] = 'Total'
            rowtot.name = tuple(tot_row_name)
        else:
            rowtot.name = 'Total'
        dataframe = dataframe.append(rowtot, ignore_index=False, sort=True)
        # dataframe = pd.concat([dataframe, rowtot], axis=0, sort=False)
    if column:
        coltot = dataframe.sum(1)
        coltot.name = 'Total'
        dataframe['Total'] = coltot
        # dataframe = pd.concat([dataframe, coltot], axis=1, sort=False)
    return dataframe

def bignum(n, precision=0):
    """ Transform a big number into a business style representation.
    
    Example:
    >>> bignum(123456)
    Output: 123K
    """
    millnames = ['', 'K', 'M', 'B', 'T']
    try:
        n = float(n)
        millidx = max(0, min(len(millnames)-1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        fmt = '{:.'+str(precision)+'f} {}'
        return fmt.format(n / 10**(3 * millidx), millnames[millidx])
    except ValueError:
        return n

@register_dataframe_booster('nmissing')
def nmissing(dataframe, show_all=False):
    """ Evaluate the number of missing values in columns in the dataframe """
    total = dataframe.shape[0]
    missing = pd.isnull(dataframe).sum().to_frame(name='nmissing')
    missing['pctmissing'] = (missing.nmissing / total * 100).apply(int) / 100
    missing.sort_values(by='nmissing', inplace=True)
    missing.reset_index(inplace=True)
    if not show_all:
        missing = missing.loc[missing.nmissing > 0]
    return missing

@register_dataframe_booster('nlevels')
def nlevels(dataframe, show_values=True):
    """Report the number of unique values (levels) for each variable. 
    Useful to inspect categorical variables.
    """
    nlvl = dataframe.nunique()
    cnt = dataframe.count().to_frame('obs')
    dtype = dataframe.dtypes.to_frame('dtype')
    levels = nlvl.to_frame('levels').join([cnt, dtype])
    levels.loc[levels.obs==0, 'obs'] = np.nan
    if show_values:
        r = []
        for li in dataframe.columns:
            unique_values = dataframe[li].unique()
            sample = ', '.join(map(str, unique_values[:5]))
            if len(unique_values) > 5:
                sample += ', ...'
            r.append(sample)
        levels['values'] = r
    levels.loc[:, 'uniqueness'] = (levels.levels / levels.obs)
    levels = levels.sort_values('uniqueness', ascending=False)
    return levels[['levels', 'obs', 'dtype', 'uniqueness', 'values']]

def cum_freq(series):
    """Return a dataframe showing the percentage, cumulative percentage, 
    and cumulative frequency of a series.
    """
    series.name='freq'
    df = pd.DataFrame(series)
    df['pct'] = series / series.sum()
    df['cumfreq'] = series.cumsum()
    df['cumpct'] = df.cumfreq / series.sum()
    return df

def df_to_sql(database, table, df, auto_str=False, if_exists='fail'):
    '''Write the {df} to the {table} in the {database}.
    Specify if_exists='replace' to replace an existing table. Set auto_str to true
    to automatically turn non-numerical data to string.'''
    import sqlite3
    if auto_str:
        for li in df:
            dtype = str(df[li].dtype)
            if ('int' not in dtype) and ('float' not in dtype):
                df[li] = df[li].astype(str)
    conn = sqlite3.connect(database)
    try:
        conn.text_factory = lambda x: x.decode('utf-8', 'ignore')
        df.to_sql(table,conn,if_exists='fail')
    finally:
        conn.close()
    
def collect(filelist, file_reader, ignore_error=False, verbose=True):
    '''collect pieces of dataframe with the same variables and merge them together'''
    def read_file(fpath):
        df = None
        try:
            df = file_reader(fpath)
        except:
            if ignore_error==True:
                pass
        return df
    if verbose:
        print("Processing {} elements..".format(len(filelist)))
    r=[]
    len_last_sentence = 0
    for s,li in xenumerate(filelist):
        if verbose:
            print(' '*len_last_sentence, end='\r') # erase last printout
            s = "{} processing {}".format(s, li)
            len_last_sentence = len(s)
            print(s, end='\r')
        r.append(read_file(li))
    return r
