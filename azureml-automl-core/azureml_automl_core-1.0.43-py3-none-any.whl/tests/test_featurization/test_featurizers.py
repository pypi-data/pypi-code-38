import unittest

from automl.client.core.common.exceptions import ConfigException
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import Imputer, MaxAbsScaler

from azureml.automl.core.configuration.feature_config import FeatureConfig
from azureml.automl.core.featurization.featurizers import Featurizers
from azureml.automl.core.featurizer.transformer import BagOfWordsTransformer, \
    WordEmbeddingTransformer, CatImputer, \
    ImputationMarker, LambdaTransformer, HashOneHotVectorizerTransformer, LabelEncoderTransformer, \
    StringCastTransformer, StatsTransformer, NimbusMLTextTargetEncoder
from azureml.automl.core.featurizer.transformer.generic import ModelBasedTargetEncoder, \
    CrossValidationTargetEncoder


class TestFeaturizers(unittest.TestCase):
    def test_error_scenario(self):
        cfg = {}
        with self.assertRaises(ConfigException):
            FeatureConfig.from_dict(cfg)

    def test_textfeaturizers_creation(self):
        cfg = {"id": "word_embeddings",
               "type": "text",
               "args": [],
               "kwargs": {
                   "embeddings_name": "wiki_news_300d_1M_subword"
               }
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, WordEmbeddingTransformer)

        cfg = {"id": "bow_transformer",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, BagOfWordsTransformer)

        cfg = {"id": "count_vectorizer",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, CountVectorizer)

        cfg = {"id": "naive_bayes",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, ModelBasedTargetEncoder)

        cfg = {"id": "string_cast",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, StringCastTransformer)

        cfg = {"id": "text_stats",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, StatsTransformer)

        cfg = {"id": "text_target_encoder",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        with self.assertRaises(ConfigException):
            Featurizers.get(obj)

        cfg = {"id": "text_target_encoder",
               "type": "text",
               "kwargs": {
                   "model_class": LogisticRegression
               }
               }
        obj = FeatureConfig.from_dict(cfg)
        assert obj is not None
        feat_obj = Featurizers.get(obj)
        assert feat_obj is not None
        assert isinstance(feat_obj, ModelBasedTargetEncoder)

        cfg = {"id": "averaged_perceptron_text_target_encoder",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, NimbusMLTextTargetEncoder)

        cfg = {"id": "tfidf_vectorizer",
               "type": "text"
               }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, TfidfVectorizer)

    def test_categorical_creation(self):
        cfg = {
            "id": "cat_imputer",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, CatImputer)

        cfg = {
            "id": "Cat_imputer",
            "type": "Categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert isinstance(feat_obj, CatImputer)

        cfg = {
            "id": "hashonehot_vectorizer",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, HashOneHotVectorizerTransformer)

        cfg = {
            "id": "labelencoder",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, LabelEncoderTransformer)

        cfg = {
            "id": "cat_targetencoder",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, CrossValidationTargetEncoder)

        cfg = {
            "id": "woe_targetencoder",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, CrossValidationTargetEncoder)

        cfg = {
            "id": "sdfasdf",
            "type": "categorical"
        }
        obj = FeatureConfig.from_dict(cfg)
        assert obj is not None
        with self.assertRaises(ConfigException):
            Featurizers.get(obj)

    def test_generic_featurizers_creation(self):
        cfg = {
            "id": "imputer",
            "type": "generic"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        assert isinstance(feat_obj, Imputer)

        cfg = {
            "id": "imputation_marker",
            "type": "generic"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert isinstance(feat_obj, ImputationMarker)

        cfg = {
            "id": "lambda_featurizer",
            "type": "generic"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert feat_obj.func(10) == 10
        assert feat_obj.func(15) == 15
        assert isinstance(feat_obj, LambdaTransformer)

        cfg = {
            "id": "minibatchkmeans_featurizer",
            "type": "generic"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert isinstance(feat_obj, MiniBatchKMeans)

        cfg = {
            "id": "maxabsscaler",
            "type": "generic"
        }
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert isinstance(feat_obj, MaxAbsScaler)

        cfg = {
            "id": "asdf",
            "type": "generic"
        }

        obj = FeatureConfig.from_dict(cfg)
        with self.assertRaises(ConfigException):
            Featurizers.get(obj)


if __name__ == "__main__":
    unittest.main()
