"""
This module mathematical functions.
"""

import math
from functools import reduce


def vector_mean(vectors):
    """
    :param vectors: List of vectors
    :return: Mean of Vectors
    """
    n = len(vectors)
    return scalar_multiply(1 / n, vector_sum(vectors))


def vector_add(v, w):
    """
    [v_1 + w_1 , ... , v_n + w_n]
    :param v: First Vector
    :param w: Second Vector
    :return: New Vector, sum of first and second
    """
    return [v_i + w_i for v_i, w_i in zip(v, w)]


def vector_subtract(v, w):
    """
    [v_1 - w_1 , ... , v_n - w_n]
    :param v: First Vector
    :param w: Second Vector
    :return: New Vector, subtraction of first and second
    """
    return [v_i - w_i for v_i, w_i in zip(v, w)]


def vector_sum(vectors):
    """
    :param vectors: Vector List of which sum is required
    :return: Sum of Vectors
    """
    return reduce(vector_add, vectors)


def scalar_multiply(c, v):
    """
    [c * v_1 , ... , c * v_n]
    :param c: Scalar Quantity
    :param v: Vector
    :return: Scalar multiplication on vector
    """
    return [c * v_i for v_i in v]


def squared_distance(v, w):
    """
    (v_1 - w_1)^2 + ... + (v_n - w_n)^2
    :param v: First Vector
    :param w: Second Vector
    :return: Distance between Vectors
    """
    return sum_of_squares(vector_subtract(v, w))


def sum_of_squares(v):
    """
    :param v: Vector
    :return: Dot Product of vector
    """
    return dot(v, v)


def dot(v, w):
    """
    v_1 * w_1 + ... + v_n * w_n
    :param v: First Vector of length n
    :param w: Second Vector of length n
    :return: Sum of products
    """
    return sum(v_i * w_i for v_i, w_i in zip(v, w))


def mean(feature_vector):
    """

    :param feature_vector: List of integer/float/double..
    :return: Mean of the feature vector.
    """
    return sum(f for f in feature_vector)/len(feature_vector)


def standard_deviation(feature_vector):
    """

    :param feature_vector: List of integer/float/double..
    :return: Mean of the feature vector.
    """
    m = mean(feature_vector)
    return math.sqrt(sum(math.pow(f - m, 2) for f in feature_vector)/len(feature_vector))


def sigmoid(x):
    try:
        exp = math.exp(-x)
    except OverflowError:
        exp = float('inf')

    return 1.0 / (1.0 + exp)
