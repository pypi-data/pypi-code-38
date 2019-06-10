import unittest

from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import Imputer, MaxAbsScaler

from azureml.automl.core.featurizer.transformer import ImputationMarker
from azureml.automl.core.featurizer.transformer import LambdaTransformer
from azureml.automl.core.featurizer.transformer import GenericFeaturizers

from ... import utilities


class TestGenericFeaturizers(unittest.TestCase):

    def test_instance_creation(self):
        tr = GenericFeaturizers.imputer()
        self.assertTrue(isinstance(tr, Imputer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = GenericFeaturizers.imputation_marker()
        self.assertTrue(isinstance(tr, ImputationMarker))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = GenericFeaturizers.lambda_featurizer()
        self.assertTrue(isinstance(tr, LambdaTransformer))
        self.assertIsNone(tr.logger)
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = GenericFeaturizers.minibatchkmeans_featurizer()
        self.assertTrue(isinstance(tr, MiniBatchKMeans))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = GenericFeaturizers.maxabsscaler()
        self.assertTrue(isinstance(tr, MaxAbsScaler))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))


if __name__ == '__main__':
    unittest.main()
