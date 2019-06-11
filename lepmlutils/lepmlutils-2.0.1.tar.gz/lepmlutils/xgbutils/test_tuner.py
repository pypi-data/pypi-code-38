import unittest
import os
import pandas as pd
from .tuner import Tuner
from .randsearcher import RandSearcher
from .randgridsearcher import RandGridSearcher

class TestTuner(unittest.TestCase):
    def setUp(self):
        self.dirname = os.path.dirname(__file__)
        self.dataset = pd.read_csv(self.dirname + "/resources/train.csv")
        
        self.features = [ 
            "Age", 
            "SibSp", 
            "Parch", 
            "Fare", 
        ]
        self.target = [
            "Survived",
        ]

    def test_error_for_bad_model_type(self):
        candidates = {
            'max_depth': range(4, 40, 10),
        }
        set_params = {
            "n_estimators": 40,
            "seed": 3
        }

        tuner = Tuner()
        try:
            tuner.tune(
                "invalid",
                candidates,
                set_params,
                self.dataset,
                self.features,
                self.target,
                3,
            )
        except ValueError:
                pass
        else:
            raise AssertionError("expected value error to have been raised")
            

    def test_partitions_correctly(self):
        candidates = {
            'max_depth': range(4, 40, 10),
        }
        set_params = {
            "n_estimators": 40,
            "seed": 3
        }

        tuner = Tuner()
        results = tuner.tune(
            "classifier",
            candidates,
            set_params,
            self.dataset,
            self.features,
            self.target,
            3,
        )

        self.assertEqual(4, len(results))
        for params in results:
            self.assertEqual(params["params"]["n_estimators"], 40)
            
        self.assertEqual(results[0]["params"]["max_depth"], 4)
        self.assertEqual(results[1]["params"]["max_depth"], 24)
        self.assertEqual(results[2]["params"]["max_depth"], 34)
        self.assertEqual(results[3]["params"]["max_depth"], 14)

        self.assertGreaterEqual(results[0]["test_score"], results[1]["test_score"])
        self.assertGreaterEqual(results[1]["test_score"], results[2]["test_score"])
        self.assertGreaterEqual(results[2]["test_score"], results[3]["test_score"])
    
    def test_runs_tunes_correctly(self):
        candidates = {
            'max_depth': range(2, 6),
            'n_estimators': range(10, 50, 10),
        }
        set_params = {
            # "n_estimators": 40,
        }

        tuner = Tuner()
        results = tuner.tune(
            "regressor",
            candidates,
            set_params,
            self.dataset,
            self.features,
            self.target,
            3,
        )

        self.assertEqual(16, len(results))
        for result in results:
            self.assertGreaterEqual(1.0, result["test_score"])
            self.assertGreaterEqual(1.0, result["train_score"])

    def test_rand_search(self):
        candidates = {
            'max_depth': range(2, 6),
            'n_estimators': range(10, 60, 10),
        }
        set_params = {
            # "n_estimators": 40,
        }

        tuner = Tuner()
        results = tuner.tune(
            "classifier",
            candidates,
            set_params,
            self.dataset,
            self.features,
            self.target,
            3,
            RandSearcher,
        )

        self.assertEqual(60, len(results))

    def test_grid_rand_search(self):
        candidates = {
            'max_depth': range(2, 6),
            'n_estimators': range(10, 40, 10),
        }
        set_params = {
            # "n_estimators": 40,
        }

        tuner = Tuner()
        results = tuner.tune(
            "classifier",
            candidates,
            set_params,
            self.dataset,
            self.features,
            self.target,
            3,
            RandGridSearcher,
        )

        self.assertEqual(12, len(results))

