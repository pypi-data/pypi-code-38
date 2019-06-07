"""
Module for assembling or merging clusters using a simple adjacency heuristic.
"""

from lib5c.algorithms.clustering.util import identify_nearby_clusters, \
    merge_clusters


def make_clusters(peaks):
    """
    Clusters peaks by adjacency.

    Parameters
    ----------
    peaks : list of peaks
        The peaks to cluster.

    Returns
    -------
    list of clusters
        The clustered peaks.
    """

    clusters = []
    for peak in sorted(peaks, key=lambda x: x['value'], reverse=True):
        nearby_clusters = identify_nearby_clusters([peak], clusters)
        if nearby_clusters:
            clusters[nearby_clusters[0]].append(peak)
        else:
            clusters.append([peak])
    return merge_clusters(clusters, merge_to_which)


def merge_to_which(clusters):
    """
    Determines which other cluster, if any, the first cluster in a list of
    clusters should be merged into.

    Parameters
    ----------
    clusters : list of clusters
        The list of clusters to consider. Ideally, this list should be sorted in
        ascending order of cluster size.

    Returns
    -------
    int
        The index of the cluster that the first cluster should be merged into.
        If the cluster should not be merged, the value will be -1.

    Notes
    -----
    Under the adjacency heuristic, the condition for merging two clusters is
    that they must contain peaks that are immediately adjacent to each other in
    2-D space.
    """
    nearby_clusters = filter(lambda x: x > 0,
                             identify_nearby_clusters(clusters[0], clusters))
    if nearby_clusters:
        return nearby_clusters[0]
    return -1
