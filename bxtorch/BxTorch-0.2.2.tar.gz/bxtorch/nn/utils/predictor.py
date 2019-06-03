#
#  nn/utils/predictor.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import numpy as np
import torch
import torch.nn as nn
import torch.multiprocessing as mp
from torch.utils.data import DataLoader
from bxtorch.utils.torch import gpu_device, to_device

class Predictor:
    """
    Given a model, the predictor can be used to easily compute predictions for
    a model. It can be seen as binding between raw data and model by using
    a dataset and enabling parallelism.
    """

    # MARK: Initialization
    def __init__(self, model, dataset_class, **dataset_kwargs):
        """
        Initializes a new predictor with the given parameters.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model to make predictions with.
        - dataset_class: type like torch.utils.data.Dataset
            The dataset class to use to make predictions. It must accept as
            first parameter a list of raw elements for prediction.
        - dataset_kwargs: keyword arguments
            Arguments passed to the dataset upon initialization.
        """
        self.model = model
        self.dataset_class = dataset_class
        self.dataset_kwargs = dataset_kwargs

    # MARK: Instance Methods
    def predict(self, samples, callbacks=[], gpu=False, **kwargs):
        """
        Computes predictions for the given samples.

        Parameters:
        -----------
        - samples: list of object
            The samples to make predictions for, fed directly to the dataset
            initializer as first parameters.
        - callbacks: list of bxtorch.nn.PredictionCallback
            Callbacks which are called as prediction progresses.
        - gpu: bool or int or list of int, default: False
            Whether to use a (specific) GPU or multiple GPUs. If multiple GPUs
            are used, one process per GPU is started to minimize
            synchronization. Make sure that using multiple GPUs makes up for
            this overhead.
        - kwargs: keyword arguments
            Additional arguments fed directly to the data loader. Includes e.g.
            ``batch_size``.

        Returns:
        --------
        - numpy.ndarray
            The predictions made by the model.
        """
        dataset = self.dataset_class(samples, **self.dataset_kwargs)

        if hasattr(dataset, 'loader'):
            loader = dataset.loader(**kwargs)
        else:
            if isinstance(gpu, list):
                kwargs['pin_memory'] = True
            kwargs['shuffle'] = False
            loader = DataLoader(dataset, **kwargs)

        num_iterations = len(loader)

        self._exec_callbacks(
            callbacks, 'before_predictions', self.model, num_iterations
        )

        if isinstance(gpu, list):
            parallel = True
            num_gpus = len(gpu)

            self.model.share_memory()
            push_queue = mp.Queue()
            pull_queue = mp.Queue()

            processes = []
            for i in range(num_gpus):
                process = mp.Process(
                    target=_worker_function,
                    args=(self.model, gpu[i], push_queue, pull_queue,
                          self._process_prediction)
                )
                process.daemon = True
                process.start()
                processes.append(process)
        else:
            parallel = False
            device = gpu_device(gpu)
            self.model.to(device)

        predictions = []
        self.model.eval()

        if parallel:
            remain_count = 0
            idx = 0

            try:
                iterator = iter(loader)

                # Provide data for twice the number of processes as lookahead 
                # to minimize time lost for synchronization
                for _ in range(num_gpus):
                    push_queue.cancel_join_thread()
                    push_queue.put((idx, next(iterator)))
                    remain_count += 1
                    idx += 1

                while True:
                    item = pull_queue.get()
                    remain_count -= 1
                    predictions.append(item)
                    self._exec_callbacks(callbacks, 'after_batch')
                    push_queue.cancel_join_thread()
                    push_queue.put((idx, next(iterator)))
                    remain_count += 1
                    idx += 1

            except StopIteration:
                for _ in range(remain_count):
                    item = pull_queue.get()
                    predictions.append(item)
                    self._exec_callbacks(callbacks, 'after_batch')
                pull_queue.close()

                for _ in range(num_gpus):
                    push_queue.cancel_join_thread()
                    push_queue.put(None)
                push_queue.close()

                for p in processes:
                    p.join()

                predictions = [
                    p[1] for p in sorted(predictions, key=lambda p:p[0])
                ]

        else:
            for x in loader:
                x = to_device(device, x)
                with torch.no_grad():
                    if isinstance(x, (list, tuple)):
                        out = self.model(*x)
                    else:
                        out = self.model(x)
                predictions.append(
                    to_device('cpu', self._process_prediction(x, out))
                )
                self._exec_callbacks(
                    callbacks, 'after_batch'
                )

        self._exec_callbacks(
            callbacks, 'after_predictions'
        )

        return self._collate_predictions(predictions)

    # MARK: Private Methods
    def _process_prediction(self, x, out):
        return out

    def _collate_predictions(self, out):
        return np.concatenate([p.numpy() for p in out])

    def _exec_callbacks(self, callbacks, func, *args):
        for callback in callbacks:
            getattr(callback, func)(*args)


def _worker_function(model, gpu, pull_queue, push_queue, process):
    device = gpu_device(gpu)
    model.to(device)

    while True:
        item = pull_queue.get()
        if item is None:
            return

        idx, x = item
        
        x = to_device(device, x)
        with torch.no_grad():
            if isinstance(x, (list, tuple)):
                out = model(*x)
            else:
                out = model(x)

        push_queue.cancel_join_thread()
        push_queue.put((idx, process(x, out)))
