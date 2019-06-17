#
#  nn/training/parallel.py
#  bxtorch
#
#  Created by Oliver Borchert on May 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
import copy
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

        # 2) Prepare training on multiple processes
        history_queue = mp.Queue()
        devices = [gpu_device(g) for g in gpu] if isinstance(gpu, list) else \
            [gpu_device(gpu)]
        device_idx = 0

        processes = []
        push_queues = []
        pull_queues = []
        done = mp.Event()

        # 2.1) Ensure that training works correctly either on GPU or CPU
        if devices[0].type == 'cuda':
            # If one or more GPUs are used for training, we need to ensure that
            # one model is kept in shared memory. The trainer in each process
            # then moves the process's model to the GPU (we cannot share
            # models on a GPU, especially not on multiple GPUs).
            # The idea is to keep one model in shared memory which will be
            # updated independently by each process.
            shared_model = copy.deepcopy(self.trainer.model)
            shared_model.share_memory()
        else:
            self.trainer.model.share_memory()
            shared_model = None

        # 3) Launch processes
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
                args=(h_queue, push_queue, pull_queue, 
                      done if i == 0 else None, self.trainer,
                      shared_model, device, kw)
            )
            process.start()

            device_idx = (device_idx + 1) % len(devices)
            processes.append(process)
            push_queues.append(push_queue)
            pull_queues.append(pull_queue)

        # 4) Perform training based on synchronization calls
        continue_training = True
        while continue_training:
            for q in push_queues:
                q.cancel_join_thread()
                q.put(True)

            for q in pull_queues:
                continue_training = continue_training and q.get()

        # 5) Finish training
        history = history_queue.get()
        history_queue.close()
        done.set()

        for q in push_queues:
            q.cancel_join_thread()
            q.put(False)
            q.close()

        # 6) Graceful shutdown
        for q in pull_queues:
            q.close()

        for p in processes:
            p.join(1) # prevent any strange locks

        return history


def _hogwild_train(history_queue, push_queue, pull_queue, done, 
                   trainer, shared_model, device, kwargs):
    # Clear GPU, setting, we will set this manually
    kwargs = {
        **trainer.parallel_restore(**kwargs),
        'gpu': None
    }
    # The synchronization callback ensures that workers are synchronized after
    # every epoch. This way, we can easily we can ensure that the evaluation
    # is carried out correctly. The synchronization callback must be the first
    # callback to ensure that training on multiple GPUs works.
    kwargs['callbacks'] = [
        xnn.SynchronizationCallback(push_queue, pull_queue)
    ] + kwargs.get('callbacks', [])

    # If we are training on a GPU, model sharing is a bit more complex.
    # ``shared_model`` needs to be updated manually after every epoch,
    # ensured by the ``ModelSharingCallback``.
    if device.type == 'cuda':
        # Ensure that all callbacks are executed after the model sharing
        # callback. This way, callbacks such as the early stopping callback
        # do still work as expected. However, it must still be executed after
        # the synchronization callback to load the latest weights before the
        # beginning of an epoch.
        kwargs['callbacks'] = kwargs['callbacks'][:1] + [
            xnn.ModelSharingCallback(shared_model)
        ] + kwargs['callbacks'][1:]

    # Now, perform training...
    trainer.device = device
    trainer.model.to(device)
    history = trainer.train(**kwargs)
    trainer.model.to('cpu')
    trainer.device = None

    # Return history if this is the "main" process
    if history_queue is not None:
        history_queue.cancel_join_thread()
        history_queue.put(history)
        done.wait()
