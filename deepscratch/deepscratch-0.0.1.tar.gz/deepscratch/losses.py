import numpy as np

class Loss:
    def __init__(self, value=None, grad=None):
        self.value = value
        self.grad = grad


def mse_loss(y_true, y_pred):
    # assert y_true.shape == y_pred.shape
    loss = np.mean(0.5 * np.power((y_true - y_pred), 2))
    grad = -(y_true - y_pred)
    return Loss(loss, grad)
