from __future__ import absolute_import
from .layers import Layer
from ..activations import *

class ReLU(Layer):
    def __init__(self):
        super().__init__()
        self.trainable = False

    def forward(self, x):
        self.layer_input = x
        return relu(x)

    def backward(self, grad):
        return grad * relu(self.layer_input, deriv=True)


class Sigmoid(Layer):
    def __init__(self):
        super().__init__()
        self.trainable = False

    def forward(self, x):
        self.layer_input = x
        return sigmoid(x)

    def backward(self, grad):
        return grad * sigmoid(self.layer_input, deriv=True)
