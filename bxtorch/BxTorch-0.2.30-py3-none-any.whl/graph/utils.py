#
#  graph/graph.py
#  bxtorch
#
#  Created by Oliver Borchert on June 09, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np

def symmetric_edge_list(edges):
    """
    Given a list of edges, this function computes a set which contains the
    edges "in both directions".

    Parameters:
    -----------
    - edges: numpy.ndarray [N, 2]
        The edges where edges are considered undirected.

    Returns:
    --------
    - numpy.ndarray [N * 2, 2]
        The edges where edges may be considered directed.
    """
    reverse_edges = np.column_stack([edges[:,1], edges[:,0]])
    return np.concatenate([edges, reverse_edges])
