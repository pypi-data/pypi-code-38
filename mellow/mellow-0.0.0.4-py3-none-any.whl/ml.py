import numpy as np
import utility as util


# knn function to find the k nearest points to the input point first we will calc
# distance from input to each training data point then sort(obv in increasing order)
# them and take first k and make predictions based upon them

def knn(X, Y, test, k = 30):
    """predicts the result based on nearest neighbour
    :param X: training data
    :param Y: label data
    :param test: test data
    :param k: neighbour points
    :return:
    """
    d = []
    size = X.shape[0]
    for i in range(size):
        d.append((util.distance(test, X[i]), Y[i]))

    # l is the list of sorted distance label
    l = np.array(sorted(d))[:, 1]
    l = l[:k]

    u = np.unique(l, return_counts=True)

    # convert the unique labels with their frequency into key value pair
    freq_dict = dict()
    for i in range(len(u[0])):
        freq_dict[u[0][i]] = u[1][i]

    # get the key whose value is maxmimum in the dictionary
    pred = int(max(freq_dict, key=freq_dict.get))
    return pred

