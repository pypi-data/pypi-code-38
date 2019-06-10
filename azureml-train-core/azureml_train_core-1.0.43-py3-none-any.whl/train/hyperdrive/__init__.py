# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The hyperdrive package contains the modules supporting hyperparameter tuning.

HyperDrive automates the process of running hyperparameter sweeps for an experiment.  Various sampling methods
are supported in conjunction with a suite of early termination policies allowing poor performing experiment runs
to be cancelled and new ones to be started.
To define a reusable machine learning workflow for HyperDrive, you may use
:class:`azureml.pipeline.steps.hyper_drive_step` to create a
:class:`azureml.pipeline.core.pipeline.Pipeline`.
"""
from .policy import BanditPolicy, MedianStoppingPolicy, NoTerminationPolicy, TruncationSelectionPolicy, \
    EarlyTerminationPolicy
from .runconfig import HyperDriveRunConfig, HyperDriveConfig, PrimaryMetricGoal
from .run import HyperDriveRun
from .sampling import RandomParameterSampling, GridParameterSampling, BayesianParameterSampling, HyperParameterSampling
from .parameter_expressions import choice, randint, uniform, quniform, loguniform, \
    qloguniform, normal, qnormal, lognormal, qlognormal
from ._search import search
from azureml.core._experiment_method import ExperimentSubmitRegistrar

__all__ = ["BanditPolicy", "MedianStoppingPolicy", "NoTerminationPolicy", "TruncationSelectionPolicy",
           "EarlyTerminationPolicy", "HyperDriveRun", "HyperDriveRunConfig", "HyperDriveConfig",
           "RandomParameterSampling", "GridParameterSampling", "BayesianParameterSampling", "HyperParameterSampling",
           "choice", "randint", "uniform", "quniform", "loguniform",
           "qloguniform", "normal", "qnormal", "lognormal", "qlognormal",
           "PrimaryMetricGoal"]

ExperimentSubmitRegistrar.register_submit_function(HyperDriveRunConfig, search)
ExperimentSubmitRegistrar.register_submit_function(HyperDriveConfig, search)
