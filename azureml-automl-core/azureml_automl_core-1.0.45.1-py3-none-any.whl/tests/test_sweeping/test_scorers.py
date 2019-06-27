import logging
import pickle
import unittest

import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.linear_model import LogisticRegression, LinearRegression

from automl.client.core.common import constants
from automl.client.core.common.activity_logger import TelemetryActivityLogger
from azureml.automl.core.scoring import Scorers


def _get_classification_data(rand_frac=0.0, random_state=42, n_samples=1000):
    """ Get X and y data splited.  The quality of the X_train data will degrade as rand_frac increases"""
    X, y = make_classification(n_samples=n_samples, n_classes=3, n_informative=4, random_state=random_state)
    X_train, y_train, X_valid, y_valid = X[:200, :], y[:200], X[200:, :], y[200:]

    # Randomly swap out X to the next row to mimic
    # bad and good transforms according to rand_frac
    rand_n = int(rand_frac * len(y_train))
    if rand_n > 0:
        rand_ints = np.random.RandomState(seed=random_state).choice(
            np.arange(len(y_train) - 1), size=rand_n, replace=False)
        X_train[rand_ints, :] = X_train[rand_ints + 1, :]

    return X_train, y_train, X_valid, y_valid


def _get_regression_data(rand_frac=0.0, random_state=42, n_samples=1000):
    """ Get X and y data splited.  The quality of the X_train data will degrade as rand_frac increases"""
    X, y = make_regression(n_samples=n_samples, n_informative=4, random_state=random_state)
    X_train, y_train, X_valid, y_valid = X[:200, :], y[:200], X[200:, :], y[200:]

    # Randomly swap out X to the next row to mimic
    # bad and good transforms according to rand_frac
    rand_n = int(rand_frac * len(y_train))
    if rand_n > 0:
        rand_ints = np.random.RandomState(seed=random_state).choice(
            np.arange(len(y_train) - 1), size=rand_n, replace=False)
        X_train[rand_ints, :] = X_train[rand_ints + 1, :]

    return X_train, y_train, X_valid, y_valid


class TestScorers(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestScorers, self).__init__(*args, **kwargs)

    def test_accuracy(self):
        acc = Scorers().get(metric_name="accuracy", task=constants.Tasks.CLASSIFICATION)

        # Produce exact same data, except X_train will be modified to reduce or enhance 'accuracy'
        X_train_experiment, y_train, X_valid, y_valid = _get_classification_data(rand_frac=0.0,
                                                                                 random_state=42,
                                                                                 n_samples=1000)
        X_train_baseline, _, _, _ = _get_classification_data(rand_frac=0.5, random_state=42, n_samples=1000)

        # Bad Baseline (X_train more noisily correlates with y_valid)
        baseline_estimator = LogisticRegression(solver='lbfgs')
        baseline_estimator.fit(X_train_baseline, y_train)
        baseline_score = acc.score(estimator=baseline_estimator,
                                   valid_features=X_valid,
                                   y_actual=y_valid)

        # Good experiment
        # Good default for regularization to induce good model
        experiment_estimator = LogisticRegression(solver='lbfgs')
        experiment_estimator.fit(X_train_experiment, y_train)
        experiment_score = acc.score(estimator=experiment_estimator,
                                     valid_features=X_valid,
                                     y_actual=y_valid)
        print("base, exp = ", baseline_score, experiment_score)

        self.assertEqual(acc.is_experiment_better_than_baseline(baseline_score=baseline_score,
                                                                experiment_score=experiment_score,
                                                                epsilon=0.01), True)
        self.assertEqual(acc.is_experiment_better_than_baseline(baseline_score=baseline_score,
                                                                experiment_score=baseline_score,
                                                                epsilon=0.01), False)

    def test_accuracy_nonsequential_label_ints(self):
        acc = Scorers().get(metric_name="accuracy", task=constants.Tasks.CLASSIFICATION)

        # Produce exact same data, except X_train will be modified to reduce or enhance 'accuracy'
        X_train_experiment, y_train, X_valid, y_valid = _get_classification_data(rand_frac=0.0,
                                                                                 random_state=42,
                                                                                 n_samples=1000)
        X_train_baseline, _, _, _ = _get_classification_data(rand_frac=0.5, random_state=42, n_samples=1000)

        # Bad Baseline (X_train more noisily correlates with y_valid)
        baseline_estimator = LogisticRegression(solver='lbfgs')
        baseline_estimator.fit(X_train_baseline, y_train)
        baseline_score = acc.score(estimator=baseline_estimator,
                                   valid_features=X_valid,
                                   y_actual=y_valid)

        # Good experiment
        # Good default for regularization to induce good model
        # modify y's to check for accuracy bug that doesn't handle class_labels correctly
        y_train_prime = y_train + 1
        y_valid_prime = y_valid + 1
        experiment_estimator = LogisticRegression(solver='lbfgs')
        experiment_estimator.fit(X_train_experiment, y_train_prime)
        experiment_score = acc.score(estimator=experiment_estimator,
                                     valid_features=X_valid,
                                     y_actual=y_valid_prime)
        print("base, exp = ", baseline_score, experiment_score)

        self.assertEqual(acc.is_experiment_better_than_baseline(baseline_score=baseline_score,
                                                                experiment_score=experiment_score,
                                                                epsilon=0.01), True)

    def test_r2_score(self):
        acc = Scorers().get(metric_name="r2_score", task=constants.Tasks.REGRESSION)
        print(acc)

        # Produce exact same data, except X_train will be modified to reduce or enhance 'accuracy'
        n_samples = 1000
        X_train_experiment, y_train, X_valid, y_valid = _get_regression_data(rand_frac=0.0,
                                                                             random_state=42,
                                                                             n_samples=n_samples)
        X_train_baseline, _, _, _ = _get_regression_data(rand_frac=0.6, random_state=42, n_samples=n_samples)

        # Bad Baseline (X_train more noisily correlates with y_valid)
        baseline_estimator = LinearRegression()
        baseline_estimator.fit(X_train_baseline, y_train)
        baseline_score = acc.score(estimator=baseline_estimator,
                                   valid_features=X_valid,
                                   y_actual=y_valid)

        # Good experiment
        # Good default for regularization to induce good model
        experiment_estimator = LinearRegression()
        experiment_estimator.fit(X_train_experiment, y_train)
        experiment_score = acc.score(estimator=experiment_estimator,
                                     valid_features=X_valid,
                                     y_actual=y_valid)

        self.assertEqual(acc.is_experiment_better_than_baseline(baseline_score=baseline_score,
                                                                experiment_score=experiment_score,
                                                                epsilon=0.01), True)
        self.assertEqual(acc.is_experiment_better_than_baseline(baseline_score=baseline_score,
                                                                experiment_score=baseline_score,
                                                                epsilon=0.01), False)

    def test_logger_pickle(self):
        # assert that a TelemetryActivityLogger survives getstate as it a pickleable instance
        logger = TelemetryActivityLogger()
        acc = Scorers().get(metric_name="accuracy", task=constants.Tasks.CLASSIFICATION, logger=logger)
        pickle.loads(pickle.dumps(acc))
        self.assertIsNotNone(acc.__getstate__()["_logger"])

        # assert that another logger is reset to None in getstate as it not a pickleable instance
        logger = logging.getLogger("")
        r2 = Scorers().get(metric_name="r2_score", task=constants.Tasks.REGRESSION, logger=logger)
        pickle.loads(pickle.dumps(r2))
        self.assertIsNone(r2.__getstate__()["_logger"])

    def test_regression_default(self):
        # TODO
        pass

    def test_avoid_timeseries(self):
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
