# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
import datetime
from dateutil import parser as date_parser
import json
from multiprocessing.dummy import Pool
import operator
import traceback
import urllib
import urllib.request
from urllib.error import HTTPError

from azureml.core.compute.amlcompute import AmlCompute
from azureml.core.run import Run
# noinspection PyProtectedMember
from azureml._restclient.run_client import RunClient
# noinspection PyProtectedMember
from azureml._restclient.metrics_client import MetricsClient
# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger
# noinspection PyProtectedMember
from azureml.widgets._constants import WIDGET_REFRESH_SLEEP_TIME, WIDGET_REFRESH_SLEEP_TIME_DATABRICKS, \
    WEB_WORKBENCH_PARENT_RUN_ENDPOINT
from azureml.widgets.run_details import RunDetails, PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._widget_run_details_base import _WidgetRunDetailsBase
# noinspection PyProtectedMember
from azureml.widgets._transformer import _DataTransformer

_logger = _TelemetryLogger.get_telemetry_logger(__name__)

if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._widget import _UserRunWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._universal_widget import _UserRunWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


class _UserRunDetails(_WidgetRunDetailsBase):
    """Generic run details widget."""

    _metrics_cache = {}
    _run_finished_states = ["completed", "failed", "canceled"]
    _str_waiting_log = "Your job is submitted in Azure cloud and we are monitoring to get logs..."
    _str_no_log = "Log is empty or no log files found."
    _str_no_selected_log = "No log is selected"

    def __init__(self, run_instance, run_type="experiment", refresh_time=REFRESH_SLEEP_TIME,
                 widget=_UserRunWidget, recursive_children=False, rehydrate_runs=False):
        self.experiment = run_instance.experiment
        self.run_instance = run_instance
        self.run_client = RunClient(
            service_context=self.experiment.workspace.service_context,
            experiment_name=self.experiment.name,
            run_id=self.run_instance.id,
            user_agent="azureml-sdk-widget-{}".format(run_type))
        self.metrics_client = MetricsClient(
            service_context=self.experiment.workspace.service_context,
            experiment_name=self.experiment.name,
            run_id=self.run_instance.id,
            user_agent="azureml-sdk-widget-{}".format(run_type))
        self.transformer = self._create_transformer()
        self.child_widget_instance = None
        self._transformed_child_runs_cache = []
        self._run_cache = {}
        self.error = None
        self.run_properties = {}
        self.properties = None
        self.tags = {}
        created_utc = self.run_instance._run_dto['created_utc']
        self.run_init_time = date_parser.parse(created_utc) if not isinstance(created_utc, datetime.datetime) \
            else created_utc
        self.run_type = run_type
        self.recursive_children = recursive_children
        self.rehydrate_runs = rehydrate_runs
        self.selected_run_log = None
        self.auto_cluster = False
        _logger.info("Creating worker pool")
        self._pool = Pool()
        super().__init__(refresh_time, widget)

    def __del__(self):
        """Destructor for the widget."""
        _logger.info("Closing worker pool")
        self._pool.close()
        if super().__del__:
            super().__del__()

    @staticmethod
    def _boundary_partition(seq, delegate):
        """
        Generator which partitions a sequence across boundary conditions declared by a boolean delegate.

        Similar to Clojure [partition-by] ( https://clojuredocs.org/clojure.core/partition-by ),
        but only matches on booleans, and yields whether or not the output sub-sequence matched the delegate.

        Example:
        ([1, 2, 4, 6, 7, 9], is_even) yields { (false, [1]), (true, [2, 4, 6]), (false, [7, 9]) }

        Empty input sequences yield nothing.
        """
        buffer = None
        state = None
        for i in seq:
            if state is None:
                # This is the first item; set it as the initial state, and begin building the buffer
                state = bool(delegate(i))
                buffer = [i]
            elif state == bool(delegate(i)):
                # This item matches the current state; add it to the buffer
                buffer.append(i)
            else:
                # This item does not match the existing state; yield current (state, buffer) pair and build anew
                if buffer:
                    yield (state, buffer)
                    buffer = [i]
                # Invert the state, since we did not match it
                state = not state
        if buffer:
            # By this time, state should always be a boolean if the buffer is not empty
            assert(state is not None)
            yield (state, buffer)

    @staticmethod
    def _numeric_grouping_ordinal(item: str) -> tuple:
        """Declares numeric tuple ordering for strings"""
        ords = []
        for (isnum, seq) in _UserRunDetails._boundary_partition(item, lambda s: s.isnumeric()):
            if isnum:
                ords.append(int("".join(seq)))
        return tuple(ords)

    @staticmethod
    def _sort_log_names(log_names):
        """Ensures logs are sorted by numeric tuple ordering"""
        return sorted(log_names, key=_UserRunDetails._numeric_grouping_ordinal)

    @staticmethod
    def _sort_logs_by_prefix(log_names):
        """Ensures logs are sorted by numeric tuple ordering, partitioning results by the first column"""
        logs_with_ordinals = [(log, _UserRunDetails._numeric_grouping_ordinal(log)) for log in log_names]
        logs_with_ordinals.sort(key=lambda i: i[1])
        by_prefix = dict()
        for (log_name, ordinal) in logs_with_ordinals:
            prefix = ordinal[0] if ordinal else -1  # -1 cannot arise from the ordinal "isnumeric" partitioning
            by_prefix.setdefault(prefix, []).append(log_name)
        ordered = [by_prefix[k] for k in sorted(by_prefix.keys())]
        return ordered

    def get_widget_data(self, widget_settings=None):
        """
        Retrieve and transform data from run history to be rendered by widget

        :param widget_settings: Settings to be applied to widget. Supported settings are: 'debug' and 'display'
        :type widget_settings: dict
        :return: Dictionary containing data to be rendered by the widget.
        :rtype: dict
        """
        if not self.settings:
            self.settings = widget_settings

        # set azure portal deep link for the run
        self.widget_instance.workbench_uri = self._get_web_workbench_run_detail_url(self.experiment)

        self.widget_instance.run_id = self.run_instance.id
        self.tags = self.run_instance.get_tags()

        run_properties_init = {'run_id': self.run_instance.id,
                               'created_utc': self.run_instance._run_dto['created_utc'],
                               'properties': self.run_instance.get_properties(),
                               'tags': self.tags}

        self.run_properties = {**self.run_properties, **run_properties_init}

        self.widget_instance.run_properties = self.run_properties

        self._pool.apply_async(func=self._get_run_metrics, callback=self._update_metrics)

        run_details = self.run_instance.get_details()

        self.error = run_details.get("error")
        run_config = run_details.get("runDefinition")

        if run_config:
            _aml_compute = run_config.get('AmlCompute') if run_config.get('Target') == 'amlcompute' else None
            self.auto_cluster = _aml_compute and _aml_compute.get('VmSize')
            self.run_properties['script_name'] = run_config.get('Script')
            self.run_properties['arguments'] = " ".join(run_config['Arguments']) \
                if 'Arguments' in run_config and run_config['Arguments'] else None

        self._pool.apply_async(func=self._get_compute_target_status, args=(run_details.get("target"),),
                               callback=self._update_compute_target_status)

        # get parent run properties
        self.run_properties['end_time_utc'] = run_details.get("endTimeUtc")
        self.run_properties['status'] = self.tags.get("_aml_system_automl_status") \
            if self.tags.get("_aml_system_automl_status") else run_details.get("status")

        # log file handling
        log_files = run_details.get("logFiles") or {}
        self.run_properties['log_files'] = log_files
        log_order_groups = _UserRunDetails._sort_logs_by_prefix(log_files.keys())
        self.run_properties['log_groups'] = log_order_groups

        # other properties
        self._add_additional_properties(self.run_properties)

        run_properties_temp = copy.deepcopy(self.run_properties)
        run_properties_temp['SendToClient'] = '1'
        self.widget_instance.run_properties = run_properties_temp
        self.properties = self.run_properties['properties']

        # selected log handling- write content for current selection or lowest log in prefix
        selected_log = self.selected_run_log
        if (not selected_log) and log_order_groups:
            # select the first item of the highest prefix
            selected_log = log_order_groups[-1][0]

        if PLATFORM == 'JUPYTER':
            # selected_log can be None here, resulting in user-friendly messages
            self._get_run_logs_async(log_files,
                                     self.run_properties['status'],
                                     self.error,
                                     selected_log)
        else:
            assert PLATFORM == "DATABRICKS"
            self._update_logs(self._get_run_logs(log_files, self.run_properties['status'], self.error, selected_log))

        # handle child runs
        child_runs = self._get_child_runs()

        # Widget renders child runs in two phases. In phase one it retrieves the child runs from backend and
        # renders them with corresponding properties. Then, in second phase, when their metrics are retrieved
        # it renders child runs again, this time it updates each child run with its corresponding best metric value.
        # we keep this cache for two purposes:
        # 1. so that in next refresh iteration we do not lose the metrics and user keeps seeing
        # updated child runs on the client
        # 2. Only query the backend for runs that are not completed
        copy_cache = copy.deepcopy(self._transformed_child_runs_cache)
        for c in child_runs:
            _run = next((x for x in copy_cache if x['run_number'] == c['run_number']), None)
            if not _run:
                # todo: switch to dict
                copy_cache.append(c)
            else:
                ind = copy_cache.index(_run)
                copy_cache[ind] = {**_run, **c}

        self.widget_instance.child_runs = copy_cache
        self._transformed_child_runs_cache = copy_cache

        # get the run with smallest datetime that is already running. We do not need to get the older runs as they
        # are completed and cached
        incomplete_runs = [x for x in self._transformed_child_runs_cache if x['status'].lower() not in
                           _UserRunDetails._run_finished_states]

        if incomplete_runs:
            def parse_created_time(date):
                return date_parser.parse(date) if not isinstance(date, datetime.datetime) else date

            self.run_init_time = min(parse_created_time(run['created_time_dt']) for run in incomplete_runs)

        transformed_children_metrics = {}
        if self._transformed_child_runs_cache:
            run_ids = [x['run_id'] for x in self._transformed_child_runs_cache]

            metrics = {}

            # get list of not cached runs for which we will retrieve metrics
            not_cached_runs = [x for x in self._transformed_child_runs_cache if x['run_id']
                               not in _UserRunDetails._metrics_cache]
            if not_cached_runs:
                metrics = self._get_metrics(not_cached_runs)

                # populate cache with metrics from completed runs
                completed_run_ids = [x['run_id'] for x in self._transformed_child_runs_cache
                                     if x['status'].lower() in _UserRunDetails._run_finished_states]
                metrics_to_be_cached = {k: v for k, v in metrics.items() if k in completed_run_ids}
                _UserRunDetails._metrics_cache = {**_UserRunDetails._metrics_cache, **metrics_to_be_cached}

            cached_run_metrics = {k: v for k, v in _UserRunDetails._metrics_cache.items() if k in run_ids}
            metrics = {**cached_run_metrics, **metrics}

            mapped_metrics = self._get_mapped_metrics(metrics, self._transformed_child_runs_cache)

            transformed_children_metrics = self.transformer.transform_widget_metric_data(mapped_metrics,
                                                                                         self._get_primary_config())
            self.widget_instance.child_runs_metrics = transformed_children_metrics

            updated_runs = self._update_children_with_metrics(self._transformed_child_runs_cache,
                                                              transformed_children_metrics)
            if updated_runs:
                self._transformed_child_runs_cache = sorted(updated_runs, key=operator.itemgetter("run_number"))
                self.widget_instance.child_runs = self._transformed_child_runs_cache

        return {'status': self.run_properties['status'],
                'workbench_run_details_uri': self._get_web_workbench_run_detail_url(self.experiment),
                'run_id': self.run_instance.id,
                'run_properties': self.run_properties,
                'child_runs': self.widget_instance.child_runs,
                'children_metrics': self.widget_instance.child_runs_metrics,
                'run_metrics': self.widget_instance.run_metrics,
                'run_logs': self.widget_instance.run_logs,
                'widget_settings': widget_settings}

    def _add_additional_properties(self, run_properties):
        run_properties['run_duration'] = self.transformer._get_run_duration(run_properties['status'],
                                                                            run_properties['created_utc'],
                                                                            run_properties['end_time_utc'])

    def _get_compute_target_status(self, target_name):
        if not self.auto_cluster:
            ws_targets = []
            try:
                ws_targets = self.experiment.workspace.compute_targets
            except Exception as e:
                if self.isDebug:
                    _logger.warning(e)

            for ct_name in ws_targets:
                ct = ws_targets[ct_name]
                if ct.name == target_name and type(ct) is AmlCompute:
                    ct_dict = {
                        "provisioning_state": ct.provisioning_state,
                        "provisioning_errors": ct.provisioning_errors
                    }
                    status_dict = {}
                    ct_status = ct.get_status()
                    if ct_status:
                        status_dict = {
                            "target_node_count": ct_status.target_node_count,
                            "allocation_state": ct_status.allocation_state,
                            "node_state_counts": ct_status.node_state_counts.serialize(),
                            "scale_settings": ct_status.scale_settings.serialize(),
                            "vm_size": ct_status.vm_size,
                            "current_node_count": ct_status.current_node_count,
                        }
                    return {**ct_dict, **status_dict}
        else:
            # Temporarily read from both tags for backwards compatibility
            _ct_status_str = self.tags.get('_aml_system_ComputeTargetStatus')
            if not _ct_status_str:
                _ct_status_str = self.tags.get('ComputeTargetStatus')
            if _ct_status_str:
                _ct_status = json.loads(_ct_status_str)

                return {
                    "allocation_state": _ct_status.get('AllocationState'),
                    "current_node_count": _ct_status.get('CurrentNodeCount'),
                    "target_node_count": _ct_status.get('TargetNodeCount'),
                    "node_state_counts": {
                        "preparingNodeCount": _ct_status.get('PreparingNodeCount'),
                        "runningNodeCount": _ct_status.get('RunningNodeCount')
                    }
                }

        return {}

    def _update_compute_target_status(self, result):
        self.widget_instance.compute_target_status = result

    def _get_run_logs_async(self, log_files, status, error, selected_log):
        self._pool.apply_async(func=self._get_run_logs, args=(log_files, status, error, selected_log),
                               callback=self._update_logs)

    def _get_run_logs(self, log_files, status, error, selected_log):
        _status = status.lower()
        logs = _UserRunDetails._str_no_log \
            if _status in _UserRunDetails._run_finished_states \
            else _UserRunDetails._str_waiting_log

        if log_files and selected_log and (selected_log in log_files):
            received_log = self._get_log(selected_log, log_files[selected_log])
            if received_log is not None:
                received_log = self._post_process_log(selected_log, received_log)
        else:
            received_log = None

        _logs = received_log or ""

        if error:
            inner_error = error.get('error')
            error_message = inner_error.get('message') if inner_error else ""
            _error = "" if not error_message else "{0}\n".format(error_message)
            _logs = "{0}\nError occurred: {1}".format(_logs, _error)
        elif _status in ['completed', 'canceled']:
            _logs = "{0}\nRun is {1}.".format(_logs, _status)

        if _logs:
            logs = _logs
        return logs

    def _get_log(self, log_name: str, log_uri: str):
        if log_uri:
            try:
                with urllib.request.urlopen(log_uri) as response:
                    log_content = response.read().decode('utf-8')
                log_content = self._post_process_log(log_name, log_content)
                return log_content
            except HTTPError as e:
                if self.isDebug:
                    self.widget_instance.error = repr(traceback.format_exception(type(e), e, e.__traceback__))
                return None
        return None

    def _post_process_log(self, log_name: str, log_content: str) -> str:
        return log_content if len(log_content) == 0 or log_content.endswith("\n") else "{}\n".format(log_content)

    def _update_logs(self, result):
        self.widget_instance.run_logs = result

    def _get_child_runs(self):
        # put a buffer for look-back due to time sync
        buffered_init_time = self.run_init_time - datetime.timedelta(seconds=20)
        child_run_dtos = self.run_client.get_child_runs(
            root_run_id=self.run_instance.id,
            recursive=self.recursive_children,
            _filter_on_server=True,
            created_after=buffered_init_time)

        if self.rehydrate_runs:
            child_runs = list(Run._rehydrate_runs(self.experiment, child_run_dtos))
        else:
            child_runs = list(Run._dto_to_run(self.experiment, child) for child in child_run_dtos)

        for child_run in child_runs:
            self._run_cache[child_run.id] = child_run

        return self.transformer.transform_widget_run_data(child_runs)

    def _get_run_metrics(self):
        run_metrics = MetricsClient.convert_metrics_to_objects(self.run_instance.get_metrics(populate=True))
        transformed_run_metrics = []

        for key, value in run_metrics.items():
            metric_data = {
                'name': key,
                'run_id': self.run_instance.id,
                # get_metrics can return array or not based on metrics being series or scalar value
                'categories': list(range(len(value))) if isinstance(value, list) else [0],
                'series': [{'data': value if isinstance(value, list) else [value]}]}
            transformed_run_metrics.append(metric_data)

        model_explanation_metric = self._get_model_explanation_metric()
        if (model_explanation_metric):
            transformed_run_metrics.append(model_explanation_metric)

        return transformed_run_metrics

    def _get_model_explanation_metric(self):
        if self.tags.get('model_explanation') != 'True':
            return None

        try:
            # Take a soft dependency on azureml-explain-model
            from azureml.explain.model._internal.explanation_client import ExplanationClient

            client = ExplanationClient.from_run(self.run_instance)
            explanation = client.download_model_explanation()

            if explanation is None:
                return None

            class_labels = None
            if hasattr(explanation, 'classes'):
                class_labels = explanation.classes
            overall_summary = explanation.get_ranked_global_values()
            overall_imp = explanation.get_ranked_global_names()
            # Classification Model's explanation includes Per_class information while Regression Model does not
            per_class_summary = None
            per_class_imp = None
            if hasattr(explanation, 'get_ranked_per_class_values'):
                per_class_summary = explanation.get_ranked_per_class_values()
            if hasattr(explanation, 'get_ranked_per_class_names'):
                per_class_imp = explanation.get_ranked_per_class_names()

            return {'name': 'model_explanation',
                    'run_id': self.run_instance.id,
                    'categories': [0],
                    'series': [{'data': [{
                        # 'classes': class_labels,
                        # 'global_importance_values': overall_summary,
                        # 'global_importance_names': overall_imp,
                        # 'per_class_values': per_class_summary,
                        # 'per_class_names': per_class_imp}]}]}
                        'class_labels': class_labels,
                        'overall_summary': overall_summary,
                        'overall_imp': overall_imp,
                        'per_class_summary': per_class_summary,
                        'per_class_imp': per_class_imp}]}]}
        except ImportError as import_error:
            _logger.error(import_error.msg)
            return None

    def _update_metrics(self, result):
        self.widget_instance.run_metrics = result

    def _get_metrics(self, child_runs):
        child_run_ids = [run['run_id'] for run in child_runs]
        # TODO: don't have a special method for widgets
        # noinspection PyProtectedMember
        return self.metrics_client.get_metrics_for_widgets(child_run_ids)

    def _get_mapped_metrics(self, metrics, child_runs):
        run_number_mapper = {c['run_id']: c['run_number'] for c in child_runs}
        return {run_number_mapper[k]: v for k, v in metrics.items()}

    def _update_children_with_metrics(self, child_runs, metrics):
        pass

    def _get_web_workbench_run_detail_url(self, experiment):
        """Generate the web workbench job url for the run details.

        :param experiment: The experiment.
        :type experiment: azureml.core.experiment.Experiment
        """
        # TODO: Host to web workbench needs to be retrieved
        return (WEB_WORKBENCH_PARENT_RUN_ENDPOINT).format(
            experiment.workspace.subscription_id,
            experiment.workspace.resource_group,
            experiment.workspace.name,
            experiment.name,
            self.run_instance.id)

    def _get_primary_config(self):
        if self.settings and 'Metric' in self.settings:
            return {
                'name': self.settings['Metric']['name'],
                'goal': self.settings['Metric']['goal'] if 'goal' in self.settings['Metric'] else 'minimize'
            }
        return {}

    def _should_stop_refresh(self, widget_data):
        return \
            widget_data['run_properties']['status'] is not None and \
            widget_data['run_properties']['status'].lower() in _UserRunDetails._run_finished_states

    def _register_events(self):
        self._register_event(self._on_selected_run_id_change, "selected_run_id")
        self._register_event(self._on_selected_run_log_change, "selected_run_log")

    def _on_selected_run_log_change(self, change):
        self.selected_run_log = change.new
        self._get_run_logs_async(self.widget_instance.run_properties['log_files'],
                                 self.widget_instance.run_properties['status'],
                                 self.error, change.new)

    def _on_selected_run_id_change(self, change):
        # work around about close of popup, selected_run_id is set to empty string right after with it is set
        # with value
        if change.new == '':
            return
        if self.child_widget_instance is not None and change.new != '':
            self.child_widget_instance.close()
        if self.widget_instance.child_runs:
            run_list = [x for x in self.widget_instance.child_runs if x['run_id'] == change.new]
            if len(run_list) > 0:
                run = self._run_cache[change.new]
                selected_run_widget = RunDetails(run)  # type: _WidgetRunDetailsBase
                display_setting = self.settings["childWidgetDisplay"] if "childWidgetDisplay" in self.settings else ""
                selected_run_widget.show(widget_settings={'display': display_setting})
                self.child_widget_instance = selected_run_widget.widget_instance

    def _get_telemetry_values(self, func):
        telemetry_values = super()._get_telemetry_values(func)
        telemetry_values['widgetRunType'] = self.run_type
        return telemetry_values

    # noinspection PyMethodMayBeStatic
    def _create_transformer(self):
        return _DataTransformer()
