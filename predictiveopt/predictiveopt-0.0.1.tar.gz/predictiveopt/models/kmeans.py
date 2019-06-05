from sklearn.cluster import KMeans
from numpy.random import choice
import pandas as pd


class KMeansModel:

    def __init__(self, x, clusters):
        self.x = x
        self.clusters = clusters
        self.model = KMeans(n_clusters=self.clusters)

    def run(self):
        self.model.fit(self.x)
        return self.model

    def sample_clusters(self, items_per_cluster):
        predicted = pd.DataFrame({'cluster': self.model.labels_})
        predicted = predicted.reset_index()
        selected = []

        for i in range(0, self.clusters):
            cluster = predicted.loc[predicted['cluster'] == i]['index']
            sample = choice(cluster, items_per_cluster, replace=False)
            selected = selected + list(sample)

        return selected
