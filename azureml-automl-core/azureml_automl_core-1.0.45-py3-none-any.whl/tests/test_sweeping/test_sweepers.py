import unittest
from sklearn.datasets import fetch_20newsgroups
import pandas as pd
import json

from automl.client.core.common import constants
from azureml.automl.core.sweeping.meta_sweeper import Sweepers

from .test_meta_sweeper import MetaSweeperStub


class TestSweepers(unittest.TestCase):
    def test_instantiation(self):
        with self.assertRaises(TypeError):
            Sweepers.get("binary")

    def test_sweeper_config(self):
        removedata = ('headers', 'footers', 'quotes')
        categories = ['alt.atheism', 'talk.religion.misc', 'comp.graphics', 'sci.space']
        data_train = fetch_20newsgroups(subset='test',
                                        categories=categories,
                                        shuffle=True,
                                        random_state=42,
                                        remove=removedata)
        sampled_X = data_train.data[:300]
        sampled_y = data_train.target[:300]
        X = pd.DataFrame(sampled_X)
        y = sampled_y
        meta_sweeper = MetaSweeperStub(constants.Tasks.CLASSIFICATION, timeout_sec=120)
        sweepers = meta_sweeper._build_sweepers(X, y, meta_sweeper._enabled_sweeper_configs)
        for sweeper in sweepers:
            self.assertIsNotNone(sweeper.config)
            obj_repr = sweeper.__repr__()
            obj_str = sweeper.__str__()
            self.assertEqual(sweeper.config, obj_repr)
            self.assertEqual(sweeper.config, obj_str)
            config_obj = json.loads(sweeper.config)
            self.assertTrue(config_obj['SweeperType'] in ['binary'])
            self.assertTrue(config_obj['DataProvider'] in ['DiskBasedDataProvider', 'InMemoryDataProvider'])
            self.assertTrue(len(config_obj['BaselineTransforms']) > 0)
            self.assertTrue(len(config_obj['ExperimentTransforms']) > 0)
            self.assertTrue(config_obj['Estimator'] in ['LogisticRegression',
                                                        'LinearRegression', 'LGBMClassifier', 'LGBMRegressor'])
            self.assertTrue(config_obj['Scorer'] in ['ClassificationScorer', 'RegressionScorer'])
            self.assertTrue(config_obj['Epsilon'] > 0)
            self.assertTrue(config_obj['IncludeBaselineInExperiment'] in [True, False])
            self.assertTrue(config_obj['Task'] in constants.Tasks.ALL)
            self.assertTrue(config_obj['MetricName']in ['accuracy'])
            self.assertTrue(config_obj['UseCrossValidation'] in [True, False])


if __name__ == '__main__':
    unittest.main()
