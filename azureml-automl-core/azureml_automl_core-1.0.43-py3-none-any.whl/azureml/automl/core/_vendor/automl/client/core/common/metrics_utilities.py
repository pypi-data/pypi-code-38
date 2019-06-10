# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for computing model evaluation metrics."""
from typing import Any, List, Optional
import numpy as np


def pad_predictions(y_pred_probs: np.ndarray,
                    trained_labels: Optional[np.ndarray],
                    class_labels: Optional[np.ndarray]) -> np.ndarray:
    """
    Add padding to the predicted probabilities for missing training classes.

    If the model is not trained on every class from the dataset it will not
    predict those missing classes.
    Here we insert columns of all zeros for those classes on which the model was not trained.
    Effectively, the model predicts these classes with zero probability.

    :param y_pred_probs: Predictions from a classification model
    :param trained_labels: The class labels on which the model was trained
    :param class_labels: The class labels from the full dataset
    :return: Padded predicted probabilities
    """
    if trained_labels is None or class_labels is None:
        return y_pred_probs
    if len(trained_labels) == len(class_labels):
        return y_pred_probs

    new_y_pred_probs_trans = []
    for class_label in class_labels:
        found = False
        for trained_index, trained_label in enumerate(trained_labels):
            if class_label == trained_label:
                new_y_pred_probs_trans.append(y_pred_probs.T[trained_index])
                found = True
                break
        if not found:
            new_y_pred_probs_trans.append(np.zeros((y_pred_probs.shape[0],)))
    return np.array(new_y_pred_probs_trans).T
