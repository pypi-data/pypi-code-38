
from qgomoku.learner import pexp_mind
from qgomoku.core.board import Board
from qgomoku.core.minimax import PExpNode
import numpy as np

import random

SIZE = 9
CHANNELS = 4

import os
# bug with python on macos
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# good luck!
if __name__ == "__main__":
    mind = pexp_mind.PExpMind(size=SIZE, init=False, channels=CHANNELS)
    mind.load_net('../trained_models/9_4_4')

    def expanding_p(depth, p):
        return np.logical_or.reduce([
            np.logical_and(depth < 2, p > -6),
            np.logical_and(depth < 4, p > -4),
            np.logical_and(depth < 6, p > -4),
            np.logical_and(depth < np.inf, p > -3)
        ])


    def permissive_expansion(depth):
        if depth < 2:
            return np.inf
        if depth < 8:
            return 5
        return 3


    mind.define_policies(expanding_p, permissive_expansion, convergence_count=5,
                         alpha=0.2, q_exp_batch_size=SIZE ** 2,
                         p_exp_batch_size=SIZE ** 3, required_depth=6, max_iters=25)

    board = Board(size=SIZE, win_chain_length=5)

    # randomize the board a bit
    for j in range(random.randint(0, int(SIZE * 2.5))):
        board.make_random_move()

    print(board.guide_print())

    while True:
        if board.get_player_to_move() == Board.FIRST_PLAYER:
            inp = input("Input your move (i.e. \"3 5\"): ")
            if len(inp.split(' ')) != 2:
                print('Incorrect number of coordinates, please try again!')
                continue
            x, y = inp.split(' ')
            try:
                x = int(x)
                y = int(y)
            except:
                print('Please input Numbers!')
                continue
            if x < 0 or x >= SIZE or y < 0 or y >= SIZE:
                print('Out of bounds!')
                continue
            if not board.is_move_available(x, y):
                print('Invalid Move!')
                continue
            result = board.move(x, y)
            print(board.guide_print())
        else:
            print('Computer is thinking...')

            possible_moves, root_node = mind.p_search(board, False, root_node=None, save_root=False)

            best_move, best_node = possible_moves[0]
            print(" ")
            print(best_move, 'Q:', best_node.q)

            if best_node.q > PExpNode.MAX_MODEL_Q:
                print('Computer Resigns!')
                break

            board.move(*best_move)
            print(board.guide_print())

        if board.game_approx_drawn():
            print("DRAW!")
            break

        if board.game_won():
            if board.get_player_to_move() == 1:
                print('COMPUTER WINS!')
            else:
                print('YOU WIN!')
            break
