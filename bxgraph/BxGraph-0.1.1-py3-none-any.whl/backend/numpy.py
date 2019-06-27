#
#  backend/numpy.py
#  bxgraph
#
#  Created by Oliver Borchert on June 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import functools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as gs
from .base import BaseGraph
from ..algorithms import stats, func

class Graph(BaseGraph):
    """
    The graph class represents undirected graphs, optionally with node features
    and labels. 

    The following datatypes are expected:
     * adjacency_matrix: numpy.ndarray or scipy.sparse.csr_matrix
     * feature_matrix: numpy.ndarray or scipy.sparse.csr_matrix
     * labels: numpy.ndarray
    """

    # MARK: Static Methods
    @staticmethod
    def load(file):
        """
        Loads a graph from the specified file.

        Note:
        -----
        Implementation adapted from https://github.com/danielzuegner/netgan.

        Parameters:
        -----------
        - file: str
            The file to load the graph from. The initialization depends on the
            extension of the file name.
        """
        if file.endswith('.npz'):
            with np.load(file, allow_pickle=True) as loader:
                loader = dict(loader)
                if 'arr_0' in loader:
                    loader = dict(loader)['arr_0'].item()
                A = sp.csr_matrix(
                    (loader['adj_data'], loader['adj_indices'],
                        loader['adj_indptr']),
                    shape=loader['adj_shape']
                )

                if 'attr_data' in loader:
                    X = sp.csr_matrix(
                        (loader['attr_data'], loader['attr_indices'],
                            loader['attr_indptr']),
                        shape=loader['attr_shape']
                    )
                else:
                    X = None

                Z = loader.get('labels')

                A = A + A.T
                A[A > 1] = 1
            
            return Graph(A, X, Z)
        raise ValueError(
            'Graph cannot be loaded if no filename extension is specified. '
            'Currently, valid extensions are [.npz].'
        )

    @staticmethod
    def _random(num_nodes, num_edges):
        A = sp.dok_matrix((num_nodes, num_nodes))
        i = 0
        while i < num_edges:
            n, m = (np.random.choice(num_nodes), np.random.choice(num_nodes))
            if n == m:
                continue
            n, m = (min(n, m), max(n, m))
            if A[n, m] == 1:
                continue
            A[n, m] = 1
            i += 1

        A = A.tocsr()
        A = A + A.T
        A[A > 1] = 1

        return Graph(A, None, None)

    # MARK: Computed Properties
    @property
    def num_edges(self):
        return int(self.adjacency.sum()) // 2

    @property
    def num_classes(self):
        return np.max(self.labels) + 1

    @property
    def node_degrees(self):
        return self.adjacency.sum(axis=1).A1.astype(np.int64)

    @property
    def edges(self):
        return np.array(self.adjacency.nonzero()).T

    # MARK: Instance Methods
    def largest_connected_component(self):
        """
        Returns a new graph containing only the nodes from the largest connected
        component.

        Returns:
        --------
        - bxgraph.Graph
            A new, potentially smaller, graph.
        """
        _, components = gs.connected_components(self.adjacency)
        largest_component = np.bincount(components).argmax()
        mask = components == largest_component
        return Graph(
            self.adjacency[mask][:, mask], 
            self.features[mask] if self.features is not None else None, 
            self.labels[mask] if self.labels is not None else None
        )

    def save(self, file):
        """
        Saves the graph to the specified file. The file should have no
        extension such that it can be saved with the .npz extension.

        Parameters:
        -----------
        - file: str
            The file to save the graph to.
        """
        data = {
            'adj_data': self.adjacency.data,
            'adj_indices': self.adjacency.indices,
            'adj_indptr': self.adjacency.indptr,
            'adj_shape': self.adjacency.shape,
            'attr_data': self.features.data,
            'attr_indices': self.features.indices,
            'attr_indptr': self.features.indptr,
            'attr_shape': self.features.shape,
            'labels': self.labels
        }
        np.savez(file, data)

    # MARK: Special Methods
    def __getattr__(self, name):
        # Check if there's a stats function or a func function
        if hasattr(stats, name):
            f = getattr(stats, name)
        elif hasattr(func, name):
            f = getattr(func, name)
        else:
            classname = self.__class__.__name__
            raise AttributeError(
                f'Cannot get attribute {name} of {classname}.'
            )
        return functools.partial(f, self)

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return False
        if other.num_nodes != self.num_nodes:
            return False
        return not (self.adjacency != other.adjacency).todense().any()
