import unittest

# Categorical
from azureml.automl.core.featurization import CategoricalFeaturizers, CatImputer, LabelEncoderTransformer,\
    HashOneHotVectorizerTransformer, OneHotEncoderTransformer

# Datetime
from azureml.automl.core.featurization import DateTimeFeaturesTransformer

# Data providers
from azureml.automl.core.featurization import DataProviders

# Generic
from azureml.automl.core.featurization import ImputationMarker, LambdaTransformer, GenericTransformer, \
    GenericFeaturizers

# Numeric
from azureml.automl.core.featurization import BinTransformer, NumericFeaturizers

# Text
from azureml.automl.core.featurization import get_ngram_len, NaiveBayes, StringCastTransformer, \
    max_ngram_len, TextTransformer, TextFeaturizers, WordEmbeddingTransformer, TFIDF_VECTORIZER_CONFIG,\
    NimbusMLTextTargetEncoder, BagOfWordsTransformer, StatsTransformer

# Timeseries
from azureml.automl.core.featurization import TimeSeriesTransformer, NumericalizeTransformer, \
    MissingDummiesTransformer, LaggingTransformer

# Data transformer
from azureml.automl.core.featurization import DataTransformer

# AutoMLTransformer(Logger)
from azureml.automl.core.featurization import AutoMLTransformer

from azureml.automl.core.featurization import Featurizers


class TestBackwardCompatibility(unittest.TestCase):
    def test_backward_compatibility(self):
        pass
