#
#  utils/torch.py
#  bxgraph
#
#  Created by Oliver Borchert on June 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

try:
    import torch
except:
    pass

def to_sparse_tensor(X):
    """
    Creates a coalesced sparse PyTorch tensor from the given matrix.

    Parameters:
    -----------
    - X: scipy.sparse.csr_matrix
        The matrix to obtain the PyTorch tensor from.

    Returns:
    --------
    - torch.sparse.FloatTensor
        The sparse tensor.
    """
    data = torch.from_numpy(X.data).float()
    X = torch.sparse.FloatTensor(
        torch.LongTensor(X.nonzero()), data, torch.Size(X.shape)
    )
    return X.coalesce()