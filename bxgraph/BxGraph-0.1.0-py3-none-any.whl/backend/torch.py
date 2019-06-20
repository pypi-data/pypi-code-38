#
#  backend/torch.py
#  bxgraph
#
#  Created by Oliver Borchert on June 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import scipy.sparse as sp
from .base import BaseGraph
from ..utils.torch import to_sparse_tensor
try:
    import torch
except:
    pass

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
        - graph: bxgraph.Graph
            The graph to initialize this PyTorch graph from.

        Returns:
        --------
        - bxgraph.TensorGraph
            A newly initialized PyTorch graph.
        """
        A = graph.adjacency
        if isinstance(A, sp.csr_matrix):
            A = to_sparse_tensor(A)
        else:
            A = torch.from_numpy(A).float()

        X = graph.features
        if isinstance(X, sp.csr_matrix):
            X = to_sparse_tensor(X)
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
        - bxgraph.TensorGraph
            A new graph moved to specified device.
        """
        return TensorGraph(
            *ut.to_device(self.adjacency, self.features, self.labels)
        )
