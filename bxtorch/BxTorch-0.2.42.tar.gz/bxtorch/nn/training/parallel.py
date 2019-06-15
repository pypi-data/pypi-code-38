#
#  nn/training/parallel.py
#  bxtorch
#
#  Created by Oliver Borchert on May 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
import torch.nn as nn
import torch.multiprocessing as mp
import bxtorch.nn as xnn
from .wrappers import History
from bxtorch.utils.torch import gpu_device

class Hogwild:
    """
    The Hogwild class enables using the Hogwild training procedure when training
    a model. Only use this class if your epochs take reasonably long (e.g. a few
    minutes) and you require multiple epochs for training (e.g. > 10).
    Otherwise, speedups might be very marginal but computational costs greatly
    increased.

    Generally, it works as follows:

    1. For each epoch, a certain number of processes is started. These processes
        each train for a single epoch while updating the weights of the same
        model. Callbacks are only passed to the first process that has been
        started.
    2. Evaluation is only performed on the first of the processes. If the others
        have already finished while evaluating, they have to wait.
    3. If training continues, each process gets notified that training
        continues.
    """

    def __init__(self, trainer):
        """
        Initializes a new Hogwild context.

        Parameters:
        -----------
        - trainer: bxtorch.nn.BaseTrainer
            A trainer whose train function to use.
        """
        self.trainer = trainer

    def train(self, num_processes=None, gpu=False, **kwargs):
        """
        Trains the passed trainer's model using Hogwild.

        Parameters:
        -----------
        - gpu: bool or int or list of int, default: False
            The GPU(s) to use for training. If multiple GPUs are specified, they
            are distributed among the processes. Generally, you shouldn't have
            more processes than GPUs.
        - num_processes: int, default: None
            The number of processes to use for Hogwild. If set to None or 0, it
            defaults to the number of processors.
        - kwargs: keyword arguments
            Arguments as passed directly to a trainer's ``train`` method.
            Subclasses of the base trainer may, however, require some
            parameters specified differently.

        Returns:
        --------
        - bxtorch.nn.History
            The history of the training for the first process.
        """
        start = mp.get_context().get_start_method()
        assert start == 'spawn' or start == 'forkserver', \
            "Multiprocessing will break if you do not use spawning to " + \
            f"create new processes. Currently, you are using '{start}'. " + \
            "Use the following command to fix this issue:\n" + \
            "torch.multiprocessing.set_start_method('spawn')."

        # 1) Prepare for Hogwild
        num_processes = num_processes or os.cpu_count()
        self.trainer.model.share_memory()

        # 2) Prepare training on multiple processes
        history_queue = mp.Queue()
        devices = [gpu_device(g) for g in gpu] if isinstance(gpu, list) else \
            [gpu_device(gpu)]
        device_idx = 0

        processes = []
        push_queues = []
        pull_queues = []
        for i in range(num_processes):
            h_queue = history_queue if i == 0 else None
            push_queue = mp.Queue()
            pull_queue = mp.Queue()

            kw = self.trainer.parallel_prepare(**kwargs)
            if i != 0:
                replace = {
                    'callbacks': [],
                    'val_data': None,
                    'val_data_init': None,
                    'eval_train': False
                }
                for k, v in replace.items():
                    if v is None and k in kw:
                        del kw[k]
                    else:
                        kw[k] = v

            device = devices[device_idx]
            process = mp.Process(
                target=_hogwild_train,
                args=(h_queue, push_queue, pull_queue, self.trainer, device, kw)
            )
            process.start()

            device_idx = (device_idx + 1) % len(devices)
            processes.append(process)
            push_queues.append(push_queue)
            pull_queues.append(pull_queue)

        # 3) Perform training based on synchronization calls
        continue_training = True
        while continue_training:
            for q in push_queues:
                q.cancel_join_thread()
                q.put(True)

            for q in pull_queues:
                continue_training = continue_training and q.get()

        # 4) Finish training
        history = history_queue.get()
        history_queue.close()

        for q in push_queues:
            q.cancel_join_thread()
            q.put(False)
            q.close()

        # 5) Graceful shutdown
        for q in pull_queues:
            q.close()

        for p in processes:
            p.join()

        return history


def _hogwild_train(history_queue, push_queue, pull_queue, trainer, device, 
                   kwargs):
    kwargs = {
        **trainer.parallel_restore(**kwargs),
        'gpu': None
    }
    kwargs['callbacks'] = kwargs['callbacks'] + [
        xnn.SynchronizationCallback(push_queue, pull_queue)
    ]

    # Train
    trainer.device = device
    trainer.model.to(device)
    history = trainer.train(**kwargs)
    trainer.model.to('cpu')
    trainer.device = None

    # Return history
    if history_queue is not None:
        history_queue.cancel_join_thread()
        history_queue.put(history)
