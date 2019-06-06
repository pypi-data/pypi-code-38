from abc import ABCMeta
from collections import namedtuple

import numpy as np
import pandas as pd
from tabulate import tabulate


MetricPoint = namedtuple("MetricPoint", "key value mode epoch")


class MetricMixin(metaclass=ABCMeta):
    """
    Mixin to add standardized support for logging performance during training/evaluation.

    """
    def __init__(self):
        self.metrics = []

    def add_metric(self, key, value, mode, epoch):
        self.metrics.append(MetricPoint(key, value, mode, epoch))

    def log_epoch_stats(self, epoch):
        """
        Log a formatted version of the stats for this epoch, across all modes
        """
        epoch_metrics = [metric for metric in self.metrics if metric.epoch == epoch]
        self._format_metrics(epoch_metrics)

    def get_best_metric(self, key, mode, best_fn):
        filtered_metrics = [
            metric
            for metric in self.metrics
            if metric.key == key and metric.mode == mode
        ]
        return best_fn(filtered_metrics, key=lambda metric: metric.value)

    def log_best_stats(self, key, mode, best_fn=max):
        """
        Log the best epoch stats given the desired key & mode
        """
        # Get the best metric
        best_metric = self.get_best_metric(key, mode, best_fn)

        print(f"Best Epoch ({key}, {mode}) = {best_metric.epoch}")  # noqa: N123

        epoch_metrics = [
            metric
            for metric in self.metrics
            if metric.epoch == best_metric.epoch
        ]
        self._format_metrics(epoch_metrics)

    def _format_metrics(self, metrics):
        rows = {metric.key for metric in metrics}
        cols = {metric.mode for metric in metrics}

        # Sort the sets to guarantee alphanumeric output
        rows = sorted(list(rows))
        cols = sorted(list(cols))

        # Format each row based on the key/mode configuration
        grid = np.empty((len(rows), len(cols)), dtype=float)

        for metric in metrics:
            grid[rows.index(metric.key)][cols.index(metric.mode)] = metric.value

        df = pd.DataFrame(grid, index=rows, columns=cols)

        print(tabulate(df, headers="keys"))  # noqa: N123
