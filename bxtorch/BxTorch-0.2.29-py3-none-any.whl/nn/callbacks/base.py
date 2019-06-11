#
#  nn/callbacks/base.py
#  bxtorch
#
#  Created by Oliver Borchert on May 09, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

from abc import ABC

class CallbackException(Exception):
    """
    Exception raised by callbacks to stop the training procedure.
    """
    pass


class TrainingCallback(ABC):
    """
    Abstract class to be subclassed by all training callbacks.
    These callbacks are passed to a trainer which calls the implemented methods
    at specific points during training.
    """

    # MARK: Instance Methods
    def before_training(self, model, num_epochs):
        """
        Method is called prior to the start of the training.
        This method must not raise exceptions.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model which is trained.
        - num_epochs: int
            The maximum number of epochs performed during training.
        """
        pass

    def before_epoch(self, current, num_iterations):
        """
        Method is called at the begining of every epoch during training.
        This method may raise exceptions if training should be stopped. Note,
        however, that stopping training at this stage is an advanced scenario.

        Parameters:
        -----------
        - current: int
            The index of the epoch that is about to start.
        - num_iterations: int
            The expected number of iterations for the batch.
        """
        pass

    def after_batch(self):
        """
        Method is called at the end of a mini-batch. If the data is not
        partitioned into batches, this function is never called.
        The method may not raise exceptions.
        """
        pass

    def after_epoch(self, metrics):
        """
        Method is called at the end of every epoch during training.
        This method may raise exceptions if training should be stopped.

        Parameters:
        -----------
        - metrics: bxtorch.nn.training.wrappers.Evaluation
            Metrics obtained after training this epoch.
        """
        pass

    def after_training(self):
        """
        Method is called upon end of the training procedure.
        The method may not raise exceptions.
        """
        pass


class PredictionCallback(ABC):
    """
    Abstract class to be subclassed by all prediction callbacks.
    These callbacks are passed to a trainer which calls the implemented methods
    at specific points during inference.
    """

    # MARK: Instance Methods
    def before_predictions(self, model, num_iterations):
        """
        Called before prediction making starts.

        Parameters:
        -----------
        - model: torch.nn.Module
            The model which is used to make predictions.
        - num_iterations: int
            The number of iterations/batches performed for prediction.
        """
        pass

    def after_batch(self):
        """
        Called after prediction is done for one batch.
        """
        pass

    def after_predictions(self):
        """
        Called after all predictions have been made.
        """
        pass
