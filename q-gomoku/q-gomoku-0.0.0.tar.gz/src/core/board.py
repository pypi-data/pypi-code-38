from collections import defaultdict

import numpy as np
import random
import json

from src.util import utils

class Move:
    def __init__(self, player, x, y):
        self.player = player
        self.x = x
        self.y = y


class GameState:
    WON = 1
    DRAW = 2
    NOT_OVER = 3

class BoardTransform:
    NUM_ROTATIONS = 8
    def __init__(self, size):
        self._size = size
        self._cached_point_rotations = defaultdict(list)
        self._cache_rotations()

    # Returns rotations and mirrors of the board state
    # This is important for teaching the convolution layers about rotational invariance
    def get_rotated_matrices(self, matrix):
        transposition_axes = (1, 0, 2)
        assert matrix.shape[0] == self._size
        return [
            matrix,
            np.transpose(matrix, axes=transposition_axes),
            np.rot90(matrix),
            np.transpose(np.rot90(matrix), axes=transposition_axes),
            np.rot90(matrix, 2),
            np.transpose(np.rot90(matrix, 2), axes=transposition_axes),
            np.rot90(matrix, 3),
            np.transpose(np.rot90(matrix, 3), axes=transposition_axes)
        ]

    def get_rotated_points(self, point):
        return self._cached_point_rotations[point]

    def coordinate_to_index(self, x, y):
        return x * self._size + y

    def index_to_coordinate(self, index):
        return int(index / self._size), int(index % self._size)

    # Precomputes some useful rotation values
    def _cache_rotations(self):
        indices = np.array(range(self._size ** 2)).reshape(self._size, self._size, 1)
        for i, matrix in enumerate(self.get_rotated_matrices(indices)):
            # iterate through the matrices
            for x in range(self._size):
                for y in range(self._size):
                    # where ever you see the matrix[x, y] value, indices[x, y] is where it originally started
                    self._cached_point_rotations[matrix[x, y, 0]].append(indices[x, y, 0])

# Board class represents the state of the game

# board perception will always be from the perspective of Player 1
# Q will always be from the perspective of Player 1 (Player 1 Wins = Q = 1, Player -1 Wins, Q = -1)

class Board:
    # channels
    NO_PLAYER = 0
    FIRST_PLAYER = 1
    SECOND_PLAYER = 2
    TURN_INFO_INDEX = 3

    STONE_PRESENT = 1
    STONE_ABSENT = 0

    def __init__(self, size=9, win_chain_length=5, draw_point=None):
        self._size = size

        # three for No Player, Player 1, Player 2, one for turn index
        self._matrix = np.zeros((self._size, self._size, 4), dtype=np.int)

        # Stone present for no player... make sense?
        self._matrix[:, :, Board.NO_PLAYER].fill(Board.STONE_PRESENT)

        # tracks which player played which spot (optimization)
        self._which_stone = np.zeros((self._size, self._size), dtype=np.int)

        self._win_chain_length = win_chain_length
        # stack of (x, y, player) tuple
        self._ops = []
        self._player_to_move = 1
        self._game_state = GameState.NOT_OVER
        self._available_moves = set()
        for i in range(self._size):
            for j in range(self._size):
                self._available_moves.add((i, j))

        self._num_moves = 0

        # number of plays at which it's a draw
        self.draw_point = draw_point if draw_point else self._size ** 2

    # for testing purposes
    def set_to_one_move_from_win(self):
        self.move(0, 0)
        self.move(0, 1)
        self.move(1, 0)
        self.move(1, 1)
        self.move(2, 0)
        self.move(2, 1)
        self.move(3, 0)
        self.move(3, 1)

    def unmove(self):
        previous_move = self._ops.pop()

        self._matrix[previous_move.x, previous_move.y, previous_move.player] = 0
        self._matrix[previous_move.x, previous_move.y, Board.NO_PLAYER] = 1
        self._which_stone[previous_move.x, previous_move.y] = Board.NO_PLAYER

        self._available_moves.add((previous_move.x, previous_move.y))
        self._flip_player_to_move()
        self._game_state = GameState.NOT_OVER

        self._num_moves -= 1

    def get_spot(self, x, y):
        return self._which_stone[x, y]

    def get_player_to_move(self):
        return self._player_to_move

    def get_player_last_move(self):
        return self._get_other_player(self.get_player_to_move())

    def get_last_move(self):
        return utils.peek_stack(self._ops)

    def get_size(self):
        return self._size

    # Places a stone at x, y for the next player's turn
    # Does not compute whether the game has completed or not (performance optimization)
    def blind_move(self, x, y):
        assert self._game_state is GameState.NOT_OVER
        self._ops.append(Move(self._player_to_move, x, y))

        self._matrix[x, y, self._player_to_move] = Board.STONE_PRESENT
        self._matrix[x, y, Board.NO_PLAYER] = Board.STONE_ABSENT

        self._which_stone[x, y] = self._player_to_move

        self._available_moves.remove((x, y))
        self._flip_player_to_move()

        self._num_moves += 1

    # Places a stone at x, y for the next player's turn
    # Computes whether game has concluded and if so, who the winner is
    def move(self, x, y):
        self.blind_move(x, y)
        self.compute_game_state()

    # Executes a random valid move
    def make_random_move(self):
        move_x, move_y = random.choice(list(self._available_moves))
        self.move(move_x, move_y)

    def _flip_player_to_move(self):
        self._player_to_move = self._get_other_player(self._player_to_move)

    def _get_other_player(self, player):
        if player == Board.FIRST_PLAYER:
            return Board.SECOND_PLAYER
        else:
            return Board.FIRST_PLAYER

    # returns None if game has not concluded, True if the last move won the game, False if draw
    # frequently called function, needs to be optimized
    def compute_game_state(self):
        last_move = utils.peek_stack(self._ops)
        if last_move:
            last_x, last_y = last_move.x, last_move.y
            if self.chain_length(last_x, last_y, -1, 0) + self.chain_length(last_x, last_y, 1, 0) >= self._win_chain_length + 1\
                    or self.chain_length(last_x, last_y, -1, 1) + self.chain_length(last_x, last_y, 1, -1) >= self._win_chain_length + 1\
                    or self.chain_length(last_x, last_y, 1, 1) + self.chain_length(last_x, last_y, -1, -1) >= self._win_chain_length + 1\
                    or self.chain_length(last_x, last_y, 0, 1) + self.chain_length(last_x, last_y, 0, -1) >= self._win_chain_length + 1:
                self._game_state = GameState.WON
                return
            if len(self._ops) == self._size ** 2:
                self._game_state = GameState.DRAW
                return
        self._game_state = GameState.NOT_OVER

    def _in_bounds(self, x, y):
        return 0 <= x < self._size and 0 <= y < self._size

    def chain_length(self, center_x, center_y, delta_x, delta_y):
        center_stone = self._which_stone[center_x, center_y]
        for chain_length in range(1, self._win_chain_length + 1):
            step_x = delta_x * chain_length
            step_y = delta_y * chain_length
            if not(0 <= center_x + step_x < self._size and 0 <= center_y + step_y < self._size and
                   self._matrix[center_x + step_x, center_y + step_y, center_stone] == 1):
                break
        return chain_length

    def is_move_available(self, x, y):
        return (x, y) in self._available_moves

    # runs a full compute
    def game_won(self):
        return self._game_state == GameState.WON

    # probably drawn, cheap check
    def game_assume_drawn(self):
        return len(self._ops) == self.draw_point

    def game_over(self):
        return self._game_state != GameState.NOT_OVER

    def get_winning_player(self):
        if self.game_over():
            return self._get_other_player(self._player_to_move)
        return Board.NO_PLAYER

    # simplest matrix representation of the board state
    def export(self):
        flatmatrix = np.zeros((self._size, self._size))
        for x in range(self._size):
            for y in range(self._size):
                if self._matrix[x, y, Board.FIRST_PLAYER] == 1:
                    flatmatrix[x, y] = Board.FIRST_PLAYER
                elif self._matrix[x, y, Board.SECOND_PLAYER] == 1:
                    flatmatrix[x, y] = Board.SECOND_PLAYER
        return {'size': str(self._size),
                           'win_chain_length': str(self._win_chain_length),
                            'boardstring': ''.join([str(elem) for elem in flatmatrix.astype(np.int32).reshape(-1)]),
                            'player_to_move': str(self._player_to_move)}

    # takes a board string and recreates a game state from it (quite slow)
    @classmethod
    def create_board_from_specs(Board, size, win_chain_length, boardstring):
        board = Board(size=size, win_chain_length=win_chain_length)
        player_1_moves = []
        player_2_moves = []
        reshaped_board = np.array([int(elem) for elem in boardstring]).reshape((size, size))
        for i in range(size):
            for j in range(size):
                if reshaped_board[i][j] == Board.FIRST_PLAYER:
                    player_1_moves.append((i, j))
                elif reshaped_board[i][j] == Board.SECOND_PLAYER:
                    player_2_moves.append((i, j))

        for i in range(len(player_1_moves)):
            board.blind_move(*player_1_moves[i])
            if i < len(player_2_moves):
                board.blind_move(*player_2_moves[i])

        return board

    @classmethod
    def load(Board, item_dict):
        return Board.create_board_from_specs(int(item_dict['size']),
                                             int(item_dict['win_chain_length']),
                                             item_dict['boardstring'])

    def pprint(self, lastmove_highlight=True):
        def display_char(x, y):
            move = utils.peek_stack(self._ops)
            if move:
                was_last_move = (x == move.x and y == move.y)
                if self._matrix[x, y, Board.FIRST_PLAYER] == 1:
                    if was_last_move and lastmove_highlight:
                        return 'X'
                    return 'x'
                elif self._matrix[x, y, Board.SECOND_PLAYER] == 1:
                    if was_last_move and lastmove_highlight:
                        return 'O'
                    return 'o'
            return ' '
        board_string = ""
        for i in range(0, self._size):
            board_string += "\n"
            for j in range(self._size):
                board_string += "|" + display_char(j, i)
            board_string += "|"
        return board_string

    def guide_print(self):
        def display_char(x, y):
            move = utils.peek_stack(self._ops)
            if move:
                was_last_move = (x == move.x and y == move.y)
                if self._matrix[x, y, Board.FIRST_PLAYER] == 1:
                    if was_last_move:
                        return 'X'
                    return 'x'
                elif self._matrix[x, y, Board.SECOND_PLAYER] == 1:
                    if was_last_move:
                        return 'O'
                    return 'o'
            return ' '
        board_string = " "

        for i in range(0, self._size):
            board_string += " " + str(i)
        for i in range(0, self._size):
            board_string += "\n" + str(i)
            for j in range(self._size):
                board_string += "|" + display_char(j, i)
            board_string += "|"
        return board_string

    def __str__(self):
        return self.pprint()

