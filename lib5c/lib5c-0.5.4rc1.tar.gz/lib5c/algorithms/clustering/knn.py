"""
Module for assembling clusters using an unassisted k-nearest neighbors
heuristic.
"""

from copy import deepcopy

import numpy as np
from scipy.spatial import KDTree

from lib5c.algorithms.clustering.util import get_vector


def make_clusters(peaks, k=8, dist_score=5, dist_k=8, dir_score=0.3, dir_k=8):
    """
    Performs k-nearest neighbors clustering of peaks.

    Parameters
    ----------
    k : int
        The number of nearest neighbors to consider when clustering.
    dist_score : float
        The distance-score threshold to use when clustering.
    dist_k : int
        The number of nearest neighbors to consider when calculating the
        distance score.
    dir_score : float
        The direction-score threshold to use when clustering.
    dir_k : int
        The number of nearest neighbors to consider when calculating the
        direction score.

    Returns
    -------
    list of clusters, list of peaks, list of peaks
        A tuple whose first element is the list of merged clusters, whose second
        element is the list of peaks that did not pass the distance score
        threshold, and whose third element is the list of peaks that did not
        pass the direction score threshold.
    """
    # dict to store cluster information
    # (-1 = no cluster, otherwise the value equals the cluster index)
    peak_to_clusters = {(peak['x'], peak['y']): -1 for peak in peaks}

    # list of clusters
    clusters = []

    # list to store singleton peaks
    # (those that fail to pass the distance score threshold)
    singleton_peaks = []

    # list to store line peaks
    # (those that fail to pass the direction score threshold)
    line_peaks = []

    peak_list = [(peak['x'], peak['y']) for peak in peaks]
    peak_tree = KDTree(peak_list)
    peak_info = {(peak['x'], peak['y']): peak for peak in peaks}
    ranked_peaks = [(peak['x'], peak['y'])
                    for peak in sorted(peaks, key=lambda x: x['value'],
                                       reverse=True)]

    for ranked_peak in ranked_peaks:
        distances, indices = peak_tree.query(ranked_peak, dist_k+1)
        distance_neighbors = [dict(peak_info[peak_list[indices[i]]],
                                   **{'distance': distances[i]})
                              for i in range(1, min(dist_k+1, len(peak_list)))]
        if distance_score(distance_neighbors) < dist_score:
            if dist_k == dir_k:
                direction_neighbors = distance_neighbors
            else:
                distances, indices = peak_tree.query(ranked_peak, dir_k+1)
                direction_neighbors = [dict(peak_info[peak_list[indices[i]]],
                                            **{'distance': distances[i]})
                                       for i in range(1, min(dir_k + 1,
                                                             len(peak_list)))]
            if direction_score(peak_info[ranked_peak],
                               direction_neighbors) >= dir_score:
                if k == dir_k:
                    knn_neighbors = direction_neighbors
                elif k == dist_k:
                    knn_neighbors = distance_neighbors
                else:
                    distances, indices = peak_tree.query(ranked_peak, k+1)
                    knn_neighbors = [dict(peak_info[peak_list[indices[i]]],
                                          **{'distance': distances[i]})
                                     for i in range(1, min(k + 1,
                                                           len(peak_list)))]
                classify_peak(peak_info[ranked_peak], knn_neighbors, clusters,
                              peak_to_clusters, weighted=True)
            else:
                line_peaks.append(peak_info[ranked_peak])
        else:
            singleton_peaks.append(peak_info[ranked_peak])

    return clusters, singleton_peaks, line_peaks


def get_knn(peak, peaks, k):
    """
    Given a list of peaks and a query peak, returns the k nearest neighbors of
    the query peak.

    Parameters
    ----------
    peak : peak
        The query peak to for which nearest neighbors should be identified.
    peaks : list of peaks
        The peaks that are candidates to be nearest neighbors.
    k : int

    Returns
    -------
    list of peaks
        The k nearest neighbors of the query peak among peaks. If fewer than k
        peaks were provided, the length of this list will be shorter than k.

    Notes
    -----
    peak may be present in peaks, but it will not be returned as a neighbor.
    """
    # list of neighbors
    neighbors = []

    for prospective_neighbor in peaks:
        temp = deepcopy(prospective_neighbor)
        difference_vector = get_vector(peak) - get_vector(temp)
        distance = np.linalg.norm(difference_vector)
        if distance > 0.5:
            temp['distance'] = distance
            temp['direction'] = difference_vector / distance
            neighbors.append(temp)

    # rank the prospective neighbors by distance
    neighbors.sort(key=lambda x: x['distance'], reverse=False)

    # return the closest k prospective neighbors
    return neighbors[0:k]


def distance_score(neighbors):
    """
    Calculates a distance-score for a peak given its neighbors.

    Parameters
    ----------
    neighbors : list of peaks
        The query peak's neighbors.

    Returns
    -------
    float
        The distance-score.

    Notes
    -----
    Lower distance-scores are better.
    """
    score = 0
    for neighbor in neighbors:
        score += neighbor['distance']
    return score / len(neighbors)


def direction_score(peak, neighbors):
    """
    Calculates a direction-score for a peak given its neighbors.

    Parameters
    ----------
    peak : peak
        The query peak.
    neighbors : list of peaks
        The query peak's neighbors.

    Returns
    -------
    float
        The direction-score.

    Notes
    -----
    Higher direction-scores are better.
    """
    x_sums = 0.0
    y_sums = 0.0
    for neighbor in neighbors:
        difference_vector = get_vector(peak) - get_vector(neighbor)
        distance = neighbor['distance']
        direction = difference_vector / distance
        x_sums += abs(direction[0])
        y_sums += abs(direction[1])
    hypotenuse = np.linalg.norm([x_sums, y_sums])
    return min(x_sums/hypotenuse, y_sums/hypotenuse)


def classify_peak(peak, neighbors, clusters, peak_to_clusters, automove=True,
                  weighted=False):
    """
    Assigns the most fitting cluster to a peak given a list of its neighbors.

    Parameters
    ----------
    peak : peak
        The peak to classify.
    neighbors : list of peaks
        The peaks that should determine the query peak's classification.
    clusters : list of clusters
        A list of clusters to classify the query peak into.
    peak_to_clusters : dict of (int, int) tuples
        The keys are (x, y) tuples that represent peak locations. The values are
        the indices of the cluster for that peak. If the value is -1, it
        indicates that the peak does not belong to any cluster.
    automove : bool
        If True, the peak will automatically be moved to the appropriate
        cluster, or a new cluster will be appended to clusters. If False, the
        index of the appropriate target cluster will be returned. If there is no
        appropriate target cluster, -1 will be returned.
    weighted : bool
        If True, weigh the votes using peak weight and distance. If False, treat
        the votes from each peak as equal.

    Returns
    -------
    int (sometimes)
        The index of the appropriate target cluster. This function has no return
        value unless automove is False.

    Notes
    -----
    This function uses a simple unweighted voting heuristic to determine which
    existing cluster in clusters the query peak should be classified into. If no
    suitable existing cluster is found, a new cluster is created containing only
    the query peak. This cluster is then appended to clusters. Pass the kwarg
    weighted=True to use a weighted voting heuristic.
    """
    # catch the case where there are no clusters to categorize into yet
    if len(clusters) == 0:
        clusters.append([peak])
        return

    # if we're using the weighted heuristic, we will need these values
    mean_value = 0
    mean_distance = 0
    if weighted:
        mean_value = sum([neighbor['value']
                          for neighbor in neighbors]) / len(neighbors)
        mean_distance = sum([neighbor['distance']
                             for neighbor in neighbors]) / len(neighbors)

    # vote
    votes = np.zeros(len(clusters))
    for neighbor in neighbors:
        index = peak_to_clusters[(neighbor['x'], neighbor['y'])]
        if index > -1:
            if not weighted:
                votes[index] += 1
            else:
                votes[index] += (neighbor['value'] / mean_value) * \
                                (mean_distance / neighbor['distance'])

    # check the results of the voting
    # if no one voted, this is a new cluster
    if np.amax(votes) == 0:
        if not automove:
            return -1
        clusters.append([peak])
        peak_to_clusters[(peak['x'], peak['y'])] = len(clusters) - 1
    else:
        if not automove:
            return np.argmax(votes)
        clusters[np.argmax(votes)].append(peak)
        peak_to_clusters[(peak['x'], peak['y'])] = np.argmax(votes)
