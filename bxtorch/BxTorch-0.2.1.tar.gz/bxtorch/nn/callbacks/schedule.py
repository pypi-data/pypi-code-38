#
#  nn/callbacks/schedule.py
#  bxtorch
#
#  Created by Oliver Borchert on May 21, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import torch
from .base import TrainingCallback

class ParameterScheduler(TrainingCallback):
    """
    The parameter scheduler is able to change the value of a variable
    over the course of the training. The scheduler modifies parameters
    **in-place**, hence, you must pass tensors to be modified and you must
    never pass them to the CPU.
    """

    # MARK: Initialization
    def __init__(self, parameter, schedule):
        """
        Initalizes a new scheduler for the given parameter.

        Parameters:
        -----------
        - parameter: torch.Tensor
            The parameter which should be modified over the course of the
            training.
        - schedule: func (float, int) -> float
            Function which should update the parameter (given as first
            argument) based on itself and the current epoch (second argument).
            The function must return the updated parameter. The scheduler
            function is called after every epoch.
        """
        self.parameter = parameter
        self.schedule = schedule
        self.epoch = None

    # MARK: Instance Methods
    def before_epoch(self, current, num_iterations):
        self.epoch = current

    def after_epoch(self, metrics):
        update = self.schedule(self.parameter.item(), self.epoch)
        self.parameter.set_(torch.tensor(update))

    def after_training(self):
        self.epoch = None
