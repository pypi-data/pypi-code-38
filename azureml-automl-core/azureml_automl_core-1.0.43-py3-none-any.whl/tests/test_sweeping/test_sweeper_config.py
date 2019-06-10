import logging
import unittest
import os
import json
import pickle

from azureml.automl.core.configuration import ConfigKeys
from azureml.automl.core.configuration.sweeper_config import SweeperConfig
from automl.client.core.common.activity_logger import TelemetryActivityLogger


class TestSweeperConfig(unittest.TestCase):
    def test_from_dict(self):
        cfg_file = os.path.join(os.path.split(__file__)[0], "..", "..", "azureml", "automl", "core",
                                "sweeping", "config.json")
        with open(cfg_file, 'r') as f:
            data = json.load(f)

            sweepers_configs = data['classification'][ConfigKeys.ENABLED_SWEEPERS]
        for cfg in sweepers_configs:
            obj = SweeperConfig.from_dict(cfg)
            assert isinstance(obj, SweeperConfig)
            assert isinstance(obj._enabled, bool)

    def test_logger_pickle(self):
        # assert that a TelemetryActivityLogger survives getstate as it a pickleable instance
        logger = TelemetryActivityLogger()
        sc = SweeperConfig(logger=logger)
        pickle.loads(pickle.dumps(sc))
        self.assertIsNotNone(sc.__getstate__()["_logger"])

        # assert that another logger is reset to None in getstate as it not a pickleable instance
        logger = logging.getLogger("")
        sc = SweeperConfig(logger=logger)
        pickle.loads(pickle.dumps(sc))
        self.assertIsNone(sc.__getstate__()["_logger"])


if __name__ == '__main__':
    unittest.main()
