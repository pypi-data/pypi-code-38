# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""run.py, module for running pipeline."""
from __future__ import print_function
import time
import sys
import re
import json
from azureml.core import Run, Experiment, ScriptRun
from azureml._restclient.utils import create_session_with_retry
from azureml.exceptions import ExperimentExecutionException, ActivityFailedException
from azureml._execution import _commands

RUNNING_STATES = ['NotStarted', 'Running', 'Queued', 'Unknown']


class PipelineRun(Run):
    """
    PipelineRun represents a run of a :class:`azureml.pipeline.core.Pipeline`.

    This class can be used to manage, check status and retrieve run details once a pipeline run is submitted.
    Use :func:`azureml.pipeline.core.PipelineRun.get_steps` to retrieve the
    :class:`azureml.pipeline.core.StepRun` objects which are created by this pipeline run. Other uses include
    retrieving the :class:`azureml.pipeline.core.graph.Graph` object associated with the pipeline run, fetching the
    status of the pipeline run, and waiting for run completion.

    .. remarks::

        A PipelineRun object is returned when submitting a Pipeline through :func:`azureml.core.Experiment.submit`.
        For more information on how to create and submit a Pipeline see the following link:
        https://aka.ms/pl-first-pipeline.

        A PipelineRun can also be instantiated with the :class:`azureml.core.Experiment` the run was submitted to
        and the PipelineRun id as follows:

        .. code-block:: python

            from azureml.core import Experiment
            from azureml.pipeline.core import PipelineRun

            experiment = Experiment(workspace, "<experiment_name>")
            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")

        Use :func:`azureml.pipeline.core.PipelineRun.wait_for_completion` to monitor the run status and optionally
        stream run logs.

        Use :func:`azureml.pipeline.core.PipelineRun.get_status` to fetch the run status.

        Use :func:`azureml.pipeline.core.PipelineRun.cancel` to cancel an ongoing PipelineRun.

        A PipelineRun will generate a :class:`azureml.pipeline.core.StepRun` for each step in the Pipeline.
        Use :func:`azureml.pipeline.core.PipelineRun.get_steps` to list the generated StepRuns.

    :param experiment: The Experiment object associated with the PipelineRun.
    :type experiment: azureml.core.Experiment
    :param run_id: The run id of the PipelineRun.
    :type run_id: str
    """

    def __init__(self, experiment, run_id, _service_endpoint=None):
        """
        Initialize a Pipeline run.

        :param experiment: The Experiment object associated with the PipelineRun.
        :type experiment: azureml.core.Experiment
        :param run_id: The run id of the PipelineRun.
        :type run_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                      service_endpoint=_service_endpoint)
        self._pipeline_run_provider = self._context.workflow_provider.pipeline_run_provider
        self._graph = None
        super(self.__class__, self).__init__(experiment, run_id)

    #######################################
    # Run methods
    #######################################

    def get_tags(self):
        """
        Get the set of tags for the run.

        :return: The dictionary of tags for the run.
        :rtype: dict
        """
        # Temporary workaround to return an empty set of tags when the tag list is not set
        try:
            return super(self.__class__, self).get_tags()
        except KeyError:
            return {}

    def _get_status(self):
        """
        Get the current status of the pipeline run.

        :return: The current status of the pipeline run.
        :rtype: str
        """
        return self._pipeline_run_provider.get_status(self._run_id)

    def complete(self):
        """
        Complete for Pipeline run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Complete is unsupported for Pipeline run.")

    def fail(self):
        """
        Fail for Pipeline run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Fail is unsupported for Pipeline run.")

    def child_run(self, name=None, run_id=None, outputs=None):
        """
        Child run for Pipeline run.

        :param name: Optional name for the child
        :type name: str
        :param run_id: Optional run_id for the child, otherwise uses default
        :type run_id: str
        :param outputs: Optional outputs directory to track for the child
        :type outputs: str
        :raises: NotImplementedError

        :return: The child run
        :rtype: azureml.core.run.Run
        """
        raise NotImplementedError("Child run is unsupported for Pipeline run.")

    #######################################
    # PipelineRun-specific methods
    #######################################

    def get_graph(self):
        """
        Get the graph of the pipeline run.

        :return: The graph.
        :rtype: azureml.pipeline.core.graph.Graph
        """
        if self._graph is None:
            self._graph = self._context.workflow_provider.graph_provider.create_graph_from_run(self._context,
                                                                                               self._run_id)
        return self._graph

    def get_status(self):
        """
        Get the current status of the pipeline run.

        :return: The run status.
        :rtype: str
        """
        return self._get_status()

    def publish_pipeline(self, name, description, version, continue_on_step_failure=None):
        """
        Publish a pipeline and make it available for rerunning.

        The original pipeline associated with the pipeline_run is used as the base for the published pipeline.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                         if a step fails, default is false.
        :type continue_on_step_failure: bool

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        return self._context.workflow_provider.published_pipeline_provider.create_from_pipeline_run(
            name=name, pipeline_run_id=self._run_id, description=description, version=version,
            continue_run_on_step_failure=continue_on_step_failure)

    def find_step_run(self, name):
        """
        Find a step run in the pipeline by name.

        :param name: Name of the step to find.
        :type name: str

        :return: List of :class:`azureml.pipeline.core.run.StepRun` objects with the provided name.
        :rtype: :class:`list`
        """
        children = self.get_children()
        step_runs = []
        for child in children:
            if name == child._run_dto['name']:
                step_runs.append(child)

        return step_runs

    def get_pipeline_output(self, pipeline_output_name):
        """
        Get the PortDataReference for the given Pipeline output.

        :param pipeline_output_name: Name of the Pipeline output to get.
        :type pipeline_output_name: str

        :return: The PortDataReference representing the Pipeline output data.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self._pipeline_run_provider.get_pipeline_output(self._context, self.id, pipeline_output_name)

    def wait_for_completion(self, show_output=True, timeout_seconds=sys.maxsize, raise_on_error=True):
        """
        Wait for the completion of this Pipeline run.

        Returns the status after the wait.

        :param show_output: show_output=True shows the pipeline run status on sys.stdout.
        :type show_output: bool
        :param timeout_seconds: Number of seconds to wait before timing out.
        :type timeout_seconds: int
        :param raise_on_error: raise_on_error=True raises an Error when the Run is in a failed state
        :type raise_on_error: bool

        :return: The final status.
        :rtype: str
        """
        print('PipelineRunId:', self.id)
        print('Link to Portal:', self.get_portal_url())

        start_time = time.time()
        status = self._get_status()

        if show_output:
            try:
                old_status = None
                processed_step_runs = []
                while status in RUNNING_STATES:
                    if not status == old_status:
                        old_status = status
                        print('PipelineRun Status:', status)
                    children = self.get_children()
                    for step_run in children:
                        if step_run.id not in processed_step_runs:
                            processed_step_runs.append(step_run.id)
                            time_elapsed = time.time() - start_time
                            print('\n')
                            step_run.wait_for_completion(timeout_seconds=timeout_seconds - time_elapsed,
                                                         raise_on_error=raise_on_error)
                            print('')
                    if time.time() - start_time > timeout_seconds:
                        print('Timed out of waiting. Elapsed time:', time.time() - start_time)
                        break
                    time.sleep(1)
                    status = self._get_status()

                summary_title = '\nPipelineRun Execution Summary'
                print(summary_title)
                print('=' * len(summary_title))
                print('PipelineRun Status:', status)

                current_details = self.get_details()
                warnings = current_details.get("warnings")
                if warnings:
                    messages = [x.get("message") for x in warnings if x.get("message")]
                    if len(messages) > 0:
                        print('\nWarnings:')
                        for message in messages:
                            print(message)
                error = current_details.get("error")
                if error and not raise_on_error:
                    print('\nError:')
                    print(json.dumps(error, indent=4))

            except KeyboardInterrupt:
                error_message = "The output streaming for the run interrupted.\n" \
                                "But the run is still executing on the compute target. \n" \
                                "Details for canceling the run can be found here: " \
                                "https://aka.ms/aml-docs-cancel-run"
                raise ExperimentExecutionException(error_message)
        else:
            while status in RUNNING_STATES:
                time.sleep(1)
                status = self._get_status()

        final_details = self.get_details()
        error = final_details.get("error")
        if error and raise_on_error:
            raise ActivityFailedException(error_details=json.dumps(error, indent=4))

        print(final_details)
        print('', flush=True)
        return status

    def cancel(self):
        """Cancel the ongoing run."""
        self._pipeline_run_provider.cancel(self._run_id)

    def get_steps(self):
        """
        Get the step runs for all pipeline steps that have completed or started running.

        :return: List of StepRuns
        :rtype: :class:`list`
        """
        return self.get_children()

    @staticmethod
    def _from_dto(experiment, run_dto):
        """
        Create a PipelineRun object from the experiment and run dto.

        :param experiment: The experiment object.
        :type experiment: azureml.core.Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The PipelineRun object.
        :rtype: PipelineRun
        """
        return PipelineRun(experiment=experiment, run_id=run_dto.run_id)

    @staticmethod
    def get_pipeline_runs(workspace, pipeline_id, _service_endpoint=None):
        """
        Fetch the pipeline runs that were generated from a published pipeline.

        :param workspace: The Workspace associated with the pipeline
        :type workspace: azureml.core.Workspace
        :param pipeline_id: Id of the published pipeline
        :type pipeline_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.run.PipelineRun`
        :rtype: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext('placeholder', workspace=workspace, service_endpoint=_service_endpoint)
        pipeline_run_provider = context.workflow_provider.pipeline_run_provider

        run_tuples = pipeline_run_provider.get_runs_by_pipeline_id(pipeline_id)
        pipeline_runs = []
        for (run_id, experiment_name) in run_tuples:
            experiment = Experiment(workspace, experiment_name)
            pipeline_run = PipelineRun(experiment=experiment, run_id=run_id, _service_endpoint=_service_endpoint)
            pipeline_runs.append(pipeline_run)

        return pipeline_runs

    @staticmethod
    def get(workspace, run_id, _service_endpoint=None):
        """
        Fetch a pipeline run based on a run ID.

        :param workspace: The Workspace associated with the pipeline
        :type workspace: azureml.core.Workspace
        :param run_id: Run ID of the pipeline run
        :type run_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str

        :return: The :class:`azureml.pipeline.core.run.PipelineRun` object.
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext('placeholder', workspace=workspace, service_endpoint=_service_endpoint)
        pipeline_run_provider = context.workflow_provider.pipeline_run_provider

        experiment_name = pipeline_run_provider.get_pipeline_experiment_name(pipeline_run_id=run_id)
        experiment = Experiment(workspace, experiment_name)

        return PipelineRun(experiment, run_id)


class StepRun(Run):
    """
    A run of a step in a :class:`azureml.pipeline.core.Pipeline`.

    This class can be used to manage, check status, and retrieve run details once the parent pipeline run is submitted
    and the pipeline has submitted the step run.

    .. remarks::

        A StepRun is created as a child run of a submitted :class:`azureml.pipeline.core.PipelineRun`. Fetch all the
        StepRuns in a PipelineRun as follows:

        .. code-block:: python

            from azureml.core import Experiment
            from azureml.pipeline.core import PipelineRun

            experiment = Experiment(workspace, "<experiment_name>")
            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")
            step_runs = pipeline_run.get_steps()

        Use :func:`azureml.pipeline.core.StepRun.get_details_with_logs` to fetch the run details and
        logs created by the run.

        StepRun can also be used to download the outputs of a run. Use
        :func:`azureml.pipeline.core.StepRun.get_outputs` to retrieve a dict of the step outputs, or use
        :func:`azureml.pipeline.core.StepRun.get_output` to retrieve the single
        :class:`azureml.pipeline.core.StepRunOutput` object for the output with the provided name. You may also use
        :func:`azureml.pipeline.core.StepRun.get_output_data` to fetch the
        :class:`azureml.pipeline.core.PortDataReference` for the specified step output directly.

        An example of downloading a step output is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineRun, StepRun, PortDataReference

            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")
            step_run = pipeline_run.find_step_run("<step_name>")[0]
            port_data_reference = step_run.get_output_data("<output_name>")
            port_data_reference.download(local_path="path")

    :param experiment: the Experiment object of the step run.
    :type experiment: azureml.core.Experiment
    :param step_run_id: the run id of the step run.
    :type step_run_id: str
    :param pipeline_run_id: the run id of the parent pipeline run.
    :type pipeline_run_id: str
    :param node_id: the id of the node in the graph that represents this step.
    :type node_id: str
    """

    def __init__(self, experiment, step_run_id, pipeline_run_id, node_id, _service_endpoint=None,
                 _is_reused=False, _current_node_id=None,
                 _reused_run_id=None, _reused_node_id=None, _reused_pipeline_run_id=None):
        """
        Initialize a Step run.

        :param experiment: the Experiment object of the step run.
        :type experiment: azureml.core.Experiment
        :param step_run_id: the run id of the step run.
        :type step_run_id: str
        :param pipeline_run_id: the run id of the parent pipeline run.
        :type pipeline_run_id: str
        :param node_id: the id of the node in the graph that represents this step.
        :type node_id: str
        :param _service_endpoint: The endpoint to connect to.
        :type _service_endpoint: str
        :param _is_reused: Whether this run is a reused previous run.
        :type _is_reused: bool
        :param _current_node_id: For reused node, the node id on the current graph.
        :type _current_node_id: str
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                      service_endpoint=_service_endpoint)
        self._pipeline_run_id = pipeline_run_id

        # StepRun may have a different experiment than the PipelineRun if it was reused, check
        experiment_name = \
            self._context.workflow_provider.pipeline_run_provider.get_pipeline_experiment_name(pipeline_run_id)

        if experiment_name != experiment.name:
            experiment = Experiment(experiment.workspace, experiment_name)
            self._context = _GraphContext(experiment.name, workspace=experiment.workspace,
                                          service_endpoint=_service_endpoint)

        self._node_id = node_id
        self._step_run_provider = self._context.workflow_provider.step_run_provider

        super(self.__class__, self).__init__(experiment, step_run_id)

        self._is_reused = _is_reused
        self._reused_run_id = _reused_run_id
        self._reused_node_id = _reused_node_id
        self._reused_pipeline_run_id = _reused_pipeline_run_id
        self._current_node_id = _current_node_id

    #######################################
    # Run methods
    #######################################

    def complete(self):
        """
        Complete for step run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Complete is unsupported for Step run.")

    def fail(self):
        """
        Fail for step run.

        :raises: NotImplementedError
        """
        raise NotImplementedError("Fail is unsupported for Step run.")

    def child_run(self, name=None, run_id=None, outputs=None):
        """
        Child run for step run.

        :param name: Optional name for the child
        :type name: str
        :param run_id: Optional run_id for the child, otherwise uses default
        :type run_id: str
        :param outputs: Optional outputs directory to track for the child
        :type outputs: str
        :raises: NotImplementedError

        :return: The child run
        :rtype: azureml.core.run.Run
        """
        raise NotImplementedError("Child run is unsupported for Step run.")

    #######################################
    # StepRun-specific methods
    #######################################

    @property
    def pipeline_run_id(self):
        """
        Return the id of the pipeline run corresponding to this step run.

        :return: The PipelineRun id.
        :rtype: str
        """
        return self._pipeline_run_id

    def get_status(self):
        """
        Get the current status of the step run.

        :return: The current status.
        :rtype: str
        """
        return self._step_run_provider.get_status(self._pipeline_run_id, self._node_id)

    def get_job_log(self):
        """
        Dump the current job log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_job_log(self._pipeline_run_id, self._node_id)

    def get_stdout_log(self):
        """
        Dump the current stdout log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_stdout_log(self._pipeline_run_id, self._node_id)

    def get_stderr_log(self):
        """
        Dump the current stderr log for the step run.

        :return: The log string.
        :rtype: str
        """
        return self._step_run_provider.get_stderr_log(self._pipeline_run_id, self._node_id)

    def get_outputs(self):
        """
        Get the step outputs.

        :return: A dictionary of StepRunOutputs with the output name as the key.
        :rtype: dict
        """
        return self._step_run_provider.get_outputs(self, self._context, self._pipeline_run_id, self._node_id)

    def get_output(self, name):
        """
        Get the node output with the given name.

        :param name: Name of the output.
        :type name: str

        :return: The StepRunOutput with the given name.
        :rtype: azureml.pipeline.core.StepRunOutput
        """
        return self._step_run_provider.get_output(self, self._context, self._pipeline_run_id, self._node_id, name)

    def get_output_data(self, name):
        """
        Get the output data from a given output.

        :param name: Name of the output.
        :type name: str

        :return: The PortDataReference representing the step output data.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self.get_output(name).get_port_data_reference()

    def wait_for_completion(self, show_output=True, timeout_seconds=sys.maxsize, raise_on_error=True):
        """
        Wait for the completion of this step run.

        Returns the status after the wait.

        :param show_output: show_output=True shows the pipeline run status on sys.stdout.
        :type show_output: bool
        :param timeout_seconds: Number of seconds to wait before timing out.
        :type timeout_seconds: int
        :param raise_on_error: raise_on_error=True raises an Error when the Run is in a failed state
        :type raise_on_error: bool

        :return: The final status.
        :rtype: str
        """
        print('StepRunId:', self.id)
        print('Link to Portal:', self.get_portal_url())

        if show_output:
            try:
                return self._stream_run_output(timeout_seconds=timeout_seconds,
                                               raise_on_error=raise_on_error)
            except KeyboardInterrupt:
                error_message = "The output streaming for the run interrupted.\n" \
                                "But the run is still executing on the compute target. \n" \
                                "Details for canceling the run can be found here: " \
                                "https://aka.ms/aml-docs-cancel-run"

                raise ExperimentExecutionException(error_message)
        else:
            status = self.get_status()
            while status in RUNNING_STATES:
                time.sleep(1)
                status = self.get_status()

            final_details = self.get_details()
            error = final_details.get("error")
            if error and raise_on_error:
                raise ActivityFailedException(error_details=json.dumps(error, indent=4))

            return status

    def _stream_run_output(self, timeout_seconds=sys.maxsize, raise_on_error=True):

        def incremental_print(log, num_printed):
            count = 0
            for line in log.splitlines():
                if count >= num_printed:
                    print(line)
                    num_printed += 1
                count += 1
            return num_printed

        num_printed_lines = 0
        current_log = None

        start_time = time.time()
        session = create_session_with_retry()

        old_status = None
        status = self.get_status()
        while status in RUNNING_STATES:
            if not status == old_status:
                old_status = status
                print('StepRun(', self.name, ') Status:', status)

            current_details = self.get_details()
            available_logs = [x for x in current_details["logFiles"]
                              if re.match("azureml-logs/[\d]{2}.+\.txt", x)]
            available_logs.sort()
            next_log = ScriptRun._get_last_log_primary_instance(available_logs) if available_logs else None

            if available_logs and current_log != next_log:
                num_printed_lines = 0
                current_log = next_log
                print("\nStreaming " + current_log)
                print('=' * (len(current_log) + 10))

            if current_log:
                content = _commands._get_content_from_uri(current_details["logFiles"][current_log], session)
                num_printed_lines = incremental_print(content, num_printed_lines)

            if time.time() - start_time > timeout_seconds:
                print('Timed out of waiting. Elapsed time:', time.time() - start_time)
                break
            time.sleep(1)
            status = self.get_status()

        summary_title = '\nStepRun(' + self.name + ') Execution Summary'
        print(summary_title)
        print('=' * len(summary_title))
        print('StepRun(', self.name, ') Status:', status)

        final_details = self.get_details()
        warnings = final_details.get("warnings")
        if warnings:
            messages = [x.get("message") for x in warnings if x.get("message")]
            if len(messages) > 0:
                print('\nWarnings:')
                for message in messages:
                    print(message)

        error = final_details.get("error")
        if error and not raise_on_error:
            print('\nError:')
            print(json.dumps(error, indent=4))
        if error and raise_on_error:
            raise ActivityFailedException(error_details=json.dumps(error, indent=4))

        print(final_details)
        print('', flush=True)

        return status

    def get_details_with_logs(self):
        """
        Return the status details of the run with log file contents.

        :return: Returns the status for the run with log file contents
        :rtype: dict
        """
        details = self.get_details()
        log_files = details.get("logFiles", {})
        session = create_session_with_retry()

        for log_name in log_files:
            content = _commands._get_content_from_uri(log_files[log_name], session)
            log_files[log_name] = content
        log_files['STDOUT'] = self.get_stdout_log()
        log_files['STDERR'] = self.get_stderr_log()
        log_files['JOBLOG'] = self.get_job_log()
        return details

    @staticmethod
    def _from_dto(experiment, run_dto):
        """
        Create a StepRun object from the experiment and run dto.

        :param experiment: The experiment object.
        :type experiment: Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The StepRun object.
        :rtype: StepRun
        """
        run_tags = getattr(run_dto, "tags", {})
        node_id = run_tags.get('azureml.nodeid')
        run_properties = getattr(run_dto, "properties", {})
        reused_run_id = run_properties.get('azureml.reusedrunid')
        reused_node_id = run_properties.get('azureml.reusednodeid')
        reused_pipeline_run_id = run_properties.get('azureml.reusedpipeline')
        is_reused = False
        if reused_run_id is not None:
            is_reused = True
        pipeline_run_id = run_tags.get('azureml.pipeline')
        return StepRun(experiment, step_run_id=run_dto.run_id, pipeline_run_id=pipeline_run_id, node_id=node_id,
                       _is_reused=is_reused, _reused_run_id=reused_run_id,
                       _reused_node_id=reused_node_id, _reused_pipeline_run_id=reused_pipeline_run_id)

    @staticmethod
    def _from_reused_dto(experiment, run_dto):
        """
        Create a StepRun object from the experiment and reused run dto.

        :param experiment: The experiment object.
        :type experiment: Experiment
        :param run_dto: The run dto object.
        :type run_dto: RunDto

        :return: The StepRun object.
        :rtype: StepRun
        """
        run_tags = getattr(run_dto, "tags", {})
        reused_run_id = run_tags.get('azureml.reusedrunid')
        reused_node_id = run_tags.get('azureml.reusednodeid')
        reused_pipeline_run_id = run_tags.get('azureml.reusedpipeline')
        current_node_id = run_tags.get('azureml.nodeid', None)
        return StepRun(experiment, step_run_id=reused_run_id, pipeline_run_id=reused_pipeline_run_id,
                       node_id=reused_node_id, _is_reused=True, _current_node_id=current_node_id)


class StepRunOutput(object):
    """
    Represents an output created by a :class:`azureml.pipeline.core.StepRun` in a Pipeline.

    StepRunOutput can be used to access the :class:`azureml.pipeline.core.PortDataReference` created by the step.

    .. remarks::

        Step run outputs are instantiated by calling :func:`azureml.pipeline.core.StepRun.get_output`. Use
        :func:`azureml.pipeline.core.StepRunOutput.get_port_data_reference` to retrieve the
        :class:`azureml.pipeline.core.PortDataReference` which can be used to download the data and can be used as an
        step input in a future pipeline.

        An example of getting the StepRunOutput from a StepRun and downloading the output data is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineRun, StepRun, PortDataReference

            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")
            step_run = pipeline_run.find_step_run("<step_name>")[0]

            step_run_output = step_run.get_output("<output_name>")

            port_data_reference = step_run_output.get_port_data_reference()
            port_data_reference.download(local_path="path")


    :param context: The graph context object.
    :type context: _GraphContext
    :param pipeline_run_id: The id of the pipeline run which created the output.
    :type pipeline_run_id: str
    :param step_run: The step run object which created the output.
    :type step_run: azureml.pipeline.core.StepRun
    :param name: The name of the output.
    :type name: str
    :param step_output: The step output.
    :type step_output: azureml.pipeline.core.graph.NodeOutput
    """

    def __init__(self, context, pipeline_run_id, step_run, name, step_output):
        """
        Initialize StepRunOutput.

        :param context: The graph context object.
        :type context: _GraphContext
        :param pipeline_run_id: The id of the pipeline run which created the output.
        :type pipeline_run_id: str
        :param step_run: The step run object which created the output.
        :type step_run: azureml.pipeline.core.StepRun
        :param name: The name of the output.
        :type name: str
        :param step_output: The step output.
        :type step_output: azureml.pipeline.core.graph.NodeOutput
        """
        self.step_run = step_run
        self.pipeline_run_id = pipeline_run_id
        self.context = context
        self.name = name
        self.step_output = step_output

    def get_port_data_reference(self):
        """
        Get port data reference produced by the step.

        :return: The port data reference.
        :rtype: azureml.pipeline.core.PortDataReference
        """
        return self.context.workflow_provider.port_data_reference_provider.create_port_data_reference(self)
