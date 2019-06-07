"""
Module for splitting clusters using a valley heuristic.
"""

from copy import deepcopy

from lib5c.algorithms.clustering.util import belongs_to_which
from lib5c.algorithms.clustering.knn import get_knn, classify_peak
from lib5c.algorithms.clustering.adjacency import make_clusters as \
    make_clusters_by_adjacency


def split_cluster(parent_cluster, guides, reassign=1.0):
    """
    Splits a cluster using the valley heuristic.

    Parameters
    ----------
    parent_cluster : cluster
        The cluster to split.
    guides : list of clusters
        The guides used to seed the child clusters. See
        ``lib5c.algorithms.clustering.valley.split_clusters()``.
    reassign : float between 0.0 and 1.0
        When a cluster is split, the peaks in the parent cluster with pvalues
        above this threshold may be discarded instead of being assigned to one
        or the other of the child clusters. When the value of this kwarg is 1.0,
        no peaks are discarded and all peaks are reassigned to one or the other
        of the child clusters. When the value of this kwarg is 0.0, all peaks
        are discarded and no peaks are reassigned to the child clusters.

    Returns
    -------
    list of clusters
        The child clusters of the parent cluster.

    Notes
    -----
    See ``lib5c.algorithms.clustering.valley.split_clusters()``.
    """

    # the child clusters
    child_clusters = [[] for guide in guides]

    # a list of unassigned_peaks
    unassigned_peaks = deepcopy(parent_cluster)

    # filter the unassigned_peaks based on the reassign threshold
    unassigned_peaks = filter(lambda x: x['pvalue'] < reassign,
                              unassigned_peaks)

    # sort the peaks
    unassigned_peaks.sort(key=lambda x: x['value'], reverse=True)

    prev_length = len(unassigned_peaks)
    iteration_at_length = 0
    while unassigned_peaks and iteration_at_length <= prev_length:
        if len(unassigned_peaks) == prev_length:
            iteration_at_length += 1
        else:
            prev_length = len(unassigned_peaks)
            iteration_at_length = 1
        # check to see if this peak is identical to a guide peak
        target = belongs_to_which(unassigned_peaks[0], guides)
        if target > -1:
            child_clusters[target].append(unassigned_peaks.pop(0))
        else:
            # find this peak's neighbors
            neighbors = get_knn(unassigned_peaks[0], [peak
                                                      for guide in guides
                                                      for peak in guide], 5)
            target = classify_peak(unassigned_peaks[0], neighbors,
                                   child_clusters, weighted=True,
                                   automove=False)
            if target > -1:
                # classification worked, move the peak
                child_clusters[target].append(unassigned_peaks.pop(0))
            else:
                # classification failed, send it back to the end of the line
                unassigned_peaks.append(unassigned_peaks.pop(0))

    return child_clusters


def split_clusters(clusters, reassign=1.0, size_threshold=3):
    """
    Splits all clusters in a list of clusters using a recursive valley-splitting
    heuristic.

    Parameters
    ---------
    clusters : list of clusters
        The list of clusters to split.
    reassign : float between 0.0 and 1.0
        When a cluster is split, the peaks in the parent cluster with pvalues
        above this threshold may be discarded instead of being assigned to one
        or the other of the child clusters. When the value of this kwarg is 1.0,
        no peaks are discarded and all peaks are reassigned to one or the other
        of the child clusters. When the value of this kwarg is 0.0, all peaks
        are discarded and no peaks are reassigned to the child clusters.
    size_threshold : int
        The minimum size of child clusters that will be created by the
        splitting. If a splitting operation would result in clusters smaller
        than this number, that splitting operation will not be performed.

    Returns
    -------
    list of clusters
        The split clusters.

    Notes
    -----
    A cluster will get split if there exists a p-value such that thresholding
    the cluster at that p-value results in the creation of at least two
    contiguous groups of high-confidence peaks (p-value below the threshold)
    larger than the ``size_threshold`` separated by a "valley" of low-confidence
    peaks (p-value above the threshold). This rule is applied recursively until
    only unsplittable, or "atomic", clusters remain.
    """
    step = 0.005
    atomic_clusters = []
    while clusters:
        for i in range(len(clusters)):
            if len(clusters[i]) >= 2*size_threshold:
                max_pvalue = max([peak['pvalue'] for peak in clusters[i]])
                current_pvalue = max_pvalue
                while True:
                    # tighten threshold
                    current_pvalue -= step

                    # filter peaks
                    filtered_peaks = filter(
                        lambda x: x['pvalue'] < current_pvalue, clusters[i])

                    if filtered_peaks:
                        # cluster by adjacency
                        guides = make_clusters_by_adjacency(filtered_peaks)

                        # remove things that are too small
                        guides = filter(lambda x: len(x) > size_threshold,
                                        guides)

                        if len(guides) > 1:
                            new_clusters = None
                            if reassign > 0.0:
                                new_clusters = split_cluster(clusters[i],
                                                             guides, reassign)
                            else:
                                new_clusters = guides
                            clusters.extend(new_clusters)
                            clusters.pop(i)
                            # break condition 1:
                            # successful split
                            break
                    else:
                        # the threshold is too tight; give up
                        atomic_clusters.append(clusters.pop(i))
                        # break condition 2:
                        # no threshold splits the cluster
                        break
                # breaks 1 and 2 feed into this one
                break
            else:
                atomic_clusters.append(clusters.pop(i))
                # break condition 3:
                # cluster is too small to even attempt split
                break

    return atomic_clusters
