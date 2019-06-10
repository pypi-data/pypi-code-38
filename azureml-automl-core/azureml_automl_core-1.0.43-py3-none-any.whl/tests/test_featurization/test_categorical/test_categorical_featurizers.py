import unittest


from azureml.automl.core.featurizer.transformer import CategoricalFeaturizers
from azureml.automl.core.featurizer.transformer import CatImputer
from azureml.automl.core.featurizer.transformer import HashOneHotVectorizerTransformer
from azureml.automl.core.featurizer.transformer import LabelEncoderTransformer
from azureml.automl.core.featurizer.transformer import OneHotEncoderTransformer
from azureml.automl.core.featurizer.transformer.generic import CrossValidationTargetEncoder

from ... import utilities


class TestCategoricalFeaturizers(unittest.TestCase):

    def test_instance_creation(self):
        tr = CategoricalFeaturizers.hashonehot_vectorizer()
        self.assertTrue(isinstance(tr, HashOneHotVectorizerTransformer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = CategoricalFeaturizers.labelencoder()
        self.assertTrue(isinstance(tr, LabelEncoderTransformer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = CategoricalFeaturizers.cat_imputer()
        self.assertTrue(isinstance(tr, CatImputer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = CategoricalFeaturizers.cat_targetencoder()
        self.assertTrue(isinstance(tr, CrossValidationTargetEncoder))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = CategoricalFeaturizers.woe_targetencoder()
        self.assertTrue(isinstance(tr, CrossValidationTargetEncoder))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = CategoricalFeaturizers.onehotencoder()
        self.assertTrue(isinstance(tr, OneHotEncoderTransformer))
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))


if __name__ == '__main__':
    unittest.main()
