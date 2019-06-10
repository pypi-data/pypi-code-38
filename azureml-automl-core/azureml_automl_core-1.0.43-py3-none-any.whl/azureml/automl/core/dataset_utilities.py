# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with azureml.core.Dataset."""
from typing import Any, Optional, Tuple, Union
import logging

from automl.client.core.common import logging_utilities
from automl.client.core.common.exceptions import DataprepException
from automl.client.core.common.types import T
from azureml.core import Dataset, Run
from azureml.data.dataset_definition import DatasetDefinition
from azureml.dataprep import Dataflow


_deprecated = 'deprecated'
_archived = 'archived'
module_logger = logging.getLogger(__name__)


def is_dataset(dataset: Any) -> bool:
    """
    Check to see if the given object is a dataset or dataset definition.

    :param dataset: object to check
    """
    return isinstance(dataset, Dataset) or isinstance(dataset, DatasetDefinition)


def log_dataset(name: str, definition: Any, run: Optional[Run] = None) -> None:
    """
    Log the dataset specified by the given definition.

    :param name: metric name
    :param definition: the dataset definition to log
    :param run: the run object to use for logging
    """
    from .dataprep_utilities import is_dataflow
    try:
        if (is_dataset(definition) or is_dataflow(definition)) and _contains_dataset_ref(definition):
            run = run or Run.get_context()
            run.log(name=name, value=_get_dataset_info(definition))
    except Exception as e:
        module_logger.warning('Unable to log dataset.\nException: {}'.format(e))


def convert_inputs(X: Any, y: Any, X_valid: Any, y_valid: Any) -> Tuple[Any, Any, Any, Any]:
    """
    Convert the given datasets to trackable definitions.

    :param X: dataset representing X
    :param y: dataset representing y
    :param X_valid: dataset representing X_valid
    :param y_valid: dataset representing y_valid
    """
    return (
        _convert_to_trackable_definition(X),
        _convert_to_trackable_definition(y),
        _convert_to_trackable_definition(X_valid),
        _convert_to_trackable_definition(y_valid)
    )


def _convert_to_trackable_definition(dataset: T) -> Union[T, Dataflow]:
    definition, trackable = _reference_dataset(dataset)
    if not trackable:
        module_logger.debug('Unable to convert input to trackable definition')
    return definition


def _reference_dataset(dataset: T) -> Tuple[Union[T, Dataflow], bool]:
    from azureml.dataprep import Dataflow

    if not is_dataset(dataset) and not isinstance(dataset, Dataflow):
        return dataset, False

    if type(dataset) == Dataflow:
        return dataset, _contains_dataset_ref(dataset)

    # un-registered dataset
    if isinstance(dataset, DatasetDefinition) and not dataset._workspace:
        return dataset, _contains_dataset_ref(dataset)

    _verify_dataset(dataset)
    return Dataflow.reference(dataset), True


def _contains_dataset_ref(definition: DatasetDefinition) -> bool:
    for step in definition._get_steps():
        if step.step_type == 'Microsoft.DPrep.ReferenceBlock' \
                and _get_ref_container_path(step).startswith('dataset://'):
            return True
    return False


def _get_dataset_info(definition: DatasetDefinition) -> str:
    for step in definition._get_steps():
        ref_path = _get_ref_container_path(step)
        if step.step_type == 'Microsoft.DPrep.ReferenceBlock' and ref_path.startswith('dataset://'):
            return ref_path
    raise DataprepException('Unexpected error, unable to retrieve dataset information.')


def _get_ref_container_path(step: Any) -> str:
    if step.step_type != 'Microsoft.DPrep.ReferenceBlock':
        return ''
    try:
        return step.arguments['reference'].reference_container_path or ''
    except AttributeError:
        # this happens when a dataflow is serialized and deserialized
        return step.arguments['reference']['referenceContainerPath'] or ''
    except KeyError:
        return ''


def _verify_dataset(dataset: Any) -> None:
    if isinstance(dataset, Dataset):
        if dataset.state == _deprecated:
            module_logger.warning('Warning: dataset \'{}\' is deprecated.'.format(dataset.name))
        if dataset.state == _archived:
            message = 'Error: dataset \'{}\' is archived and cannot be used.'.format(dataset.name)
            ex = DataprepException(message)
            logging_utilities.log_traceback(
                ex,
                module_logger
            )
            raise ex
    if isinstance(dataset, DatasetDefinition):
        if dataset._state == _deprecated:
            message = 'Warning: this definition is deprecated.'
            dataset_and_version = ''
            if dataset._deprecated_by_dataset_id:
                dataset_and_version += 'Dataset ID: \'{}\' '.format(dataset._deprecated_by_dataset_id)
            if dataset._deprecated_by_definition_version:
                dataset_and_version += 'Definition version: \'{}\' '.format(dataset._deprecated_by_definition_version)
            if dataset_and_version:
                message += ' Please use \'{}\' instead.'.format(dataset_and_version.strip(' '))
            module_logger.warning(message)
        if dataset._state == _archived:
            message = 'Error: definition version \'{}\' is archived and cannot be used'.format(dataset._version_id)
            ex = DataprepException(message)
            logging_utilities.log_traceback(
                ex,
                module_logger
            )
            raise ex
