"""
Module containing utility functions used for computing scoring metrics.
"""

import numpy as np
from sklearn.metrics import confusion_matrix


def cohens_kappa(y1, y2):
    """
    Computes Cohen's kappa score for the agreement between two classifications.

    Implementation taken from `sklearn.metrics.cohen_kappa_score()`.

    Parameters
    ----------
    y1, y2 : np.ndarray
        The two classifications.

    Returns
    -------
    float
        The kappa.
    """
    confusion = confusion_matrix(y1, y2)
    p = confusion / float(confusion.sum())
    p_observed = np.trace(p)
    p_expected = np.dot(p.sum(axis=0), p.sum(axis=1))
    return (p_observed - p_expected) / (1 - p_expected)
