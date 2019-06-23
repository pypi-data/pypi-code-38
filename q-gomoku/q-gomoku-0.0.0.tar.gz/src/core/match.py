
import numpy as np
from src.core.board import Board
from src.core.game_record import GameRecord

# a match between two ai's
class Match:
    def __init__(self, mind1, mind2, size=9, random_seed=42, opening_moves=10, draw_point=50, trivialize=False):
        self.board = Board(size=size, win_chain_length=5, draw_point=draw_point)

        random_state = np.random.RandomState(random_seed)

        if not trivialize:
            # randomize the board a bit
            for j in range(random_state.randint(0, opening_moves)):
                self.board.make_random_move()
        else:
            self.board.set_to_one_move_from_win()

        self.players = {Board.FIRST_PLAYER: mind1, Board.SECOND_PLAYER: mind2}
        self.game_record = GameRecord.create(self.board)

    def play(self):
        print(self.board)
        current_player = self.board.get_player_to_move()

        while True:
            move, current_q, best_q = self.players[current_player].make_move(self.board,
                                                    as_player=current_player,
                                                    epsilon=0.1,
                                                    consistency_check=False,
                                                    verbose=True)
            print(self.board.pprint())

            self.game_record.add_move(move, current_q, best_q)
            self.board.move(*move)

            if self.board.game_over():
                self.game_record.set_winner(self.board.get_winning_player())
                break

            if current_player == Board.FIRST_PLAYER:
                current_player = Board.SECOND_PLAYER
            else:
                current_player = Board.FIRST_PLAYER

        return self.game_record.export()
