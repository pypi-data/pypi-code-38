import json
import unittest
import re

from ddt import ddt, data, file_data
import numpy as np
import pandas as pd
from sklearn_pandas import DataFrameMapper

from azureml.automl.core.featurization import TextTransformer
from azureml.automl.core.featurizer.transformer import StringCastTransformer
from azureml.automl.core._engineered_feature_names import _GenerateEngineeredFeatureNames
from sklearn.feature_extraction.text import TfidfVectorizer

tokenizer = re.compile(r"(?u)\b\w\w+\b")


@ddt
class TestTextTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.engineered_feature_name_generator = _GenerateEngineeredFeatureNames()
        super(TestTextTransformer, self).__init__(*args, **kwargs)

    @file_data('text_test_data.json')
    def test_get_transforms(self, X, y):
        df = pd.DataFrame(X)
        df.columns = ["news"]
        text_transformer = TextTransformer()
        transforms = text_transformer.get_transforms("news", "news", 2, self.engineered_feature_name_generator)
        assert(transforms is not None)
        assert(len(transforms) == 2)
        # Assert that column data is the same
        assert transforms[0][0] == transforms[1][0]
        assert isinstance(transforms[0][1][0], StringCastTransformer)
        assert isinstance(transforms[1][1][0], StringCastTransformer)

        assert isinstance(transforms[0][1][1], TfidfVectorizer)
        assert isinstance(transforms[1][1][1], TfidfVectorizer)


if __name__ == '__main__':
    unittest.main()


# # This is how text_test_data.json has been generated
# def get_20news():
#     from sklearn.datasets import fetch_20newsgroups
#     data = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
#     X = np.array(data.data[0:500])
#     y = np.array(data.target[0:500])
#     del data
#     with open('text_test_data.json', 'w') as fp:
#         json.dump({"newsgroups": {"X": X.tolist(), "y": y.tolist()}}, fp)
#     fp.close()
#     return X.ravel(), y
