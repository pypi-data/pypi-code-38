import unittest
import os
from ddt import ddt, file_data
import numpy as np
import pandas as pd

from unittest.mock import patch

from azureml.automl.core.featurizer.transformer import CategoricalFeaturizers


def _get_encoder(te_type: str, **kwargs):
    if te_type == 'te':
        return CategoricalFeaturizers.cat_targetencoder(**kwargs)
    elif te_type == 'woe':
        return CategoricalFeaturizers.woe_targetencoder(**kwargs)


@ddt
class TestCatTargetEncoder(unittest.TestCase):
    """
    Tests to ensure CatTargetEncoder works in KFold and NonKFold setting.
    """
    def __init__(self, *args, **kwargs):
        super(TestCatTargetEncoder, self).__init__(*args, **kwargs)

    @patch('sklearn.model_selection.KFold.split')
    @patch('sklearn.model_selection.StratifiedKFold.split')
    @file_data(os.path.join('..', 'data', 'categorical_test_data.json'))
    def test_fit_transform(self, stratify_mock, kfold_mock, data_filename, te_type, output_cols, fail_stratify=0):

        # setup data
        cls_dir_path = os.path.dirname(os.path.abspath(__file__))
        data_file_path = os.path.join(cls_dir_path, '..', 'data', data_filename)
        data = pd.read_csv(data_file_path)
        X = pd.Series(data.X)
        y = np.array(data.y)
        fold = data.fold
        expected_result = data[output_cols].values

        num_fold = len(fold.unique())

        if num_fold > 1:
            # select mock
            fold_values = pd.Series(fold.unique()).apply(
                lambda x: (fold[fold != x].index.values, fold[fold == x].index.values))
            if fail_stratify == 1:
                stratify_mock.side_effects = ValueError("Mock failure of stratification")
                kfold_mock.return_value = fold_values
            else:
                stratify_mock.return_value = fold_values

        te = _get_encoder(te_type, **{'num_folds': num_fold})
        features = te.fit_transform(X, y)

        assert features is not None
        assert np.isclose(features, expected_result, atol=0.001).all()


if __name__ == '__main__':
    unittest.main()
