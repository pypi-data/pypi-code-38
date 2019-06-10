import json
import unittest
from typing import Dict, List

from azureml.automl.core.featurization import Featurizers

from automl.client.core.common import constants
from sklearn.linear_model import LogisticRegression

from azureml.automl.core.configuration.feature_config import FeatureConfig
from azureml.automl.core.featurizer.transformer import BagOfWordsTransformer, \
    WordEmbeddingTransformer, CatImputer, \
    ImputationMarker, LambdaTransformer, HashOneHotVectorizerTransformer, LabelEncoderTransformer, \
    StringCastTransformer, StatsTransformer, NimbusMLTextTargetEncoder, TextFeaturizers, \
    CategoricalFeaturizers, OneHotEncoderTransformer, DateTimeFeaturesTransformer, \
    GenericFeaturizers, NumericFeaturizers, BinTransformer, DateTimeFeaturizers
from azureml.automl.core.featurizer.transformer.generic import ModelBasedTargetEncoder, \
    CrossValidationTargetEncoder


class TestTransformerSerDeser(unittest.TestCase):
    def test_text_featurizers_to_dict(self):
        text_featurizers = TextFeaturizers()

        word_embedding_origin = text_featurizers.word_embeddings()
        assert isinstance(word_embedding_origin, WordEmbeddingTransformer)
        dct_origin = word_embedding_origin._to_dict()
        assert dct_origin["id"] == "word_embeddings"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["embeddings_name"] == "wiki_news_300d_1M_subword"
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        word_embedding_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(word_embedding_new, WordEmbeddingTransformer)

        bow_transformer_origin = text_featurizers.bow_transformer()
        assert isinstance(bow_transformer_origin, BagOfWordsTransformer)
        dct_origin = bow_transformer_origin._to_dict()
        assert dct_origin["id"] == "bow_transformer"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 7
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        bow_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(bow_transformer_new, BagOfWordsTransformer)

        naive_bayes_origin = text_featurizers.naive_bayes()
        assert isinstance(naive_bayes_origin, ModelBasedTargetEncoder)
        dct_origin = naive_bayes_origin._to_dict()
        assert dct_origin["id"] == "naive_bayes"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["model_class"] == 'sklearn.naive_bayes.MultinomialNB'
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        naive_bayes_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(naive_bayes_new, ModelBasedTargetEncoder)
        assert naive_bayes_origin._model_class == naive_bayes_new._model_class

        text_target_encoder_origin = text_featurizers.text_target_encoder(
            model_class=LogisticRegression)
        assert isinstance(text_target_encoder_origin, ModelBasedTargetEncoder)
        dct_origin = text_target_encoder_origin._to_dict()
        assert dct_origin["id"] == "text_target_encoder"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["model_class"] == 'sklearn.linear_model.logistic.LogisticRegression'
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        text_target_encoder_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(text_target_encoder_new, ModelBasedTargetEncoder)
        assert text_target_encoder_origin._model_class == text_target_encoder_new._model_class

        string_cast_transformer_origin = text_featurizers.string_cast()
        assert isinstance(string_cast_transformer_origin, StringCastTransformer)
        dct_origin = string_cast_transformer_origin._to_dict()
        assert dct_origin["id"] == "string_cast"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        string_cast_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(string_cast_transformer_new, StringCastTransformer)

        stats_transformer_origin = text_featurizers.text_stats()
        assert isinstance(stats_transformer_origin, StatsTransformer)
        dct_origin = stats_transformer_origin._to_dict()
        assert dct_origin["id"] == "text_stats"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["token_pattern"] == r"(?u)\w\w+\b"
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        stats_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(stats_transformer_new, StatsTransformer)

        averaged_perceptron_origin = text_featurizers.averaged_perceptron_text_target_encoder()
        assert isinstance(averaged_perceptron_origin, NimbusMLTextTargetEncoder)
        dct_origin = averaged_perceptron_origin._to_dict()
        assert dct_origin["id"] == "averaged_perceptron_text_target_encoder"
        assert dct_origin["type"] == "text"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        averaged_perceptron_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(averaged_perceptron_new, NimbusMLTextTargetEncoder)

    def test_categorical_featurizers_to_dict(self):
        categorical_featurizers = CategoricalFeaturizers()

        cat_imputer_origin = categorical_featurizers.cat_imputer()
        assert isinstance(cat_imputer_origin, CatImputer)
        dct_origin = cat_imputer_origin._to_dict()
        assert dct_origin["id"] == "cat_imputer"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["copy"] is True
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        cat_imputer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(cat_imputer_new, CatImputer)

        hashonehot_vectorizer_origin = categorical_featurizers.hashonehot_vectorizer()
        assert isinstance(hashonehot_vectorizer_origin, HashOneHotVectorizerTransformer)
        dct_origin = hashonehot_vectorizer_origin._to_dict()
        assert dct_origin["id"] == "hashonehot_vectorizer"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["hashing_seed_val"] == constants.hashing_seed_value
        assert dct_origin["kwargs"]["num_cols"] == 8096
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        hashonehot_vectorizer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(hashonehot_vectorizer_new, HashOneHotVectorizerTransformer)

        labelencoder_origin = categorical_featurizers.labelencoder()
        assert isinstance(labelencoder_origin, LabelEncoderTransformer)
        dct_origin = labelencoder_origin._to_dict()
        assert dct_origin["id"] == "labelencoder"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["hashing_seed_val"] == constants.hashing_seed_value
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        labelencoder_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(labelencoder_new, LabelEncoderTransformer)

        cat_targetencoder_origin = categorical_featurizers.cat_targetencoder()
        assert isinstance(cat_targetencoder_origin, CrossValidationTargetEncoder)
        dct_origin = cat_targetencoder_origin._to_dict()
        assert dct_origin["id"] == "cat_targetencoder"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["task"] == constants.Tasks.CLASSIFICATION
        assert dct_origin["kwargs"]["num_folds"] == 5
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        cat_targetencoder_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(cat_targetencoder_new, CrossValidationTargetEncoder)

        woe_targetencoder_origin = categorical_featurizers.woe_targetencoder()
        assert isinstance(woe_targetencoder_origin, CrossValidationTargetEncoder)
        dct_origin = woe_targetencoder_origin._to_dict()
        assert dct_origin["id"] == "woe_targetencoder"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["task"] == constants.Tasks.CLASSIFICATION
        assert dct_origin["kwargs"]["num_folds"] == 5
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        woe_targetencoder_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(woe_targetencoder_new, CrossValidationTargetEncoder)

        onehotencoder_origin = categorical_featurizers.onehotencoder()
        assert isinstance(onehotencoder_origin, OneHotEncoderTransformer)
        dct_origin = onehotencoder_origin._to_dict()
        assert dct_origin["id"] == "onehotencoder"
        assert dct_origin["type"] == "categorical"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        onehotencoder_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(onehotencoder_new, OneHotEncoderTransformer)

    def test_datetime_featurizers_to_dict(self):
        datetime_featurizers = DateTimeFeaturizers()

        datetime_transformer_origin = datetime_featurizers.datetime_transformer()
        assert isinstance(datetime_transformer_origin, DateTimeFeaturesTransformer)
        dct_origin = datetime_transformer_origin._to_dict()
        assert dct_origin["id"] == "datetime_transformer"
        assert dct_origin["type"] == "datetime"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        datetime_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(datetime_transformer_new, DateTimeFeaturesTransformer)

    def test_generic_featurizers_to_dict(self):
        generic_featurizers = GenericFeaturizers()

        imputation_marker_origin = generic_featurizers.imputation_marker()
        assert isinstance(imputation_marker_origin, ImputationMarker)
        dct_origin = imputation_marker_origin._to_dict()
        assert dct_origin["id"] == "imputation_marker"
        assert dct_origin["type"] == "generic"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        imputation_marker_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(imputation_marker_new, ImputationMarker)

        lambda_transformer_origin = generic_featurizers.lambda_featurizer()
        assert isinstance(lambda_transformer_origin, LambdaTransformer)
        dct_origin = lambda_transformer_origin._to_dict()
        assert dct_origin["id"] == "lambda_featurizer"
        assert dct_origin["type"] == "generic"
        assert len(dct_origin["args"]) == 0
        assert len(dct_origin["kwargs"]) == 0
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        lambda_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(lambda_transformer_new, LambdaTransformer)

    def test_numeric_featurizers_to_dict(self):
        numeric_featurizers = NumericFeaturizers()

        bin_transformer_origin = numeric_featurizers.bin_transformer()
        assert isinstance(bin_transformer_origin, BinTransformer)
        dct_origin = bin_transformer_origin._to_dict()
        assert dct_origin["id"] == "bin_transformer"
        assert dct_origin["type"] == "numeric"
        assert len(dct_origin["args"]) == 0
        assert dct_origin["kwargs"]["num_bins"] == 5
        json_string = self._json_serializable(dct_origin)
        dct_new = self._json_deserializable(json_string)
        self._compare_dict(dct_origin, dct_new)
        bin_transformer_new = self._create_transformer_from_dict(dct_new)
        assert isinstance(bin_transformer_new, BinTransformer)

    def _json_serializable(self, dct: Dict):
        try:
            return json.dumps(dct)
        except TypeError:
            self.fail("Unable to serialize the dict object to json")

    def _json_deserializable(self, json_string: str):
        try:
            return json.loads(json_string)
        except TypeError:
            self.fail("Unable to deserialize the json string to dict object")

    @staticmethod
    def _create_transformer_from_dict(cfg: Dict):
        obj = FeatureConfig.from_dict(cfg)
        feat_obj = Featurizers.get(obj)
        assert obj is not None
        assert feat_obj is not None
        return feat_obj

    def _compare_dict(self, dct1: Dict, dct2: Dict):
        assert len(dct1) == len(dct2)
        for k, v in dct1.items():
            value = dct2.get(k)
            if isinstance(v, Dict) and isinstance(value, Dict):
                self._compare_dict(v, value)
            elif isinstance(v, List) and isinstance(value, List):
                assert len(v) == len(value)
                for index, item in enumerate(v):
                    assert isinstance(item, type(value[index]))
                    assert item == value[index]
            elif isinstance(v, type(value)):
                assert v == value
            else:
                self.fail("Two dicts are not identical.")


if __name__ == "__main__":
    unittest.main()
