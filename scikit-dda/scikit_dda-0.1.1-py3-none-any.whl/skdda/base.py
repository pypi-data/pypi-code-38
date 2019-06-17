"""
Scikit-learn-compatible Deep Discriminant Analysis.

Used in
David Diaz-Vico, Jose R. Dorronsoro
"Deep vs Kernel Fisher Discriminant Analysis"

@author: David Diaz Vico
@license: MIT
"""

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.neural_network import MLPRegressor


def fisher_y(y):
    """ y_ij = (n-n_j)/(n*sqrt(n_j)) if class(y_i)==j else -sqrt(n_j)/n """
    n = len(y)
    targets, counts = np.unique(y, return_counts=True)
    c = len(targets)
    lsrlda_y = np.zeros((n, c))
    for i, target in enumerate(y):
        t = targets.tolist().index(target)
        for j in range(c):
            lsrlda_y[i, j] = (n - counts[t]) / (n * np.sqrt(counts[t])) if j == t else -np.sqrt(counts[t] / n)
    return lsrlda_y


class FisherTransformer(BaseEstimator, TransformerMixin):
    """Fisher transformer. Can be combined with MLPRegressor to form a Deep
    Discriminant Analysis classifier.

    Parameters
    ----------
    regressor: RegressorMixin, default=MLPRegressor()
         Scikit-learn RegressorMixin estimator. Use MLPRegressor to get a Deep
         Discriminant Analysis classifier.

    """

    def __init__(self, regressor=MLPRegressor()):
        self.regressor = regressor

    def fit(self, X, y, **fit_params):
        self.regressor.fit(X, fisher_y(y), **fit_params)
        return self

    def transform(self, X):
        return self.regressor.predict(X).reshape((len(X), -1))

    def fit_transform(self, X, y, **fit_params):
        return self.fit(X, y, **fit_params).transform(X)
