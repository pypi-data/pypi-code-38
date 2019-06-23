import numpy as np


class LinearRegressor:

    def __init__(self):
        self.theta = None

    def hypothesis(self, theta, x):
        return np.dot(theta.T, x)

    def get_theta(self, x, y):
        first_term = np.linalg.pinv(np.dot(x.T, x))
        second_term = np.dot(x.T, y)
        return np.dot(first_term, second_term)

    def fit(self, x, y):
        """
        fit the parameter x and y.
        :param x: training data x
        :param y: training data y
        :return: theta
        """
        self.theta = self.get_theta(x, y)

    def predict(self, test):
        """
        predict the value of Y for the given data test
        :param test: test data shape should be same as X
        :return: prediction for the given test float value
        """

        return self.hypothesis(self.theta, test)


class LocallyWeightedRegressor:

    def hypothesis(self, theta, x):
        return np.dot(theta.T, x)

    def get_weight(self, x, test, tau):
        """
        :param x: training data
        :param test: test  point
        :param tau: hyper-parameter tau
        :return:
        """
        # Create W
        m = x.shape[0]
        w = np.eye(m)

        for i in range(m):
            w[i, i] = np.exp(-np.dot((x[i] - test), (x[i] - test).T) / (2 * tau * tau))

        return w

    def get_theta(self, x, y, w):
        """
        :param x: training data
        :param y: training outputs
        :param w:  weight matrix
        :return: theta
        """
        theta = np.dot(np.linalg.pinv(np.dot(np.dot(x.T, w), x)), np.dot(np.dot(x.T, w), y))
        return theta

    def predict(self, x, y, test, tau=1.0):
        """
        :param x: training data x
        :param y: training data labels y
        :param test: data whose output we want to predict
        :param tau: hyper-parameter
        :return: predicted value float
        """
        w = self.get_weight(x, test, tau)
        theta = self.get_theta(x, y, w)
        return self.hypothesis(theta, test)
