#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# clustercollection.py
# Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
# Implements the basic framework for a collection of clusters
#

from ditto_lib.utils.logging import logger
from ditto_lib.utils.checker import check_package
from ditto_lib.itemcollection import ItemCollection
from ditto_lib.clustering.cluster import Cluster

from random import randint
from math import sqrt

try:
    from sklearn.cluster import KMeans, MeanShift, DBSCAN, AgglomerativeClustering
except:
    KMeans = MeanShift = DBSCAN, AgglomerativeClustering = None

class ClusterCollection(ItemCollection):
    '''
    Basic class for computing different clustering algorithms

    Args:
    name(str): The name for the collection
    cluster_amount: The amount of clusters to group the items into. Defaults to 0. 
        It is best to experiment and find the best value for this parameter. Some 
        clustering alogrithms may override this input. 
    '''

    def __init__(self, name, cluster_amount=0):
        super(ClusterCollection, self).__init__(name)
        self._clusters = []
        self._cluster_amount = cluster_amount

    def __len__(self):
        '''
        Returns how many clusters are being stored in this collection
        '''
        return len(self._clusters)

    @property
    def cluster_amount(self):
        '''
        Return the amount of clusters, or centroid that this
        collection contains. 
        '''
        return self._cluster_amount

    @cluster_amount.setter
    def cluster_amount(self, cluster_amount):
        '''
        Set the amount of clusters, or centroids that this 
        collection contains
        '''
        self._cluster_amount = cluster_amount

    @property
    def clusters(self):
        '''
        Get all clusters associated with this collection
        '''
        return self._clusters

    def run_kmean(self, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
        '''
        Run KMean clustering algorithm

        Args:
        excluded_attributes(set): Any attributes to exclude from being included in the
            clustering algorithm
        scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
            continuing to downstream classifiers. Defaults to standard
        **kwargs: Arguments and their descriptions can be found at the scikit-learn KMean 
            web page
        '''
        check_package(KMeans, 'sklearn', 'run_kmean')
        self._cluster_setup()
        raw = self.raw(excluded_attributes=excluded_attributes, scale_method=scale_method, weights=weights)
        results = KMeans(self._cluster_amount, **kwargs).fit(raw['values'])
        logger.log('debug', "Iterations = {}".format(results.n_iter_))
        results = results.labels_
        for index, item in enumerate(self._df.items.keys()):
            self._clusters[results[index]].add_item(item, self._df.items[item])

    def run_meanshift(self, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
        '''
        Run Meanshift clustering algorithm

        Args:
        excluded_attributes(set): Any attributes to exclude from being included in the
            clustering algorithm
        scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
            continuing to downstream classifiers. Defaults to standard
        **kwargs: Arguments and their descriptions can be found at the scikit-learn KMean 
            web page
        '''
        check_package(MeanShift, 'sklearn', 'run_meanshift')
        raw = self.raw(excluded_attributes=excluded_attributes, scale_method=scale_method, weights=weights)
        results = MeanShift(**kwargs).fit(raw['values']).labels_
        self._cluster_amount = max(results) + 1
        self._cluster_setup()
        logger.log('info', "Amount of clusters generated {}".format(self._cluster_amount))
        for index, item in enumerate(self._df.items.keys()):
            self._clusters[results[index]].add_item(item, self._df.items[item])

    def run_dbscan(self, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
        '''
        Run dbscan clustering algorithm

        Args:
        excluded_attributes(set): Any attributes to exclude from being included in the
            clustering algorithm
        scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
            continuing to downstream classifiers. Defaults to standard
        **kwargs: Arguments and their descriptions can be found at the scikit-learn KMean 
            web page
        '''
        check_package(DBSCAN, 'sklearn', 'run_dbscan')
        raw = self.raw(excluded_attributes=excluded_attributes, scale_method=scale_method, weights=weights)
        results = DBSCAN(**kwargs).fit(raw['values']).labels_
        new_max = max(results) + 1
        noisy_items = []
        for idx, value in enumerate(results):
            if value == -1:
                print(idx)
                logger.log('debug', "Item {} denoted as noisy item".format(raw['item_names'][idx]))
                noisy_items.append(raw['item_names'][idx])
                results[idx] = new_max
        self._cluster_amount = max(results) + 1
        self._cluster_setup()
        logger.log('info', "Amount of clusters generated {}".format(self._cluster_amount))
        for index, item in enumerate(self._df.items.keys()):
            self._clusters[results[index]].add_item(item, self._df.items[item])
        return noisy_items

    def run_agglomerative(self, excluded_attributes=set(), scale_method='standard', weights=None, **kwargs):
        '''
        Run agglomerative clustering algorithm
        
        Args:
        excluded_attributes(set): Any attributes to exclude from being included in the
            clustering algorithm
        scale_method(None, 'robust', 'min_max', 'standard', 'max_abs'): A method to scale the data before
            continuing to downstream classifiers. Defaults to standard
        **kwargs: Arguments and their descriptions can be found at the scikit-learn KMean 
            web page
        '''
        check_package(AgglomerativeClustering, 'sklearn', 'run_agglomerative')
        raw = self.raw(excluded_attributes=excluded_attributes, scale_method=scale_method, weights=weights)
        self._cluster_setup()
        logger.log('info', "Fitting for agglomerative clustering")
        results = AgglomerativeClustering(**kwargs).fit(raw['values']).labels_
        logger.log('info', "Agglomerative clustering fit complete")
        for index, item in enumerate(self._df.items.keys()):
            self._clusters[results[index]].add_item(item, self._df.items[item])

    def item_cluster(self, name):
        '''
        Returns the cluster that the item belongs to.
        Takes the name of the item. Returns None if not 
        cluster contains the given item
        '''
        for cluster in self._clusters:
            if cluster.contains(name):
                logger.log('debug', "{} in cluster {}".format(name, cluster.name))
                return cluster
        logger.log('error', "Could not find item {} in {}".format(name, self.name))
        return None

    def get_cluster(self, name):
        '''
        Returns the cluster with the given name
        '''
        for cluster in self._clusters:
            if cluster.name == name:
                return cluster
        logger.log('error', "Could not find cluster {} in {}".format(name, self.name))
        raise ValueError("Could not find cluster {} in {}".format(name, self.name))

    def cluster_as_itemcollection(self, cluster_name, copy=False):
        '''
        Return the cluster with the given cluster name as 
        an item collection

        Args:
        cluster_name(str): The name of the cluster to get as an item collection
        copy(bool): True if you'd like a deep copy, False if not. Defaults to False
        '''
        for cluster in self._clusters:
            if cluster.name == cluster_name:
                return cluster.as_itemcollection(self.attributes, copy=copy)
        logger.log('error', "Could not find cluster {} in {}".format(cluster_name, self.name))
        raise ValueError("Could not find cluster {} in {}".format(cluster_name, self.name))

    def _cluster_setup(self):
        self._clusters = []
        for i in range(self._cluster_amount):
            self._clusters.append(Cluster('Cluster {}'.format(i)))
