# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Access metrics client"""
import logging
import os

from collections import defaultdict

from azureml.core._metrics import (_metric_type_initializers, Artifact, InlineMetric, ImageMetric,
                                   INLINE_METRICS, AZUREML_TABLE_METRIC_TYPE, AZUREML_OLD_IMAGE_METRIC_TYPE)

from azureml.exceptions import AzureMLException
from azureml._logging import START_MSG, STOP_MSG
from azureml._async import TaskQueue, BatchTaskQueue

from .contracts.utils import get_metric_types_filter_expression
from .run_client import RunClient
from .models.batch_metric_dto import BatchMetricDto

module_logger = logging.getLogger(__name__)

AZUREML_METRICS_CLIENT_BATCH_SIZE_ENV_VAR = "AZUREML_METRICS_BATCH_SIZE"
AZUREML_METRICS_CLIENT_BATCH_CUSHION_ENV_VAR = "AZUREML_METRICS_BATCH_CUSHION"
AZUREML_METRICS_CLIENT_POLLING_INTERVAL_ENV_VAR = "AZUREML_METRICS_POLLING_INTERVAL"

AZUREML_MAX_NUMBER_METRICS_BATCH = 50
AZUREML_METRICS_CLIENT_BATCH_CUSHION = 5
AZUREML_METRICS_CLIENT_MIN_POLLING_INTERVAL = 1  # Minimum supported interval


class MetricsClient(RunClient):
    """Metrics client class"""

    def __init__(self, *args, **kwargs):
        self._use_batch = kwargs.pop("use_batch", True)
        self._flush_eager = kwargs.pop("flush_eager", False)
        super(MetricsClient, self).__init__(*args, **kwargs)
        self._task_queue_internal = None

    @property
    def _task_queue(self):
        if self._task_queue_internal is not None:
            return self._task_queue_internal

        if self._use_batch:
            max_batch_size = int(os.environ.get(AZUREML_METRICS_CLIENT_BATCH_SIZE_ENV_VAR,
                                                AZUREML_MAX_NUMBER_METRICS_BATCH))
            batch_cushion = int(os.environ.get(AZUREML_METRICS_CLIENT_BATCH_CUSHION_ENV_VAR,
                                               AZUREML_METRICS_CLIENT_BATCH_CUSHION))
            interval = int(os.environ.get(AZUREML_METRICS_CLIENT_POLLING_INTERVAL_ENV_VAR,
                                          AZUREML_METRICS_CLIENT_MIN_POLLING_INTERVAL))
            self._logger.debug(
                "Overrides: Max batch size: {0}, batch cushion: {1}, Interval: {2}.".format(
                    max_batch_size, batch_cushion, interval))

            self._task_queue_internal = BatchTaskQueue(self._log_batch,
                                                       worker_pool=self._pool,
                                                       interval=interval,
                                                       max_batch_size=max_batch_size,
                                                       batch_cushion=batch_cushion,
                                                       _ident="PostMetricsBatch",
                                                       _parent_logger=self._logger)
        else:
            self._task_queue_internal = TaskQueue(worker_pool=self._pool,
                                                  _ident="PostMetricsSingle",
                                                  _parent_logger=self._logger)

        self._logger.debug("Used {} for use_batch={}.".format(type(self._task_queue_internal), self._use_batch))
        return self._task_queue_internal

    def get_rest_client(self, user_agent=None):
        """get service rest client"""
        return self._service_context._get_metrics_restclient(user_agent=user_agent)

    @classmethod
    def dto_to_metrics_dict(cls, metrics_dto, artifact_client=None, populate=False,
                            data_container=None):
        """convert metrics_dto to dictionary"""
        out = {}
        metric_types = {}
        original_cell_types = {}
        for metric in metrics_dto:
            name = metric.name
            data_location = metric.data_location
            metric_type = metric.metric_type
            schema = metric.schema
            cell_types = {prop.property_id: prop.type for prop in schema.properties}
            if name not in metric_types:
                metric_types[name] = metric_type
                original_cell_types[name] = cell_types

            if metric_types[name] == metric_type:
                if metric_type in INLINE_METRICS:
                    if metric_type == AZUREML_TABLE_METRIC_TYPE:
                        InlineMetric.add_table(name, out, original_cell_types[name], metric.cells, cell_types)
                    else:
                        InlineMetric.add_cells(name, out, original_cell_types[name], metric.cells, cell_types)
                else:
                    if metric_type == AZUREML_OLD_IMAGE_METRIC_TYPE:
                        data_location = metric.cells[0][name]
                    # TODO: don't pass is_image_metric
                    is_image_metric = _metric_type_initializers[metric_type] == ImageMetric
                    artifact = Artifact.create_unpopulated_artifact_from_data_location(data_location,
                                                                                       metric_type,
                                                                                       is_image_metric,
                                                                                       data_container)
                    if populate:
                        artifact.retrieve_artifact(artifact_client)
                    value = artifact if populate else artifact.data_location

                    if name in out:
                        if not isinstance(out[name], list):
                            out[name] = [out[name]]
                        out[name].append(value)
                    else:
                        out[name] = value
            else:
                module_logger.warning("Conflicting metric types, logged metric "
                                      "of type: {} to name: {}, expected metric "
                                      "type is {}".format(metric_type, name,
                                                          metric_types[name]))
        return out

    def _get_metrics_for_run(self, metric_types=None):
        """get metrics with the same run_id"""
        expression = "{}{}".format("RunId eq ", self._run_id)
        if metric_types is not None:
            metric_expression = get_metric_types_filter_expression(metric_types)
            expression = "({}) and ({})".format(expression, metric_expression)
        return self._execute_with_experiment_arguments(self._client.run_metric.list,
                                                       filter=expression,
                                                       is_paginated=True)

    def _get_metrics_for_runs(self, run_ids, use_batch=False, metric_types=None):
        metric_dtos_by_run = defaultdict(list)

        if use_batch:
            tasks = self.get_metrics_in_batches_by_run_ids(run_ids, metric_types=metric_types)
        else:
            tasks = [self.get_metrics_by_run_ids(run_ids=run_ids, metric_types=metric_types)]

        for task in tasks:
            for dto in task:
                metric_dtos_by_run[dto.run_id].append(dto)

        return metric_dtos_by_run

    @staticmethod
    def convert_metrics_to_objects(metrics):
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, Artifact) and not metric_value._is_image_metric:
                metrics[metric_name] = metric_value.convert_to_object()
        return metrics

    def get_all_metrics(self, run_ids=None, populate=False, artifact_client=None,
                        convert_to_object=False, use_batch=False, metric_types=None,
                        data_container=None):
        if run_ids is None:
            metric_dtos_by_run = {self._run_id: self._get_metrics_for_run(metric_types=metric_types)}
        else:
            metric_dtos_by_run = self._get_metrics_for_runs(run_ids, use_batch=use_batch, metric_types=metric_types)

        if convert_to_object:
            metrics = {
                runid: MetricsClient.convert_metrics_to_objects(
                    self.dto_to_metrics_dict(metric_dto_list, populate=populate,
                                             artifact_client=artifact_client,
                                             data_container=data_container)
                ) for runid, metric_dto_list in metric_dtos_by_run.items()
            }
        else:
            metrics = {
                runid: self.dto_to_metrics_dict(metric_dto_list, populate=populate,
                                                artifact_client=artifact_client,
                                                data_container=data_container)
                for runid, metric_dto_list in metric_dtos_by_run.items()
            }

        if run_ids is None:
            return metrics[self._run_id]
        return metrics

    # TODO: find a better way to do this (with artifacts it breaks)
    def get_metrics_for_widgets(self, run_ids):
        metric_types = INLINE_METRICS
        metrics = self.get_all_metrics(run_ids, use_batch=True, metric_types=metric_types)

        # convert non-(list, dict) metrics (i.e. scalar metrics logged only once to lists)
        # this is necessary because current widget code expects everything as a list or dict
        for run_id, run_metrics in metrics.items():
            for metric_name, metric_value in run_metrics.items():
                if isinstance(metric_value, list) or isinstance(metric_value, dict):
                    continue
                else:
                    metrics[run_id][metric_name] = [metric_value]

        return metrics

    def flush(self, timeout_seconds=120):
        with self._log_context("FlushingMetricsClient"):
            self._task_queue.flush(self.identity, timeout_seconds=timeout_seconds)

    def log(self, metric):
        metric_dto = metric.create_metric_dto()
        if isinstance(self._task_queue, BatchTaskQueue):
            self._task_queue.add_item(metric_dto)
        else:
            ident = "{}_{}".format(self._task_queue._tasks.qsize(), self._task_queue._identity)
            async_task = self._execute_with_run_arguments(self._client.run_metric.post,
                                                          metric_dto,
                                                          is_async=True,
                                                          new_ident=ident)
            self._task_queue.add_task(async_task)
            if not self._flush_eager:
                return async_task

        if self._flush_eager:
            self.flush()

    def _log_batch(self, metric_dtos, is_async=False):
        if len(metric_dtos) > AZUREML_MAX_NUMBER_METRICS_BATCH:
            raise AzureMLException("Number of metrics {} is greater than "
                                   "the max number of metrics that should be "
                                   "sent in batch {}".format(len(metric_dtos),
                                                             AZUREML_MAX_NUMBER_METRICS_BATCH))

        batch_metric_dto = BatchMetricDto(metric_dtos)
        res = self._execute_with_run_arguments(self._client.run_metric.post_batch,
                                               batch_metric_dto,
                                               is_async=is_async)
        return res

    def __enter__(self):
        self._logger.debug(START_MSG)
        return self

    def __exit__(self, *args):
        self.flush()
        self._logger.debug(STOP_MSG)
