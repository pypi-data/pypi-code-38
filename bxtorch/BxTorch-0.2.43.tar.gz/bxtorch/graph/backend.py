#
#  graph/graph.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from abc import ABC, abstractmethod
import functools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as gs
import torch
import bxtorch.utils.torch as ut
import bxtorch.graph.stats as stats
import bxtorch.graph.func as func

class BaseGraph(ABC):
    """
    Abstract base class for graph implementations using matrices.
    """

    # MARK: Initialization
    def __init__(self, adjacency, features, labels):
        """
        Initializes a new graph. The types of the passed inputs depend on the
        particular implementation of the subclass.

        Parameters:
        -----------
        - adjacency: matrix [N, N]
            The graph's symmetric adjacency matrix. Unless the graph is small or
            dense, it should be sparse.
        - features: matrix [N, D]
            The graph's feature matrix. Should only be sparse if the features 
            are sparse. The parameter may be None if the graph does not have
            node features.
        - labels: vector [N]
            The labels for all nodes. May be None if the graph does not have
            node labels.
        """
        assert adjacency.shape[0] == adjacency.shape[1], \
            "Adjacency matrix is not square."
        assert features is None or adjacency.shape[0] == features.shape[0], \
            "Dimensions of adjacency matrix and feature matrix are invalid."
        assert labels is None or adjacency.shape[0] == labels.shape[0], \
            "Dimension of label matrix is invalid."
        
        self.adjacency = adjacency
        self.features = features
        self.labels = labels

    # MARK: Computed Properties
    @property
    def num_nodes(self):
        """
        Computes the number of nodes in the graph.

        Returns:
        --------
        - int
            The number of nodes.
        """
        return self.adjacency.shape[0]

    @property
    @abstractmethod
    def num_edges(self):
        """
        Computes the number of edges in the graph.

        Returns:
        --------
        - int
            The number of edges.
        """
        pass

    @property
    @abstractmethod
    def num_classes(self):
        """
        Computes the number of classes assuming the node labels are present.

        Returns:
        --------
        - int
            The number of classes
        """
        pass

    # MARK: Special Methods
    def __repr__(self):
        name = self.__class__.__name__
        result = f'{name}(<nodes: {self.num_nodes}, edges: {self.num_edges}'
        if self.features is not None:
            result += f', features: {self.features.shape[1]}'
        if self.labels is not None:
            result += f', classes: {self.num_classes}'
        return result + '>)'

    def __len__(self):
        return self.adjacency.shape[0]


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
        - bxtorch.graph.Graph
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


class TensorGraph(BaseGraph):
    """
    The graph class represents undirected graphs, optionally with node features
    and labels as PyTorch (sparse) tensors. Some operations can be implemented more efficiently with this graph. Further, this implementation can be used
    more easily with PyTorch models.

    The following datatypes are expected:
     * adjacency_matrix: torch.FloatTensor or torch.sparse.FloatTensor
     * feature_matrix: torch.FloatTensor or torch.sparse.FloatTensor
     * labels: torch.FloatTensor
    """

    # MARK: Static Methods
    @staticmethod
    def from_graph(graph):
        """
        Initializes a new PyTorch graph given a simple graph.

        Parameters:
        -----------
        - graph: bxtorch.graph.Graph
            The graph to initialize this PyTorch graph from.

        Returns:
        --------
        - bxtorch.graph.TensorGraph
            A newly initialized PyTorch graph.
        """
        A = graph.adjacency
        if isinstance(A, sp.csr_matrix):
            A = ut.to_sparse_tensor(A)
        else:
            A = torch.from_numpy(A).float()

        X = graph.features
        if isinstance(X, sp.csr_matrix):
            X = ut.to_sparse_tensor(X)
        elif X is not None:
            X = torch.from_numpy(X).float()

        Z = graph.labels
        if Z is not None:
            Z = torch.from_numpy(Z).float()
        
        return TensorGraph(A, X, Z)

    # MARK: Computed Properties
    @property
    def num_edges(self):
        return len(self.adjacency.values()) // 2
    
    @property
    def num_classes(self):
        return int(torch.max(self.labels) + 1)

    @property
    def node_degrees(self):
        return torch.sparse.sum(self.adjacency, dim=1).values().long()

    @property
    def edges(self):
        return self.adjacency.indices().transpose(0, 1)
    
    # MARK: Instance Methods
    def to(self, device):
        """
        Moves the graph to the specified device and returns it.

        Parameters:
        -----------
        - device: torch.device
            The device the graph should be moved to.

        Returns:
        --------
        - bxtorch.graph.TensorGraph
            A new graph moved to specified device.
        """
        return TensorGraph(
            *ut.to_device(self.adjacency, self.features, self.labels)
        )
