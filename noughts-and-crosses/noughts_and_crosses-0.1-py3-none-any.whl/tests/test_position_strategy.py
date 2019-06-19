import pytest
from unittest.mock import patch

from noughts_and_crosses import position_strategy
from sklearn import linear_model
import numpy as np


class TestRandomPositionStrategy(object):

    def test_can_be_updated(self):
        assert position_strategy.RandomPositionStrategy.CAN_BE_UPDATED == False

    def test_choose_counter_position(self):
        strategy = position_strategy.RandomPositionStrategy()

        positions = [
            strategy.choose_counter_position(None) for __ in range(100)]

        assert all(0 <= position <= 8 for position in positions)


class TestMlPositionStrategy(object):

    def test_choose_counter_position(self):
        board = [0] * 9
        strategy = position_strategy.MlPositionStrategy(
            0.0, {
                position: linear_model.SGDClassifier() for position in range(9)}
        )

        probabilities = [
            [[1, 0]],
            [[1, 0]],
            [[1, 0]],
            [[1, 1]],
            [[1, 0]],
            [[1, 0]],
            [[1, 0]],
            [[1, 0]],
            [[1, 0]]
        ]

        with patch.object(
                linear_model.SGDClassifier, 'predict_proba',
                side_effect=probabilities):
            position = strategy.choose_counter_position(board)

        assert position == 3


def test_initialise_linear_model():
    lm = position_strategy.initialise_linear_model()
    assert list(lm.classes_ == [-1, 1])


@pytest.mark.parametrize('board, expected_features', [
    (np.array([2, 3]).reshape(1, -1),
     np.array([2.0, 3.0, 4.0, 6.0, 9.0]).reshape(1, -1))
])
def test_create_features(board, expected_features):
    np.testing.assert_almost_equal(
        position_strategy.create_features(board), expected_features)
