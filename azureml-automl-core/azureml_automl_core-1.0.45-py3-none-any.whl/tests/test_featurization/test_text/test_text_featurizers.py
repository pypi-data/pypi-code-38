import unittest

from nimbusml.feature_extraction.text import NGramFeaturizer
from nimbusml.linear_model import AveragedPerceptronBinaryClassifier
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

from automl.client.core.common.exceptions import ConfigException
from azureml.automl.core.featurizer.transformer import TextFeaturizers, NimbusMLTextTargetEncoder, \
    BagOfWordsTransformer, WordEmbeddingTransformer
from azureml.automl.core.featurizer.transformer.text.constants import TFIDF_VECTORIZER_CONFIG
from azureml.automl.core.featurizer.transformer import StringCastTransformer
from azureml.automl.core.featurizer.transformer.generic import ModelBasedTargetEncoder
from azureml.automl.core.featurizer.transformer.text import StatsTransformer

from ... import utilities


class TestTextFeaturizers(unittest.TestCase):

    def test_instance_creation(self):
        tr = TextFeaturizers.bow_transformer()
        assert isinstance(tr, BagOfWordsTransformer)

        tr = TextFeaturizers.count_vectorizer()
        assert isinstance(tr, CountVectorizer)

        tr = TextFeaturizers.naive_bayes()
        assert isinstance(tr, ModelBasedTargetEncoder)
        assert tr._model_class == MultinomialNB

        tr = TextFeaturizers.string_cast()
        assert isinstance(tr, StringCastTransformer)
        self.assertTrue(utilities.check_pickleable(tr), msg="Failed to pickle {}".format(type(tr).__name__))

        tr = TextFeaturizers.text_stats()
        assert isinstance(tr, StatsTransformer)

        tr = TextFeaturizers.text_target_encoder(**{"model_params": {"C": 1.0}, "model_class": LogisticRegression})
        assert isinstance(tr, ModelBasedTargetEncoder)
        assert tr._model is None
        assert tr._model_class == LogisticRegression
        assert tr._model_params == {"C": 1.0}
        assert tr.get_model() is None

        tr = TextFeaturizers.tfidf_vectorizer()
        assert isinstance(tr, TfidfVectorizer)

        tr = TextFeaturizers.tfidf_vectorizer(use_idf=False,
                                              norm='l2',
                                              max_df=0.95,
                                              analyzer='char',
                                              ngram_range=(3, 3))
        assert isinstance(tr, TfidfVectorizer)
        assert tr.ngram_range == (3, 3)
        assert tr.use_idf is False
        assert tr.norm == 'l2'
        assert tr.analyzer == 'char'
        assert tr.max_df == 0.95

        tr = TextFeaturizers.tfidf_vectorizer(use_idf=TFIDF_VECTORIZER_CONFIG.USE_IDF,
                                              norm=TFIDF_VECTORIZER_CONFIG.NORM,
                                              analyzer=TFIDF_VECTORIZER_CONFIG.WORD_ANALYZER,
                                              ngram_range=(1, 2))
        assert isinstance(tr, TfidfVectorizer)
        assert tr.ngram_range == (1, 2)
        assert tr.use_idf is TFIDF_VECTORIZER_CONFIG.USE_IDF
        assert tr.norm == TFIDF_VECTORIZER_CONFIG.NORM
        assert tr.analyzer == TFIDF_VECTORIZER_CONFIG.WORD_ANALYZER

        with self.assertRaises(ConfigException):
            TextFeaturizers.text_target_encoder(**{"model_params": {"C": 1.0}})

        tr = TextFeaturizers.averaged_perceptron_text_target_encoder()
        assert isinstance(tr, NimbusMLTextTargetEncoder)
        assert isinstance(tr._learner, AveragedPerceptronBinaryClassifier)
        assert isinstance(tr._featurizer, NGramFeaturizer)

        tr = TextFeaturizers.word_embeddings()
        assert isinstance(tr, WordEmbeddingTransformer)
        tr.initialize()
        m = tr.model
        assert m is not None
        assert m.vector_size == tr.dim


if __name__ == '__main__':
    unittest.main()
