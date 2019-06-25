import json
import unittest

import numpy as np
import pandas as pd

from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import Imputer, MaxAbsScaler

from azureml.automl.core.featurization import GenericTransformer
from azureml.automl.core._engineered_feature_names import _GenerateEngineeredFeatureNames, FeatureTypeRecognizer


class TestGenericTransformer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.engineered_feature_name_generator = _GenerateEngineeredFeatureNames()
        super(TestGenericTransformer, self).__init__(*args, **kwargs)

    def test_get_transforms(self):
        d = {'col1': [1, 2, 3, 4, 5, 6, 7, 8, 9],
             'col2': [11, 12, 13, 14, 15, 16, 17, 18, 19]}
        df = pd.DataFrame(data=d)
        df.columns = ["col1", "col2"]
        generic_transformer = GenericTransformer()
        column_groups = {}
        column_groups.setdefault(FeatureTypeRecognizer.Numeric, ["col1", "col2"])
        transforms = generic_transformer.get_transforms(column_groups, self.engineered_feature_name_generator)
        assert(transforms is not None)
        assert(transforms[0][0][0] == 'col1')
        assert(transforms[0][0][1] == 'col2')
        assert(len(transforms) == 1)
        assert(isinstance(transforms[0][1][0], Imputer))
        assert(isinstance(transforms[0][1][1], MaxAbsScaler))
        assert(isinstance(transforms[0][1][2], MiniBatchKMeans))


if __name__ == '__main__':
    unittest.main()
