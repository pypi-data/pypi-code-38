#
#  nn/functional/metrics.py
#  bxtorch
#
#  Created by Oliver Borchert on May 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import torch

def accuracy(y_pred, y_true):
    """
    Computes the accuracy of the class predictions.

    Parameters:
    -----------
    - y_pred: torch.LongTensor [N] or torch.FloatTensor [N, C]
        The class predictions made by the model. Can be either specific classes
        or predictions for each class.
    - y_true: torch.LongTensor [N]
        The actual classes.

    Returns:
    --------
    - torch.FloatTensor
        The accuracy.
    """
    y_pred = _ensure_classes(y_pred)
    return (y_pred == y_true).float().mean()


def recall(y_pred, y_true, c=1):
    """
    Computes the recall score of the class predictions.

    Parameters:
    -----------
    - y_pred: torch.LongTensor [N] or torch.FloatTensor [N, C]
        The class predictions made by the model. Can be either specific classes
        or predictions for each class.
    - y_true: torch.LongTensor [N]
        The actual classes.
    - c: int, default: 1
        The class to calculate the recall score for. Default assumes a binary
        classification setting.

    Returns:
    --------
    - torch.FloatTensor
        The recall score.
    """
    y_pred = _ensure_classes(y_pred)

    y_pred = y_pred == c
    y_true = y_true == c

    correct = (y_pred[y_true == y_pred]).sum()
    true_correct = y_true.sum()
    
    return correct.float() / true_correct.float()


def precision(y_pred, y_true, c=1):
    """
    Computes the precision score of the class predictions.

    Parameters:
    -----------
    - y_pred: torch.LongTensor [N] or torch.FloatTensor [N, C]
        The class predictions made by the model. Can be either specific classes
        or predictions for each class.
    - y_true: torch.LongTensor [N]
        The actual classes.
    - c: int, default: 1
        The class to calculate the recall score for. Default assumes a binary
        classification setting.

    Returns:
    --------
    - torch.FloatTensor
        The precision score.
    """
    y_pred = _ensure_classes(y_pred)

    y_pred = y_pred == c
    y_true = y_true == c

    correct = (y_pred[y_true == y_pred]).sum()
    true_correct = y_pred.sum()
    
    return correct.float() / true_correct.float()


def f1_score(y_pred, y_true, c=1):
    """
    Computes the F1-score of the class predictions.

    Parameters:
    -----------
    - y_pred: torch.LongTensor [N] or torch.FloatTensor [N, C]
        The class predictions made by the model. Can be either specific classes
        or predictions for each class.
    - y_true: torch.LongTensor [N]
        The actual classes.
    - c: int, default: 1
        The class to calculate the recall score for. Default assumes a binary
        classification setting.

    Returns:
    --------
    - torch.FloatTensor
        The F1-score.
    """
    y_pred = _ensure_classes(y_pred)
    p = precision(y_pred, y_true, c=c)
    r = recall(y_pred, y_true, c=c)
    return (2 * p * r) / (p + r)


def _ensure_classes(y):
    assert y.dim() == 1 and y.dim() <= 2, \
        f"Invalid dimensionality {y.dim()} of predictions."

    if y.dim() == 2:
        return torch.argmax(y)
    elif y.dtype == torch.float32:
        return torch.round(y)
    return y
