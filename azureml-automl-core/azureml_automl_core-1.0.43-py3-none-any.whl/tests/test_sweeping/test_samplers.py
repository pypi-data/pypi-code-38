import unittest

import numpy as np
from sklearn.datasets import make_classification, make_regression

from azureml.automl.core.sampling import SplittingConfig
from azureml.automl.core.sampling.count_sampler import CountSampler
from azureml.automl.core.sampling.data_provider import InMemoryDataProvider, DiskBasedDataProvider
from automl.client.core.common import constants


class TestSamplers(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestSamplers, self).__init__(*args, **kwargs)

    def _get_samples(self, max_rows, nrows_original, task, n_classes=None, min_examples_per_class=None):
        cs = CountSampler(42,
                          min_examples_per_class=min_examples_per_class,
                          max_rows=max_rows,
                          task=task)
        if task == constants.Tasks.CLASSIFICATION:
            X, y = make_classification(n_samples=nrows_original,
                                       n_classes=n_classes,
                                       n_informative=10,
                                       random_state=42)
        else:
            X, y = make_regression(n_samples=nrows_original, random_state=42)

        return cs.sample(X=X, y=y)

    def test_split_config_fractions(self):
        # Constrained by min_examples_per_class
        min_examples_per_class = 500
        max_rows = 4000
        nrows_original = 20000
        n_classes = 3

        # Constrained by min_examples_per_class
        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.CLASSIFICATION,
                                                        n_classes=n_classes,
                                                        min_examples_per_class=min_examples_per_class)
        assert np.isclose(split.test_size, 0.5)

    def test_split_config_fractions_and_data_provider(self):
        # Constrained by min_examples_per_class
        min_examples_per_class = 2000
        max_rows = 10000
        nrows_original = 15750  # This setting was causing ValueError before precision fix.
        n_classes = 14

        # Constrained by min_examples_per_class
        X_sampled, y_sampled, split_config = self._get_samples(max_rows,
                                                               nrows_original,
                                                               task=constants.Tasks.CLASSIFICATION,
                                                               n_classes=n_classes,
                                                               min_examples_per_class=min_examples_per_class)
        provider = InMemoryDataProvider(X_sampled, y_sampled, split_config)

        # Check that this runs without an exception
        X_train, y_train, X_valid, y_valid = provider.get_train_validation_sets()

    def test_classification(self):
        # Constrained by min_examples_per_class
        min_examples_per_class = 500
        max_rows = 4000
        nrows_original = 20000
        n_classes = 3

        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.CLASSIFICATION,
                                                        n_classes=n_classes,
                                                        min_examples_per_class=min_examples_per_class)

        assert np.shape(X_sampled)[0] == 2 * n_classes * min_examples_per_class
        assert np.isclose(split.test_size, 0.5)

        # constrained by max_rows
        min_examples_per_class = 2000
        max_rows = 10000
        nrows_original = 20000
        n_classes = 10

        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.CLASSIFICATION,
                                                        n_classes=n_classes,
                                                        min_examples_per_class=min_examples_per_class)
        assert np.shape(X_sampled)[0] == 2 * max_rows

        # Small dataset:
        min_examples_per_class = 2000
        max_rows = 10000
        nrows_original = 500
        n_classes = 10

        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.CLASSIFICATION,
                                                        n_classes=n_classes,
                                                        min_examples_per_class=min_examples_per_class)
        assert np.shape(X_sampled)[0] == nrows_original
        assert np.isclose(split.test_size, 0.2)

    def test_regression(self):
        # constrained by max_rows
        max_rows = 10000
        nrows_original = 20000

        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.REGRESSION)
        assert np.shape(X_sampled)[0] == 2 * max_rows

        # Small regression dataset
        max_rows = 10000
        nrows_original = 1000

        X_sampled, y_sampled, split = self._get_samples(max_rows,
                                                        nrows_original,
                                                        task=constants.Tasks.REGRESSION)
        assert np.shape(X_sampled)[0] == nrows_original
        assert np.isclose(split.test_size, 0.2)


if __name__ == '__main__':
    unittest.main()
