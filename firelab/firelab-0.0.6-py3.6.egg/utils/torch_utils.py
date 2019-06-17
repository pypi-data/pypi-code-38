import torch


# TODO: check `no_cuda` argument in config
use_cuda = torch.cuda.is_available()


def cudable(x):
    "Transforms torch tensor/module to cuda tensor/module"
    return x.cuda() if use_cuda and is_cudable(x) else x


def is_cudable(x):
    # return hasattr(x, "cuda") and callable(getattr(x, "cuda"))
    return torch.is_tensor(x) or isinstance(x, torch.nn.Module)