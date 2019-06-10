# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""This package contains the core functionality for Azure Machine Learning service pipelines.

Azure Machine Learning service pipelines represent a collections of
:class:`azureml.pipeline.core.PipelineStep` which can be executed as a workflow.
For more details about pipeline and its advantages, you may refer to,
https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines.
"""
from .builder import PipelineStep, PipelineData, StepSequence
from .pipeline import Pipeline
from .graph import PublishedPipeline, PortDataReference, OutputPortBinding, InputPortBinding, TrainingOutput
from .graph import PipelineParameter, PipelineDataset
from .schedule import Schedule, ScheduleRecurrence, TimeZone
from .pipeline_endpoint import PipelineEndpoint
from .module import Module, ModuleVersion, ModuleVersionDescriptor
from .run import PipelineRun, StepRun, StepRunOutput

__all__ = ["PipelineRun",
           "StepRun",
           "StepRunOutput",
           "PipelineStep",
           "PipelineData",
           "Pipeline",
           "PublishedPipeline",
           "PipelineParameter",
           "PortDataReference",
           "OutputPortBinding",
           "InputPortBinding",
           "TrainingOutput",
           "StepSequence",
           "Schedule",
           "ScheduleRecurrence",
           "TimeZone",
           "PipelineEndpoint",
           "Module",
           "ModuleVersion",
           "ModuleVersionDescriptor",
           "PipelineDataset"
           ]
