import unittest
import pickle
from io import BytesIO

from ddt import ddt, data, file_data

import numpy as np
import pandas as pd
from azureml.automl.core.featurizer.transformer.text.wordembedding_transformer import WordEmbeddingTransformer

from azureml.automl.core.featurizer.transformer import TextFeaturizers
from ..data.mock_embeddings_provider import MockWordEmbeddingsProvider


@ddt
class TestWordEmbeddingTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestWordEmbeddingTransformer, self).__init__(*args, **kwargs)

    @file_data('text_test_data.json')
    def test_transform(self, X, y):
        df = pd.DataFrame(X[0:2])
        df.columns = ["news"]
        vector_size = 10
        num_rows = len(df)
        transformer = WordEmbeddingTransformer(embeddings_provider=MockWordEmbeddingsProvider(
            vector_size=vector_size))
        features = transformer.fit_transform(df.values)
        assert features.shape == (num_rows, vector_size)
        assert np.array_equal(np.zeros((num_rows, vector_size)), features) is False

        # Test in and out of vocabulary
        data1 = np.random.rand(101)
        features = transformer.fit_transform(data1.astype(str))
        assert features.shape == (101, vector_size)

        # Test in vocabulary
        data2 = np.arange(100)
        features = transformer.fit_transform(data2.astype(str))
        assert np.array_equal(np.zeros((100, vector_size)), features) is False

        # Test out of vocabulary
        data3 = np.arange(100, 200)
        features = transformer.fit_transform(data3.astype(str))
        assert np.array_equal(np.zeros((100, vector_size)), features)

        # Test out of vocabulary pandas series
        data4 = pd.Series(np.arange(100, 200))
        features = transformer.fit_transform(data4.astype(str))
        assert np.array_equal(np.zeros((100, vector_size)), features)

        # Test in vocabulary pandas series
        data5 = pd.Series(np.arange(100))
        features = transformer.fit_transform(data5.astype(str))
        assert np.array_equal(np.zeros((100, vector_size)), features) is False

    def test_newsgroups_transform(self):
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.model_selection import train_test_split

        removedata = ('headers', 'footers', 'quotes')
        categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']

        data_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42,
                                        remove=removedata)
        X_train, _, y_train, _ = train_test_split(data_train.data, data_train.target, test_size=0.33, random_state=42)

        X_train = pd.DataFrame(data=X_train)
        stringcast = TextFeaturizers.string_cast()
        string_data = stringcast.fit_transform(X_train.values)
        transformer = TextFeaturizers.word_embeddings()
        features = transformer.fit_transform(string_data, y_train)
        assert features is not None
        assert features[0].shape == (transformer.dim,)
        assert features.shape == (len(X_train), transformer.dim)

    def test_check_picklability(self):
        tr = TextFeaturizers.word_embeddings()
        X = pd.Series(["Hello"], ["Hello1"])
        tr.fit_transform(X)
        # TODO Figure out how to import the check_pickeable from test_utilities

        # Currently tests is not a module therefore, importing by using relative path is throwing
        # the following error: ValueError: attempted relative import beyond top-level package
        def check_pickleable(obj):
            try:
                with BytesIO() as f:
                    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
                return True
            except Exception:
                return False
        check_pickleable(tr)


if __name__ == "__main__":
    unittest.main()
