import torch.nn as nn


def count_parameters(model: nn.Module):
    """
    Count parameters and buffers in model
    parameters: weight, bias
    buffers: running_mean, running_var
    :param model: nn.Module
    :return: num_parameters, num_buffers
    """
    num_parameters = sum(p.numel() for p in model.parameters())
    # for loop for PyTorch 0.4
    num_buffers = 0
    for m in model.modules():
        for buffer in m._buffers.values():
            num_buffers += buffer.numel()
    return num_parameters, num_buffers
