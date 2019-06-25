import unittest

from azureml.automl.core.featurizer.transformer import BinTransformer

from azureml.automl.core.featurizer.transformer import NumericFeaturizers

from ... import utilities


class TestNumericFeaturizers(unittest.TestCase):

    def test_instance_creation(self):
        tr = NumericFeaturizers.bin_transformer()
        self.assertTrue(isinstance(tr, BinTransformer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))


if __name__ == '__main__':
    unittest.main()
