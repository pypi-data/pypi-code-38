#
#  nn/training/trainer.py
#  bxtorch
#
#  Created by Oliver Borchert on May 09, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import copy
from abc import ABC, abstractmethod
import time
import functools
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from bxtorch.nn.callbacks import CallbackException, TrainingCallback, \
    PredictionCallback
import bxtorch.nn.utils as xnnu
from .wrappers import History, Evaluation
from bxtorch.utils.torch import gpu_device, to_device
from bxtorch.nn.data import InfiniteDataLoader, InfiniteDataset
from bxtorch.nn.callbacks.base import TrainingCallback, PredictionCallback

class BaseTrainer(TrainingCallback, PredictionCallback, ABC):
    """
    A base class for training and evaluating models. Generally, this class
    should be seen as "binding" between a model and some data. Models should
    always be wrapped in a trainer, both when being trained, and when performing
    inference (i.e. evaluation). The trainer ensures that the model's 
    environment is correct and prevents plenty of pitfalls.

    A concrete implementation of this class is tailored to a specific type of 
    data (e.g. independent, identically distributed data samples) and/or model
    types (e.g. GANs).
    """

    # MARK: Initialization
    def __init__(self, model):
        """
        Initializes a new trainer for a specified model.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model to train or evaluate.
        """
        self.model = model
        self.device = None
        self._cache = {}
        self._iteration = None

    # MARK: Instance Methods
    def optimizer(self, optimizer='adam', **kwargs):
        """
        Convenience function to create an optimizer for the model from a string.

        Parameters:
        -----------
        - optimizer: str, default: 'adam'
            The optimizer to use. Acceptable values are all optimizers from
            torch.optim (upper and lowercase does not matter).
        - kwargs: keyword arguments
            Arguments passed to the optimizer during initalization.
        """
        valid_optimizers = [
            'ASGD', 'Adadelta', 'Adagrad', 'Adam', 'Adamax', 'LBFGS',
            'RMSprop', 'Rprop', 'SGD', 'SparseAdam'
        ]
        for opt in valid_optimizers:
            if opt.lower() == optimizer.lower():
                return getattr(optim, opt)(self.model.parameters(), **kwargs)
        raise ValueError(f'Invalid optimizer {optimizer}.')

    def train(self, train_data, val_data=None, epochs=20, val_iterations=None,
              eval_every=1, eval_train=False, callbacks=[], metrics={},
              gpu=False, **kwargs):
        """
        Method for training the model with the supplied parameters.

        Parameters:
        -----------
        - train_data: torch.DataLoader or bxtorch.nn.InfiniteDataLoader
            A data loader to obtain training data from. The samples yielded by
            the data loader depend on a specific trainer implementation.
        - val_data: torch.DataLoader or bxtorch.nn.InfiniteDataLoader, 
                default: None
            A data loader to use for validation. If the loader is an infinite
            data loader, ``val_iterations`` must also be given. If not supplied,
            no validation will be performed.
        - epochs: int, default: 20
            The number of epochs to train for. If the given data is an infinite
            data loader, this value defines the number of iterations (and 
            should most probably be increased).
        - val_iterations: int, default: None
            The number of iterations to perform for validation. Must be given
            only if ``val_data`` is an infinite data loader. Otherwise, the
            parameter is ignored.
        - eval_every: int, default: 1
            How many iterations should pass until validation is called again.
            This should only be set if ``train_data`` is an infinite loader,
            otherwise it will be ignored. Note that everything works as if
            ``epochs // eval_every`` epochs is trained while ``eval_every`` can
            be considered the number of mini-batches.
        - eval_train: bool, default: False
            Whether to compute metrics (apart from the loss) for both the
            validation and the train data. If this flag is set to False,
            metrics will only be computed for the validation data.
        - callbacks: list of bxtorch.nn.TrainingCallback or 
                bxtorch.nn.PredictionCallback, default: []
            The callbacks to use for training and inference. The training
            callbacks and prediction callbacks will be filtered automatically.
        - metrics: dict of str -> func, default: {}
            Metrics to compute during evaluation for the validation data (and
            potentially for the training data). The keys for the metrics define
            their name.
        - gpu: bool or int or list of int, default: False
            Governs, whether training and evaluation should be performed on a
            GPU. If set to True, the GPU with the most amount of free memory is
            selected (if there are multiple GPUs). If set to an integer, the GPU
            with the specified index is used. If set to a list of integers, the
            specified GPUs are used to train and evaluate the model und multiple
            GPUs simultaneously. In this case, the batch sizes of the data
            loaders should be adjusted accordingly. If set to None, the model
            won't be moved. Only do this if you know what you are doing.
        - kwargs: keyword arguments
            Additional keyword arguments dependent on the specific subclass.

        Returns:
        --------
        - bxtorch.nn.training.wrappers.History
            A history object summarizing stats from the training. It contains
            as properties the development of the loss as ``train_loss`` (and
            potentially ``val_loss``, if ``val_data`` is supplied and the 
            keyword arguments include a function called ``loss``). If
            additional metrics are supplied, there will be a property 
            ``val_<metric>`` for each metric, and potentially ``train_<metric>``
            if ``eval_train`` is set to True.
        """
        # 1) Setup
        exception = None
        tic = time.time()

        if isinstance(train_data, InfiniteDataLoader):
            epochs = epochs // eval_every

        # 1.1) Callbacks
        train_callbacks = [
            c for c in callbacks if isinstance(c, TrainingCallback)
        ]
        prediction_callbacks = [
            c for c in callbacks if isinstance(c, PredictionCallback)
        ]

        self._exec_callbacks(
            train_callbacks, 'before_training', self.model, epochs
        )

        # 1.2) Metrics
        metric_history = []
        if 'loss' in kwargs:
            val_metrics = {**metrics, **{'loss': kwargs['loss']}}
        else:
            val_metrics = metrics

        # 1.3) Data loading
        train_epoch_is_iteration = not isinstance(train_data, DataLoader)
        if train_epoch_is_iteration:
            train_iterator = iter(train_data)

        # 1.4) GPU support
        if gpu is not None:
            self._setup_device(gpu)
            self.model.to(self.device)
        
        # 2) Train for number of epochs
        for current_epoch in range(epochs):
            # 2.1) Prepare
            if train_epoch_is_iteration:
                batch_iterations = eval_every
            else:
                batch_iterations = len(train_data)
                
            try:
                self._exec_callbacks(
                    train_callbacks, 'before_epoch', current_epoch, 
                    batch_iterations
                )
            except CallbackException as e:
                exception = e
                break

            if not train_epoch_is_iteration:
                train_iterator = iter(train_data)

            # 2.2) Train
            self.model.train()

            train_batch_weights = []
            train_losses = []

            if train_epoch_is_iteration:
                # 2.2.1) Infinite iterator
                for _ in range(eval_every):
                    item = next(train_iterator)
                    item = to_device(self.device, item)
                    loss = self._train_batch(item, **kwargs)
                    train_losses.append(loss)
                    self._exec_callbacks(
                        train_callbacks, 'after_batch'
                    )
            else:
                # 2.2.2) Dataset
                for item in train_iterator:
                    item = to_device(self.device, item)
                    loss = self._train_batch(item, **kwargs)
                    train_batch_weights.append(len(item))
                    train_losses.append(loss)
                    self._exec_callbacks(
                        train_callbacks, 'after_batch'
                    )

            # 2.3) Validate
            batch_metrics = Evaluation(
                self._collate_train_losses(train_losses),
                train_batch_weights
            )

            if val_data is not None:
                eval_val = self.evaluate(
                    val_data, iterations=val_iterations, metrics=val_metrics,
                    callbacks=prediction_callbacks, gpu=None
                ).with_prefix('val_')
                batch_metrics = Evaluation.merge(batch_metrics, eval_val)

            if eval_train:
                eval_train = self.evaluate(
                    train_data, iterations=val_iterations, metrics=metrics,
                    callbacks=prediction_callbacks, gpu=None
                ).with_prefix('train_')
                batch_metrics = Evaluation.merge(batch_metrics, eval_train)

            batch_metrics = Evaluation.merge(
                batch_metrics, Evaluation({'_timestamp': time.time()})
            )

            metric_history.append({
                'micro_train_loss': train_losses,
                **batch_metrics.to_dict()
            })

            # 2.4) Finish epoch
            try:
                self._exec_callbacks(
                    train_callbacks, 'after_epoch', batch_metrics
                )
            except CallbackException as e:
                exception = e
                break

        # 3) Finish training

        # 3.1) If GPU used
        if gpu is not None:
            self.model.to('cpu', non_blocking=True)
            self.device = None

        # 3.2) Finish callbacks
        self._exec_callbacks(
            train_callbacks, 'after_training'
        )
        if exception is not None:
            print(exception)

        return History(time.time() - tic, metric_history)

    def evaluate(self, data, iterations=None, metrics={}, callbacks=[],
                 gpu=False):
        """
        Evaluates the model on the given data and computes the supplied metrics.

        Parameters:
        -----------
        - data: torch.DataLoader or bxtorch.nn.InfiniteDataLoader
            A data loader to obtain evaluation samples from. The expected 
            samples depend on a specific trainer subclass.
        - iterations: int, default: None
            The number of samples used for evaluating if the given data is an
            infinite data loader.
        - metrics: dict of str -> func, default: {}
            The metrics to evaluate the model for. The keys define the names of
            the metrics when retrieving the evaluated result from the return
            parameter.
        - callbacks: list of bxtorch.nn.PredictionCallback, default: []
            Callbacks to use while computing predictions. Usually, they are 
            used for logging.
        - gpu: bool or int or list of int, default: False
            Governs, whether training and evaluation should be performed on a
            GPU. If set to True, the GPU with the most amount of free memory is
            selected (if there are multiple GPUs). If set to an integer, the GPU
            with the specified index is used. If set to a list of integers, the
            specified GPUs are used to train and evaluate the model und multiple
            GPUs simultaneously. In this case, the batch sizes of the data
            loaders should be adjusted accordingly. If set to None, the model
            won't be moved. Only do this if you know what you are doing.

        Returns:
        --------
        - bxtorch.nn.training.wrappers.Evaluation
            An evaluation object, yielding as properties the metrics with their
            specified names.
        """
        num_predictions = iterations or len(data)
        self._exec_callbacks(
            callbacks, 'before_predictions', self.model, num_predictions
        )

        if gpu is not None:
            self._setup_device(gpu)
            self.model.to(self.device)

        self.model.eval()

        predictions = []
        targets = []

        iterator = iter(data)
        for _ in range(num_predictions):
            item = next(iterator)
            item = to_device(self.device, item)

            with torch.no_grad():
                prediction, target = self._predict_batch(item)

            predictions.append(to_device('cpu', prediction))
            targets.append(to_device('cpu', target))

            self._exec_callbacks(
                callbacks, 'after_batch'
            )

        self._exec_callbacks(
            callbacks, 'after_predictions'
        )
        
        predictions = self._collate_predictions(predictions)
        targets = self._collate_targets(targets)

        result = {
            k: f(predictions, targets).item()
            for k, f in metrics.items()
        }

        if gpu is not None:
            self.model.to('cpu', non_blocking=True)
            self.device = None

        return Evaluation(result)

    def parallel_prepare(self, **kwargs):
        """
        The parallel prepare function prepares the trainer for being passed to
        another thread. It ensures that the trainer's model is moved into
        shared memory.
        
        Parameters:
        -----------
        - kwargs: keyword arguments
            The parameters passed to the ``train`` function. All parameters
            which are not thread safe (such as data loaders or optimizers)
            must be passed as ``<parameter>_init`` and will then be initialized
            on the background thread.

        Returns:
        --------
        - dict
            The parameters which can safely be passed to a background thread.
        """
        self.model.share_memory()

        def get_item(k, v):
            if k == 'train_data' or k == 'val_data':
                return (f'{k}_init', self._get_loader_init(v))
            return (k, v)

        return dict(get_item(k, v) for k, v in kwargs.items())

    def parallel_restore(self, **kwargs):
        """
        Based on the return values of the ``parallel_prepare`` function, this
        function should use the passed parameters to construct the actual
        parameters passed to the ``train`` function.

        Parameters:
        -----------
        - kwargs: keyword arguments
            The parameters retrieved from the ``parallel_prepare`` function.
            All parameters which are passed as ``<parameters>_init`` will be
            converted into the parameter ``<parameter>``. They are expected to
            be functions which take the model as first parameter.

        Returns:
        --------
        - dict
            The parameters to pass to the train function.
        """
        result = {}

        for k, v in kwargs.items():
            if k.endswith('_init'):
                result[k[:-5]] = v(self.model)
            else:
                result[k] = v

        return result

    # MARK: Private Methods
    @abstractmethod
    def _train_batch(self, data, **kwargs):
        """
        Runs a single step in training. If the training data represents an 
        infinite dataset, this equals a single iteration, otherwise a 
        mini-batch.

        Parameters:
        -----------
        - data: object
            The data for the current iteration/mini-batch.

        Returns:
        --------
        - object
            The loss computed for the batch. If the returned value is not float,
            overwrite ``_collate_train_losses``.
        """
        pass

    @abstractmethod
    def _predict_batch(self, data, **kwargs):
        """
        Runs a single step for inference. The data is either a mini-batch or a 
        single iteration, depending on the data used for evaluation.

        Parameters:
        -----------
        - data: object
            The data for the current iteration/mini-batch.
        - kwargs: keyword arguments
            Additional arguments dependent on the subclass and passed directly
            from the evaluation method.

        Returns:
        --------
        - torch.Tensor
            The output from the model.
        - object
            The target, i.e. correct output. If this is not a ``torch.Tensor``, 
            the ``_collate_targets`` should be overriden.
        """
        pass

    def _collate_train_losses(self, losses):
        """
        Combines the losses obtained from the ``_train_batch`` function.
        The default implementation assumes that simple floats are returned.

        Parameters:
        -----------
        - losses: list of object
            The losses returned from ``_train_batch``.
        
        Returns:
        --------
        - dict of str -> (float or list of float)
            The loss names mapped to their values.
        """
        return {'train_loss': losses}

    def _collate_predictions(self, predictions):
        """
        Combines the predictions obtained from the ``_predict_batch`` function.
        The default implementation assumes that predictions are tensors and can 
        simply be conatenated.

        Parameters:
        -----------
        - list of objects
            The predictions.

        Returns:
        --------
        - object
            An object to be used as predicted value for some metric.
        """
        return torch.cat(predictions)

    def _collate_targets(self, targets):
        """
        Combines the targets in a way that it can be passed to some metric.
        The default implementation assumes that targets are tensors and simply
        concatenates them.

        Parameters:
        -----------
        - list of object
            The targets.

        Returns:
        --------
        - object
            An object to be used as true target with some metric.
        """
        return torch.cat(targets)

    def _setup_device(self, gpu):
        if isinstance(gpu, list):
            self.model = xnnu.DataParallel(self.model, device_ids=gpu)
            self.device = gpu_device(gpu[0])
        else:
            self.device = gpu_device(gpu)

    def _exec_callbacks(self, callbacks, func, *args):
        for callback in ([self] + callbacks):
            getattr(callback, func)(*args)

    def _get_loader_init(self, loader):
        if isinstance(loader, DataLoader):
            return functools.partial(
                _dataloader_init, loader.dataset, _dataloader_kwargs(loader)
            )
        elif isinstance(loader, InfiniteDataLoader):
            return functools.partial(
                _infinite_loader_init, loader.dataset,
                _infinite_loader_kwargs(loader)
            )
        else:
            raise ValueError(
                f"Cannot safely pass type {loader.__class__.__name__} to a" +
                " background thread. Please supply it as init function."
            )


def _dataloader_kwargs(loader):
    return {
        'batch_sampler': loader.batch_sampler,
        'num_workers': loader.num_workers,
        'collate_fn': loader.collate_fn,
        'pin_memory': loader.pin_memory,
        'timeout': loader.timeout,
        'worker_init_fn': loader.worker_init_fn
    }

def _infinite_loader_kwargs(loader):
    return {
        'batch_size': loader.batch_size,
        'num_workers': loader.num_workers,
        'prefetch': getattr(loader, 'prefetch', 0),
        'pin_memory': loader.pin_memory,
        'collate_fn': loader.collate_fn
    }

def _dataloader_init(dataset, kwargs, model):
    return DataLoader(dataset, **kwargs)

def _infinite_loader_init(dataset, kwargs, model):
    return InfiniteDataLoader(dataset, **kwargs)
