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


def tensor_backward(experiment, original, result, *args, **kwargs):
    # args[0] is self, the Tensor (loss):
    try:
        if experiment.curr_step is None:
            experiment.curr_step = 0
        else:
            experiment.curr_step += 1
        if experiment.log_graph:
            model = experiment._storage["torch"].get("model", None)
            if experiment.curr_step == 0 and model is not None:
                experiment.set_model_graph(str(model))
        if experiment.auto_metric_logging:
            ## Throttle report to every 10 batch updates:
            if experiment.curr_step % 10 == 0:
                loss = args[0]
                if len(loss.data.shape) == 0:
                    experiment.log_metric(
                        "loss", loss.data.item(), step=experiment.curr_step
                    )
                else:
                    experiment.log_metric(
                        "loss", loss.data.mean().item(), step=experiment.curr_step
                    )
    except Exception:
        LOGGER.info("Failed to run Tensor.backward logger", exc_info=True)
    return result


def model_constructor(experiment, original, *args, **kwargs):
    ## Assume the first one is the model:
    try:
        model = experiment._storage["torch"].get("model", None)
        if model is None:
            experiment._storage["torch"]["model"] = args[1]
    except Exception:
        LOGGER.info("Failed to run Module.__init__ logger", exc_info=True)


def patch(module_finder):
    ## For testing:
    check_module("torch")

    ## For each backpropagation of the gradient:
    module_finder.register_after("torch.tensor", "Tensor.backward", tensor_backward)
    ## For each model constructor:
    module_finder.register_after(
        "torch.nn.modules.module", "Module.__init__", model_constructor
    )


check_module("torch")
