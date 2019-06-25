import unittest
import numpy as np
from azureml.automl.core.featurizer.transformer.text import TextFeaturizers


class TestStringCastTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestStringCastTransformer, self).__init__(*args, **kwargs)

    def test_transform(self):
        tr = TextFeaturizers.string_cast()
        x = np.array([['A', 'B'], [3, 4]])
        expected_output = np.array([["A", "B"], ["3", "4"]])
        self.assertTrue(np.all(tr.fit_transform(x) == expected_output))


if __name__ == '__main__':
    unittest.main()
