import random
import numpy as np
from sklearn import linear_model, preprocessing


class PositionStrategy(object):

    CAN_BE_UPDATED = False

    def __init__(self, *args, **kwargs):
        pass

    def choose_counter_position(self, game):
        pass


class RandomPositionStrategy(PositionStrategy):

    def choose_counter_position(self, board):
        """
        Randomly choose a position on which to place the counter.

        Parameters
        ----------
        board : list of int

        Returns
        -------
        int
        """
        return random.randint(0, 8)


class MlPositionStrategy(PositionStrategy):

    CAN_BE_UPDATED = True

    def __init__(self, exploration_probability, position_models):
        """
        Position strategy based on machine learning logic.

        Parameters
        ----------
        exploration_probability : float
            Value in the range [0.0, 1.0]. Dictate the trade-off between
            exploration and exploitation for the strategy. The larger the value,
            the more likely it is that the strategy will pick a random value.
        position_models : dict of (int, sklearn.SGDClassifier)
            Map each possible position to a model that dictates whether that
            position will be selected.
        """
        self.exploration_probability = exploration_probability
        self.position_models = position_models

    @classmethod
    def initialise_linear_selector(cls):
        """
        Initialise the strategy to use simple logistic regression models.

        Returns
        -------
        Instantiated version of this class.
        """
        return cls(
            1.0,
            {position: initialise_linear_model() for position in range(9)}
        )

    def update(self, counter, episode_recorder):
        """
        Update the position models.

        Iterate over the different models in the class, calling a partial fit
        method on each. The strategy should be, as a result, better in its
        choice of move in future games.

        Parameters
        ----------
        counter : int
            Integer with value either 1 (representing crosses) or -1
            (representing noughts).
        episode_recorder : noughts_and_crosses.recorder.EpisodeRecorder
            Episode recorder containing records associated with a finished
            episode.
        """
        for position_model_idx in range(9):
            boards = episode_recorder.extract_boards(counter, position_model_idx)

            if boards.size == 0:
                continue

            features = create_features(boards)
            labels = episode_recorder.extract_labels(counter, position_model_idx)
            weights = episode_recorder.extract_weights(counter, position_model_idx)

            self.position_models[position_model_idx].partial_fit(
                features, labels, sample_weight=weights)

        print('Updated position models')

    def choose_counter_position(self, board):
        """
        Choose a position based on the models underpinning the strategy.

        This strategy contains an exploration and exploitation capacity. The
        larger the value of the exploration_probability associated with the
        class, the more likely this method is to ignore its models and select
        a random strategy.

        Parameters
        ----------
        board : list of int

        Returns
        -------
        int
        """
        if random.random() < self.exploration_probability:
            return random.randint(0, 8)

        best_position = None
        max_probability = 0
        features = create_features(np.array(board).reshape(1, -1))
        for position, model in self.position_models.items():
            #if board[position] != 0:
            #    continue
            probability = model.predict_proba(features)[0][1]
            if probability >= max_probability:
                max_probability = probability
                best_position = position

        return best_position


def initialise_linear_model():
    """Initialise a logistic regression model that supports partial fitting."""
    lm = linear_model.SGDClassifier(loss='log')
    lm.partial_fit(
        np.concatenate([
            create_features(np.array([0] * 9).reshape(1, -1)),
            create_features(np.array([0] * 9).reshape(1, -1))
        ]),
        np.array([1, -1]),
        np.array([1, -1])
    )

    return lm


pairwise_featurer = preprocessing.PolynomialFeatures(include_bias=False)


def create_features(board):
    return pairwise_featurer.fit_transform(board)