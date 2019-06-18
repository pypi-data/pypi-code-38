#
#  utils/stdio.py
#  bxtorch
#
#  Created by Oliver Borchert on May 11, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
import sys
import time
import datetime
import numpy as np

_ERASE_LINE = '\x1b[2K'

class ProgressBar:
    """
    The progress bar can be used to print progress for a specific task where
    N work items have to be processed. The progress bar also measures the
    execution time and provides an estimated remaining time for the  operation.

    A common use case for the progress bar are for-loops where one work item is
    completed per iteration. The progress bar is intended to be used either 
    from within a with statement or a for-loop.
    """

    # MARK: Static Methods
    @staticmethod
    def frac(num, denom):
        """
        Initializes a new progress bar with ceil(num/denom) work items.

        Parameters:
        -----------
        - num: int
            Numerator of the fraction.
        - denom: int
            Denominator of the fraction.

        Returns:
        --------
        - bxtorch.utils.ProgressBar
            The progress bar.
        """
        return ProgressBar(int(np.ceil(num / denom)))

    # MARK: Initialization
    def __init__(self, total, file=None):
        """
        Initializes a new progress bar with the given number of work items.

        Parameters:
        -----------
        - total: int
            The number of work items to be processed.
        - file: str, default: None
            If given, defines the file where the progress bar should write to
            instead of the command line. Intermediate directories are created
            automatically.
        """
        self.current = 0
        self.total = total
        self.tic = None
        self._counter = None
        if file is not None:
            os.makedirs(file, exist_ok=True)
            self.stream = open(file, 'a+')
        else:
            self.stream = sys.stdout

    # MARK: Instance Methods
    def start(self):
        """
        Starts to record the progress of the operation. Time measuring is
        initiated and the beginning of the operation is indicated on the
        command line.

        This method should never be called explicitly. It is implicitly called
        at the beginning of a with statement.
        """
        self.tic = time.time()
        self._print_progress(compute_eta=False)

    def step(self):
        """
        Tells the progress bar that one work item has been processed. The 
        command line output is updated as well as the estimated finishing time
        of the operation.

        If used from within a with statement, this method must be called
        explicitly, otherwise, it should not be called.
        """
        self.current += 1
        self._print_progress()

    def finish(self, metrics={}):
        """
        Stops the progress bar and prints the total duration of the operation.
        If metrics are given, these will be printed along with the duration.

        If metrics are given, this method must be called explicitly, otherwise,
        it is implicitly called at the end of a with statement or for loop.
        
        Note:
        -----
        Do not call this method multiple times.

        Parameters:
        -----------
        - metrics: dict, default: {}
            The metrics to print as key-value pairs. Usually, they provide more
            information about the operation whose progress has been tracked.
        """
        toc = time.time()
        self._print_done(metrics)
        self.tic = None

    # MARK: Special Methods
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tic is not None:
            self.finish()
        return False

    def __iter__(self):
        return self

    def __next__(self):
        if self._counter is None:
            self.start()
            self._counter = 0
            return self._counter
        elif self._counter < self.total - 1:
            self.step()
            self._counter += 1
            return self._counter
        else:
            self.finish()
            raise StopIteration

    # MARK: Private Methods
    def _print_progress(self, compute_eta=True):
        perc = self.current / self.total
        p = int(np.round(perc * 30))
        progress = "" if p == 0 else "=" * (p - 1) + ">" if p < 30 else "=" * 30
        whitespace = " " * (30 - p)
        elapsed = time.time() - self.tic
        elapsed_time = datetime.timedelta(0, int(elapsed))
        if compute_eta:
            eta = datetime.timedelta(0, int((1 - perc) / perc * elapsed))
        else:
            eta = 'n/a'
        print(
            "{} [{}{}] ({:02.1%}) ETA {} [Elapsed {}]".format(
                _ERASE_LINE, progress, whitespace, perc, eta, elapsed_time
            ),
            end='\r',
            file=self.stream
        )
        self.stream.flush()

    def _print_done(self, metrics):
        elapsed = datetime.timedelta(0, int(time.time() - self.tic))
        m_strings = []
        for k, v in sorted(metrics.items(), key=lambda k:k[0]):
            split = k.split('__')
            if len(split) > 1:
                f = split[1]
            else:
                f = '{:.5f}'
            string = f'{split[0]}: {f}'.format(v)
            m_strings += [string]
        print_text = " [Elapsed {}] {}".format(elapsed, ", ".join(m_strings))
        print(f"{_ERASE_LINE}{print_text}", file=self.stream)
        self.stream.flush()

    # MARK: Special Methods
    def __del__(self):
        if self.stream != sys.stdout:
            self.stream.close()


def ensure_valid_directories(file):
    """
    Creates intermediate directories to ensure that files can be saved to their
    specified directory.

    Parameters:
    -----------
    - file: str
        The absolute path to the file whose directory structure to ensure.
    """
    dir = "/".join(file.split('/')[:-1])
    os.makedirs(dir, exist_ok=True)
