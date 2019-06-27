import unittest
import os
import pickle
import tempfile

from sklearn.datasets import make_classification
from azureml.automl.core.sampling.data_provider import InMemoryDataProvider, DiskBasedDataProvider
from azureml.automl.core.sampling import SplittingConfig


class TestDataProvider(unittest.TestCase):
    def test_in_memory_provider(self):
        split_config = SplittingConfig(task="classification", train_size=0.5, test_size=0.5)
        X, y = make_classification(n_samples=100, n_features=6, random_state=42)
        provider = InMemoryDataProvider(X, y, split_config)
        X_train, y_train, X_valid, y_valid = provider.get_train_validation_sets()
        self.assertEqual(len(X_train), len(X_valid))
        self.assertRaises(NotImplementedError, lambda: provider.get_cross_validation_sets())

    def test_disk_based_provider(self):
        split_config = SplittingConfig(task="classification", train_size=0.5, test_size=0.5)
        X, y = make_classification(n_samples=100, n_features=6, random_state=42)
        handle, file_name = tempfile.mkstemp()
        os.close(handle)
        try:
            with open(file_name, "wb") as f:
                pickle.dump((X, y), f)
            provider = DiskBasedDataProvider(file_name, split_config)
            X_train, y_train, X_valid, y_valid = provider.get_train_validation_sets()
            self.assertEqual(len(X_train), len(X_valid))
            self.assertRaises(NotImplementedError, lambda: provider.get_cross_validation_sets())
        finally:
            os.remove(file_name)


if __name__ == '__main__':
    unittest.main()
