import numpy as np

class Optimizer:
    def __init__(self):
        pass

    def update(self):
        pass


class SGD(Optimizer):
    def __init__(self, layers, lr=0.001, momentum=0.1):
        self.lr = lr
        self.momentum = momentum
        self.layers = list(layers)

    def update(self):
        for layer in self.layers:
            if layer.trainable:
                for param, grad in zip(layer.parameters(), layer.dparameters()):
                    param -= self.lr * grad