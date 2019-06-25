import unittest

from ddt import ddt, file_data
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline, make_union
from sklearn.preprocessing import Normalizer
from sklearn_pandas import DataFrameMapper

from azureml.automl.core.featurizer.transformer import TextFeaturizers


@ddt
class TestTextTargetEncoder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestTextTargetEncoder, self).__init__(*args, **kwargs)

    @file_data('text_test_data.json')
    def test_fit_transform(self, X, y):
        df = pd.DataFrame(X)
        df.columns = ["news"]
        y = np.array(y)
        txtte = TextFeaturizers.text_target_encoder(**{"model_params": {"C": 1.0}, "model_class": LogisticRegression})

        interm_transforms = [("news", [make_pipeline(TextFeaturizers.string_cast(),
                                                     make_union(
                                                         TextFeaturizers.tfidf_vectorizer(
                                                             use_idf=False,
                                                             analyzer='char',
                                                             ngram_range=(3, 3)),
                                                         TextFeaturizers.tfidf_vectorizer(
                                                             use_idf=False,
                                                             analyzer='word',
                                                             ngram_range=(1, 2))),
                                                     Normalizer(copy=False))], {"alias": "intermin_features"})]

        mapper = DataFrameMapper(interm_transforms, input_df=True, sparse=True)
        mapper.fit(df, y)
        numeric_features = mapper.transform(df)
        features = txtte.fit_transform(numeric_features, y)
        assert features is not None
        assert features.shape == (len(X), len(np.unique(y)))


if __name__ == '__main__':
    unittest.main()
