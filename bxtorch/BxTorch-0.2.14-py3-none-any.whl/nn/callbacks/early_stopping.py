#
#  nn/callbacks/early_stopping.py
#  bxtorch
#
#  Created by Oliver Borchert on May 09, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import copy
from .base import TrainingCallback, CallbackException

class EarlyStopping(TrainingCallback):
    """
    The early stopping callback watches a specified metric and interrupts
    training if the metric does not decrease for a specified number of epochs.
    """

    # MARK: Initialization
    def __init__(self, metric='val_loss', patience=5, restore_best=False,
                 minimize=True):
        """
        Initializes a new early stopping callback.

        Parameters:
        -----------
        - metric: str, default: 'val_loss'
            The metric to watch during training.
        - patience: int, default: 5
            The number of epochs that training still continues although the
            watched metric is greater than its smallest value during training.
        - restore_best: bool, default: False
            Whether the model's parameter should be set to the parameters which
            showed the best performance in terms of the watched metric.
        - minimize: bool, default: True
            Whether to minimize or maximize the given metric.
        """
        self.patience = patience
        self.epoch = None
        self.counter = None
        self.best_metric = None
        self.model = None
        self.state_dict = None
        self.restore_best = restore_best
        self.metric = metric
        self.minimize = minimize

    # MARK: Instance Methods
    def before_training(self, model, num_epochs):
        self.model = model
        if self.restore_best:
            self.state_dict = copy.deepcopy(model.state_dict())
        self.epoch = 0
        self.counter = 0
        self.best_metric = float('inf') if self.minimize else -float('inf')

    def after_epoch(self, metrics):
        self.epoch += 1
        if self._is_metric_better(metrics):
            if self.restore_best:
                self.state_dict = copy.deepcopy(self.model.state_dict())
            self.counter = 0
            self.best_metric = metrics[self.metric]
        else:
            self.counter += 1
            if self.counter == self.patience:
                raise CallbackException(
                    f"Early stopping after epoch {self.epoch} (patience {self.patience})."
                )

    def after_training(self):
        if self.restore_best and self.counter > 0:
            self.model.load_state_dict(self.state_dict)

    # MARK: Private Methods
    def _is_metric_better(self, metrics):
        if self.minimize:
            return metrics[self.metric] < self.best_metric
        else:
            return metrics[self.metric] > self.best_metric
