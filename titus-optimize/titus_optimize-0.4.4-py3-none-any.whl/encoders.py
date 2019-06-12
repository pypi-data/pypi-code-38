import numpy as np
import pandas as pd
from pandas import Categorical
from pandas.core.frame import DataFrame

def is_bow_col(probe_df, col_name):
    """
    Check whether or not a given column has values that are Bag-of-Word
    """
    for r in probe_df.itertuples(index=False):
        v = getattr(r, col_name)
        if v is not None:
            return type(v) == list or type(v) == tuple or type(v) == np.ndarray
    raise Exception("Impossible to assert whether or not column `%s` is a BoW: the column is null" % (col_name,))

def is_dense_bow_col(probe_df, col_name):
    """
    Check if a column has dense Bag-of-Words values. These are valid values
    for a dense Bag-of-Words column:
    [1.6, -7.1]
    (-5.4, 0.0, 8.6)
    [3, 8, 9]
    """
    if not is_bow_col(probe_df, col_name):
        return False
    for r in probe_df.itertuples(index=False):
        v = getattr(r, col_name)
        if v is not None and len(v) > 0:
            if type(v[0]) == tuple:
                return False
            return type(v[0]) == int or type(v[0]) == float or np.issubdtype(v[0], np.number)
    raise Exception("Impossible to assert whether or not column `%s` is a dense BoW: the column has no non-empty BoWs" % (col_name,))

class DenseIntEncoder(object):
    def __init__(self):
        self.column_names = {} # keys: 'all', 'continuous', 'categorical', 'dense_bow'
        self.lookup_index = {} # keys: column names
        self.reverse_lookup = []

    def transform(self, data_frame, batch_sz = 2048):
        """
        This function dictionary-encode the categoricals of a dataframe
        one mini-batch at a time from the previously learnt mapping.
        It returns an iterator of np.array encoded mini-batches.
        The reason for doing it by mini-batches is to amortize all the
        python slowness costs, while avoiding allocating the whole
        transformed matrix at once.
        Supports columns with NaN values.
        Supports columns that have dense BoW values: [0.0, 0.0, 2.0, 0.0, 1.0]
        """
        if not isinstance(data_frame, DataFrame):
            raise Exception("Only works on pandas DataFrames")

        df = data_frame.reset_index()
        df.drop(["index"], axis=1, inplace=True)

        sz = len(df)
        curr_sz = 0

        tot_num_cols = len(self.reverse_lookup)

        buffer = np.zeros((batch_sz, tot_num_cols), dtype=np.float32)

        while curr_sz < sz:
            sliced_df = df.iloc[curr_sz : curr_sz + batch_sz]
            sliced_df = sliced_df.reset_index()
            sliced_df.drop(["index"], axis=1, inplace=True)
            n = len(sliced_df)

            for c in self.column_names['all']:
                if c in self.column_names['continuous']:
                    serie = sliced_df[c]
                    buffer[:n, self.lookup_index[c]] = serie

                else: # categorical
                    if c in self.column_names['dense_bow']:
                        col_offset, d = self.lookup_index[c]
                        indices = sorted(d.values())
                        for cat_ind, mapped_ind in enumerate(indices):
                            buffer[:n, mapped_ind] = [e[cat_ind] if e is not None else np.nan for e in sliced_df[c]]

                    else: # regular categorical
                        col_offset, d = self.lookup_index[c]
                        for ind_it, cv in enumerate(sliced_df[c]):
                            ind_c = d.get(cv, np.nan)
                            buffer[ind_it, col_offset] = ind_c
                        
            curr_sz += batch_sz
            yield buffer[:n,:]
    
    def transform_single(self, row):
        tot_num_cols = len(self.reverse_lookup)
        res = np.zeros((1, tot_num_cols), dtype=np.float32)
        for c in self.column_names['all']:
            if c in self.column_names['continuous']:
                res[0, self.lookup_index[c]] = getattr(row, c)
            else: # categorical
                if c in self.column_names['dense_bow']:
                    col_offset, d = self.lookup_index[c]
                    indices = sorted(d.values())
                    v = getattr(row, c)
                    if v is None:
                        res[0, indices] = np.nan
                    else:
                        for cat_ind, mapped_ind in enumerate(indices):
                            res[0, mapped_ind] = v[cat_ind] if v[cat_ind] is not None else np.nan
                else: # regular categorical
                    col_offset, d = self.lookup_index[c]
                    res[0, col_offset] = d.get(getattr(row, c), np.nan)
        return res

    def fit_transform(self, data_frame, drop_original=False):
        """
        The output is an np.array where string columns have been replaced
        with their dictionary integer-encoded values, and BoW columns have
        been expanded in individual columns.
        Supports columns with NaN values.
        Supports columns that have dense BoW values: [0.0, 0.0, 2.0, 0.0, 1.0]
        """
        if not isinstance(data_frame, DataFrame):
            raise Exception("Only works on pandas DataFrames")

        data = data_frame.reset_index()
        data.drop(["index"], axis=1, inplace=True)


        self.column_names['all'] = data.columns
        cat_cols = data.select_dtypes(include=['object', 'category']).columns
        self.column_names['categorical'] = cat_cols
        cont_cols = [c for c in data.columns if c not in cat_cols]
        self.column_names['continuous'] = cont_cols
        self.column_names['dense_bow'] = []

        N = len(data)
        
        all_column_names = list(data.columns)
        D = 0 # total number of columns, after exploding of BoW ones
        # first quick pass to determine D and populate
        # column index lookups for non-categorical features
        for c in all_column_names:
            if c not in cat_cols:
                self.lookup_index[c] = D
                D += 1
            elif not is_bow_col(data, c):
                D += 1
            elif is_dense_bow_col(data, c):
                self.column_names['dense_bow'].append(c)
                codes = []
                for v in data[c]:
                    if v is not None and len(v) > 0:
                        codes = [D + i for i in range(len(v))]
                        break
                if len(codes) == 0:
                    raise Exception("The dense bow column `%s` has only empty or None values." % (c,))
                self.lookup_index[c] = [D, {str(i): c for i, c in enumerate(codes)}]
                D += len(codes)
            else:
                raise Exception("Type in column %s is not supported." % (c,))
        
        # Now initialize and populate the encoded matrix
        res = np.zeros((N, D), dtype=np.float32)
        
        offset_col = 0
        for c in all_column_names:
            if c not in cat_cols:
                res[:,offset_col] = data[c].values
                offset_col += 1
            else:
                serie = data[c]
                if c not in self.column_names['dense_bow']:
                    cat = Categorical(serie.values, ordered=False)
                    codes = np.where(cat.codes >= 0,cat.codes,np.nan)
                    
                    res[:,offset_col] = codes
                    
                    mapping = {}
                    for ind, cv in enumerate(cat.categories):
                        mapping[cv] = ind
                    self.lookup_index[c] = [offset_col, mapping]
                    offset_col += 1 
                else:
                    num_codes = len(self.lookup_index[c][1])
                    for ii in range(num_codes):
                        res[:,offset_col + ii] = [e[ii] if e is not None else np.nan for e in serie]
                    offset_col += num_codes
            if drop_original:
                data.drop([c], axis=1, inplace=True)
        
        # build reverse lookup
        self.reverse_lookup = [None] * offset_col
        for col_name, v in self.lookup_index.items():
            if type(v) == int:
                self.reverse_lookup[v] = col_name
            else:
                if col_name in self.column_names['dense_bow']:
                    for category, ind_cat in v[1].items():
                        self.reverse_lookup[ind_cat] = (col_name, category)
                else:
                    # in the case of categorical - return col_name and mapping to categories
                    self.reverse_lookup[v[0]] = (col_name,v[1])
        if not drop_original:
            return res
        return res, data

    def get_continuous_col_index(self, name):
        """
        Given a continuous column name, returns its encoded column index.
        """
        return self.lookup_index[name]

    def get_categorical_col_index(self, name, category = None):
        """
        Given a categorical column name and the category, returns its encoded
        column index (post one-hot). If `category` is not specified, returns
        all the encoded indices of the column.
        """
        if category is not None:
            return self.lookup_index[name][category]
        else:
            return sorted(self.lookup_index[name].values())