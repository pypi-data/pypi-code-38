"""
Module for merging clusters using an enclave-swallowing heuristic.
"""

from lib5c.algorithms.clustering.util import identify_nearby_clusters


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
    Under the enclave heuristic, the condition for merging an orphan cluster
    into a parent cluster is that the orphan cluster's peaks must have more
    adjacent neighbors among the parent cluster's peaks than among the orphan
    cluster's peaks.
    """

    nearby_clusters = identify_nearby_clusters(clusters[0], clusters)
    if nearby_clusters:
        counts = [nearby_clusters.count(i) for i in range(len(clusters))]
        if len(counts) > 1:
            max_other = max(counts[1:])
            if max_other >= 2 and max_other > counts[0]:
                return counts.index(max_other)
    return -1
