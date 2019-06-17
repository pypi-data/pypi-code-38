from __future__ import absolute_import
import numpy as np


class Layer:
    ''' Base class for all layers. '''
    def __init__(self):
        self.trainable = False
    
    def forward(self, x):
        raise NotImplementedError()

    def backward(self, grad):
        raise NotImplementedError()

    def __call__(self, x):
        return self.forward(x)

    def parameters(self):
        raise NotImplementedError()

    def dparameters(self):
        raise NotImplementedError()

    def nparameters(self):
        ''' Total number of trainable parameters in the layer '''
        return 0

    def repr(self):
        return ''

    def __repr__(self):
        name = self.__class__.__name__
        args = self.repr()
        params = self.nparameters()
        return f'\033[01m{name}\033[00m({args}), \033[1;92m{params}\033[00m params'


class Linear(Layer):
    ''' Fully connected neural network '''
    def __init__(self, in_features, out_features):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.W = np.random.random((in_features, out_features))
        self.b = np.zeros((1, out_features))
        self.trainable = True

    def forward(self, x):
        self.layer_input = x
        return np.dot(x, self.W) + self.b

    def backward(self, grad):
        # Calculate gradient
        self.__dW = np.dot(self.layer_input.T, grad)
        self.__db = np.sum(grad, axis=0, keepdims=True)

        # Calculate gradient for next layer
        dx = np.dot(grad, self.W.T)
        return dx

    def parameters(self):
        return [self.W, self.b]

    def dparameters(self):
        return [self.__dW, self.__db]

    def nparameters(self):
        return np.prod(self.W.shape) + np.prod(self.b.shape)

    def repr(self):
        return f'{self.in_features} → {self.out_features}'
