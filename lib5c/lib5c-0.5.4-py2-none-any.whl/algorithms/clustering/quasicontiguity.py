"""
Module for splitting clusters using a quasicontiguity heuristic.
"""

from copy import deepcopy

import numpy as np

from lib5c.algorithms.clustering.util import get_vector


def split_cluster(cluster, distance_threshold=3, size_threshold=2):
    """
    Identifies the subclusters of a cluster, as determined by quasicontiguity
    and a size threshold.

    Parameters
    ----------
    cluster : cluster
        The cluster to determine the subclusters of.
    distance_threshold : float
        If two peaks are separated by a distance less than this threshold, they
        are considered "quasicontiguous".
    size_threshold : int
        If the size of a subcluster would be smaller than this threshold, that
        subcluster is not split from its parent.

    Returns
    -------
    list of clusters
        The subclusters of the query cluster.
    """
    # the subclusters of this cluster
    subclusters = []
    # make a copy of the cluster - we will be removing from this list
    unassigned_peaks = deepcopy(cluster)
    # we want to assign all the peaks
    while unassigned_peaks:
        # create a new subcluster around this peak
        current_subcluster = [unassigned_peaks.pop(0)]
        # we will attempt to grow this subcluster until it stops growing
        # as long as the cluster grows, this flag will be True
        # when it stops growing, this flag will be false
        # and we will exit this while loop
        change_flag = True
        while change_flag:
            # reset the change_flag
            change_flag = False
            # a list to store the indices of the peaks that will get annexed in
            # this round of growth
            # we choose to do it this way since we don't want to modify
            # unassigned_peaks while looping through it
            indices_to_annex = []
            # look at all the unassigned_peaks to see if there are any we can
            # annex
            for i in range(len(unassigned_peaks)):
                # we should annex unassigned_peaks[i] if it's close to any of
                # the member peaks of the current subcluster
                for member_peak in current_subcluster:
                    distance = np.linalg.norm(get_vector(unassigned_peaks[i]) -
                                              get_vector(member_peak))
                    if distance < distance_threshold:
                        indices_to_annex.append(i)
                        break
            # if there are any unassigned peaks that should be annexed to the
            # current subcluster, do that now
            if indices_to_annex:
                for index in sorted(indices_to_annex, reverse=True):
                    current_subcluster.append(unassigned_peaks.pop(index))
                # set the change_flag
                change_flag = True
        # the current subcluster is done growing
        # add it to the list of subclusters
        subclusters.append(current_subcluster)
    # exclude subclusters that don't pass the size threshold
    subclusters = filter(lambda x: len(x) >= size_threshold, subclusters)
    # return subclusters
    return subclusters


def split_clusters(clusters, distance_threshold=3, size_threshold=2):
    """
    Iteratively splits all clusters in a list by quasicontiguity (as determined
    by a distance and size threshold) and returns the resulting subclusters.

    Parameters
    ----------
    clusters : list of clusters
        The clusters to split.
    distance_threshold : float
        If two peaks are separated by a distance less than this threshold, they
        are considered "quasicontiguous".
    size_threshold : int
        If the size of a subcluster would be smaller than this threshold, that
        subcluster is not split from its parent.

    Returns
    -------
    list of clusters
        The list of split clusters.
    """
    atomic_clusters = []
    for cluster in clusters:
        atomic_clusters.extend(
            split_cluster(cluster, distance_threshold, size_threshold))
    return atomic_clusters
