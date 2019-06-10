# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs."""
from typing import Optional, Union, TextIO
import os

WIDTH_ITERATION = 10
WIDTH_PIPELINE = 48
WIDTH_SAMPLING = 13
WIDTH_DURATION = 10
WIDTH_METRIC = 10
WIDTH_BEST = 10


class Column:
    """Constants for column names."""

    ITERATION = 'ITERATION'
    PIPELINE = 'PIPELINE'
    SAMPLING = 'SAMPLING %'
    DURATION = 'DURATION'
    METRIC = 'METRIC'
    BEST = 'BEST'


class ConsoleInterface:
    """Class responsible for printing iteration information to console."""

    def __init__(self, metric: str, file_handler: Optional[TextIO] = None, mask_sampling: bool = False) -> None:
        """
        Initialize the object.

        :param metric: str representing which metric is being used to score the pipeline.
        :param file_handler: file-like object to output to. If not provided, output will be discarded.
        :param mask_sampling: bool decide whether the sample columns should be masked or not.
        """
        self.metric = metric
        self.metric_pretty = metric
        self.mask_sampling = mask_sampling

        if file_handler is None:
            # Prevent file handle resource leak
            import atexit
            devnull = open(os.devnull, 'w')
            atexit.register(devnull.close)
            self.file_handler = devnull
        else:
            self.file_handler = file_handler

        self.columns = [
            Column.ITERATION,
            Column.PIPELINE,
            Column.SAMPLING,
            Column.DURATION,
            Column.METRIC,
            Column.BEST,
        ]

        self.descriptions = [
            'The iteration being evaluated.',
            'A summary description of the pipeline being evaluated.',
            'Percent of the training data to sample.',
            'Time taken for the current iteration.',  # 'Error or warning message for the current iteration.',
            'The result of computing %s on the fitted pipeline.' % (self.metric_pretty,),
            'The best observed %s thus far.' % self.metric_pretty,
        ]

        self.widths = [
            WIDTH_ITERATION,
            WIDTH_PIPELINE,
            WIDTH_SAMPLING,
            WIDTH_DURATION,
            WIDTH_METRIC,
            WIDTH_BEST
        ]

        if mask_sampling:
            del self.columns[2]
            del self.descriptions[2]
            del self.widths[2]

        self.sep_width = 3
        self.filler = ' '
        self.total_width = sum(self.widths) + (self.sep_width * (len(self.widths) - 1))

    def _format_float(self, v: Union[float, str]) -> str:
        """
        Format float as a string.

        :param v:
        :return:
        """
        if isinstance(v, float):
            return '{:.4f}'.format(v)
        return v

    def _format_int(self, v: Union[int, str]) -> str:
        """
        Format int as a string.

        :param v:
        :return:
        """
        if isinstance(v, int):
            return '%d' % v
        return v

    def print_descriptions(self) -> None:
        """
        Print description of AutoML console output.

        :return:
        """
        self.file_handler.write('\n')
        self.file_handler.write(('*' * self.total_width) + '\n')
        for column, description in zip(self.columns, self.descriptions):
            self.file_handler.write(column + ': ' + description + '\n')
        self.file_handler.write(('*' * self.total_width) + '\n')
        self.file_handler.write('\n')

    def print_columns(self) -> None:
        """
        Print column headers for AutoML printing block.

        :return:
        """
        self.print_start(Column.ITERATION)
        self.print_pipeline(Column.PIPELINE, '', Column.SAMPLING)
        self.print_end(Column.DURATION, Column.METRIC, Column.BEST)

    def print_start(self, iteration: Union[int, str] = '') -> None:
        """
        Print iteration number.

        :param iteration:
        :return:
        """
        iteration = self._format_int(iteration)

        s = iteration.rjust(self.widths[0], self.filler)[-self.widths[0]:] + self.filler * self.sep_width
        self.file_handler.write(s)
        self.file_handler.flush()

    def print_pipeline(self, preprocessor: Optional[str] = '',
                       model_name: Optional[str] = '', train_frac: Union[str, float] = 1) -> None:
        """
        Format a sklearn Pipeline string to be readable.

        :param preprocessor: string of preprocessor name
        :param model_name: string of model name
        :param train_frac: float of fraction of train data to use
        :return:
        """
        separator = ' '
        if preprocessor is None:
            preprocessor = ''
            separator = ''
        if model_name is None:
            model_name = ''
        combined = preprocessor + separator + model_name
        self.file_handler.write(combined.ljust(self.widths[1], self.filler)[:(self.widths[1] - 1)])

        if not self.mask_sampling:
            try:
                train_frac = float(train_frac)
            except ValueError:
                pass
            sampling_percent = None  # type: Optional[Union[str,float]]
            sampling_percent = train_frac if isinstance(train_frac, str) else train_frac * 100
            sampling_percent = str(self._format_float(sampling_percent))
            self.file_handler.write(sampling_percent.ljust(self.widths[2], self.filler)[:(self.widths[2] - 1)])
        self.file_handler.flush()

    def print_end(self, duration: Union[float, str] = "", metric: Union[float, str] = "",
                  best_metric: Union[float, str] = "") -> None:
        """
        Print iteration status, metric, and running best metric.

        :param duration: Status of the given iteration
        :param metric: Score for this iteration
        :param best_metric: Best score so far
        :return:
        """
        metric, best_metric = tuple(map(self._format_float, (metric, best_metric)))
        duration, metric, best_metric = tuple(map(str, (duration, metric, best_metric)))

        i = 2 if self.mask_sampling else 3
        s = duration.ljust(self.widths[i], self.filler)
        s += metric.rjust(self.widths[i + 1], self.filler)
        s += best_metric.rjust(self.widths[i + 2], self.filler)
        self.file_handler.write(s + '\n')
        self.file_handler.flush()

    def print_error(self, message: Union[BaseException, str]) -> None:
        """
        Print an error message to the console.

        :param message: Error message to display to user
        :return:
        """
        self.file_handler.write('ERROR: ')
        self.file_handler.write(str(message).ljust(self.widths[1], self.filler) + '\n')
        self.file_handler.flush()

    def print_line(self, message: str) -> None:
        """Print a message (and then a newline) on the console."""
        self.file_handler.write(message + '\n')
        self.file_handler.flush()
