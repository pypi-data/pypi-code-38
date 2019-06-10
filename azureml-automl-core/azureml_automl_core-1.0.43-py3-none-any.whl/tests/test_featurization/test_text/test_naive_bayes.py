import unittest
import numpy as np
import azureml.automl.core.preprocess as pp


class NaiveBayesTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(NaiveBayesTests, self).__init__(*args, **kwargs)

    def test_naive_bayes(self):
        tr = pp.NaiveBayes()
        x = np.array([[1, 2], [3, 4]])
        y = np.array([0, 1])
        expected_output = np.round(np.array([[0.51213801, 0.48786199], [0.49794067, 0.50205933]]), 5)
        output = np.round(tr.fit_transform(x, y), 5)
        self.assertTrue(np.all(output == expected_output))
