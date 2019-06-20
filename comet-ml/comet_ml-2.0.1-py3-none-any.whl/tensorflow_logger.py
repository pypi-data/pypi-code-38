# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************


import logging

from comet_ml._logging import check_module

LOGGER = logging.getLogger(__name__)


optimizers_hyper_params = {
    "AdagradDAOptimizer": [
        "_learning_rate",
        "_initial_gradient_squared_accumulator_value",
        "_l1_regularization_strength",
        "_l2_regularization_strength",
    ],
    "ProximalAdagradOptimizer": [
        "_learning_rate",
        "_initial_accumulator_value",
        "_l1_regularization_strength",
        "_l2_regularization_strength",
    ],
    "ProximalGradientDescentOptimizer": [
        "_learning_rate",
        "_l1_regularization_strength",
        "_l2_regularization_strength",
    ],
    "RMSPropOptimizer": ["_learning_rate", "_decay", "_momentum", "_epsilon"],
    "AdadeltaOptimizer": ["_lr", "_rho", "_epsilon"],
    "GradientDescentOptimizer": ["_learning_rate"],
    "MomentumOptimizer": ["_learning_rate", "_momentum", "_use_nesterov"],
    "AdamOptimizer": ["_lr", "_beta1", "_beta2", "_epsilon"],
    "FtrlOptimizer": [
        "_learning_rate",
        "_learning_rate_power",
        "_initial_accumulator_value",
        "_l1_regularization_strength",
        "_l2_regularization_strength",
    ],
    "AdagradOptimizer": ["_learning_rate", "_initial_accumulator_value"],
}


def extract_params_from_optimizer(optimizer):
    optimizer_name = optimizer.__class__.__name__
    optimizer_params = optimizers_hyper_params.get(optimizer_name, [])

    hyper_params = {}
    for param in optimizer_params:
        if hasattr(optimizer, param):
            value = getattr(optimizer, param)
            if param[0] == "_":
                hyper_params[param[1:]] = value  # remove underscore prefix
            else:
                hyper_params[param] = value

    hyper_params["Optimizer"] = optimizer_name
    return hyper_params


def estimator_logger(experiment, original, value, *args, **kwargs):
    try:
        if len(args) > 0:
            LOGGER.debug("TENSORFLOW LOGGER CALLED")
            params = extract_params_from_optimizer(args[0])
            experiment.log_parameters(params)

    except Exception:
        LOGGER.error(
            "Failed to extract parameters from Estimator.init()", exc_info=True
        )


OPTIMIZER = [
    (
        "tensorflow.python.training.gradient_descent",
        "GradientDescentOptimizer.__init__",
    ),
    ("tensorflow.python.training.momentum", "MomentumOptimizer.__init__"),
    (
        "tensorflow.python.training.proximal_adagrad",
        "ProximalAdagradOptimizer.__init__",
    ),
    (
        "tensorflow.python.training.proximal_gradient_descent",
        "ProximalGradientDescentOptimizer.__init__",
    ),
    ("tensorflow.python.training.adadelta", "AdadeltaOptimizer.__init__"),
    ("tensorflow.python.training.adagrad", "AdagradOptimizer.__init__"),
    ("tensorflow.python.training.adagrad_da", "AdagradDAOptimizer.__init__"),
    ("tensorflow.python.training.adam", "AdamOptimizer.__init__"),
    ("tensorflow.python.training.ftrl", "FtrlOptimizer.__init__"),
    ("tensorflow.python.training.rmsprop", "RMSPropOptimizer.__init__"),
]


def patch(module_finder):
    check_module("tensorflow")

    # Register the methods
    for module, object_name in OPTIMIZER:
        module_finder.register_after(module, object_name, estimator_logger)


check_module("tensorflow")
