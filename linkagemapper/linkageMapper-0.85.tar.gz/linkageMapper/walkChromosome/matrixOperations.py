#!/bin/python

import numpy as np

import scipy
import fastcluster


def seriation(Z, N, cur_index):
    '''
        input:
            - Z is a hierarchical tree (dendrogram)
            - N is the number of points given to the clustering process
            - cur_index is the position in the tree for the recursive traversal
        output:
            - order implied by the hierarchical tree Z

        seriation computes the order implied by a hierarchical tree (dendrogram)
    '''
    if cur_index < N:
        return [cur_index]
    else:
        left = int(Z[cur_index - N, 0])
        right = int(Z[cur_index - N, 1])
        return (seriation(Z, N, left) + seriation(Z, N, right))


def compute_serial_matrix(dist_mat, method="ward"):
    '''
        input:
            - dist_mat is a distance matrix
            - method = ["ward","single","average","complete"]
        output:
            - seriated_dist is the input dist_mat,
              but with re-ordered rows and columns
              according to the seriation, i.e. the
              order implied by the hierarchical tree
            - res_order is the order implied by
              the hierarhical tree
            - res_linkage is the hierarhical tree (dendrogram)

        compute_serial_matrix transforms a distance matrix into 
        a sorted distance matrix according to the order implied 
        by the hierarchical tree (dendrogram)
    '''
    N = len(dist_mat)
    flat_dist_mat = scipy.spatial.distance.squareform(dist_mat)
    res_linkage = fastcluster.linkage(flat_dist_mat, method=method, preserve_input=True)
    res_order = seriation(res_linkage, N, N + N-2)

    seriated_dist = reorderMatrix(dist_mat, res_order)

    return seriated_dist, res_order, res_linkage


def reorderMatrix(original_matrix, res_order):
    N = len(original_matrix)
    reordered_matrix = np.zeros((N, N))

    a, b = np.triu_indices(N, k=1)
    reordered_matrix[a, b] = original_matrix[[res_order[i] for i in a],
                                             [res_order[j] for j in b]]
    reordered_matrix[b, a] = reordered_matrix[a, b]
    return reordered_matrix



