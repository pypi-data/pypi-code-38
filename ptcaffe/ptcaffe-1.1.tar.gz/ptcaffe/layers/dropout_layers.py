from __future__ import division, print_function

import torch
from torch import nn
from torch.nn import functional as F
from collections import OrderedDict
import copy

__all__ = ['Dropout', 'Dropout3D', 'DropBlock2D']


class Dropout(nn.Module):
    def __init__(self, layer, input_shape):
        super(Dropout, self).__init__()
        dropout_param = layer.get('dropout_param', OrderedDict())
        dropout_ratio = float(dropout_param.get('dropout_ratio', 0.5))
        self.dropout = nn.Dropout(dropout_ratio, inplace=False)

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        return self.dropout(x)


class Dropout3D(nn.Module):
    def __init__(self, layer, input_shape):
        super(Dropout3D, self).__init__()
        dropout_param = layer.get('dropout_param', OrderedDict())
        dropout_ratio = float(dropout_param.get('dropout_ratio', 0.5))
        self.dropout = nn.Dropout3d(dropout_ratio, inplace=False)

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        return self.dropout(x)


class DropBlock2D_pytorch(nn.Module):
    r"""Randomly zeroes spatial blocks of the input tensor.
    As described in the paper
    `DropBlock: A regularization method for convolutional networks`_ ,
    dropping whole blocks of feature map allows to remove semantic
    information as compared to regular dropout.
    Args:
        keep_prob (float, optional): probability of an element to be kept.
        Authors recommend to linearly decrease this value from 1 to desired
        value.
        block_size (int, optional): size of the block. Block size in paper
        usually equals last feature map dimensions.
        stepsize (int, optional ): if 1 (default) it use keep_prob,
        if >1, keep_prob will start from 1 and linearly go down to keep_prob
        after pass stepsize number of batch
    Shape:
        - Input: :math:`(N, C, H, W)`
        - Output: :math:`(N, C, H, W)` (same shape as input)
    .. _DropBlock: A regularization method for convolutional networks:
       https://arxiv.org/abs/1810.12890
    """

    def __init__(self, keep_prob=0.9, block_size=7, stepsize=1):
        super(DropBlock2D_pytorch, self).__init__()
        self.keep_prob = keep_prob
        self.block_size = block_size
        self.stepsize = stepsize
        # -----------post init-----
        self.passed_batch = [0]

    @staticmethod
    def annealing_linear(start, end, pct):
        return start + pct * (end - start)

    def forward(self, input):
        if not self.training or self.keep_prob == 1:
            return input
        if self.passed_batch[0] < self.stepsize:
            self.passed_batch[0] += 1
        pct = float(self.passed_batch[0]) / self.stepsize
        keep_prob = self.annealing_linear(1, self.keep_prob, pct)
        gamma = (1. - keep_prob) / self.block_size ** 2
        for sh in input.shape[2:]:
            gamma *= sh / (sh - self.block_size + 1)
        M = torch.bernoulli(torch.ones_like(input) * gamma)
        Msum = F.conv2d(M,
                        torch.ones((input.shape[1], 1, self.block_size, self.block_size)).to(device=input.device,
                                                                                             dtype=input.dtype),
                        padding=self.block_size // 2,
                        groups=input.shape[1])
        torch.set_printoptions(threshold=5000)
        mask = (Msum < 1).to(device=input.device, dtype=input.dtype)
        return input * mask * mask.numel() / mask.sum()  # TODO input * mask * self.keep_prob ?


# ----ptcaffe layer--------------
class DropBlock2D(DropBlock2D_pytorch):
    def __init__(self, layer, input_shape):
        param = layer['dropblock_param']
        keep_prob = float(param['keep_prob'])
        block_size = int(param['block_size'])
        stepsize = int(param.get('stepsize', 1))
        super(DropBlock2D, self).__init__(keep_prob, block_size, stepsize)

    def forward(self, inputs):
        return super(DropBlock2D, self).forward(inputs)

    def forward_shape(self, *input_shape):
        return copy.copy(input_shape)
