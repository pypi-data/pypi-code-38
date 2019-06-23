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
        # it will have the distance( from the input point ) and label of each point as tuple ie : (distance, label)
        d = []
        r = x.shape[0]
        for i in range(r):
            d.append((self.distance(test, x[i]), y[i]))

        # l is the list of sorted distance label
        l = np.array(sorted(d))[:, 1]
        l = l[:k]
        u = np.unique(l, return_counts=True)

        # convert the unique labels with their frequency into key value pair
        freq_dict = dict()
        for i in range(len(u[0])):
            freq_dict[u[0][i]] = u[1][i]

        # get the key whose value is maxmimum in the dictionary
        pred = max(freq_dict, key=freq_dict.get)
        return pred

class LogisticRegressor:
    pass
