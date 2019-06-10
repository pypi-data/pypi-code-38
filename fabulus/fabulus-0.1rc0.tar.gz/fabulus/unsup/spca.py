import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class SPCA(PCA):
    def __init__(self, n_components=None, scaler: StandardScaler = StandardScaler(), copy=True,
                 whiten=False, svd_solver='auto', tol=0.0, iterated_power='auto',
                 random_state=None):
        super().__init__(n_components, copy, whiten, svd_solver, tol, iterated_power, random_state)

        if type(scaler) is not StandardScaler:
            raise TypeError(f'scale has to be of type {StandardScaler} but was {type(scaler)}')
        self.scaler = scaler

    def fit(self, X, y=None) -> 'SPCA':
        self.scaler.fit(X)
        super().fit(self.scaler.transform(X))
        return self

    def transform(self, X) -> np.ndarray:
        return super().transform(self.scaler.transform(X))

    def fit_transform(self, X, y=None) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def score(self, X, y=None):
        return super().score(self.scaler.transform(X))

    def score_samples(self, X):
        return super().score_samples(self.scaler.transform(X))

    def inverse_transform(self, X) -> np.ndarray:
        return self.scaler.inverse_transform(super().inverse_transform(X))
