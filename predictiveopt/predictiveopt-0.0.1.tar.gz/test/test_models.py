import unittest
from predictiveopt.models import KMeansModel, LinearRegressionModel
import pandas as pd


class TestModels(unittest.TestCase):

    def test_linear_regression(self):
        # Given
        expected = pd.Series([4, 5, 6, 2])

        # When
        model = LinearRegressionModel(pd.Series([1, 2, 3, 4, 5, 6]).values.reshape(-1, 1), [6, 5, 4, 3, 2, 1],
                                      pd.Series([3, 2, 1, 5]).values.reshape(-1, 1))
        actual = model.run()

        # Then
        self.assertEqual(expected.values[0], round(actual.values[0]))
        self.assertEqual(expected.values[1], round(actual.values[1]))
        self.assertEqual(expected.values[2], round(actual.values[2]))
        self.assertEqual(expected.values[3], round(actual.values[3]))

    def test_kmeans(self):
        # Given
        expected = 2

        # When
        model = KMeansModel(pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).values.reshape(-1, 1), clusters=2)
        model.run()

        actual = model.sample_clusters(items_per_cluster=1)

        # Then
        self.assertEquals(expected, len(actual))
