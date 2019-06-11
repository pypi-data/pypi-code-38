#
#  graph/walker.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

from abc import ABC, abstractmethod
import numpy as np
import torch
import bxtorch.utils.numpy as npu
import numba

class RandomWalker(ABC):
    """
    Base random walker class for different random walkers on graphs.
    """

    # MARK: Initialization
    def __init__(self, graph):
        """
        Initializes a new random walker on the specified graph.

        Parameters:
        -----------
        - graph: bxtorch.graph.Graph
            The graph to generate random walks for.
        """
        self.graph = graph

    # MARK: Instance Methods
    def sample_walks(self, num_walks, steps, **kwargs):
        """
        Function to sample a batch of walks.

        Parameters:
        -----------
        - num_walks: int
            The number of walks to generate.
        - steps: int
            The number of steps for the random walker. Must be positive.
        - kwargs: keyword arguments
            Arguments dependent on the subclass.

        Returns:
        --------
        - numpy.ndarray [num_walks, steps]
            The indices of the nodes sampled in the random walks.
        """
        assert steps > 0, \
            "Random walker must at least visit one node."
        assert num_walks > 0, \
            "Random walker must at least make one walk."

        result = np.zeros((num_walks, steps), dtype=np.int64)
        self._sample_walks(result, **kwargs)
        return result

    def walk_generator(self, steps, **kwargs):
        """
        Generator function which yields random walks infinitely often.

        Parameters:
        -----------
        - steps: int
            The number of steps for the random walker. Must be positive.
        - kwargs: keyword arguments
            Arguments dependent on the subclass.

        Returns:
        --------
        - numpy.ndarray [steps]
            The indices of the nodes sampled in the random walk.
        """
        assert steps > 0, \
            "Random walker must at least visit one node."

        while True:
            out = np.zeros(steps, dtype=np.int64)
            yield self._generate_random_walk(out, **kwargs)

    # MARK: Private Methods
    @abstractmethod
    def _generate_random_walk(self, out, **kwargs):
        pass

    def _sample_walks(self, out, **kwargs):
        for i in range(out.shape[0]):
            self._generate_random_walk(out[i], **kwargs)


class BiasedSecondOrderRandomWalker(RandomWalker):
    """
    Random walker sampling random walks by using the biased second-order
    strategy described in *node2vec: Scalable Feature Learning for Networks*
    (Grover and Leskovec -- 2016).

    The walker accepts the following keyword arguments:
    - p: float
        The *return parameter*. If it is > max(q, 1), then walks tend to not
        revisit visited nodes, if it is set to < min(q, 1), then the walks tend 
        to explore the initial node's neighborhood. Must be set to a positive 
        value.
    - q: float
        The *in-out parameter*. If is greater than 1, then walks tend to explore
        the local neighborhood, otherwise depth-first walking is more likely. 
        Must be set to a positive value.
    """

    # MARK: Initialization
    def __init__(self, graph):
        super().__init__(graph)
        self.cum_degrees = np.cumsum(graph.node_degrees)
        self.edges = np.array(graph.adjacency.nonzero()).T

    # MARK: Private Methods
    def _generate_random_walk(self, out, p, q):
        assert p > 0 and q > 0, \
            "Return parameter p and in-out parameter q must be greater 0."

        return _generate_biased_second_order_random_walk(
            self.cum_degrees, self.edges, self.graph.num_nodes, out, p, q
        )

    def _sample_walks(self, out, p, q):
        _generate_biased_second_order_batch(
            self.cum_degrees, self.edges, self.graph.num_nodes, out, p, q
        )
        
#################
### FUNCTIONS ###
#################
@numba.njit
def _generate_biased_second_order_random_walk(cum_degrees, edges, N, out, p, q):

    # 1) Choose random node as starting node
    out[0] = np.random.choice(N)

    # 2) Sample transitions
    prev_neighbors = None

    for i in range(1, out.shape[0]):
        node = out[i - 1]

        # 2.1) Find neighbors
        upper = cum_degrees[node]
        if node == 0:
            neighbors = edges[:upper, 1]
        else:
            lower = cum_degrees[node - 1]
            neighbors = edges[lower:upper, 1]

        # 2.2) If this is the first transition, choose random node from 
        #      neighbors
        if i == 1:
            idx = np.random.choice(len(neighbors))
            out[i] = neighbors[idx]
            prev_neighbors = neighbors
            continue

        # 2.3) Else, sample transition according to search bias alpha
        prev_node = out[i - 2]

        dist_0 = neighbors == prev_node
        dist_1 = npu.intersection_mask(neighbors, prev_neighbors)
        dist_2 = 1 - dist_0 - dist_1

        alpha = dist_0 / p + dist_1 + dist_2 / q
        alpha_bins = np.cumsum(alpha / alpha.sum())
        sample = np.random.rand()
        choice = np.sum(alpha_bins <= sample)
        out[i] = neighbors[choice]

        # 2.4) Prepare next transition
        prev_neighbors = neighbors

    return out

@numba.njit(parallel=True)
def _generate_biased_second_order_batch(cum_degrees, edges, N, out, p, q):
    for i in numba.prange(out.shape[0]):
        _generate_biased_second_order_random_walk(
            cum_degrees, edges, N, out[i], p, q
        )
