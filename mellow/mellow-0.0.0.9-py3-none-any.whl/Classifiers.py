import numpy as np


class KNN:
    def distance(self, p1, p2):
        """
        It is used to calculate the distance between two points in euclidean Space
        :param p1: coordinate of point one in euclidean space
        :param p2: coordinate of point two in euclidean space
        :return: distance between p1 and p2 float value
        """
        return np.sum((p2 - p1) ** 2) ** .5

    def predict(self, x, y, test, k=10):
        """predicts the result based on nearest neighbour
        :param x: training data
        :param y: label data
        :param test: test data
        :param k: neighbour points
        :return:
        """
        d = []
        size = x.shape[0]
        for i in range(size):
            d.append((self.distance(test, x[i]), y[i]))

        # l is the list of sorted distance label
        label = np.array(sorted(d))[:, 1]
        label = label[:k]

        unique = np.unique(label, return_counts=True)

        # convert the unique labels with their frequency into key value pair
        freq_dict = dict()
        size = len(unique)
        for i in range(size):
            freq_dict[unique[0][i]] = unique[1][i]

        # get the key whose value is maximum in the dictionary
        pred = max(freq_dict, key=freq_dict.get)
        return pred


class LogisticRegressor:
    pass
