import pickle

import keras
import numpy as np
from src.core.board import Board, GameState
from src.core.minimax import PExpNode
from src.core import minimax
from keras import losses
from keras.layers import Input, Convolution2D, Dense, Flatten, BatchNormalization
from keras.models import Model  # basic class for specifying and training a neural network
from sortedcontainers import SortedList


class PExpMind:
    def __init__(self, size, channels=1, init=True):

        self.size = size
        self.channels = channels

        if self.size == 7:
            self.value_est = self.value_model_7()
            self.policy_est = self.policy_model_7()
        elif self.size == 9:
            self.value_est = self.value_model_9()
            self.policy_est = self.policy_model_9()
        else:
            self.value_est = self.get_value_model()
            self.policy_est = self.get_policy_model()

        # search and training parameters
        self._max_expansion = lambda depth: np.inf if depth < 2 else 5
        self._p_threshold = lambda depth, log_p: log_p > -10
        self._move_convergence_count = lambda depth: 5

        self.p_exp_batch_size = 100
        self.max_iters = 10
        self.required_depth = 4

        # initialization
        init_examples = 10

        if init:
            sample_x = [np.random.randint(-1, 1, size=(init_examples, size, size, self.channels))]
            self.value_est.fit(sample_x, y=np.zeros(init_examples), epochs=1, batch_size=100)
            self.policy_est.fit(sample_x, y=np.zeros((init_examples, self.size ** 2)))

        self.train_vectors = []
        self.train_q = []
        self.train_p = []

        self.fitted = False

        self.memory_root = None

    def value_model_7(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and conv network is padding
        conv_1 = Convolution2D(64, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(32, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)

        flat = Flatten()(bn3)

        hidden = Dense(10, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(1, use_bias=False)(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss=losses.mean_squared_error, optimizer='adam', metrics=['mean_squared_error'])

        return model

    def value_model_9(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and conv network is padding
        conv_1 = Convolution2D(64, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(32, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)
        conv_3 = Convolution2D(16, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn3)
        bn4 = BatchNormalization()(conv_3)

        flat = Flatten()(bn4)

        hidden = Dense(20, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(1, use_bias=False)(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss=losses.mean_squared_error, optimizer='adam', metrics=['mean_squared_error'])

        return model

    def policy_model_7(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and conv network is padding
        conv_1 = Convolution2D(64, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(32, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)
        conv_3 = Convolution2D(16, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn3)
        bn4 = BatchNormalization()(conv_3)
        conv_4 = Convolution2D(8, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn4)
        bn5 = BatchNormalization()(conv_4)

        flat = Flatten()(bn5)

        hidden = Dense(self.size ** 2, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(self.size ** 2, activation='softmax')(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return model


    def policy_model_9(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and value network
        conv_1 = Convolution2D(64, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(64, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)
        conv_3 = Convolution2D(64, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn3)
        bn4 = BatchNormalization()(conv_3)
        conv_4 = Convolution2D(32, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn4)
        bn5 = BatchNormalization()(conv_4)
        conv_5 = Convolution2D(16, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn5)
        bn6 = BatchNormalization()(conv_5)

        flat = Flatten()(bn6)

        hidden = Dense(self.size ** 2, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(self.size ** 2, activation='softmax')(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return model

    def get_value_model(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and conv network is padding
        conv_1 = Convolution2D(64, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(32, (3, 3), padding='valid', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)
        #conv_3 = Convolution2D(32, (3, 3), padding='valid', activation='relu',
        #                       kernel_initializer='random_normal', use_bias=False)(bn3)
        #bn4 = BatchNormalization()(conv_3)
        #conv_4 = Convolution2D(16, (3, 3), padding='valid', activation='relu',
        #                       kernel_initializer='random_normal', use_bias=False)(bn4)
        #bn5 = BatchNormalization()(conv_4)

        flat = Flatten()(bn3)

        hidden = Dense(10, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(1, use_bias=False)(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss=losses.mean_squared_error, optimizer='adam', metrics=['mean_squared_error'])

        return model

    def get_policy_model(self):
        inp = Input(shape=(self.size, self.size, self.channels))

        # key difference between this and conv network is padding
        conv_1 = Convolution2D(64, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(inp)
        bn2 = BatchNormalization()(conv_1)
        conv_2 = Convolution2D(32, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn2)
        bn3 = BatchNormalization()(conv_2)
        conv_3 = Convolution2D(16, (3, 3), padding='same', activation='relu',
                               kernel_initializer='random_normal', use_bias=False)(bn3)
        bn4 = BatchNormalization()(conv_3)
        #conv_4 = Convolution2D(8, (3, 3), padding='same', activation='relu',
        #                       kernel_initializer='random_normal', use_bias=False)(bn4)
        #bn5 = BatchNormalization()(conv_4)

        flat = Flatten()(bn4)

        hidden = Dense(10, activation='relu', kernel_initializer='random_normal', use_bias=False)(flat)
        bn_final = BatchNormalization()(hidden)

        out = Dense(self.size ** 2, activation='softmax')(bn_final)

        model = Model(inputs=[inp], outputs=out)
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return model

    def pvs_k_principal_variations(self, leaf_nodes):
        # include the best move according to q
        principal_variations = []
        for item in leaf_nodes:
            if item.game_status == GameState.NOT_OVER:
                principal_variations.append(item)
            if len(principal_variations) == self.p_exp_batch_size:
                break
        return principal_variations

    def p_search(self, board, is_maximizing, root_node=None, save_root=True, consistency_check=False, verbose=True):

        if root_node is None:
            root_node = PExpNode(parent=None,
                                                is_maximizing=is_maximizing,
                                                full_move_list=minimax.MoveList(moves=(), position_hash=[]))

        principal_variations = [root_node]

        transposition_table = {}

        # all nodes at the leaves of the search tree
        leaf_nodes = SortedList(principal_variations, key=lambda x: x.p_comparator)

        i = 0
        MAXED_DURATION = 5

        previously_removed = set()

        principal_qs = []
        best_children = []
        # if we haven't completed enough iterations
        # or we're on a really shallow PV
        while True:
            i += 1

            # the ways P search terminates
            if i > self.max_iters:
                # break if there's some hanging issue
                if i > self.max_iters * 5:
                    break

                # same child has been best child for awhile now
                if len(set(best_children[-self._move_convergence_count:])) == 1\
                        and len(root_node.principal_variation.full_move_list) > self.required_depth:
                    break

                if root_node.principal_variation.game_status == GameState.DRAW:
                    break

            # searching doesn't get us anywhere for awhile
            if root_node.principal_variation and root_node.principal_variation.q:
                best_children.append(root_node.best_child)
                principal_qs.append(root_node.principal_variation.q)
                # had the same best q for MAXED_DURATION iterations
                if len(principal_qs) > MAXED_DURATION and np.abs(np.mean(principal_qs[-MAXED_DURATION : -1])) == 1:
                    if verbose:
                        print('Maxed Duration')
                    break

            # p expansion
            self.p_expand(board, principal_variations, leaf_nodes, transposition_table, previously_removed, verbose=verbose)

            principal_variations = self.pvs_k_principal_variations(leaf_nodes)

            # nothing left
            if not principal_variations:
                break

            # P will already have been expanded so do a Q eval
            #self.q_eval_top_leaves(leaf_nodes, min_eval_q=k ** 2, max_eval_q=k ** 2)
            self.q_eval(leaf_nodes)

            # this is used in case the p expansion doesn't capture the nodes we need to hit (if q_exp_batch_size is large enough this isn't needed)
            next_pvs = self.highest_leaf_qs(leaf_nodes, is_maximizing, max_p_eval=self.p_exp_batch_size * 2, num_leaves=self.q_exp_batch_size)
            print('Difference between P Expand and Q expand', len(next_pvs) + len(principal_variations), len(set(next_pvs + principal_variations)))

            #principal_variations.extend(next_pvs)

            if consistency_check:
                root_node.consistent_pv()

            # this check doesn't hold if we do PV Q extensions
            #if root_node.principal_variation:
            #    root_node.top_down_q()
            #    assert(abs(root_node.principal_variation.q - root_node.negamax()[0]) < 1E-4)

            # if we have a PV, add it to expand
            if root_node.principal_variation and root_node.principal_variation.game_status == GameState.NOT_OVER:
                # pv could point to a 'stable' node that doesn't expand
                #assert(root_node.principal_variation not in previously_removed)
                assert(not root_node.principal_variation.has_children())
                principal_variations.append(root_node.principal_variation)

            # remove duplicates
            principal_variations = set(principal_variations)

            print('Root', str(root_node))

        q_stats, p_stats = root_node.recursive_stats()
        print('Explored ' + str(p_stats) + " States (Q evals: " + str(q_stats) + ") in " + str(i) + " Iterations")

        possible_moves = root_node.get_sorted_moves()

        for move, q in possible_moves:
            node = root_node.children[move]
            print('Move', move, str(node))

        if save_root:
            self.pickle_root(board, root_node)

        return possible_moves, root_node


    def highest_leaf_qs(self, leaf_nodes, is_maximizing, max_p_eval=100, num_leaves=10):
        num_eval = min(max_p_eval, len(leaf_nodes))
        valid_leaves = [leaf for leaf in leaf_nodes.islice(0, num_eval) if leaf.is_assigned_q and leaf.game_status == GameState.NOT_OVER]
        best_leaves = sorted(valid_leaves, key=lambda x: abs(x.q), reverse=True)
        return best_leaves[:num_leaves]

    def q_eval(self, nodes):
        parents_to_update = set()
        board_matrices = []
        nodes = [node for node in nodes if not node.is_assigned_q]
        for leaf in nodes:
            # normally not, but it can be if nodes = PV's children
            assert(leaf.game_status == GameState.NOT_OVER)
            assert(not leaf.has_children())
            parents_to_update.update(leaf.parents)
            board_matrices.append(leaf.get_matrix())

        # if nothing to eval, get out
        if len(board_matrices) == 0:
            return

        # attach q predictions to all leaves and compute q tree at once
        q_predictions = np.clip(
                    self.value_est.predict(np.array(board_matrices), batch_size=1000).reshape(len(board_matrices)),
                    a_max=PExpNode.MAX_MODEL_Q,
                    a_min=PExpNode.MIN_MODEL_Q
            )

        for i, leaf in enumerate(nodes):
            # it's possible to have transposition assign q's even if we filtered above
            if not leaf.is_assigned_q:
                leaf.assign_q(q_predictions[i], GameState.NOT_OVER)

        for parent in parents_to_update:
            parent.recalculate_q()

    def q_eval_top_leaves(self, leaf_nodes, min_eval_q=10, max_eval_q=1000):
        # will only contain leaves of games not being over
        num_eval = min(max(min_eval_q, len(leaf_nodes)), max_eval_q)
        best_leaves = leaf_nodes.islice(0, num_eval)
        self.q_eval(best_leaves)

    # returns a list of board vectors for each node in nodes_to_expand
    def get_board_vectors(self, board, nodes_to_expand):
        p_search_vectors = []
        for parent in nodes_to_expand:
            # for each move except the last, make rapid moves on board
            if parent.has_matrix():
                p_search_vectors.append(parent.get_matrix())
            else:
                for move in parent.full_move_list.moves:
                    board.blind_move(*move)

                p_search_vectors.append(board.get_matrix())

                for _ in parent.full_move_list.moves:
                    board.unmove()
        return p_search_vectors

    accessed_transposition = 0

    # p_threshold(depth, p) returns a boolean vector filter
    # max_expansion(depth) returns an integer
    def define_policies(self, p_threshold, max_expansion, convergence_count,
                        alpha=0.2, p_exp_batch_size=25, q_exp_batch_size=25,
                        required_depth=4, max_iters=20):
        self._p_threshold = p_threshold
        self._max_expansion = max_expansion
        self._move_convergence_count = convergence_count

        self.p_exp_batch_size = p_exp_batch_size
        self.q_exp_batch_size = q_exp_batch_size
        self.alpha = alpha
        self.required_depth = required_depth
        self.max_iters = max_iters
    # Expand all nodes_to_expand, updating leaf_nodes in place
    # Also passes
    def p_expand(self, board, nodes_to_expand, leaf_nodes, transposition_table, previously_removed, verbose=True):
        for parent in nodes_to_expand:
            if parent in previously_removed:
                continue
            # parent could be a 'stable' node
            #assert(parent not in previously_removed)
            # should NOT be expanding any non-leaf node
            assert(parent in leaf_nodes)
            try:
                leaf_nodes.remove(parent)
            except ValueError:
                print(parent.p_comparator)
            previously_removed.add(parent)

        # each board state is defined by a list of moves
        p_search_vectors = self.get_board_vectors(board, nodes_to_expand)
        p_search_nodes = list(nodes_to_expand)

        p_board_vectors = np.array(p_search_vectors).reshape(len(p_search_vectors), self.size, self.size,
                                                             self.channels)

        log_p_predictions = np.log(self.policy_est.predict([p_board_vectors], batch_size=len(p_board_vectors))).reshape(-1)

        parent_index = np.hstack([np.full(shape=(self.size ** 2), fill_value=i) for i in range(len(nodes_to_expand))])
        parent_depth = np.hstack([np.full(shape=(self.size ** 2), fill_value=len(i.full_move_list.moves)) for i in nodes_to_expand])
        move_index = np.array([list(range(self.size ** 2)) * len(nodes_to_expand)])
        zipped_predictions = np.vstack([parent_index, parent_depth, move_index, log_p_predictions]).transpose()

        threshold_filter = self._p_threshold(zipped_predictions[:, 1], zipped_predictions[:, 3])
        filtered_predictions = zipped_predictions[threshold_filter]

        if verbose:
            print('Num P over threshold', len(filtered_predictions), 'out of', (len(nodes_to_expand) * self.size ** 2))

        new_leaves = []
        q_update = set()

        # numpy array of unique parent indices, start and end indices of each parent's move lists, and the count of the number of moves per parent
        unique_parents, move_indices, parent_counts = np.unique(filtered_predictions[:, 0], return_counts=True, return_index=True)

        # i is the parent meta index, index of parent index
        for i, parent_index in enumerate(unique_parents):
            parent = p_search_nodes[int(parent_index)]

            # build out the position really quickly (without checking if the game's over, since we know this is a valid position)
            for move in parent.full_move_list.moves:
                board.blind_move(*move)

            max_move_indices = move_indices[i + 1] if i < len(unique_parents) - 1 else filtered_predictions.shape[0]
            sorted_moves = sorted(filtered_predictions[move_indices[i]:max_move_indices, 2:4], key=lambda x: x[1], reverse=True)
            num_moves = min(len(sorted_moves), self._max_expansion(parent.depth()))

            self.create_children(board, parent, sorted_moves[:num_moves], new_leaves, q_update, transposition_table)

            for _ in parent.full_move_list.moves:
                board.unmove()

        for parent in q_update:
            parent.recalculate_q()

        leaf_nodes += new_leaves

        return len(new_leaves) > 0

    def create_children(self, board, parent, sorted_moves, new_leaves, q_update, transposition_table):
        for move_index, log_p_prediction in sorted_moves:
            child_move = self.index_to_move(move_index)
            if board.is_move_available(*child_move):
                child, made_new_child = parent.create_child(child_move, transposition_table)
                if made_new_child:
                    board.move(child_move[0], child_move[1])
                    child.assign_p(log_p_prediction)
                    # if game is over, then we have our q
                    if board.game_won():
                        winning_q = PExpNode.MIN_Q if board.get_player_to_move() == Board.FIRST_PLAYER else PExpNode.MAX_Q
                        child.assign_q(winning_q, GameState.WON)
                        q_update.add(parent)

                    elif board.game_assume_drawn():
                        child.assign_q(0, GameState.DRAW)
                        q_update.add(parent)

                    else:
                        new_leaves.append(child)
                        child.set_matrix(board.get_matrix())

                    # unmove for child
                    board.unmove()
                else:
                    PExpMind.accessed_transposition += 1
                    q_update.add(parent)

    def q(self, board):
        return self.value_est.predict([np.array([board.get_matrix().reshape(self.size, self.size, -1)])])[0][0]

    def pick_random_move(self, board, possible_moves):
        picked_action = 0

        # abs is only there to handle floating point problems
        qs = np.array([node.q for _, node in possible_moves])
        if board.get_player_to_move() == 1:
            distribution = np.abs(qs + 1.0) / 2
        else:
            # not sure this is correct
            distribution = sorted(-np.abs(qs - 1.0) / 2)

        if sum(distribution) > 0:
            distribution = (distribution.astype(np.float64) / sum(distribution))
            picked_action = np.random.choice(range(len(possible_moves)), 1, p=distribution)[0]

        return picked_action

    # used to pick a branch and fast forward it to use it as root node
    def cleanse_memory_tree(self, board, root_node, moves):
        if self.memory_root is not None:
            # self-play
            if np.alltrue(np.equal(self.memory_root.get_matrix(), board.get_matrix())):
                starting_root = self.memory_root
            for child in self.memory_root.children.values():
                if np.alltrue(np.equal(child.get_matrix(), board.get_matrix())):
                    #print('Found Previous Child')
                    starting_root = child
                    break
        #root_node.parents = []
        #root_node.cleanse_memory(moves)

        return None

    # with epsilon probability will select random move
    # returns whether game has concluded or not
    def make_move(self, board, as_player, verbose=True, epsilon=0.1, save_root=False, consistency_check=False):
        current_q = self.q(board)
        assert(as_player == board.get_player_to_move())

        # incomplete
        starting_root = self.cleanse_memory_tree(self.memory_root, None, None)

        # array of [best_move, best_node], root node of move calculations
        is_maximizing = True if board.get_player_to_move() == Board.FIRST_PLAYER else False
        possible_moves, root_node = self.p_search(board, is_maximizing,
                                                  root_node=starting_root,
                                                  consistency_check=consistency_check,
                                                  save_root=save_root, verbose=verbose)

        # best action is 0th index
        picked_action = 0

        # pick a suboptimal move randomly
        if np.random.random_sample() < epsilon:
            if verbose:
                print('suboptimal move')
            picked_action = self.pick_random_move(board, possible_moves)

        if len(possible_moves) == 0:
            print("Error in P Expand Search")

        picked_move, picked_node = possible_moves[picked_action]
        # add training example assuming best move
        best_move, best_node = possible_moves[0]
        best_q = best_node.q

        # q update with learning rate self.alpha
        #new_best_q = (1 - self.alpha) * current_q + self.alpha * best_q

        # compress to model valid range
        #new_best_q = max(min(new_best_q, PExpNode.MAX_MODEL_Q), PExpNode.MIN_MODEL_Q)

        #print(current_q, best_q)
        #self.add_train_example(board, new_best_q, best_move)

        # picked move may not equal best move if we're making a suboptimal one
        #board.move(*picked_move)

        self.memory_root = root_node.children[picked_move[0], picked_move[1]]

        return best_move, current_q, best_q

    def pickle_root(self, board, root_node):
        # save for debugging
        import sys
        sys.setrecursionlimit(100000)
        saving_hash = str(hash(tuple(board.get_matrix().reshape(-1))))
        with open('src/logs/' + saving_hash + '.pkl', 'wb') as f:
            root_node.set_matrix(board.get_matrix())
            pickle.dump(root_node, f)
            print('Root saved at ', saving_hash)

    def one_hot_p(self, move_index):
        vector = np.zeros((self.size ** 2))
        vector[move_index] = 1.
        return vector

    def move_to_index(self, move):
        return move[0] * self.size + move[1]

    def index_to_move(self, index):
        return np.int(index / self.size), np.int(index % self.size)

    # adds rotations
    def add_train_example(self, board, result, move):
        board_vectors = board.get_rotated_matrices()

        for i, vector in enumerate(board_vectors):
            self.train_vectors.append(vector)
            self.train_q.append(result)
            # get the i'th rotation
            which_rotation = board.get_rotated_point(self.move_to_index(move))[i]
            self.train_p.append(self.one_hot_p(which_rotation))


    def save(self, filename):
        self.value_est.save(filename + '_value.net')
        self.policy_est.save(filename + '_policy.net')

    def load_net(self, filename):
        self.value_est = keras.models.load_model(filename + '_value.net')
        self.policy_est = keras.models.load_model(filename + '_policy.net')
       
    def load(self, value_file, policy_file):
        self.value_est = keras.models.load_model(value_file)
        self.policy_est = keras.models.load_model(policy_file)