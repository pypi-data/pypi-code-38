import types
import warnings

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

warnings.simplefilter('default')

__author__ = "VLE"
__copyright__ = "Copyright 2017, OCTO Technology"
__version__ = "1.12"
__email__ = "vlevorato@octo.com"


class RollingWindower(BaseEstimator, TransformerMixin):
    """
    Compute rolling aggregated values for a given dataframe.

    Classical operators (mean, std, median, etc.) or custom operators can be used to compute the windows. 
    Windows are based on index, which could be a simple integer or a pandas timestamp. Use **kwargs to pass extra
    arguments to pandas rolling function (like min_periods for instance).
    
    
    Parameters
    ----------   
        operation: str or function, optional, default 'mean'
            Set the aggregation function used to aggregate a window.

        windows: list, optional, default [3]
            Set the windows used to aggregate data. Time windows can be set also (see pandas time unit
            syntax) if the dataframe index is a timestamp
            Examples:
                [3]: one window of size 3
                [2,5]: one window of size 2 and one window of size 5
                [2s, 10s]: one window of 2 secs and one window of 10 secs
            
        diff_mode: boolean, optional, default False
            Process the difference between values and its window aggregate value.
                
    
    Examples
    --------
        >>> import pandas as pd
        >>> from bdacore.preprocessing.ts.rolling import RollingWindower
        >>> df = pd.DataFrame({'data': [0, 1, 2, 3, 4]})
        >>> roller = RollingWindower(windows=[2,3])
        >>> df_roll = roller.transform(df)
        >>> df_roll
           mean_2_data  mean_3_data
        0          NaN          NaN
        1          0.5          NaN
        2          1.5          1.0
        3          2.5          2.0
        4          3.5          3.0
      
        >>> df_ts = pd.DataFrame({'data': [0, 1, 2, 3, 4]}, \
                            index=[pd.Timestamp('20130101 09:00:00'), \
                                pd.Timestamp('20130101 09:00:02'), \
                                pd.Timestamp('20130101 09:00:03'), \
                                pd.Timestamp('20130101 09:00:05'), \
                                pd.Timestamp('20130101 09:00:06')])
        >>> roller = RollingWindower(windows=['5s', '2s'])
        >>> df_roll = roller.transform(df_ts)
        >>> df_roll
                             mean_5s_data  mean_2s_data
        2013-01-01 09:00:00           0.0           0.0
        2013-01-01 09:00:02           0.5           1.0
        2013-01-01 09:00:03           1.0           1.5
        2013-01-01 09:00:05           2.0           3.0
        2013-01-01 09:00:06           2.5           3.5



    """

    def __init__(self, operation='mean', windows=[3], diff_mode=False, **kwargs):
        self.operation = operation
        self.windows = windows
        self.diff_mode = diff_mode
        self.kwargs = kwargs
        if type(windows[0]) is int:
            warnings.warn(
                "Using integer values for windows size can be erroneous. Consider timed windows instead "
                "such as: RollingWindower(windows=['5s', '2s']) ",
                UserWarning)

    def fit(self, X=None, y=None):
        """
        No-op.
        This method doesn't do anything. It exists purely for compatibility
        with the scikit-learn transformer API.
        
        Parameters
        ----------
            X: array-like
            y: array-like

        Returns
        -------
            self: RollingWindower

        """

        return self

    def transform(self, raw_X):
        """
        Transform a dataframe into aggregated values corresponding to window sizes
        
        Parameters
        ----------
            raw_X: dataframe
                Input pandas dataframe.

        Returns
        -------
            X: dataframe 
                Dataframe with columns having rolling measures (one per window)

        """

        X = pd.DataFrame()

        for window in self.windows:

            X_m = raw_X.rolling(window, **self.kwargs).agg(self.operation)
            diff_name = ''

            # if diff_mode = True, calculate difference between aggregated value and value
            if self.diff_mode:
                warnings.warn("diff mode is deprecated and will be removed in next major version.", DeprecationWarning)
                diff_name = 'diff_'
                X_m_diff = raw_X.sub(X_m)
                X_m = X_m_diff

            columns_name = []

            if isinstance(self.operation, types.FunctionType):
                col_name = self.operation.__name__
            else:
                col_name = self.operation

            for col in X_m.columns:
                columns_name.append(col_name + '_' + diff_name + str(window) + '_' + col)

            X_m.columns = columns_name

            if len(X) == 0:
                X = X_m
            else:
                X = X.join(X_m)

        return X
