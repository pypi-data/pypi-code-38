"""
Module for assembling clusters using a greedy heuristic.
"""

from copy import deepcopy

import numpy as np

from lib5c.algorithms.clustering.util import get_vector, center_of_mass


def make_clusters(peaks):
    """
    Merges peaks using a greedy merge criterion that grows clusters by
    iteratively assimilating all peaks within r + 2 units of the existing
    cluster's centroid where r is thre cluster's current radius.

    Parameters
    ----------
    peaks : list of peaks
        The peaks to be clustered.

    Returns
    -------
    list of clusters
        The clustered peaks.
    """
    # make a copy
    peaks_copy = deepcopy(peaks)

    # list of clusters
    clusters = []

    # sort peaks
    peaks_copy.sort(key=lambda x: x['value'], reverse=True)

    while peaks_copy:
        first_peak = peaks_copy.pop(0)
        new_cluster = [first_peak]
        centroid = get_vector(first_peak)
        r = 0
        nearby_peaks = filter(
            lambda x: np.linalg.norm(centroid - get_vector(x)) < r + 2,
            peaks_copy)
        while nearby_peaks:
            # add nearby peaks
            for peak in nearby_peaks:
                new_cluster.append(peaks_copy.pop(peaks_copy.index(peak)))

            # recalculate centroid and radius
            centroid = center_of_mass(new_cluster)
            r = max([np.linalg.norm(centroid - get_vector(peak))
                     for peak in new_cluster])

            # look for nearby peaks
            nearby_peaks = filter(
                lambda x: np.linalg.norm(centroid - get_vector(x)) < r + 2,
                peaks_copy)
        clusters.append(new_cluster)

    return clusters
