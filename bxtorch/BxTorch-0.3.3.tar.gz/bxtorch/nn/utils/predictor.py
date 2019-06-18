#
#  nn/utils/predictor.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
import numpy as np
import torch
import torch.nn as nn
import torch.multiprocessing as mp
from torch.utils.data import DataLoader, Dataset
from bxtorch.utils.torch import gpu_device, to_device
import bxtorch.multiprocessing as xmp

class Predictor:
    """
    Given a model, the predictor can be used to easily compute predictions for
    a model. It can be seen as binding between raw data and model by using
    a dataset and enabling parallelism.
    """

    # MARK: Initialization
    def __init__(self, model, dataset_class=None, **dataset_kwargs):
        """
        Initializes a new predictor with the given parameters.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model to make predictions with.
        - dataset_class: type like torch.utils.data.Dataset, default: None
            The dataset class to use to make predictions. It must accept as
            first parameter a list of raw elements for prediction. In case no
            class is defined, the ``predict`` function expects to receive a
            dataset instead of raw elements.
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
            If a list of objects is given, the samples to make predictions for
            are fed directly to the dataset initializer as first parameters. If
            a dataset is given, the dataset will be used to make predictions.
        - callbacks: list of bxtorch.nn.PredictionCallback
            Callbacks which are called as prediction progresses.
        - gpu: bool or int or list of int, default: False
            Whether to use a (specific) GPU or multiple GPUs. If multiple GPUs
            are used, one process per GPU is started to minimize
            synchronization. Make sure that using multiple GPUs makes up for
            this overhead. If ``False`` is specified, all cores of the 
            computer are used to make predictions in parallel.
        - kwargs: keyword arguments
            Additional arguments fed directly to the data loader. Includes e.g.
            ``batch_size``.

        Returns:
        --------
        - numpy.ndarray
            The predictions made by the model.
        """
        if isinstance(samples, Dataset):
            dataset = samples
        else:
            dataset = self.dataset_class(samples, **self.dataset_kwargs)

        if hasattr(dataset, 'loader'):
            loader = dataset.loader(**kwargs)
        else:
            if isinstance(gpu, list) or gpu != False:
                kwargs['pin_memory'] = True
            kwargs['shuffle'] = False
            loader = DataLoader(dataset, **kwargs)

        num_iterations = len(loader)

        self._exec_callbacks(
            callbacks, 'before_predictions', self.model, num_iterations
        )

        self.model.eval()

        if isinstance(gpu, list) or gpu == False: # parallel computation
            if isinstance(gpu, list):
                num_workers = len(gpu)
            elif isinstance(gpu, bool):
                num_workers = os.cpu_count()
            else:
                num_workers = 1

            self.model.share_memory()

            callback = lambda:self._exec_callbacks(callbacks, 'after_batch')
            vectorizer = xmp.Vectorizer(
                _worker_func, _worker_init, callback_func=callback,
                num_workers=num_workers, gpu=gpu, model=self.model
            )

            predictions = vectorizer.process(
                loader, self.model, self._process_prediction
            )
        else: # sequential computation
            device = gpu_device(gpu)
            self.model.to(device)

            predictions = []

            for x in loader:
                out = _worker_func(
                    x, self.model, self._process_prediction, device
                )
                predictions.append(out)
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


def _worker_func(item, model, process, device):
    x = to_device(device, item)
    with torch.no_grad():
        if isinstance(x, (list, tuple)):
            out = model(*x)
        elif isinstance(x, dict):
            out = model(**x)
        else:
            out = model(x)
    return to_device('cpu', process(x, out))


def _worker_init(rank, gpu, model):
    if isinstance(gpu, list):
        device = gpu_device(gpu[rank])
    else:
        device = gpu_device(gpu)
    model.to(device)
    return device
