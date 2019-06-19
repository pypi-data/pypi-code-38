from noughts_and_crosses.position_strategy import (
    RandomPositionStrategy, MlPositionStrategy)


class Player(object):

    def __init__(self, counter, strategy):
        """
        Player of noughts and crosses.

        Parameters
        ----------
        counter : int
            Integer with value either 1 (representing crosses) or -1
            (representing noughts).
        strategy : noughts_and_crosses.position_strategy.PositionStrategy
        """
        self.counter = counter
        self.position_strategy = strategy

    @classmethod
    def initialise_random_player(cls, counter):
        """
        Player of noughts and crosses whose moves are randomly chosen.

        Parameters
        ----------
        counter : int
            Integer with value either 1 (representing crosses) or -1
            (representing noughts).

        Returns
        -------
        Instantiated version of this class.
        """
        return cls(counter, RandomPositionStrategy())

    @classmethod
    def initialise_ml_player(cls, counter):
        """
        Player of noughts and crosses whose moves are based on ML logic.

        Parameters
        ----------
        counter : int
            Integer with value either 1 (representing crosses) or -1
            (representing noughts).

        Returns
        -------
        Instantiated version of this class.
        """
        return cls(counter, MlPositionStrategy.initialise_linear_selector())

    def update(self, episode_recorder):
        """
        Update the underlying model on which an ML player is choosing moves.

        Parameters
        ----------
        episode_recorder : noughts_and_crosses.recorder.EpisodeRecorder
            Episode recorder containing records associated with a finished
            episode.
        """
        self.position_strategy.update(self.counter, episode_recorder)

    def choose_position(self, board):
        """
        Choose a position on which to place a counter on the board.

        Parameters
        ----------
        board : list of int
            Current state of the board before the new counter is placed.

        Returns
        -------
        int
            Value in the range [0, 8] representing the position on which the
            new counter will be placed.
        """
        return self.position_strategy.choose_counter_position(board)
