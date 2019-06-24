"""
    The Logistic Regression is a statistical model in which a logistic function is user to model a binary
    dependent variable(One of the most simplest form of Logistic function).

    Here the logistic function is a sigmoid function.

    X is list of lists of features
    y list of outcomes
"""

from functools import partial, reduce
from aitools.utils import mathematics
from aitools.core.utils import gradient_descent
import math
import random


class LogisticRegression:

    """
        Logistic Regression takes two inputs independent features(X as list of list) and dependent features(y as list).
        As an input it takes list of list
        As an output it gives the likelihood of X's
    """

    def __init__(self):
        self.beta = None

    def build(self, independent_features, dependent_feature):
        """
            To build the independent features and dependent features are required.
            Once build is complete it stores the coefficients in self.beta for further
            classifications

            ** Internal and external dimensions should be same.
        :param independent_features: X
        :param dependent_feature: y
        """
        base_func = partial(log_likelihood, independent_features, dependent_feature)
        gradient_func = partial(log_gradient, independent_features, dependent_feature)

        beta_zero = [random.random() for _ in range(len(independent_features[0]))]
        self.beta = gradient_descent.maximize_batch(base_func, gradient_func, beta_zero)

    def predict(self, independent_features):
        """
            To predict the likelihood of independent features.

            ** Internal dimensions should be same as of independent features used to train the
            Model
        :param independent_features: X(list of lists)
        :return: likelihood of X's
        """

        likelihood = []

        for features in independent_features:
            likelihood.append({
                'feature': features,
                'likelihood': mathematics.sigmoid(mathematics.dot(self.beta, features))
            })

        return likelihood


def log_likelihood(x, y, beta):
    """
    :param x: X
    :param y: y
    :param beta: coefficients
    :return: sum of log of logistic function.
    """
    return sum(
        log_likelihood_i(x_i, y_i, beta)
        for x_i, y_i in zip(x, y)
    )


def log_likelihood_i(x_i, y_i, beta):
    """
    :param x_i: list of features
    :param y_i: output of features
    :param beta: coefficients
    :return: log of Logistic Function of ith point.
    """

    if y_i == 1:
        return math.log(mathematics.sigmoid(mathematics.dot(x_i, beta)))
    else:
        return math.log(1 - mathematics.sigmoid(mathematics.dot(x_i, beta)))


def log_gradient(x, y, beta):
    """
    :param x: X
    :param y: y
    :param beta: coefficients
    :return: vector of optimized coefficients
    """
    return reduce(
        mathematics.vector_add,
        [log_gradient_i(x_i, y_i, beta) for x_i, y_i in zip(x, y)]
    )


def log_gradient_i(x_i, y_i, beta):
    """
    :param x_i: list of features
    :param y_i: output of those features
    :param beta: coefficients
    :return: log likelihood corresponding to the ith data point
    """
    return [log_partial_ij(x_i, y_i, beta, j) for j, _ in enumerate(beta)]


def log_partial_ij(x_i, y_i, beta, j):
    """
    :param x_i: list of features
    :param y_i: output of those features
    :param beta: coefficients
    :param j: j the index of the derivative, i is the index of the data point
    :return: output excluding logistic function.
    """
    return (y_i - mathematics.sigmoid(mathematics.dot(x_i, beta))) * x_i[j]
