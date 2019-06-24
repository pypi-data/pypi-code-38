"""
    K-Means algorithm is a classification unsupervised machine learning algorithm. As an input it takes K as number of
    clusters. And it requires data points on single or multiple dimensions for training.
"""

from aitools.utils import mathematics

import matplotlib.pyplot as plt
import random


class KMeans:

    def __init__(self, k):
        """
        :param k: Number of Clusters to be formed
        """
        self.k = k
        self.means = None

    def predict(self, cluster):
        """
        :param cluster: Input which needs to be classify
        :return: Minimum Value of squared distance, Helps in Cluster classification
        """
        return min(range(self.k),
                   key=lambda i: mathematics.squared_distance(cluster, self.means[i]))

    def build(self, inputs):
        """
            self.mean is populated by this function only and provides skeleton a
            for classification.
        :param inputs: List of Vectors
        :return: None
        """
        self.means = random.sample(inputs, self.k)
        assignment = None

        while True:

            new_assignment = map(self.predict, inputs)
            # new_assignment contains map object memory location and it changes in every iteration.
            # Hot fix for Infinite loop thing, that always happens when we compares new_assignment
            # and old assignment directly.
            if assignment is not None and len(set(assignment) - set(new_assignment)) == 0:
                return

            assignment = new_assignment

            for i in range(self.k):
                i_points = [p for p, a in zip(inputs, assignment) if a == 1]
                if i_points:
                    # Classification skeleton formation
                    self.means[i] = mathematics.vector_mean(i_points)


def squared_clustering_error(inputs, k):
    clusters = KMeans(k)
    clusters.build(inputs)
    means = clusters.means
    assignment = map(clusters.predict, inputs)

    return sum(mathematics.squared_distance(input, means[cluster])
               for input, cluster in zip(inputs, assignment))


# One way of choosing K : plotting sum of squared errors
def plot_k_with_squared_clustering_error(inputs, clusters):
    ks = range(1, clusters)
    errors = [squared_clustering_error(inputs, k) for k in ks]
    plt.plot(ks, errors)
    plt.xticks(ks)
    plt.xlabel('K')
    plt.ylabel('Error')
    plt.show()
