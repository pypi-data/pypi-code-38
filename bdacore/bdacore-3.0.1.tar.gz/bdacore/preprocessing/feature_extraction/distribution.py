import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

__author__ = "VLE"
__copyright__ = "Copyright 2018, OCTO Technology"
__version__ = "1.0"
__email__ = "vlevorato@octo.com"


class DistributionTransformer(BaseEstimator, TransformerMixin):
    """
    Build a discrete distribution (histogram) for feature engineering for each column, per line, 
    following a rolling window. It captures the evolving distribution of a feature.
    
    For instance, if a serie is composed of the following values: [3, 10, 12, 23], and with a window parameter of 3,
    it takes these values, and apply histogram (bins=4) function on it:
    [3] => [0, 0, 1, 0]
    [3, 10] => [1, 0, 0, 1]
    [3, 10, 12] => [1, 0, 0, 2]
    [10, 12, 23] => [2, 0, 0, 1]

    Parameters
    ----------   
        window: int
            Size of the rolling window.

        bins: int, optional, (default=4)
            Amount of bins used to estimate distribution

    Examples
    --------
    >>> import pandas as pd
    >>> from bdacore.preprocessing.feature_extraction import DistributionTransformer

    >>> df = pd.DataFrame({'sales': [3, 10, 12, 23, 48, 19, 21]})
    >>> distrib_transformer = DistributionTransformer(3)
    >>> distrib_transformer.fit_transform(df)
       sales_bin_1  sales_bin_2  sales_bin_3  sales_bin_4
    0            0            0            1            0
    1            1            0            0            1
    2            1            0            0            2
    3            2            0            0            1
    4            1            1            0            1
    5            2            0            0            1
    6            2            0            0            1
    """

    def __init__(self, window, bins=4):
        self.window = window
        self.bins = bins

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
            self

        """

        return self

    def transform(self, X):
        """
        Transform a dataframe to build discrete distribution per column.
        
        Parameters
        ----------
           X: dataframe
               Input pandas dataframe.
        
        Returns
        -------
           X: dataframe 
               Dataframe with bin values per column.
        
        """
        X_distrib = pd.DataFrame()

        for col in X.columns:
            col_serie = X[col]
            bins_list = []
            if type(self.window) is int:
                for i in range(0, len(col_serie)):
                    min_bound = i - self.window + 1
                    if min_bound < 0:
                        min_bound = 0
                    max_bound = i + 1
                    if max_bound >= len(col_serie):
                        max_bound = len(col_serie)
                    bins_list.append(np.histogram(col_serie[min_bound:max_bound], bins=self.bins)[0])

            X_col_distrib = pd.DataFrame(bins_list)
            X_col_distrib = X_col_distrib.set_index(X.index)
            X_col_distrib.columns = [col + '_bin_' + str(i) for i in range(1, self.bins + 1)]

            if len(X_distrib) == 0:
                X_distrib = X_col_distrib
            else:
                X_distrib = X_distrib.join(X_col_distrib)

        return X_distrib
