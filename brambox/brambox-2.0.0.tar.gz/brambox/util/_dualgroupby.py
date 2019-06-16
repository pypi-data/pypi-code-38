#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   GroupBy operation on 2 datasets together (eg. annotations and detections)
#
#   TODO:
#   Split apply in 3 different APIs
#       - [X] apply: expose all variables through pandas dataframes (slow, but easier to work with for end user)
#       - [X] np_apply:  work with ndarray from start to finish (faster, when fancy pandas stuff not needed)
#       - [ ] c_apply: Cythonized apply that works with prange for multithreaded execution
#
import numpy as np
import pandas as pd
from ._pd import np_col

__all__ = ['DualGroupBy']


class DualGroupBy:
    """ This class provides a way to perform a GroupBy operation on 2 datasets at once.
    This is usefull if you want to perform statistics on both annotations and detections.
    You would then group both datasets by images and perform your statistics for each image on both subsets.

    Args:
        df1 (pandas.DataFrame): The first dataframe you want to perform grouped operations on
        df2 (pandas.DataFrame): The second dataframe you want to perform grouped operations on
        key (string): The name of the column you want to group by

    Warning:
        While this class works pretty similar to the pandas.groupby operation,
        not all functionality from the latter is implemented. |br|
        If you feel like something useful is missing, feel free to implement it and send a PR.

    Example:
        >>> det = bb.io.load(...)   # detection dataframe
        >>> anno = bb.io.load(...)  # annotation dataframe
        >>> number_of_boxes = bb.util.DualGroupBy(det, anno, 'image').apply(lambda d, a: len(d)+len(a))
        >>> print(number_of_boxes)
        >>> # number_of_boxes will be a dataframe with 1 column containing the sum of det and anno per image
    """
    def __init__(self, df1, df2, key):
        assert key in df1.columns and key in df2.columns, f'[{key}] not available in both DataFrames'

        self.key = key
        self._df1 = df1
        self.df1 = {col: np_col(df1, col) for col in df1.columns}
        self.df2 = {col: np_col(df2, col) for col in df2.columns}

        self.lendf1 = self.df1[key].shape[0]
        self.keys, keys_as_int = np.unique(np.concatenate([self.df1[key], self.df2[key]]), return_inverse=True)
        self.num_keys = keys_as_int.max()
        self.df1_intkeys, self.df2_intkeys = np.split(keys_as_int, self.df1[key].shape)
        self.df1_idx = self._set_indices(self.df1_intkeys)
        self.df2_idx = self._set_indices(self.df2_intkeys)

    def _set_indices(self, keys_as_int):
        indices = [[] for i in range(self.num_keys+1)]
        for i, k in enumerate(keys_as_int):
            indices[k].append(i)
        return [np.array(elt, dtype=np.int64) for elt in indices]

    def apply(self, fn):
        """ Applies a function on the grouped subsets of both datasets.

        Args:
            fn (callable): A function that takes 2 dataframes as input and needs to return a value or dataframe

        Returns:
            pandas.DataFrame: DataFrame with the results from the function *fn* on each group.
        """
        def fn_wrapper(sub_df1):
            try:
                idx = np.where(self.keys == sub_df1.name)[0][0]
                sub_df2 = pd.DataFrame({col: val[self.df2_idx[idx]] for col, val in self.df2.items()}, index=self.df2_idx[idx])
            except IndexError:
                sub_df2 = pd.DataFrame({col: val[0:0] for col, val in self.df2.items()})
            return fn(sub_df1, sub_df2)

        return self._df1.groupby(self.key, sort=False).apply(fn_wrapper)

    def np_apply(self, fn, shape=None, dtype=np.object, default=np.nan):
        """ Faster apply version that uses dictionaries of numpy arrays instead of pandas dataframes.

        Args:
            fn (callable): A function that takes 2 dictionaries (of numpy arrays) and needs to return a number or numpy array
            shape (list): The shape of the output array that is returned by *fn*; Default **None** (expects a single number or one-dimensional array with length equal to that of the df1 subset)
            dtype (numpy type): The type that is returned by *fn*; Default **np.object**

        Returns:
            numpy.ndarray: Numpy array of with return values.

        Note:
            By default, the returned numpy array is a one-dimensional array with its length equal to that
            of the number items in the first dataframe *df1*. |br|
            If you want more dimensions, pass them as the **shape** parameter.
            (eg. if you want a [len_df1, 3] array, pass [3] as the shape parameter)

        Warning:
            This function is created with the purpose of performing transformation applies and not aggregation or filtration operations.
            This is because the returned array will always have at least one dimension equal to the number of items in *df1*. |br|
            You can still use it for aggregation by returning a single number, which will then be assigned to every item of that group, but filtration is currently no doable.
        """
        if shape is None:
            shape = []
        result = np.full([self.lendf1] + shape, default, dtype=dtype)

        for i1, i2 in zip(self.df1_idx, self.df2_idx):
            if i1.shape[0] == 0:
                continue

            result[i1] = fn(
                {col: val[i1] for col, val in self.df1.items()},
                {col: val[i2] for col, val in self.df2.items()},
            )

        return result
