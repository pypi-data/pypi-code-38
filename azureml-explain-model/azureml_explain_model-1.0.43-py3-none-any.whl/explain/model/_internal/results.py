# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a set of functions for retrieving model explanation result data from run history."""

import numpy as np

from .constants import History, ExplainType
from .common import module_logger, _sort_feature_list_single, \
    _sort_feature_list_multiclass
try:
    from azureml._async import TaskQueue, WorkerPool
    from azureml.exceptions import UserErrorException
    from azureml._restclient.assets_client import AssetsClient
except ImportError:
    module_logger.warning("Could not import azureml.core, required if using run history")
from .explanation_client import _create_download_dir, _download_artifact


def _download_model_summary(run, download_dir, summary_name, top_k=None):
    explanation_asset = None
    storage_metadata = None
    asset_found = False
    assets_client = AssetsClient(run.experiment.workspace.service_context)
    explanation_assets = assets_client.get_assets_by_run_id_and_name(run.id, History.EXPLANATION_ASSET)
    if len(explanation_assets) > 0:
        explanation_asset = explanation_assets[0]
        metadata_artifact_name = explanation_asset.meta[History.METADATA_ARTIFACT]
        storage_metadata = _download_artifact(run, download_dir, metadata_artifact_name)
        meta_keys = storage_metadata.keys()
        for key in meta_keys:
            if summary_name in key:
                asset_found = True
                break
    if not asset_found:
        return _download_artifact(run, download_dir, summary_name)
    else:
        if History.NUM_FEATURES in storage_metadata[summary_name]:
            num_columns_to_return = int(storage_metadata[summary_name][History.NUM_FEATURES])
            num_blocks = int(storage_metadata[summary_name][History.NUM_BLOCKS])
        else:
            num_columns_to_return = int(storage_metadata[summary_name][History.NUM_FEATURES + '_' + summary_name])
            num_blocks = int(storage_metadata[summary_name][History.NUM_BLOCKS + '_' + summary_name])
        if top_k is not None:
            num_columns_to_return = min(top_k, num_columns_to_return)
    # this does not support explanation version v3, as this function is being deprecated
    full_data = np.array(_download_artifact(run, download_dir, summary_name + '_0'))
    concat_dim = full_data.ndim - 1
    # Get the blocks
    for idx in range(1, num_blocks):
        block_name = '{}_{}'.format(summary_name, str(idx))
        block = np.array(_download_artifact(run, download_dir, block_name))
        full_data = np.concatenate([full_data, block], axis=concat_dim)
        num_columns_read = full_data.shape[concat_dim]
        if num_columns_read >= num_columns_to_return:
            break
    full_data_list = full_data[..., :num_columns_to_return].tolist()
    return full_data_list


def get_model_explanation(run):
    """Return the feature importance values.
    :param run: An object that represents a model explanation run.
    :type run: azureml.core.run.Run
    :rtype: (Union[numpy.ndarray, list[numpy.ndarray]], numpy.ndarray)
    :return: tuple(local_importance_values, expected_values) where
        - local_importance_values = For a model with a single output such as regression, this returns
        a matrix of feature importance values. For models with vector outputs this function returns a
        list of such matrices, one for each output. The dimension of this matrix is (# examples x # features).
        - expected_values = The expected value of the model applied to the set of initialization examples.
        For SHAP values, when a version older than 0.20.0 is used, this value is None. The expected
        values are in the last columns of the matrices in local_importance_values. In this case, the
        dimension of those matrix is (# examples x (# features + 1)). This causes each row to sum to
        the model output for that example.
    """
    module_logger.warning('WARNING: This API is being deprecated. '
                          'Please use the ExplanationClient for the most up-to-date experience.')
    download_dir = _create_download_dir()

    try:
        local_importance_values = _download_artifact(run, download_dir, 'local_importance_values')
    except UserErrorException:
        local_importance_values = _download_artifact(run, download_dir, 'shap_values')
    expected_values = None
    try:
        expected_values = _download_artifact(run, download_dir, 'expected_values')
    except Exception:
        module_logger.warning(
            "expected_values is not found in Artifact service")
    return local_importance_values, expected_values


def get_model_explanation_from_run_id(workspace, experiment_name, run_id):
    """Return the feature importance values.

    :param workspace: An object that represents a workspace.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of the experiment.
    :type experiment_name: str
    :param run_id: A GUID that represents a run.
    :type run_id: str
    :rtype: (Union[numpy.ndarray, list[numpy.ndarray]], numpy.ndarray)
    :return: tuple(local_importance_values, expected_values) where
        - local_importance_values = For a model with a single output such as regression, this
        returns a matrix of feature importance values. For models with vector outputs this function
        returns a list of such matrices, one for each output. The dimension of this matrix
        is (# examples x # features).
        - expected_values = The expected value of the model applied to the set of initialization examples.
        For SHAP values, when a version older than 0.20.0 is used, this value is None. The expected
        values are in the last columns of the matrices in local_importance_values. In this case, the
        dimension of those matrix is (# examples x (# features + 1)). This causes each row to sum to
        the model output for that example.
    """
    try:
        from azureml.core import Experiment, Run
    except ImportError as exp:
        module_logger.error("Could not import azureml.core.run")
        raise exp
    experiment = Experiment(workspace, experiment_name)
    run = Run(experiment, run_id=run_id)
    shap_values, expected_values = get_model_explanation(run)
    return shap_values, expected_values


def get_model_summary_from_run_id(workspace, experiment_name, run_id, global_importance_only=False, top_k=None):
    """Return the feature importance values.

    :param workspace: An object that represents a workspace.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of an experiment_name.
    :type experiment_name: str
    :param run_id: A GUID that represents a run.
    :type run_id: str
    :param global_importance_only: A flag that indicates whether to return per class summary.
    :type global_importance_only: bool
    :param top_k: An integer that indicates the number of the most important features to return.
    :type top_k: int
    :rtype: (list, list, list, list)
    :return: tuple(overall_local_importance_values, overall_important_features,
        per_class_local_importance_values, per_class_important_features) where
        - overall_local_importance_values = The model level feature importance values sorted
        in descending order.
        - overall_important_features = The feature names sorted in the same order as in
        global_importance_values or the indexes that would sort global_importance_values.
        - per_class_local_importance_values = The class level feature importance values
        sorted in descending order where a binary classification (this class or not) is
        evaluated. Only available for the classification case.
        - per_class_important_features = The feature names sorted in the same order as
        in per_class_values or the indexes that would sort per_class_values. Only
        available for the classification case.
    """
    try:
        from azureml.core import Experiment, Run
    except ImportError as exp:
        module_logger.error("Could not import azureml.core.run")
        raise exp
    experiment = Experiment(workspace, experiment_name)
    run = Run(experiment, run_id=run_id)
    return get_model_summary(run, global_importance_only, top_k)


def get_model_summary(run, global_importance_only=False, top_k=None):
    """Return the feature importance values.

    :param run: An object that represents a model explanation run.
    :type run: azureml.core.run.Run
    :param global_importance_only: A flag that indicates whether to return per class summary.
    :type global_importance_only: bool
    :param top_k: An integer that indicates the number of the most important features to return.
    :type top_k: int
    :rtype: (list, list, list, list)
    :return: tuple(overall_local_importance_values, overall_important_features
        per_class_local_importance_values, per_class_important_features) where
        - overall_local_importance_values = The model level feature importance values sorted in
        descending order.
        - overall_important_features = The feature names sorted in the same order as in
        global_importance_values or the indexes that would sort global_importance_values.
        - per_class_local_importance_values = The class level feature importance values
        sorted in descending order where a binary classification (this class or not) is evaluated.
        Only available for the classification case.
        - per_class_important_features = The feature names sorted in the same order as in
        per_class_values or the indexes that would sort per_class_values. Only available for
        the classification case.
    """
    module_logger.warning('WARNING: This API is being deprecated. '
                          'Please use the ExplanationClient for the most up-to-date experience.')
    download_dir = _create_download_dir()
    feature_names = None
    try:
        feature_names = _download_artifact(run, download_dir, History.FEATURES)
    except Exception:
        module_logger.info(
            "features is not found in Artifact service")

    pool = WorkerPool(_parent_logger=module_logger)
    with TaskQueue(worker_pool=pool,
                   _ident="DownloadExplanationSummaries",
                   _parent_logger=module_logger) as task_queue:
        try:
            model_type = run.get_properties()[ExplainType.MODEL]
        except Exception:
            module_logger.info("failed to retrieve model_type from properties, retrieving from metrics instead")
            model_type = run.get_metrics()[ExplainType.MODEL]
        if model_type == ExplainType.CLASSIFICATION and not global_importance_only:
            summaries = [
                History.GLOBAL_IMPORTANCE_VALUES,
                History.GLOBAL_IMPORTANCE_RANK,
                History.PER_CLASS_VALUES,
                History.PER_CLASS_RANK
            ]
            results = []
            for summary_name in summaries:
                task = task_queue.add(_download_model_summary, run, download_dir, summary_name, top_k)
                results.append(task)
            results = list(map(lambda task: task.wait(), results))
            global_importance_values, global_importance_rank, per_class_values, per_class_rank = results
            global_importance = global_importance_rank
            per_class_importance = per_class_rank
            if feature_names is not None:
                global_importance = _sort_feature_list_single(feature_names, global_importance_rank)
                per_class_importance = _sort_feature_list_multiclass(feature_names, per_class_rank)
            return global_importance_values, global_importance, per_class_values, per_class_importance
        else:
            overall_summaries = [
                History.GLOBAL_IMPORTANCE_VALUES,
                History.GLOBAL_IMPORTANCE_RANK
            ]
            overall_results = []
            for summary_name in overall_summaries:
                task = task_queue.add(_download_model_summary, run, download_dir, summary_name, top_k)
                overall_results.append(task)
            overall_results = list(map(lambda task: task.wait(), overall_results))

            global_importance_values, global_importance_rank = overall_results
            global_importance = global_importance_rank
            if feature_names is not None:
                global_importance = _sort_feature_list_single(feature_names, global_importance_rank)
            return global_importance_values, global_importance


def get_classes(run):
    """Return the class names or None if not found in Artifact service.

    :param run: An object that represents a model explanation run.
    :type run: azureml.core.run.Run
    :rtype: numpy.ndarray
    :return: The class names passed to explain_model. The order of the class names matches the model output.
    """
    module_logger.warning('WARNING: This API is being deprecated. '
                          'Please use the ExplanationClient for the most up-to-date experience.')
    download_dir = _create_download_dir()
    classes = None
    try:
        classes = _download_artifact(run, download_dir, 'classes')
    except Exception:
        module_logger.warning(
            "classes is not found in Artifact service")
    return classes
