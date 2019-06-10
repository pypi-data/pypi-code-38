# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Wrapper for pipeline fit output."""
from typing import Any, Dict, Optional, Union
import json
import traceback

from sklearn.pipeline import Pipeline as SKPipeline

from automl.client.core.common import constants, utilities
from automl.client.core.common.exceptions import ClientException
from .automl_base_settings import AutoMLBaseSettings
from .automl_pipeline import AutoMLPipeline
from .pipeline_run_helper import PipelineRunOutput


class FitOutput:
    """Data class encapsulating the return values from training."""

    MAX_OUTPUT_SIZE = 1024 * 1024

    def __init__(self, automl_settings: AutoMLBaseSettings, pipeline: AutoMLPipeline) -> None:
        """
        Initialize a FitOutput object.

        :param automl_settings: the settings used for training
        :param pipeline: the pipeline being used to train
        """
        self._settings = automl_settings
        self._errors = {}   # type: Dict[str, Dict[str, Union[BaseException, str, bool]]]
        self._pipeline = pipeline

        self.framework = 'sklearn'
        self.class_labels = None

        self._pipeline_run_output = None    # type: Optional[PipelineRunOutput]
        self._onnx_model = None
        self._onnx_model_resource = {}    # type: Dict[Any, Any]

    def record_pipeline_results(self, pipeline_run_output: PipelineRunOutput) -> None:
        """
        Record the results from pipeline execution.

        :param pipeline_run_output: the pipeline execution return object
        """
        self._pipeline_run_output = pipeline_run_output

    def set_onnx_model(self, onnx_model: Any) -> None:
        """
        Set the onnx model of the fitted pipeline.

        :param onnx_model: the converted onnx model.
        """
        self._onnx_model = onnx_model

    def set_onnx_model_resource(self, onnx_model_res: Dict[Any, Any]) -> None:
        """
        Set the resource of onnx model.

        :param onnx_model_res: the resource of the converted onnx model.
        """
        self._onnx_model_resource = onnx_model_res

    @property
    def training_size(self) -> float:
        """Get the training size."""
        return self._pipeline.training_size

    @property
    def predicted_time(self) -> float:
        """Get the predicted time."""
        return self._pipeline.predicted_time

    @property
    def actual_time(self) -> float:
        """Get the actual time."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fit_time
        else:
            return 0

    @property
    def fitted_pipeline(self) -> SKPipeline:
        """Get the fitted pipeline."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fitted_pipeline
        else:
            return constants.Defaults.INVALID_PIPELINE_FITTED

    @property
    def fitted_pipelines_train(self) -> Union[SKPipeline, str]:
        """Get the partially trained fitted pipelines."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.fitted_pipelines_train
        else:
            return constants.Defaults.INVALID_PIPELINE_FITTED

    @property
    def onnx_model(self) -> Any:
        """Get the converted ONNX model."""
        return self._onnx_model

    @property
    def onnx_model_resource(self) -> Dict[Any, Any]:
        """Get the resource of the converted ONNX model."""
        return self._onnx_model_resource

    @property
    def run_properties(self) -> Optional[str]:
        """Get the pipeline run properties."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.run_properties
        else:
            return None

    @property
    def run_preprocessor(self) -> Optional[str]:
        """Get the preprocessor name."""
        return self.pretrain_props['run_preprocessor']

    @property
    def run_algorithm(self) -> Optional[str]:
        """Get the algorithm name."""
        return self.pretrain_props['run_algorithm']

    @property
    def goal(self) -> str:
        """Get the training goal."""
        suffixes = {
            constants.OptimizerObjectives.MINIMIZE: 'min',
            constants.OptimizerObjectives.MAXIMIZE: 'max',
            constants.OptimizerObjectives.NA: 'NA'
        }
        suffix = suffixes.get(self._settings.metric_operation)

        if suffix is None:
            raise NotImplementedError()

        return '{}_{}'.format(self._settings.primary_metric, suffix)

    @property
    def pretrain_props(self) -> Dict[str, Optional[str]]:
        """Get the pretrain properties."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.pretrain_props
        else:
            return {
                'run_template': 'automl_child',
                'run_preprocessor': None,
                'run_algorithm': None
            }

    @property
    def primary_metric(self) -> str:
        """Get the primary metric."""
        return self._settings.primary_metric

    @property
    def scores(self) -> Dict[str, Any]:
        """Get the pipeline scores."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.scores
        else:
            return constants.Defaults.INVALID_PIPELINE_VALIDATION_SCORES

    @property
    def score(self) -> float:
        """Get the primary pipeline score."""
        return self.scores.get(self.primary_metric, constants.Defaults.DEFAULT_PIPELINE_SCORE)

    @property
    def training_type(self) -> Optional[str]:
        """Get the training type."""
        if self._pipeline_run_output:
            return self._pipeline_run_output.training_type
        else:
            return None

    @property
    def pipeline_script(self) -> str:
        """Get the pipeline script."""
        return self._pipeline.pipeline_script

    @property
    def pipeline_id(self) -> str:
        """Get the pipeline hash id."""
        return self._pipeline.pipeline_id

    @property
    def num_classes(self) -> Optional[int]:
        """Get the number of classes for a classification task."""
        return self._settings.num_classes

    @property
    def errors(self) -> Dict[str, Dict[str, Union[BaseException, str, bool]]]:
        """Get errors from training."""
        return self._errors

    @property
    def friendly_errors(self) -> str:
        """Get errors from training in JSON format."""
        return json.dumps(self._format_errors(self._errors))

    def add_error(self, exception_type: str, exception: BaseException, is_critical: Optional[bool] = True) -> None:
        """Add an error to the list of training errors."""
        self._errors[exception_type] = {
            'exception': exception,
            'traceback': traceback.format_exc(),
            'is_critical': is_critical if is_critical else False
        }

    def get_output_dict(self) -> Dict[str, Any]:
        """Get a dictionary representing this object's output."""
        output = {
            'staticProperties': {},
            'score': self.score,
            'run_properties': self.run_properties,
            'pipeline_script': self.pipeline_script,
            'pipeline_id': self.pipeline_id,
            'training_type': self.training_type,
            'num_classes': self.num_classes,
            'framework': self.framework,
            'fit_time': self.actual_time,
            'goal': self.goal,
            'class_labels': self.class_labels,
            'primary_metric': self.primary_metric,
            'errors': self.errors,
            'fitted_pipeline': self.fitted_pipeline,
            'pipeline_python_obj': self.fitted_pipeline,
            'friendly_errors': self.friendly_errors,
            'pipeline_spec': self.pipeline_script,
            'onnx_model': self.onnx_model,
            'onnx_model_resource': self.onnx_model_resource,
            self._settings.primary_metric: self.score
        }
        output.update(self.pretrain_props)
        return output

    def get_sanitized_output_dict(self) -> Dict[str, str]:
        """Get a dictionary representing this object's output with None values replaced with empty strings."""
        output_dict = self.get_output_dict()

        # Temporary hack to get around run property immutability.
        # TODO: Refactor pipeline_run_helper so we can get the pretrain properties inside fit_pipeline
        immutable_keys = [
            'run_template',
            'run_preprocessor',
            'run_algorithm',
            'pipeline_spec',
            self._settings.primary_metric
        ]
        # Exclude large objects from output.
        large_keys = [
            'onnx_model'
        ]
        for key in (immutable_keys + large_keys):
            if key in output_dict:
                del output_dict[key]
        output = utilities.convert_dict_values_to_str(output_dict)

        # Cap the output size to 1MB (the real limit is somewhat higher, but this is a good limit due to overhead)
        output_len = len(json.dumps(output))
        if output_len > FitOutput.MAX_OUTPUT_SIZE:
            raise ClientException('Fit output size exceeded {} bytes, actual size is {} bytes.'
                                  .format(FitOutput.MAX_OUTPUT_SIZE, output_len))
        return output

    @staticmethod
    def _format_errors(errors: Dict[str, Any]) -> Dict[str, str]:
        friendly_errors = {}
        for error in errors:
            friendly_errors[error] = str(errors[error]['exception'])
        return friendly_errors
