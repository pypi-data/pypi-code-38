import numpy as np


def relu(x, deriv=False):
    if not deriv:
        return np.where(x >= 0, x, 0)
    return np.where(x >= 0, x, 0)

def sigmoid(x, deriv=False):
    sigm = 1. / (1. + np.exp(-x))
    if not deriv:
        return sigm
    return sigm * (1. - sigm)

