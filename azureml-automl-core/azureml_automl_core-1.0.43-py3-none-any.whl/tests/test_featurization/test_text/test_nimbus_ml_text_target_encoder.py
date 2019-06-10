import unittest

from azureml.automl.core.featurizer.transformer import TextFeaturizers
from azureml.automl.core.featurizer.transformer.text.nimbus_ml_text_target_encoder import NimbusMLTextTargetEncoder
from azureml.automl.core.featurizer.transformer.featurization_utilities import if_package_exists
from azureml.automl.core.featurizer.transformer.text.constants import NIMBUS_ML_PARAMS
from azureml.automl.core.featurizer.transformer.automltransformer import AutoMLTransformer

from ... import utilities


class TestNimbusMLTextFeaturizers(unittest.TestCase):

    @if_package_exists("test_avg_perceptron_text_target_encoder_creation", [NIMBUS_ML_PARAMS.NIMBUS_ML_PACKAGE_NAME])
    def test_avg_perceptron_text_target_encoder_creation(self):
        from nimbusml.feature_extraction.text import NGramFeaturizer
        from nimbusml.linear_model import AveragedPerceptronBinaryClassifier

        tr = TextFeaturizers.averaged_perceptron_text_target_encoder()

        assert isinstance(tr, NimbusMLTextTargetEncoder)
        assert isinstance(tr, AutoMLTransformer)
        assert tr._model is None
        assert isinstance(tr._featurizer, NGramFeaturizer)
        assert isinstance(tr._learner, AveragedPerceptronBinaryClassifier)
        assert tr.get_model() is None
        self.assertTrue(utilities.check_pickleable(
            tr), msg="Failed to pickle {}".format(type(tr).__name__))

    @if_package_exists("test_avg_perceptron_text_target_encoder_output", [NIMBUS_ML_PARAMS.NIMBUS_ML_PACKAGE_NAME])
    def test_avg_perceptron_text_target_encoder_output(self):
        from nimbusml.datasets import get_dataset
        import pandas as pd
        from sklearn_pandas import DataFrameMapper
        path = get_dataset('wiki_detox_train').as_filepath()
        data = pd.read_csv(path, sep='\t')
        column = "SentimentText"
        # fit and transform
        df = pd.DataFrame(data=data, columns=[column])
        y = data.iloc[:, 0]

        column = "SentimentText"
        tr = []
        avg_perceptron = TextFeaturizers.averaged_perceptron_text_target_encoder()
        tr.append((column,
                   ([avg_perceptron]),
                   {"alias": "word_char_grams"}))

        # Data frame mapper and generate features
        mapper = DataFrameMapper(tr, input_df=True, sparse=True)
        # fit and transform
        df = pd.DataFrame(data=data, columns=[column])

        features = mapper.fit_transform(df, y)
        self.assertEqual(238, features.shape[0])
        self.assertEqual(2, features.shape[1])

    @if_package_exists("test_featurizer_learner_type", [NIMBUS_ML_PARAMS.NIMBUS_ML_PACKAGE_NAME])
    def test_featurizer_learner_type(self):
        from nimbusml.feature_extraction.text import NGramFeaturizer
        from nimbusml.feature_extraction.text.extractor import Ngram
        from nimbusml.linear_model import AveragedPerceptronBinaryClassifier
        featurizer = NGramFeaturizer(char_feature_extractor=Ngram(weighting=NIMBUS_ML_PARAMS.NGRAM_CHAR_WEIGHTING,
                                                                  ngram_length=NIMBUS_ML_PARAMS.NGRAM_CHAR_LENGTH,
                                                                  all_lengths=NIMBUS_ML_PARAMS.NGRAM_CHAR_ALL_LENGTHS),
                                     word_feature_extractor=Ngram(weighting=NIMBUS_ML_PARAMS.NGRAM_WORD_WEIGHTING,
                                                                  ngram_length=NIMBUS_ML_PARAMS.NGRAM_WORD_LENGTH,
                                                                  all_lengths=NIMBUS_ML_PARAMS.NGRAM_WORD_ALL_LENGTHS),
                                     vector_normalizer="L2")
        avg_perceptron = AveragedPerceptronBinaryClassifier(
            num_iterations=NIMBUS_ML_PARAMS.AVG_PERCEPTRON_ITERATIONS)
        avg_perceptron = TextFeaturizers.averaged_perceptron_text_target_encoder()

        with self.assertRaises(TypeError):
            NimbusMLTextTargetEncoder(
                featurizer="featurizer", learner=avg_perceptron)

        with self.assertRaises(TypeError):
            NimbusMLTextTargetEncoder(featurizer=featurizer, learner="learner")
