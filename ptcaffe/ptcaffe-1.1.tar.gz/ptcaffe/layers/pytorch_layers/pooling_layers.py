from __future__ import division, print_function

import torch.nn as nn
from ptcaffe.utils.utils import parse_types

__all__ = ['AdaptiveAvgPool2d', 'AdaptiveMaxPool2d']

class AdaptiveAvgPool2d(nn.AdaptiveAvgPool2d):
    def __init__(self, layer, input_shape):
        kwargs = parse_types(layer['pytorch_param'])
        super(AdaptiveAvgPool2d, self).__init__(**kwargs)

    def forward_shape(self, input_shape):
        return [input_shape[0], input_shape[1], self.output_size, self.output_size]


class AdaptiveMaxPool2d(nn.AdaptiveMaxPool2d):
    def __init__(self, layer, input_shape):
        kwargs = parse_types(layer['pytorch_param'])
        super(AdaptiveMaxPool2d, self).__init__(**kwargs)

    def forward_shape(self, input_shape):
        return [input_shape[0], input_shape[1], self.output_size, self.output_size]
