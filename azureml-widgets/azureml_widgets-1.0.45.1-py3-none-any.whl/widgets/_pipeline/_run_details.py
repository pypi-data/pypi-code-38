# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from multiprocessing.dummy import Pool

from azureml.widgets._constants import MULTIRUN_WIDGET_REFRESH_SLEEP_TIME, WIDGET_REFRESH_SLEEP_TIME_DATABRICKS
from azureml.widgets.run_details import PLATFORM
# noinspection PyProtectedMember
from azureml.widgets._userrun._run_details import _UserRunDetails
# noinspection PyProtectedMember
from azureml.widgets._pipeline._transformer import _PipelineGraphTransformer
# noinspection PyProtectedMember
from azureml.widgets._telemetry_logger import _TelemetryLogger

_logger = _TelemetryLogger.get_telemetry_logger(__name__)

if PLATFORM == 'JUPYTER':
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._widget import _UserRunWidget
    # noinspection PyProtectedMember
    from azureml.widgets._pipeline._widget import _PipelineWidget
    REFRESH_SLEEP_TIME = MULTIRUN_WIDGET_REFRESH_SLEEP_TIME
else:
    assert PLATFORM == "DATABRICKS"
    # noinspection PyProtectedMember
    from azureml.widgets._userrun._universal_widget import _UserRunWidget
    # noinspection PyProtectedMember
    from azureml.widgets._pipeline._universal_widget import _PipelineWidget
    REFRESH_SLEEP_TIME = WIDGET_REFRESH_SLEEP_TIME_DATABRICKS


class _StepRunDetails(_UserRunDetails):
    """StepRun run details widget."""

    def __init__(self, run_instance):
        """
        Initialize a StepRun widget call.
        """
        _logger.info("Creating worker pool")
        self._pool = Pool()
        super().__init__(run_instance, "Pipeline", refresh_time=REFRESH_SLEEP_TIME,
                         widget=_UserRunWidget, rehydrate_runs=True)

    def __del__(self):
        """Destructor for the widget."""
        _logger.info("Closing worker pool")
        self._pool.close()
        if super().__del__:
            super().__del__()

    def _get_run_logs_async(self, log_files, status, error, process):
        self._pool.apply_async(func=self._get_run_logs, args=(log_files, status, error, process),
                               callback=self._update_logs)

    def _get_run_logs(self, log_files, status, error, process):
        _status = status.lower()
        logs = _UserRunDetails._str_waiting_log \
            if _status in _UserRunDetails._run_finished_states \
            else _UserRunDetails._str_no_log

        stdout_log = self.run_instance.get_stdout_log()
        stderr_log = self.run_instance.get_stderr_log()
        job_log = self.run_instance.get_job_log()
        if stdout_log or stderr_log or job_log:
            return "{0}\n{1}\n".format(job_log, stdout_log) \
                   + ("Error occurred: {0}\n".format(stderr_log) if stderr_log else "")
        else:
            return logs

    def _create_transformer(self):
        return _PipelineGraphTransformer()


class _PipelineRunDetails(_UserRunDetails):
    """Pipeline run details widget."""

    def __init__(self, run_instance):
        """
        Initialize a Pipeline widget call.
        """
        super().__init__(run_instance, "Pipeline", refresh_time=MULTIRUN_WIDGET_REFRESH_SLEEP_TIME,
                         widget=_PipelineWidget, rehydrate_runs=True)

    def get_widget_data(self, widget_settings=None):
        widget_data = super().get_widget_data(widget_settings)
        graph = self.transformer._transform_graph(self.run_instance.get_graph(),
                                                  list(self._run_cache.values()))
        widget_data['child_runs'] = graph['child_runs']
        widget_data['graph'] = graph
        self.widget_instance.child_runs = graph['child_runs']
        self.widget_instance.graph = graph
        return widget_data

    def _create_transformer(self):
        return _PipelineGraphTransformer()
