
import numpy as np

from qgomoku.core.board import Board, BoardTransform
from qgomoku.core.game_record import GameRecord

from qgomoku.util import utils

class FeatureBoard_v1_1:
    CHANNELS = 4
    def __init__(self, board):
        self._size = board.get_size()
        self._ops = []
        self.tensor = np.zeros((self._size, self._size, FeatureBoard_v1_1.CHANNELS))
        self._player_to_move = FeatureBoard_v1_1._board_player_to_value(board.get_player_to_move())
        self._init(board)

    @staticmethod
    def _board_player_to_value(board_player):
        return 1 if board_player == Board.FIRST_PLAYER else -1

    def _init(self, board):
        for i in range(board.get_size()):
            for j in range(board.get_size()):
                if board.get_spot(i, j) == Board.FIRST_PLAYER:
                    self.tensor[i, j, 0] = 1
                elif board.get_spot(i, j) == Board.SECOND_PLAYER:
                    self.tensor[i, j, 1] = 1
        self._update_last_player()

    def _get_features(self):
        return np.copy(self.tensor)

    def get_p_features(self):
        return self._get_features()

    def get_q_features(self):
        return self._get_features()

    def _last_move(self):
        return utils.peek_stack(self._ops)

    def _clear_last_move(self, last_move):
        if last_move:
            self.tensor[last_move.x, last_move.y, 2] = 0

    def _update_last_move(self, last_move):
        if last_move:
            self.tensor[last_move.x, last_move.y, 2] = 1

    def _set_spot(self, move):
        player_index = 0 if self._player_to_move == Board.FIRST_PLAYER else 1
        self.tensor[move.x, move.y, player_index] = 1

    def _clear_spot(self, move):
        self.tensor[move.x, move.y, 0] = 0
        self.tensor[move.x, move.y, 1] = 0

    def _flip_player(self):
        if self._player_to_move == Board.FIRST_PLAYER:
            self._player_to_move = Board.SECOND_PLAYER
        else:
            self._player_to_move = Board.FIRST_PLAYER

    def _update_last_player(self):
        player_value = 1 if self._player_to_move == Board.FIRST_PLAYER else -1
        self.tensor[:, :, 3].fill(player_value)

    def move(self, move):
        assert move
        self._clear_last_move(self._last_move())
        self._ops.append(move)
        self._set_spot(move)
        self._update_last_move(move)
        self._update_last_player()
        self._flip_player()

    def unmove(self):
        last_move = self._ops.pop()
        self._clear_last_move(last_move)
        self._clear_spot(last_move)
        self._update_last_move(self._last_move())
        self._update_last_player()
        self._flip_player()

class FeatureSet_v1_1:
    CHANNELS = 4
    def __init__(self, record_string, learning_rate=0.2):
        self.q_features = []
        self.q_labels = []
        self.p_features = []
        self.p_labels = []
        self.channels = 4
        self._learning_rate = learning_rate
        self.iterate_on(GameRecord.parse(record_string))

    def make_feature_tensors(self, board, next_move, curr_q, next_q, make_p=True, make_q=True):
        # board's last move should be last_move, next_move not performed yet
        feature_tensor = FeatureBoard_v1_1(board).get_p_features()

        rot = BoardTransform(size=board.get_size())
        tensor_rotations = rot.get_rotated_matrices(feature_tensor)
        to_move_rotations = rot.get_rotated_points(rot.coordinate_to_index(*next_move))

        for i in range(len(tensor_rotations)):
            if make_q:
                self.q_features.append(tensor_rotations[i])
                # here is the q learning update
                self.q_labels.append(self.bound_q(curr_q * (1 - self._learning_rate) + next_q * self._learning_rate))
            if make_p:
                self.p_features.append(tensor_rotations[i])
                self.p_labels.append(to_move_rotations[i])

    def bound_q(self, q):
        return max(min(q, 1.0), -1.0)

    def get_q(self):
        return self.q_features, self.q_labels

    def get_p(self):
        return self.p_features, self.p_labels

    def iterate_on(self, record):
        board = Board.load(record.get_initial_state())
        q_assessments = record.get_q_assessments()

        for i, move in enumerate(record.get_moves()):
            if record.get_winning_player() == board.get_player_to_move():
                self.make_feature_tensors(board, move, q_assessments[i][0], q_assessments[i][1])
            # learn drawn positions
            elif record.get_winning_player() == Board.NO_PLAYER:
                self.make_feature_tensors(board, move, q_assessments[i][0], q_assessments[i][1], make_p=False)
            board.move(*move)