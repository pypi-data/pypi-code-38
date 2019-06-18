#
#  nn/training/proxy.py
#  bxtorch
#
#  Created by Oliver Borchert on June 18, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import torch.optim as optim
from bxtorch.utils.stdlib import flatten

class ProxyOptimizer(optim.Optimizer):
    """
    Optimizer for use with Hogwild!. It is only intended for internal usage,
    do not use this class directly. The idea is simply to provide a proxy for 
    an optimizer on a shared model while gradients are collected from another
    model (which is e.g. optimized on the GPU). It should generally be used
    with some appropriate callbacks during training.
    """

    # MARK: Initialization
    def __init__(self, optimizer, shared_optimizer):
        """
        Initializes a new proxy optimizer. Note that two optimizers are 
        required (instead of a model and an optimizer) as an optimizer must
        not necessarily optimize all parameters of a model. Evidently, both
        given optimizers must optimize the same parameters (of different
        models with the same architecture).

        Parameters:
        -----------
        - optimizer: torch.optim.Optimizer
            The "actual" optimizer.
        - shared_optimizer: torch.optim.Optimizer
            The optimizer to which all calls are proxied. 
        """
        # Initialize super with all parameters such that operations like
        # ``zero_grad`` still work as expected. Otherwise, do not pass any
        # configuration information.
        super().__init__(
            flatten([g['params'] for g in optimizer.param_groups]), {}
        )

        self.optimizer = optimizer
        self.shared_optimizer = shared_optimizer
    
    # MARK: Instance Methods
    def step(self, closure=None):
        """
        Performs an optimization step by passing the gradients of the model
        to the shared optimizer and performing an optimization step on the
        shared model.

        Parameters:
        -----------
        - closure: callable
            A closure to reevaluate the model and return the loss.
        """
        # 1) Move the gradients to the shared model

        # Optimizers must have the same param groups, otherwise behavior is
        # undefined
        param_groups = zip(
            self.optimizer.param_groups, 
            self.shared_optimizer.param_groups
        )
        for parameter_group, shared_parameter_group in param_groups:
            parameters = zip(
                parameter_group['params'],
                shared_parameter_group['params']
            )
            # Now, actually move parameters, try not to block
            for parameter, shared_parameter in parameters:
                device = shared_parameter.device
                grad = parameter.grad
                # We set the gradient directly as we then don't need to zero
                # the gradient
                shared_parameter._grad = grad.to(device, non_blocking=True)

        # 2) Perform update step on shared model
        # The model weights from the updated model should then be loaded by
        # an appropriate callback.
        return self.shared_optimizer.step(closure)
