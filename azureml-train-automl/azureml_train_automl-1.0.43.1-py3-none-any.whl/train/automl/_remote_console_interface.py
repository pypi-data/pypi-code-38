# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Console interface for AutoML experiments logs"""
from typing import Any, DefaultDict, Dict, List
from collections import defaultdict
import json
import numpy as np
import pytz
import time
import warnings
from automl.client.core.common import constants, logging_utilities
from automl.client.core.common.metrics import minimize_or_maximize
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core._experiment_observer import ExperimentStatus
from ._azureautomlsettings import AzureAutoMLSettings
from . import _constants_azureml


class RemoteConsoleInterface():
    """
    Class responsible for printing iteration information to console for a remote run
    """

    def __init__(self, logger, file_logger=None):
        """
        RemoteConsoleInterface constructor
        :param logger: Console logger for printing this info
        :param file_logger: Optional file logger for more detailed logs
        """
        self._ci = None
        self._console_logger = logger
        self.logger = file_logger
        self.metric_map = {}        # type: Dict[str, Dict[str, float]]
        self.run_map = {}           # type: Dict[str, Any]
        self.best_metric = None

    def print_scores(self, parent_run, primary_metric):
        """
        Print all history for a given parent run
        :param parent_run: AutoMLRun to print status for
        :param primary_metric: Metric being optimized for this run
        :return:
        """
        setup_complete = False
        best_metric = None
        parent_run_properties = parent_run.get_properties()
        automl_settings = AzureAutoMLSettings(
            experiment=None, **json.loads(parent_run_properties['AMLSettingsJsonString']))
        tags = parent_run.get_tags()
        total_children_count = int(tags.get('iterations', "0"))
        if total_children_count == 0:
            total_children_count = automl_settings.iterations
        max_concurrency = automl_settings.max_concurrent_iterations

        i = 0
        child_runs_not_finished = []

        while i < total_children_count:
            child_runs_not_finished.append('{}_{}'.format(parent_run.run_id, i))
            i += 1

        objective = minimize_or_maximize(metric=primary_metric)

        while True:
            runs_to_query = child_runs_not_finished[:max_concurrency]

            status = parent_run.get_tags().get('_aml_system_automl_status', None)
            if status is None:
                status = parent_run.get_status()
            if status in ('Completed', 'Failed', 'Canceled'):
                parent_errors = parent_run.get_properties().get('errors')
                if parent_errors is not None and parent_errors.startswith("Setup iteration failed"):
                    if self._ci is None:
                        self._ci = ConsoleInterface("score", self._console_logger)
                    self._ci.print_line("")
                    self._ci.print_error(parent_errors)
                    break
                if runs_to_query is not None and len(runs_to_query) == 0:
                    break

            # initialize ConsoleInterface when setup iteration is complete
            if not setup_complete:
                setup_run_list = list(parent_run._client.run.get_runs_by_run_ids(
                    run_ids=['{}_{}'.format(parent_run.run_id, 'setup')]))
                # if this is a local run there will be no setup iteration
                if len(setup_run_list) == 0:
                    setup_run = parent_run
                else:
                    setup_run = setup_run_list[0]

                if setup_run:
                    if _constants_azureml.Properties.PROBLEM_INFO in setup_run.properties:
                        problem_info_str = setup_run.properties[_constants_azureml.Properties.PROBLEM_INFO]
                        problem_info_dict = json.loads(problem_info_str)
                        subsampling = problem_info_dict.get('subsampling', False)
                        self._ci = ConsoleInterface("score", self._console_logger, mask_sampling=not subsampling)
                        setup_complete = True

                if setup_complete:
                    try:
                        self._ci.print_descriptions()
                        self._ci.print_columns()
                    except Exception as e:
                        logging_utilities.log_traceback(e, self.logger)
                        raise
                else:
                    time.sleep(10)
                    continue

            new_children_dtos = parent_run._client.run.get_runs_by_run_ids(run_ids=runs_to_query)
            runs_finished = []

            for run in new_children_dtos:
                run_id = run.run_id
                status = run.status
                if ((run_id not in self.run_map) and (status in ('Completed', 'Failed'))):
                    runs_finished.append(run_id)
                    self.run_map[run_id] = run

            if runs_finished:
                run_metrics_map = parent_run._client.get_metrics(run_ids=runs_finished)

                for run_id in run_metrics_map:
                    self.metric_map[run_id] = run_metrics_map[run_id]

                for run_id in runs_finished:
                    if "setup" in run_id:
                        continue
                    run = self.run_map[run_id]
                    status = run.status
                    properties = run.properties
                    current_iter = properties.get('iteration', None)
                    # Bug-393631
                    if current_iter is None:
                        continue
                    run_metric = self.metric_map.get(run_id, {})
                    print_line = properties.get('run_preprocessor', "") + " " + properties.get('run_algorithm', "")

                    start_iter_time = run.created_utc.replace(tzinfo=pytz.UTC)

                    end_iter_time = run.end_time_utc.replace(tzinfo=pytz.UTC)

                    iter_duration = str(end_iter_time - start_iter_time).split(".")[0]

                    if primary_metric in run_metric:
                        score = run_metric[primary_metric]
                    else:
                        score = constants.Defaults.DEFAULT_PIPELINE_SCORE

                    if best_metric is None or best_metric == 'nan' or np.isnan(best_metric):
                        best_metric = score
                    elif objective == constants.OptimizerObjectives.MINIMIZE:
                        if score < best_metric:
                            best_metric = score
                    elif objective == constants.OptimizerObjectives.MAXIMIZE:
                        if score > best_metric:
                            best_metric = score
                    else:
                        best_metric = 'Unknown'

                    self._ci.print_start(current_iter)
                    self._ci.print_pipeline(print_line)
                    self._ci.print_end(iter_duration, score, best_metric)

                    errors = properties.get('friendly_errors', None)
                    if errors is not None:
                        error_dict = json.loads(errors)
                        for error in error_dict:
                            self._ci.print_error(error_dict[error])
                    if run_id in child_runs_not_finished:
                        child_runs_not_finished.remove(run_id)

            time.sleep(10)

    def print_featurization_progress(self, parent_run):
        try:
            while True:
                tags = parent_run.get_tags()

                status = tags.get('_aml_system_automl_status', None)
                if status is None:
                    status = parent_run.get_status()
                if status in ('Running', 'Completed', 'Failed', 'Canceled'):
                    break

                preprocessing_progress = tags.get('preprocessing_progress', "")
                if preprocessing_progress == ExperimentStatus.ModelSelection:
                    break

                self._console_logger.print_line("Current status: {}.".format(preprocessing_progress))
                time.sleep(10)
        except Exception:
            pass

    @staticmethod
    def _show_output(current_run, logger, file_logger, primary_metric):
        try:
            remote_printer = RemoteConsoleInterface(
                logger, file_logger)
            remote_printer.print_featurization_progress(current_run)
            remote_printer.print_scores(current_run, primary_metric)
        except KeyboardInterrupt:
            logger.write("Received interrupt. Returning now.")
