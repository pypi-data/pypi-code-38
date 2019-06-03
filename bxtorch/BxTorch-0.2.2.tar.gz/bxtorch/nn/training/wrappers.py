#
#  nn/training/wrappers.py
#  bxtorch
#
#  Created by Oliver Borchert on May 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np
import matplotlib.pyplot as plt

class History:
    """
    This class summarizes metrics obtained during training of a model.
    """

    # MARK: Static Methods
    @staticmethod
    def cat(hist1, hist2):
        """
        Concatenates the two history objects.

        Parameters:
        -----------
        - hist1: bxtorch.nn.History
            The first history.
        - hist2: bxtorch.nn.History
            The second history.

        Returns:
        --------
        - bxtorch.nn.History
            The concatenated history object.
        """
        return History(hist1._metrics + hist2._metrics)
    
    # MARK: Initialization
    def __init__(self, metrics):
        """
        Initializes a new history object.

        Parameters:
        -----------
        - metrics: list of dict
            The metrics from each training step.
        """
        self._metrics = metrics

    # MARK: Instance Methods
    def plot(self, only=None, save_to=None):
        """
        Plots the history via matplotlib. If running in a Jupyter notebook, this
        call should be followed by a call to ``plt.show()``. For all metrics
        ``<metric>``, the function combines ``val_<metric>`` and
        ``train_<metric>`` (if available) into plots, yet uses different
        subplots for different metrics.

        Parameters:
        -----------
        - only: list of str, default: None
            If this value is defined, the history is only visualized for the
            given metrics. 
        - save_to: str, default: None
            If given, the generated plot is saved to the given file.
        """
        x = np.arange(len(self))
        raise NotImplementedError

    # MARK: Special Methods
    def __getstate__(self):
        return self._metrics

    def __setstate__(self, state):
        self._metrics = state

    def __len__(self):
        return len(self._metrics)

    def __getattr__(self, name):
        if len(self._metrics) == 0:
            raise AttributeError(
                f'Length of history is 0. Metric {name} cannot be accessed.'
            )
        if name in self._metrics[0]:
            return [m[name] for m in self._metrics]
        else:
            raise AttributeError(f'Metric {name} does not exist.')
            

class Evaluation:
    """
    This class summarizes metrics obtained when evaluating a model.
    """

    # MARK: Static Methods
    @staticmethod
    def merge(eval1, eval2, *eval_other):
        """
        Merges multiple evaluations into one.

        Parameters:
        -----------
        - eval1: torch.nn.training.wrappers.Evaluation
            The first evaluation.
        - eval2: torch.nn.training.wrappers.Evaluation
            The second evaluation.
        - eval_other: varargs of torch.nn.training.wrappers.Evaluation
            Additional evaluations.

        Returns:
        --------
        - torch.nn.training.wrappers.Evaluation
            The merged evaluation.
        """
        result = Evaluation({})
        metrics = {}
        for e in [eval1, eval2] + list(eval_other):
            for k, v in e._metrics.items():
                metrics[k] = v
        result._metrics = metrics
        return result

    # MARK: Initialization
    def __init__(self, metrics, weights=None):
        """
        Initializes a new evaluation wrapper from the given metrics.

        Parameters:
        -----------
        - metrics: dict of str -> list of float
            The metrics computed. The keys define the metric names, the values
            provide the metrics computed over all batches.
        - weights: list of int, default: None
            The length of the batches. Should be supplied if the batches for
            which the metrics have been computed have differing sizes. If so,
            this list must contain the sizes of all batches.
        """
        result = {}
        for metric, values in metrics.items():
            if weights is None or len(weights) == 0:
                average = np.mean(values)
            else:
                weights = np.array(weights)
                values = np.array(values)
                average = weights.dot(values) / np.sum(weights)
            result[metric] = average
        self._metrics = result

    # MARK: Instance Methods
    def to_dict(self):
        """
        Returns the evaluation object as plain dictionary.

        Returns:
        --------
        - dict
            The dictionary.
        """
        return {k: v for k,v in self._metrics.items() if not k.startswith('_')}

    def with_prefix(self, prefix):
        """
        Initializes a new evaluation wrapper where all metrics are prefixed
        with the given prefix. Useful when merging evaluations.

        Parameters:
        -----------
        - prefix: str
            The prefix to use.

        Returns:
        --------
        - torch.nn.training.wrappers.Evaluation
            The resulting evaluation.
        """
        result = Evaluation({})
        result._metrics = {f'{prefix}{k}': v for k, v in self._metrics.items()}
        return result

    # MARK: Special Methods
    def __getstate__(self):
        return self._metrics

    def __setstate__(self, state):
        self._metrics = state

    def __contains__(self, item):
        return item in self._metrics

    def __getitem__(self, item):
        return self._metrics[item]

    def __getattr__(self, name):
        try:
            return self._metrics[name]
        except KeyError:
            class_name = self.__class__.__name__
            raise AttributeError(
                f'{class_name} does not provide metric {name}.'
            )
