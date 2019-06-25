import unittest

from ddt import ddt, file_data
from azureml.automl.core.featurizer.transformer import BagOfWordsTransformer
from azureml.automl.core.featurizer.transformer.text import TextFeaturizers


@ddt
class TestBagOfWordsTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBagOfWordsTransformer, self).__init__(*args, **kwargs)

    @file_data("text_test_data.json")
    def test_transform(self, X, y):
        tr = TextFeaturizers.bow_transformer()
        self.assertTrue(isinstance(tr, BagOfWordsTransformer))
        # Using numpy array
        import numpy as np
        X = np.array(X)
        y = np.array(y)
        features = tr.fit_transform(X, y)
        assert features is not None
        assert features.shape == (4, 1965)


if __name__ == '__main__':
    unittest.main()
