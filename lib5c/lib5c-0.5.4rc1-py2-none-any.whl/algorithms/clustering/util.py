"""
Module containing utility functions for clustering 5C interactions.
"""

import numpy as np

from lib5c.util.parallelization import parallelize_regions


def clusters_to_array(clusters, size):
    """
    Assembles clusters into a 2-D array for plotting on a heatmap.

    Parameters
    ----------
    clusters : list of clusters
        The clusters to be converted to a 2-D array.
    size : int
        The height and width of the array to generate. This should be equal to
        the number of bins in the region.

    Returns
    -------
    2-D array
        A 2-D array with each clusters having been assigned a different
        sequential integer value for all its pixels. The next consecutive
        integer is a gap value, and then the one after that is a default value
        for all pixels not in a cluster.

    Notes
    -----
    It is recommended to plot the resulting array using a rapidly-changing
    colorscale such as plt.get_cmap('gist_ncar').
    """
    num_clusters = len(clusters)
    array = np.zeros([size, size]) + num_clusters + 2

    for i in range(num_clusters):
        for peak in clusters[i]:
            array[peak['x']][peak['y']] = i
            array[peak['y']][peak['x']] = i

    return array


def get_vector(peak):
    """
    Gets an array representing a peak's location.

    Parameters
    ----------
    peak : peak

    Returns
    -------
    1D numpy array of length 2
        The peak's location as an (x, y) ordered pair.
    """
    return np.array([peak['x'], peak['y']])


def center_of_mass(cluster):
    """
    Computes the center of mass, or centroid, of a cluster.

    Parameters
    ----------
    cluster : cluster
        The cluster to consider.

    Returns
    -------
    1D numpy array of length 2
        The centroid of the cluster.

    Notes
    -----
    For the purpose of this calculation, the mass of a peak is taken to be its
    value.
    """
    m = 0
    vector_sum = np.array([0, 0])
    for peak in cluster:
        m += peak['value']
        vector_sum += peak['value'] * get_vector(peak)
    return vector_sum / m


def belongs_to_which(peak, clusters):
    """
    Identifies which cluster out of a list of clusters, if any, a peak belongs
    to.

    Parameters
    ----------
    peak : peak
        The query peak to consider.
    clusters : list of clusters
        The clusters to look for the query peak in.

    Returns
    -------
    int
        The index of the cluster within the list of clusters which contains the
        query peak, or -1 if no cluster in the list of clusters contains the
        query peak.
    """
    return get_cluster(peak['x'], peak['y'], clusters)


def belongs_to(peak, cluster):
    """
    Checks if a peak belongs to a cluster.

    Parameters
    ----------
    peak : peak
        The query peak.
    cluster : cluster
        The cluster to search for it in.

    Returns
    -------
    bool
        True if peak belongs to cluster, False otherwise.
    """
    return belongs_to_which(peak, [cluster]) == 0


def get_cluster(x, y, clusters):
    """
    Identifies which cluster, if any, a specified point belongs to.

    Parameters
    ----------
    x : int
        x-coordinate of the point to consider.
    y : int
        y-coordinate of the point to consider.
    clusters : list of clusters
        List of clusters to search.

    Returns
    -------
    int
        The index of the cluster which contains the point (x,y). If no cluster
        in the list contains the point, the value
        is -1.
    """
    for i in range(len(clusters)):
        for peak in clusters[i]:
            if peak['x'] == x and peak['y'] == y:
                return i
    return -1


def ident(peak1, peak2):
    """
    Checks whether two peaks are the same peak.

    Parameters
    ----------
    peak1 : peak
    peak2 : peak

    Returns
    -------
    bool
        True if the peaks are the same peak, False otherwise.
    """
    return peak1['x'] == peak2['x'] and peak1['y'] == peak2['y']


def identify_nearby_clusters(cluster, clusters):
    """
    Figures out which other clusters from a list of clusters are adjacent to a
    query cluster.

    Parameters
    ----------
    cluster : cluster
        The query cluster to consider.
    clusters : list of clusters
        The clusters to check for adjacency to the query cluster.

    Returns
    -------
    list of int
        The indices of clusters within the list of clusters that were found to
        be adjacent to the query cluster.

    Notes
    -----
    This may include duplicates. To get rid of them, just use::

        set(identify_nearby_clusters(cluster, clusters))

    To identify one nearby cluster at random, use::

        nearby_clusters = identify_nearby_clusters(cluster, clusters)
        if nearby_clusters:
            nearby_clusters[0]

    To see what clusters are near a single peak, use::

        identify_nearby_clusters([peak], clusters)

    If cluster is in clusters, the cluster will be reported as adjacent to
    itself. As an example of how to avoid this in
    cases where it is undesirable, use::

        filter(lambda x: x > 0, identify_nearby_clusters(clusters[0], clusters))

    """
    nearby = []
    threshold = -1
    for peak in cluster:
        up = get_cluster(peak['x'], peak['y'] + 1, clusters)
        if up > threshold:
            nearby.append(up)
        down = get_cluster(peak['x'], peak['y'] - 1, clusters)
        if down > threshold:
            nearby.append(down)
        left = get_cluster(peak['x'] - 1, peak['y'], clusters)
        if left > threshold:
            nearby.append(left)
        right = get_cluster(peak['x'] + 1, peak['y'], clusters)
        if right > threshold:
            nearby.append(right)
        ne = get_cluster(peak['x'] + 1, peak['y'] + 1, clusters)
        if ne > threshold:
            nearby.append(ne)
        se = get_cluster(peak['x'] + 1, peak['y'] - 1, clusters)
        if se > threshold:
            nearby.append(se)
        nw = get_cluster(peak['x'] - 1, peak['y'] + 1, clusters)
        if nw > threshold:
            nearby.append(nw)
        sw = get_cluster(peak['x'] - 1, peak['y'] - 1, clusters)
        if sw > threshold:
            nearby.append(sw)
    return nearby


def merge_clusters(clusters, merge_to_which):
    """
    Recursively merges clusters together from smallest to largest according to a
    specified merge function.

    Parameters
    ----------
    clusters : list of clusters
        The clusters to be merged. All elements will be removed from this list
        when this function is called.
    merge_to_which : function
        Function that takes in a list of clusters and returns the index of the
        cluster the first cluster in the list should be merged into. If the
        first cluster in the list should not be merged, this function should
        return -1.

    Returns
    -------
    list of clusters
        The list of merged clusters.
    """
    # list to store merged clusters
    merged_clusters = []

    while clusters:
        # sort the clusters from smallest to largest
        clusters.sort(key=lambda x: len(x), reverse=False)

        # attempt to merge this cluster into another cluster by adjacency
        merge_to = merge_to_which(clusters)
        if merge_to == -1:
            # this one didn't merge
            merged_clusters.append(clusters.pop(0))
        else:
            # merge this cluster into the chosen cluster
            clusters[merge_to].extend(clusters[0])
            clusters.pop(0)

    return merged_clusters


@parallelize_regions
def reshape_cluster_array_to_dict(cluster_array, ignored_values=None):
    """
    Reshapes loops dict structure into a nested dict structure.

    Parameters
    ----------
    cluster_array: np.ndarray
        The entries of this array are cluster ID's. Values that will be ignored
        include '', 'n.s.', 'NA', 'NaN', np.nan.
    ignored_values: set, optional
        Set of values in cluster_array that should not be treated as cluster
        ID's. By default this will be {'', 'n.s.', 'NA', 'NaN', np.nan}

    Returns
    --------
    Dict[Any, List[Dict[str, Any]]]
        The outer dict's keys are cluster ID's, its values are lists of points
        belonging to that cluster, with the points being provided as dicts with
        the following strucure::

            {
                'x': int,
                'y': int,
                'value': 0
            }

    Notes
    -----
    To rectangularize the returned data structure against a full list of cluster
    ID's, use something like::

        cluster_dict = reshape_cluster_array_to_dict(cluster_array)
        for cluster_id in all_cluster_ids:
            if cluster_id not in cluster_dict:
                cluster_dict[cluster_id] = []

    Examples
    --------
    >>> import numpy as np
    >>> cluster_array = np.array([['', 'cow'], ['cow', 'grass']])
    >>> reshape_cluster_array_to_dict(cluster_array)
    {'grass': [{'y': 1, 'x': 1, 'value': 0}],
     'cow': [{'y': 1, 'x': 0, 'value': 0},
             {'y': 0, 'x': 1, 'value': 0}]}
    """
    # resolve ignored_values
    if ignored_values is None:
        ignored_values = {'', 'n.s.', 'NA', 'NaN', np.nan}

    # identify non-ignored cluster id's
    cluster_ids = set(np.unique(cluster_array)) - ignored_values

    # prepare data structure
    cluster_dict = {cluster_id: [] for cluster_id in cluster_ids}

    # fill in data structure
    for i in range(cluster_array.shape[0]):
        for j in range(cluster_array.shape[1]):
            cluster_id = cluster_array[i, j]
            if cluster_id in cluster_ids:
                cluster_dict[cluster_id].append({'x': i, 'y': j, 'value': 0})

    return cluster_dict


def flatten_clusters(clusters):
    """
    Flattens a list of clusters to a flat list of peaks.

    Parameters
    ----------
    clusters : list of list of peaks
        The clusters to flatten.

    Returns
    -------
    list of peaks
        The flattened peaks.
    """
    return [peak for cluster in clusters for peak in cluster]


def peaks_to_array_index(peaks, shape):
    """
    Convert a sparse list of peaks to a dense boolean array.

    Parameters
    ----------
    peaks : list of peaks
        The peaks to convert.
    shape : tuple of int
        The shape of the resulting array.

    Returns
    -------
    np.ndarray
        The dense boolean array.
    """
    idx = np.zeros(shape, dtype=bool)
    for peak in peaks:
        idx[peak['x'], peak['y']] = True
        idx[peak['y'], peak['x']] = True
    return idx


def array_index_to_peaks(idx):
    """
    Convert a dense boolean array to a sparse list of peaks.

    Parameters
    ----------
    idx : np.ndarray
        Boolean array to convert.

    Returns
    -------
    list of peaks
        The peaks.
    """
    return [{'x': i, 'y': j, 'value': 0}
            for i in range(idx.shape[0])
            for j in range(i+1)
            if idx[i, j]]
