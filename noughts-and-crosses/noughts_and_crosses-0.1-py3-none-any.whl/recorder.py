import numpy as np
from collections import Counter

ERROR_WEIGHT = 10
DRAW_MOVE_WEIGHT = 1
FINAL_VICTORY_PLACEMENT_WEIGHT = 10
VICTORY_LOSS_MODE_WEIGHT = 2


class GameRecorder(object):

    def __init__(
            self, placement_errors=None, correct_placements=None, winner=None):
        """
        Create an empty recorder.

        Parameters
        ----------
        placement_errors : list of lists
            List of all attempted moves in the game that resulted in a placement
            exception. Each attempted move is expected to be structured as a
            list of 11 elements. The first element is the player counter, the
            second is the position on which the player attempted to place a
            counter and the remaining elements represent the state of the board
            when the move was made.
        correct_placements : list of lists
            List of all successful moves in the game. Each successful move is
            structured as the attempted moves in the object placement_errors.
        winner : int
            Either 1 if crosses won the game, or -1 if noughts won the game.
        """
        self.placement_errors = placement_errors or []
        self.correct_placements = correct_placements or []
        self.winner = winner or None

    def record_placement_error(self, player, board, position):
        """Record the fact that an attempted move led to a placement error."""
        self.placement_errors.append((player, position, *board))

    def record_correct_placement(self, player, board, position):
        """Record a successful placement."""
        self.correct_placements.append((player, position, *board))

    def record_winner(self, winner):
        """Record the winner of the game."""
        self.winner = winner


class EpisodeRecorder(object):

    def __init__(self, records=None, winners=None):
        self.records = records or []
        self.winners = winners or []

    def snapshot_game(self, game_recorder):
        """
        Augment the existing records with that of the current game recorder.

        Parameters
        ----------
        game_recorder : GameRecorder
        """
        self.winners.append(game_recorder.winner)

        self.records.extend(
            [[-1 * ERROR_WEIGHT, *record]
             for record in game_recorder.placement_errors]
        )

        if game_recorder.winner is not None:

            self.records.extend(
                [[
                    VICTORY_LOSS_MODE_WEIGHT * record[0] * game_recorder.winner,
                    *record
                ]
                 for record in game_recorder.correct_placements[:-1]]
            )
            self.records.append([
                FINAL_VICTORY_PLACEMENT_WEIGHT,
                *game_recorder.correct_placements[-1]
            ])

        else:
            self.records.extend(
                [[DRAW_MOVE_WEIGHT, *record]
                 for record in game_recorder.correct_placements]
            )

    def finish_recording(self):
        """Indicate the recorder to stop recording new moves."""
        self.records = np.array(self.records)

    def extract_boards(self, counter, position):
        """
        Extract the boards leading to each move in the episode for a given
        position and counter.

        Parameters
        ----------
        counter : int
            Either 1 (crosses) or -1 (noughts).
        position : int
            Value in the range [0, 8]

        Returns
        -------
        np.array
        """
        return self.records[(self.records[:, 1] == counter)
                            & (self.records[:, 2] == position), 3:]

    def extract_weights(self, counter, position):
        """
        Extract the weights of each move in the episode for a given position
        and counter.

        The following weights are used:
            1 : move that resulted in a draw
            2 : move that eventually resulted in a win or loss
            10 : move that directly won a game; move that yielded a placement
                exception

        Parameters
        ----------
        counter : int
            Either 1 (crosses) or -1 (noughts).
        position : int
            Value in the range [0, 8]

        Returns
        -------
        np.ndarray
        """
        return np.abs(
            self.records[(self.records[:, 1] == counter)
                         & (self.records[:, 2] == position), 0]
        )

    def extract_labels(self, counter, position):
        """
        Extract the labels of each move in the episode for a given position
        and counter.

        The following labels are used:
            -1 : the player of the move lost
            1 : the player of the move either won or drew

        Parameters
        ----------
        counter : int
            Either 1 (crosses) or -1 (noughts).
        position : int
            Value in the range [0, 8]

        Returns
        -------
        np.ndarray
        """
        return np.sign(
            self.records[(self.records[:, 1] == counter)
                         & (self.records[:, 2] == position), 0]
        )

    def print_metrics(self):
        """Print out the fraction of crosses and noughts victories."""
        winner_counter = Counter(self.winners)

        print('Crosses win fraction: {}'.format(
            winner_counter[1] / len(self.winners)))
        print('Noughts win fraction: {}'.format(
            winner_counter[-1] / len(self.winners)))
