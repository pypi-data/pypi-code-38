from __future__ import division, print_function

import torch.nn as nn
from ptcaffe.utils.utils import parse_types

__all__ = ['Conv1d', 'Conv2d', 'Conv3d']

class Conv1d(nn.Conv1d):
    def __init__(self, layer, input_shape):
        kwargs = parse_types(layer['pytorch_param'])
        kwargs['in_channels'] = input_shape[1]
        super(Conv1d, self).__init__(**kwargs)

    def forward_shape(self, input_shape):
        output_shape = [input_shape[0], self.out_channels, -1]

class Conv2d(nn.Conv2d):
    def __init__(self, layer, input_shape):
        kwargs = parse_types(layer['pytorch_param'])
        kwargs['in_channels'] = input_shape[1]
        super(Conv1d, self).__init__(**kwargs)

    def forward_shape(self, input_shape):
        output_shape = [input_shape[0], self.out_channels, -1, -1]

class Conv3d(nn.Conv3d):
    def __init__(self, layer, input_shape):
        kwargs = parse_types(layer['pytorch_param'])
        kwargs['in_channels'] = input_shape[1]
        super(Conv3d, self).__init__(**kwargs)

    def forward_shape(self, input_shape):
        output_shape = [input_shape[0], self.out_channels, -1, -1, -1]
