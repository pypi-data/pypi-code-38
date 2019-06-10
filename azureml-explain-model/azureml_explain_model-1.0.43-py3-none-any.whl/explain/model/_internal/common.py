# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines common constants and methods used by the model explanation package."""

import logging
import numpy as np

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.INFO)


def _sort_values(values, order):
    return np.array(values)[order]


def unsort_1d(values, order):
    """Unsort a sorted 1d array based on the order that was used to sort it.

    :param values: The array that has been sorted.
    :type values: numpy.array
    :param order: The order list that was originally used to sort values.
    :type order: numpy.array
    :return: The unsorted array.
    :rtype: numpy.array
    """
    order_inverse = [None] * len(order)
    for i in range(len(order)):
        order_inverse[order[i]] = i
    return np.array(values)[order_inverse]


def unsort_2d(values, order):
    """Unsort a sorted 2d array based on the order that was used to sort it.

    :param values: The array that has been sorted.
    :type values: numpy.array
    :param order: The order list that was originally used to sort values.
    :type order: numpy.ndarray
    :return: The unsorted array.
    :rtype: numpy.array
    """
    return np.array([unsort_1d(values[i], order[i]).tolist() for i in range(len(order))])


def _order_imp(summary):
    """Compute the ranking of feature importance values.

    :param summary: A 3D array of the feature importance values to be ranked.
    :type summary: numpy.ndarray
    :return: The rank of the feature importance values.
    :rtype: numpy.ndarray
    """
    return summary.argsort()[..., ::-1]


# sorts a single dimensional feature list according to order
def _sort_feature_list_single(features, order):
    return list(map(lambda x: features[x], order))


# returns a list of lists, where each internal list is the feature list sorted according to the order of a single class
def _sort_feature_list_multiclass(features, order):
    return [list(map(lambda x: features[x], order_i)) for order_i in order]


# do the equivalent of a numpy array slice on a two-dimensional list
def _two_dimensional_slice(lst, end_index):
    return list(map(lambda x: x[:end_index], lst))
