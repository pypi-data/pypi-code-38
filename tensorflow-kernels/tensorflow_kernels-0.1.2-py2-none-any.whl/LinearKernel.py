import tensorflow as tf

__author__ = "Stefano Campese"

__version__ = "0.1"
__maintainer__ = "Stefano Campese"
__email__ = "sircampydevelop@gmail.com"


class LinearKernel():
    """
    Linear kernel, defined as a dot product between vectors
        K(x, y) = <x, y>
    """

    def __init__(self):
        self._dim = None

    def _compute(self, x, y):
        self._dim = x.shape[1]
        return tf.matmul(x, tf.transpose(y))

    def dim(self):
        return self._dim
