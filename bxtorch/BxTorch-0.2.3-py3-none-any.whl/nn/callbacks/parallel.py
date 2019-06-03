#
#  nn/callbacks/parallel.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
from .base import TrainingCallback, CallbackException

class SynchronizationCallback(TrainingCallback):
    """
    Synchronizer callback which can be used within a parallel environment to
    stop and resume training at specific points.
    """

    # MARK: Initialization
    def __init__(self, push_queue, pull_queue):
        """
        Initializes a new synchronizer.

        Parameters:
        -----------
        - push_queue: torch.multiprocessing.Queue
            The queue onto which the parallel environment pushes whether the
            current epoch should be trained. If ``False`` is passed, training
            is stopped.
        - pull_queue: torch.multiprocessing.Queue
            The queue onto which the callback pushes ``True`` to indicate that 
            the epoch is finished. Upon end of training, it pushes ``False``.
        """
        self.push_queue = push_queue
        self.pull_queue = pull_queue

    # MARK: Instance Methods
    def before_epoch(self, current, num_iterations):
        cont = self.push_queue.get()
        if not cont:
            raise CallbackException(
                f'Process {os.getpid()} is told to finish training.'
            )

    def after_epoch(self, metrics):
        self.pull_queue.cancel_join_thread()
        self.pull_queue.put(True)

    def after_training(self):
        self.pull_queue.cancel_join_thread()
        self.pull_queue.put(False)
