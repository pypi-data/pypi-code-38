import numpy as np

from src.core.board import GameState

class MoveList:
    # moves should be a tuple
    def __init__(self, moves, position_hash):
        self.moves = moves
        self.list_hash = position_hash

    # hashes are unique to board positions, allowing variation in the order of created moves
    def append(self, new_move):
        new_hash_elem = (-1) ** (len(self.moves) % 2) * (new_move[0] * 100 + new_move[1])
        new_list_hash = list(self.list_hash)
        new_list_hash.append(new_hash_elem)
        return MoveList((self.moves + (new_move, )), sorted(new_list_hash))

    def __eq__(self, other):
        return self.moves == other.moves

    def __hash__(self):
        return hash(self.moves)

    def __len__(self):
        return len(self.moves)
    # incomplete
    def cleanse(self, moves):
        move_list = list(self.moves)
        for move in moves:
            move_list.remove(move)
            self.list_hash.remove(move)
        self.moves = move_list

    def transposition_hash(self):
        return tuple(self.list_hash)

# search tree where we search strictly according to the likelihood function
class PExpNode:
    MAX_Q = 1
    # largest Q allowed by model prediction (MAX_Q is a minimax certified win)
    MAX_MODEL_Q = 0.99
    MIN_Q = -1
    MIN_MODEL_Q = -0.99
    UNASSIGNED_Q = None

    def __init__(self, parent, is_maximizing, full_move_list):

        # with transposition, can have multiple parents
        if parent:
            self.parents = [parent]
        else:
            self.parents = []

        # full move tree
        self.full_move_list = full_move_list

        self.is_maximizing = is_maximizing
        # is the game over with this move list
        self.game_status = GameState.NOT_OVER
        # for debugging
        # key is move
        self.children = {}
        self.children_with_q = []
        # current best child
        self.best_child = None

        self.principal_variation = None
        self.q = PExpNode.UNASSIGNED_Q
        self.assigned_q = False

        # log likelihood of playing this move given root board state (used for PVS search)
        self.log_total_p = 0
        # log_total_p converted to integer that's easy to sort
        self.p_comparator = 0

        # only allowed to set once
        self.p_assigned = False

        # the quality of this move
        self.move_goodness = 0

        self._matrix = None

    def set_matrix(self, matrix):
        self._matrix = matrix

    def get_matrix(self):
        return self._matrix

    def has_matrix(self):
        return self._matrix is not None

    def has_children(self):
        return len(self.children) > 0

    transposition_access = 0

    # creates a new PExpNode and appends it as a child
    # will fish out of transposition table if it finds a suitable match
    # note this does NOT compute q for child
    def create_child(self, move, transposition_table):
        new_move_list = self.full_move_list.append(move)

        # build the hash of the transposition to check whether the position has been visited before
        transposition_hash = new_move_list.transposition_hash()
        child_found = transposition_hash in transposition_table
        child = None
        # transposed position exists
        if child_found:
            PExpNode.transposition_access += 1
            child = transposition_table[transposition_hash]
            child.parents.append(self)
            if child.is_assigned_q:
                self.children_with_q.append(child)
        else:
            child = PExpNode(parent=self,
                            is_maximizing=not self.is_maximizing,
                            full_move_list=new_move_list)
            transposition_table[transposition_hash] = child

        self.children[move] = child

        return child, not child_found

    def get_sorted_moves(self):
        valid_children = [tup for tup in self.children.items() if tup[1].q is not PExpNode.UNASSIGNED_Q]
        return sorted(valid_children, key=lambda x: x[1].move_goodness, reverse=self.is_maximizing)

    # used ONLY for leaf assignment
    def assign_q(self, q, game_status):
        assert (len(self.children) == 0)

        # mark game status
        self.game_status = game_status

        # for a leaf node, the principal variation is itself
        self.q = q
        assert(PExpNode.MIN_Q <= q <= PExpNode.MAX_Q)
        self.principal_variation = self
        assert(not self.assigned_q)
        self.assigned_q = True

        for parent in self.parents:
            parent.children_with_q.append(self)

        self.assign_move_goodness()

    def assign_move_goodness(self):
        # play shorter sequences if advantageous, otherwise play longer sequences
        if self.q > 0:
            # because of the comparisons that use equality check in SortedSet, we need this value to be an integer
            # 1E6 multiplier allows the length of the full move list to be small in comparison to q
            self.move_goodness = int(self.q * 1E6 - len(self.principal_variation.full_move_list))
        else:
            self.move_goodness = int(self.q * 1E6 + len(self.principal_variation.full_move_list))

    # ab cutoff for when we know we can
    # Not sure if it applies regardless of parent
    def ab_valid(self):
        if len(self.parents) > 0 and self.parents[0].q:
            return self.parents[0].is_maximizing and self.parents[0].q < PExpNode.MAX_Q \
                    or not self.parents[0].is_maximizing and self.parents[0].q > PExpNode.MIN_Q
        return True

    def assign_p(self, log_p):
        assert(not self.p_assigned)
        self.log_total_p = self.parents[0].log_total_p + log_p
        self.p_assigned = True
        # Ideally
        self.p_comparator = int((min(-self.log_total_p, 100)) * 1E6)

    def depth(self):
        return len(self.full_move_list.moves)

    # returns if this node is better than another, comparing Q value
    def better_q(self, other):
        return self.move_goodness > other.move_goodness

    # Computes a bottom-up recomputation of Q
    def recalculate_q(self):
        # if this node is still a leaf, break
        if len(self.children_with_q) == 0:
            return

        # we are going to have to frequently search for the max, so might as well sort while we're at it
        sign = 1 if self.is_maximizing else -1
        self.children_with_q.sort(key=lambda x: sign * x.move_goodness, reverse=True)
        self.best_child = self.children_with_q[0]

        self.principal_variation = self.best_child.principal_variation
        self.q = self.best_child.q
        self.assigned_q = True

        self.assign_move_goodness()

        # update parents
        for parent in self.parents:
            # if this node is in the PV line
            if parent.best_child == self or parent.best_child is None or (
                    (parent.is_maximizing and self.better_q(parent.best_child)) or
                    (not parent.is_maximizing and not self.better_q(parent.best_child))
            ):
                parent.recalculate_q()

    def cleanse_memory(self, moves):
        for child in self.children:
            child.cleanse_memory(moves)

    # DEBUGGING METHODS

    def recursive_stats(self):
        num_q = 1 if self.assigned_q else 0
        num_nodes = len(self.children)
        if not self.has_children():
            self.num_nodes = num_nodes
            return num_q, num_nodes

        for child in self.children.values():
            child_q, child_nodes = child.recursive_stats()
            num_q += child_q
            num_nodes += child_nodes
        self.num_nodes = num_nodes
        return num_q, num_nodes

    def recursive_children(self, include_game_end=False):
        leaves = []
        for child in self.children.values():
            if child.has_children():
                leaves.extend(child.recursive_children())
            else:
                if not include_game_end and child.game_status == GameState.NOT_OVER\
                        or include_game_end:
                    leaves.append(child)
        return leaves

    # Assert consistency
    def consistent_pv(self):
        if self.has_children():
            valid_children = [tup for tup in self.children.items() if tup[1].q is not PExpNode.UNASSIGNED_Q]
            assert(len(valid_children) == len(self.children_with_q))
            if len(valid_children) == 0:
                return

            if self.is_maximizing:
                best_move = max(valid_children, key=lambda x: x[1].move_goodness)[0]
            else:
                best_move = min(valid_children, key=lambda x: x[1].move_goodness)[0]

            assert(self.children[best_move].q - self.best_child.q < 1E-6)

            if self.assigned_q:
                if abs(self.q - self.children[best_move].q) > 1E-6:
                    print("Q Inconsistency")
                    print(self)
                    print(self.children[best_move])
                    self.principal_variation.recalculate_q()
                    self.children[best_move].principal_variation.recalculate_q()
                assert(abs(self.q - self.children[best_move].q) < 1E-6)
            assert(abs(self.principal_variation.q - self.children[best_move].principal_variation.q) < 1E-6)

            # using negamax framework
            #if self.principal_variation != self.children[best_move].principal_variation:
            #    self.whole_set_q()
            assert(self.principal_variation.log_total_p < 0)

            for child in self.children.values():
                child.consistent_pv()

    def top_down_q(self):
        valid_children = [tup for tup in self.children.items() if tup[1].q]
        if len(valid_children) == 0:
            return

        for _, child in valid_children:
            child.top_down_q()

        if self.is_maximizing:
            best_move = max(valid_children, key=lambda x: x[1].move_goodness)[0]
        else:
            best_move = min(valid_children, key=lambda x: x[1].move_goodness)[0]

        self.principal_variation = self.children[best_move].principal_variation
        self.q = self.children[best_move].q

    def negamax(self):
        valid_children = [tup for tup in self.children.items() if tup[1].q]
        if len(valid_children) == 0:
            return self.q, self

        best_child = None
        if self.is_maximizing:
            value = -np.inf
            for move, child in valid_children:
                child_value, next_child = child.negamax()
                assert(abs(child_value - next_child.principal_variation.q) < 1E-4)
                if child_value > value:
                    best_child = next_child
                    value = child_value
        else:
            value = np.inf
            for move, child in valid_children:
                child_value, next_child = child.negamax()
                assert (abs(child_value - next_child.principal_variation.q) < 1E-4)
                if child_value < value:
                    best_child = next_child
                    value = child_value

        return value, best_child

    # does formal expansion rather than a move list check
    def real_principal_variation(self):
        sign = 1 if self.is_maximizing else -1
        valid_children = [tup for tup in self.children.items() if tup[1].is_assigned_q]
        if len(valid_children) == 0:
            return []
        best_move, best_child = max(valid_children, key=lambda x: sign * x[1].move_goodness)
        return [str(best_move)] + best_child.real_principal_variation()


    @classmethod
    # whether the q is from a game result (as opposed to an approximation of game state)
    def is_result_q(cls, q, epsilon=1E-7):
        return abs(q) > PExpNode.MAX_Q - epsilon or abs(q) < epsilon

    def __str__(self):
        if self.principal_variation:
            return ("PV: " + ', '.join(self.real_principal_variation()) + " Q: {0:.4f} P: {1:.4f}").format(self.q, self.principal_variation.log_total_p)
        else:
            return "Position: " + str(self.full_move_list.moves) + " P: {0:.4f}".format(self.log_total_p)