import unittest

from boarml import CnnBaseArchitecture, ModelGenerator

from predictiveopt import PredictiveHyperOpt
import pandas as pd
import numpy as np
from numpy.random import seed
from tensorflow import set_random_seed


class TestAlgorithm(unittest.TestCase):

    def test_simulation(self):
        # Given
        expected = 87.69
        seed(13)
        set_random_seed(13)

        hp_searcher = PredictiveHyperOpt(total_models_count=50, full_models_count=5, final_epoch=45, partial_epochs=[4, 1], batch_size=1024,
                                         final_models_count=20)

        data = pd.read_csv('resources/simulation.txt', header=0)

        # When
        average_accuracy = hp_searcher.simulate(data, total_runs=10)

        # Then
        self.assertEquals(expected, average_accuracy)

    def test_real(self):
        # Given
        expected = 31.0
        expected_architecture = CnnBaseArchitecture((32, 32, 3), 10)
        expected_architecture = expected_architecture.build_from_file('resources/expected_architecture.txt')
        seed(13)
        set_random_seed(13)

        x_train = np.load('resources/x_train.npy')
        y_train = np.load('resources/y_train.npy')
        x_test = np.load('resources/x_test.npy')
        y_test = np.load('resources/y_test.npy')

        # Creating the architecture from file
        arch = CnnBaseArchitecture((32, 32, 3), 10)
        arch = arch.build_from_file('resources/architecture.txt')

        # Creating the generator
        generator = ModelGenerator(arch, 'keras', removal_rate=0.2, duplication_rate=0.2, amendment_rate=0.5, seed=13)

        # Performing Predictive Hyper Opt
        hp_searcher = PredictiveHyperOpt(total_models_count=10, full_models_count=1, final_epoch=3, partial_epochs=[2, 1], final_models_count=2,
                                         batch_size=250)

        actual, architecture = hp_searcher.run(generator, x_train, y_train, x_test, y_test)

        # Then
        self.assertEquals(expected, actual)
        self.assertEquals(str(expected_architecture), architecture)
