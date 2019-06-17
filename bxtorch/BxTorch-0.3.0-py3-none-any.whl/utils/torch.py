#
#  utils/torch.py
#  bxtorch
#
#  Created by Oliver Borchert on May 10, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np
import torch

def gpu_device(gpu):
    """
    Returns a device based on the passed parameters.
    
    Parameters:
    -----------
    - gpu: bool or int
        If int, the returned device is the GPU with the specified ID.
        If False, the returned device is the CPU, if True, the returned
        device is given as the GPU with the highest amount of free memory.
        
    Returns:
    --------
    - torch.device
        A PyTorch device.
    """
    if isinstance(gpu, bool) and gpu:
        assert torch.cuda.is_available()
        gpu = np.argmin([
            torch.cuda.memory_cached(torch.device(f'cuda:{i}'))
            for i in range(torch.cuda.device_count())
        ])
        return torch.device(f'cuda:{gpu}')
    elif isinstance(gpu, bool):
        return torch.device('cpu')
    else:
        assert gpu < torch.cuda.device_count()
        return torch.device(f'cuda:{gpu}')


def to_device(device, *args):
    """
    Passes the given tensors to the specified device.

    Parameters:
    -----------
    - device: torch.device
        The device to pass tensors to.
    - args: varargs of (torch.Tensor or list of torch.Tensor)
        The tensors to pass to the specified device. Tensors may be given in 
        lists such that a single variable can easily be assigned to a list of
        tensors upon function return. The given tensors may also be None, then
        None is returned for that tensor.

    Returns:
    --------
    - list of (torch.Tensor or list of torch.Tensor)
        The given tensors passed to the specified device. If tensors were passed
        as lists, they are also returned as lists.
    """
    def _to_device(x):
        if x.is_contiguous():
            return x.to(device, non_blocking=True)
        else:
            return x.contiguous().to(device, non_blocking=True)

    return _recursive_apply('to', _to_device, *args)


def share_memory(*args):
    """
    Shares the memory of the given tensors.

    Parameters:
    -----------
    - args: varargs of (torch.Tensor or list of torch.Tensor)
        The tensors to share the memory.

    Returns:
    --------
    - list of (torch.Tensor or list of torch.Tensor)
        The tensors in shared memory.
    """
    return _recursive_apply('share_memory_', lambda x: x.share_memory_(), *args)


def pin_memory(*args):
    """
    Pins the memory of the given tensors.

    Parameters:
    -----------
    - args: varargs of (torch.Tensor or list of torch.Tensor)
        The tensors to pin the memory.

    Returns:
    --------
    - list of (torch.Tensor or list of torch.Tensor)
        The tensors with pinned memory.
    """
    return _recursive_apply('pin_memory', lambda x: x.pin_memory(), *args)


def _recursive_apply(attribute, function, *args):
    if len(args) > 1:
        return [_recursive_apply(attribute, function, t) for t in args]
    elif len(args) == 1 and isinstance(args[0], list):
        return [_recursive_apply(attribute, function, t) for t in args[0]]
    elif len(args) == 1 and isinstance(args[0], tuple):
        return tuple(
            [_recursive_apply(attribute, function, t) for t in args[0]]
        )
    elif len(args) == 1 and isinstance(args[0], dict):
        return {
            k: _recursive_apply(attribute, function, v) 
            for k, v in args[0].items()
        }
    elif len(args) == 1 and hasattr(args[0], attribute):
        return function(args[0])
    elif len(args) == 1 and args[0] is not None:
        return args[0]
    else:
        return None
    

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

_eyes = {}

def to_one_hot(X, n):
    """
    Creates a one-hot matrix from a set of indices.

    Parameters:
    -----------
    - X: torch.LongTensor [N, D]
        The indices to convert into one-hot vectors.
    - n: int
        The number of entries in the one-hot vectors.

    Returns:
    --------
    - torch.ByteTensor [N, D, n]
        The one-hot matrix.
    """
    if n not in _eyes:
        _eyes[n] = torch.eye(n)
    return _eyes[n][X]
