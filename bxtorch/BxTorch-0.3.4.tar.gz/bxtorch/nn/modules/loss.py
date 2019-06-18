#
#  nn/modules/__init__.py
#  bxtorch
#
#  Created by Oliver Borchert on May 19, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

import numpy as np
from sklearn.utils.class_weight import compute_class_weight
import torch
import torch.nn as nn
import torch._jit_internal as _jit

@_jit.weak_module
class BCELoss(nn.Module):
    """
    Binary cross entropy loss which allows for easy weighting of classes as
    well as an index which is ignored in calculations. With default parameters,
    this loss defaults to PyTorch's built-in BCELoss.
    """
    
    # MARK: Initialization
    def __init__(self, labels=None, ignore_index=None):
        """
        Initializes a new BCELoss.

        Parameters:
        -----------
        - labels: np.ndarray [N], default: None
            If given, class weights are computed according to the given labels.
        - ignore_index: int, default: None
            If given, this index in the labels is ingored when computing the
            loss.
        """
        self.ignore_index = ignore_index

        if labels is not None:
            weights = compute_class_weight(
                'balanced', np.arange(np.max(labels) + 1), labels
            )
            self.weights = torch.as_tensor(weights, dtype=torch.float)
            self.loss = nn.BCELoss(reduction='none')
        else:
            self.weights = None
            self.loss = nn.BCELoss()

    # MARK: Instance Methods
    @_jit.weak_script_method
    def forward(self, y_pred, y_true):
        if self.ignore_index is not None:
            mask = ~(y_true == self.ignore_index)
            y_pred = y_pred[mask]
            y_true = y_true[mask]

        if self.weights is not None:
            self.class_weights = self.class_weights.to(y_pred.device)
            bce = self.loss(y_pred, y_true)
            return (bce * self.class_weights[y_true.long()]).mean()

        return self.loss(y_pred, y_true)
