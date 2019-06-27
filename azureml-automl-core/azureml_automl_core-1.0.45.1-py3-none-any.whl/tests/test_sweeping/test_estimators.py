import unittest

from sklearn.datasets import make_classification, make_regression
from azureml.automl.core.estimation.estimators import Estimators


class TestEstimators(unittest.TestCase):
    def test_lgbm_classifier(self):
        X, y = make_classification(n_samples=1000, n_features=6, random_state=42)
        lgbm = Estimators.get("lgbm_classifier")
        lgbm.fit(X, y)

    def test_lgbm_regressor(self):
        X, y = make_regression(n_samples=1000, n_features=6, random_state=42)
        lgbm = Estimators.get("lgbm_regressor")
        lgbm.fit(X, y)

    def test_logistic_regression(self):
        X, y = make_classification(n_samples=1000, n_features=6, random_state=42)
        lgbm = Estimators.get("logistic_regression")
        lgbm.fit(X, y)

    def test_linear_regression(self):
        X, y = make_regression(n_samples=1000, n_features=6, random_state=42)
        lgbm = Estimators.get("linear_regression")
        lgbm.fit(X, y)


if __name__ == '__main__':
    unittest.main()
