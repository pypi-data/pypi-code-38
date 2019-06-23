import numpy as np
import json
import pickle

class GameRecord:

    # winning_player values
    DRAW = 0
    # winning_player = Board.FIRST_PLAYER or Board.SECOND_PLAYER
    def __init__(self, initial_state_string, moves, winning_player, q_assessments):
        self.initial_state = initial_state_string
        self.moves = moves
        self._winning_player = winning_player
        self.q_assessments = q_assessments

    # initial_board_state (Board): initial position of the game
    @classmethod
    def create(cls, initial_board_state):
        return GameRecord(initial_board_state.export(), [], GameRecord.DRAW, [])

    @classmethod
    def parse(cls, string):
        obj_dict = json.loads(string)
        return GameRecord(obj_dict['initial_state'],
                          obj_dict['moves'],
                          obj_dict['winning_player'],
                          obj_dict['q_assessments'])

    class PrettyFloat(float):
        def __repr__(self):
            return '%.15g' % self

    def add_move(self, move, curr_q, best_q):
        # assert we have not concluded the game yet
        if self._winning_player != GameRecord.DRAW:
            raise ValueError
        self.moves.append(move)
        self.q_assessments.append((GameRecord.PrettyFloat(curr_q), GameRecord.PrettyFloat(best_q)))

    def set_winner(self, player):
        self._winning_player = player

    def export(self):
        obj_dict = {
            'initial_state': self.initial_state,
            'moves': self.moves,
            'winning_player': self._winning_player,
            'q_assessments': self.q_assessments
        }
        return json.dumps(obj_dict)

    def get_initial_state(self):
        return self.initial_state

    def get_moves(self):
        return self.moves

    def get_winning_player(self):
        return self._winning_player

    def get_q_assessments(self):
        return self.q_assessments