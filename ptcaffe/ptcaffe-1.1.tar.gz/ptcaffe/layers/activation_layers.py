from __future__ import division, print_function

import copy

import torch.nn as nn
import torch.nn.functional as F

__all__ = ['ReLU', 'ReLU6', 'Sigmoid', 'Softmax']


class ReLU(nn.Module):
    def __init__(self, layer, input_shape):
        nn.Module.__init__(self)
        bname = layer['bottom']
        tname = layer['top']
        self.inplace = (bname == tname)
        if 'inplace' in layer and layer['inplace'] == 'false':
            self.inplace = False
        self.leaky_relu = False
        if 'relu_param' in layer and 'negative_slope' in layer['relu_param']:
            self.leaky_relu = True
            self.negative_slope = float(layer['relu_param']['negative_slope'])
        else:
            self.model = nn.ReLU(self.inplace)

    def __repr__(self):
        if self.inplace:
            return 'ReLU(inplace)'
        else:
            return 'ReLU()'

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        if self.leaky_relu:
            return F.leaky_relu(x, negative_slope=self.negative_slope, inplace=self.inplace)
        else:
            return self.model(x)
            # return F.relu_(x, inplace=self.inplace) # this is not inplace


class ReLU6(nn.Module):
    def __init__(self, layer, input_shape):
        nn.Module.__init__(self)
        bname = layer['bottom']
        tname = layer['top']
        self.inplace = (bname == tname)

    def __repr__(self):
        return 'ReLU6()'

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        if x.is_leaf:
            return F.relu6(x)
        else:
            return F.relu6(x, inplace=self.inplace)


class Sigmoid(nn.Module):
    def __init__(self, layer, input_shape):
        super(Sigmoid, self).__init__()

    def forward(self, x):
        return F.sigmoid(x)

    def forward_shape(self, original_shape):
        return copy.copy(original_shape)

    def __repr__(self):
        return 'Sigmoid()'


class Softmax(nn.Module):
    def __init__(self, layer, input_shape):
        super(Softmax, self).__init__()
        axis = 1
        if 'softmax_param' in layer and 'axis' in layer['softmax_param']:
            axis = int(layer['softmax_param']['axis'])
        self.axis = axis

    def __repr__(self):
        return 'Softmax(axis=%d)' % self.axis

    def forward_shape(self, input_shape):
        return copy.copy(input_shape)

    def forward(self, x):
        x = F.softmax(x, dim=self.axis)
        return x
