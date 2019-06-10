# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""schedule.py, module for defining schedule and schedule recurrence."""
from __future__ import print_function
import time
import re
import logging
from datetime import datetime
from enum import Enum
from collections import OrderedDict
from azureml._html.utilities import to_html, make_link
from azureml.pipeline.core.run import PipelineRun
from azureml.pipeline.core.graph import PublishedPipeline
from azureml.core import Experiment


class Schedule(object):
    """
    A Schedule submits a Pipeline on a specified schedule.

    Once a Pipeline is published, a Schedule can be used to submit the Pipeline at a specified interval or
    when changes to a Blob storage location are detected.

    .. remarks::

        Two types of schedules are supported. The first uses a time recurrence to submit a Pipeline on a
        given schedule. The second monitors an :class:`azureml.data.azure_storage_datastore.AzureBlobDatastore`
        for added or modified blobs and will submit a Pipeline when changes are detected.

        To create a Schedule which will submit a Pipeline on a recurrence schedule, use the
        :class:`azureml.pipeline.core.ScheduleRecurrence` when creating the Schedule.

        A ScheduleRecurrence is used when creating a Schedule for a Pipeline as follows:

        .. code-block:: python

            from azureml.pipeline.core import Schedule, ScheduleRecurrence

            recurrence = ScheduleRecurrence(frequency="Hour", interval=12)
            schedule = Schedule.create(workspace, name="TestSchedule", pipeline_id="pipeline_id",
                                       experiment_name="helloworld", recurrence=recurrence)

        This Schedule will submit the provided :class:`azureml.pipeline.core.PublishedPipeline` every 12 hours.
        The submitted Pipeline will be created under the Experiment with the name "helloworld".

        To create a Schedule which will trigger PipelineRuns on modifications to a Blob storage location, specify
        a Datastore and other info when creating the Schedule.

        .. code-block:: python

            from azureml.pipeline.core import Schedule
            from azureml.core.datastore import Datastore

            datastore = Datastore(workspace=ws, name="workspaceblobstore")

            schedule = Schedule.create(workspace, name="TestSchedule", pipeline_id="pipeline_id"
                                       experiment_name="helloworld", datastore=datastore,
                                       polling_interval=5, path_on_datastore="file/path")

        Note that the polling_interval and path_on_datastore parameters are optional. The polling_interval specifies
        how often to poll for modifications to the Datastore, and by default is 5 minutes. path_on_datastore can
        be used to specify which folder on the Datastore to monitor for changes. If None, the Datastore container
        is monitored. Note: blob additions/modifications in sub-folders of the path_on_datastore or the Datastore
        container (if no path_on_datastore is specified) are not detected.

        Additionally, if the Pipeline was constructed to use a :class:`azureml.data.datapath.DataPath`
        :class:`azureml.pipeline.core.PipelineParameter` to describe a step input, use the data_path_parameter_name
        parameter when creating a Datastore trigger Schedule to set the input to the changed file when a PipelineRun
        is submitted by the Schedule.

        In the following example, when the Schedule triggers the PipelineRun, the value of the "input_data"
        PipelineParameter will be set as the file which was modified/added:

        .. code-block:: python

            from azureml.pipeline.core import Schedule
            from azureml.core.datastore import Datastore

            datastore = Datastore(workspace=ws, name="workspaceblobstore")

            schedule = Schedule.create(workspace, name="TestSchedule", pipeline_id="pipeline_id",
                                       experiment_name="helloworld", datastore=datastore,
                                       data_path_parameter_name="input_data")


        See the following link for more details on Schedules: `https://aka.ms/pl-schedule`

    :param workspace: Workspace object this Schedule will belong to.
    :type workspace: azureml.core.Workspace
    :param id: The id of the Schedule.
    :type id: str
    :param name: The name of the Schedule.
    :type name: str
    :param description: Description of the schedule.
    :type description: str
    :param pipeline_id: The id of the pipeline the schedule will submit.
    :type pipeline_id: str
    :param status: The status of the schedule.
    :type status: str
    :param recurrence: The recurrence for the schedule.
    :type recurrence: azureml.pipeline.core.ScheduleRecurrence
    :param datastore_name: The name of the datastore to monitor for modified/added blobs.
                           Note: VNET Datastores are not supported.
    :type datastore_name: str
    :param polling_interval: How long, in minutes, between polling for modified/added blobs.
    :type polling_interval: int
    :param data_path_parameter_name: The name of the data path pipeline parameter to set with the changed blob path.
    :type data_path_parameter_name: str
    :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                     if a step fails. If provided, this will override the continue_on_step_failure
                                     setting for the Pipeline.
    :type continue_on_step_failure: bool
    :param path_on_datastore: Optional. The path on the datastore to monitor for modified/added blobs. Note: the
                              path_on_datastore will be under the container for the datastore, so the actual path
                              the schedule will monitor will be container/path_on_datastore. If none, the
                              datastore container is monitored. Additions/modifications made in a subfolder of the
                              path_on_datastore are not monitored. Only supported for DataStore schedules.
    :type path_on_datastore: str
    :param _schedule_provider: The schedule provider.
    :type _schedule_provider: _AevaScheduleProvider object
    """

    def __init__(self, workspace, id, name, description, pipeline_id, status, recurrence,
                 datastore_name, polling_interval, data_path_parameter_name,
                 continue_on_step_failure, path_on_datastore, _schedule_provider=None):
        """
        Initialize Schedule.

        :param workspace: Workspace object this Schedule will belong to.
        :type workspace: azureml.core.Workspace
        :param id: The id of the Schedule.
        :type id: str
        :param name: The name of the Schedule.
        :type name: str
        :param description: Description of the schedule.
        :type description: str
        :param pipeline_id: The id of the pipeline the schedule will submit.
        :type pipeline_id: str
        :param status: The status of the schedule, either 'Active' or 'Disabled'.
        :type status: str
        :param recurrence: The recurrence for the schedule.
        :type recurrence: azureml.pipeline.core.ScheduleRecurrence
        :param datastore_name: The name of the datastore to monitor for modified/added blobs.
                               Note: VNET Datastores are not supported.
        :type datastore_name: str
        :param polling_interval: How long, in minutes, between polling for modified/added blobs.
        :type polling_interval: int
        :param data_path_parameter_name: The name of the data path pipeline parameter to set with
                                         the changed blob path.
        :type data_path_parameter_name: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                         if a step fails. If provided, this will override the continue_on_step_failure
                                         setting for the Pipeline.
        :type continue_on_step_failure: bool
        :param path_on_datastore: Optional. The path on the datastore to monitor for modified/added blobs. Note: the
                                  path_on_datastore will be under the container for the datastore, so the actual path
                                  the schedule will monitor will be container/path_on_datastore. If none, the
                                  datastore container is monitored. Additions/modifications made in a subfolder of the
                                  path_on_datastore are not monitored. Only supported for DataStore schedules.
        :type path_on_datastore: str
        :param _schedule_provider: The schedule provider.
        :type _schedule_provider: _AevaScheduleProvider object
        """
        self._id = id
        self._status = status
        self._name = name
        self._description = description
        self._recurrence = recurrence
        self._pipeline_id = pipeline_id
        self._workspace = workspace
        self._schedule_provider = _schedule_provider
        self._datastore_name = datastore_name
        self._polling_interval = polling_interval
        self._data_path_parameter_name = data_path_parameter_name
        self._continue_on_step_failure = continue_on_step_failure
        self._path_on_datastore = path_on_datastore
        if self._recurrence is not None:
            self._schedule_type = 'Recurrence'
        else:
            self._schedule_type = 'DataStore'

    @property
    def id(self):
        """
        Get the ID for the schedule.

        :return: The ID.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """
        Name of the schedule.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the schedule.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def pipeline_id(self):
        """
        Get the id of the pipeline the schedule submits.

        :return: The id.
        :rtype: str
        """
        return self._pipeline_id

    @property
    def status(self):
        """
        Status of the schedule.

        :return: The status.
        :rtype: str
        """
        return self._status

    @property
    def recurrence(self):
        """
        Get the schedule recurrence.

        :return: The schedule recurrence.
        :rtype: azureml.pipeline.core.ScheduleRecurrence
        """
        return self._recurrence

    @property
    def datastore_name(self):
        """
        Name of the Datastore used for the schedule.

        :return: The Datastore name.
        :rtype: str
        """
        return self._datastore_name

    @property
    def polling_interval(self):
        """
        How long, in minutes, between polling for modified/added blobs.

        :return: The Polling Interval.
        :rtype: int
        """
        return self._polling_interval

    @property
    def data_path_parameter_name(self):
        """
        Get the name of the data path pipeline parameter to set with the changed blob path.

        :return: The Data Path Parameter Name.
        :rtype: str
        """
        return self._data_path_parameter_name

    @property
    def continue_on_step_failure(self):
        """
        Get the value of the continue_on_step_failure setting.

        :return: The value of the continue_on_step_failure setting
        :rtype: bool
        """
        return self._continue_on_step_failure

    @property
    def path_on_datastore(self):
        """
        Get the Path on the Datastore the schedules monitors.

        :return: The Path on datastore.
        :rtype: str
        """
        return self._path_on_datastore

    @staticmethod
    def create(workspace, name, pipeline_id, experiment_name, recurrence=None, description=None,
               pipeline_parameters=None, wait_for_provisioning=False, wait_timeout=3600,
               datastore=None, polling_interval=5, data_path_parameter_name=None, continue_on_step_failure=None,
               path_on_datastore=None, _workflow_provider=None, _service_endpoint=None):
        """
        Create a schedule.

        Specify recurrence for a time-based schedule or specify a Datastore, (optional) polling_interval,
        and (optional) data_path_parameter_name to create a schedule which will monitor the Datastore location
        for modifications/additions.

        :param workspace: Workspace object this Schedule will belong to.
        :type workspace: azureml.core.Workspace
        :param name: The name of the Schedule.
        :type name: str
        :param pipeline_id: The id of the pipeline the schedule will submit.
        :type pipeline_id: str
        :param experiment_name: The name of the experiment the schedule will submit runs on.
        :type experiment_name: str
        :param recurrence: The recurrence for the schedule.
        :type recurrence: azureml.pipeline.core.ScheduleRecurrence
        :param description: Description of the schedule.
        :type description: str
        :param pipeline_parameters: Dictionary of parameters to assign new values {param name, param value}
        :type pipeline_parameters: dict
        :param wait_for_provisioning: Whether to wait for provisioning of the schedule to complete.
        :type wait_for_provisioning: bool
        :param wait_timeout: Number of seconds to wait before timing out.
        :type wait_timeout: int
        :param datastore: The Datastore to monitor for modified/added blobs. Note: VNET Datastores are not supported.
                          Can not use with a Recurrence.
        :type datastore: azureml.data.azure_storage_datastore.AzureBlobDatastore
        :param polling_interval: How long, in minutes, between polling for modified/added blobs. Default is 5 minutes.
                                 Only supported for DataStore schedules.
        :type polling_interval: int
        :param data_path_parameter_name: The name of the data path pipeline parameter to set
                                         with the changed blob path. Only supported for DataStore schedules.
        :type data_path_parameter_name: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                 if a step fails. If provided, this will override the continue_on_step_failure
                                 setting for the Pipeline.
        :type continue_on_step_failure: bool
        :param path_on_datastore: Optional. The path on the datastore to monitor for modified/added blobs. Note: the
                                  path_on_datastore will be under the container for the datastore, so the actual path
                                  the schedule will monitor will be container/path_on_datastore. If none, the
                                  datastore container is monitored. Additions/modifications made in a subfolder of the
                                  path_on_datastore are not monitored. Only supported for DataStore schedules.
        :type path_on_datastore: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :return: The created schedule.
        :rtype: azureml.pipeline.core.Schedule
        """
        if recurrence is not None:
            if datastore is not None:
                raise ValueError('Can not specify both a Recurrence and a Datastore')
            if data_path_parameter_name is not None:
                raise ValueError('Data Path parameter name can only be specified for Datastore schedules.')
            if path_on_datastore is not None:
                raise ValueError('Path on datastore parameter can only be specified for Datastore schedules.')
            recurrence.validate()

        datastore_name = None
        if datastore is not None:
            if datastore.datastore_type != 'AzureBlob':
                raise ValueError('Datastore must be of type AzureBlobDatastore')
            datastore_name = datastore.name

        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        schedule_provider = graph_context.workflow_provider.schedule_provider
        schedule = schedule_provider.create_schedule(name, pipeline_id, experiment_name, recurrence=recurrence,
                                                     datastore_name=datastore_name, description=description,
                                                     data_path_parameter_name=data_path_parameter_name,
                                                     polling_interval=polling_interval,
                                                     pipeline_parameters=pipeline_parameters,
                                                     continue_on_step_failure=continue_on_step_failure,
                                                     path_on_datastore=path_on_datastore)

        if wait_for_provisioning:
            schedule._wait_for_provisioning(timeout_seconds=wait_timeout)
        return schedule

    def update(self, name=None, description=None, recurrence=None, pipeline_parameters=None, status=None,
               wait_for_provisioning=False, wait_timeout=3600, datastore=None, polling_interval=None,
               data_path_parameter_name=None, continue_on_step_failure=None, path_on_datastore=None):
        """
        Update the schedule.

        :param name: The new name of the Schedule.
        :type name: str
        :param recurrence: The new recurrence for the schedule.
        :type recurrence: azureml.pipeline.core.ScheduleRecurrence
        :param description: The new description of the schedule.
        :type description: str
        :param pipeline_parameters: Dictionary of parameters to assign new values {param name, param value}
        :type pipeline_parameters: dict
        :param status: The new status of the schedule: 'Active' or 'Disabled'.
        :type status: str
        :param wait_for_provisioning: Whether to wait for provisioning of the schedule to complete.
        :type wait_for_provisioning: bool
        :param wait_timeout: Number of seconds to wait before timing out.
        :type wait_timeout: int
        :param datastore: The Datastore to monitor for modified/added blobs. Note: VNET Datastores are not supported.
        :type datastore: azureml.data.azure_storage_datastore.AzureBlobDatastore
        :param polling_interval: How long, in minutes, between polling for modified/added blobs. Default is 5 minutes.
        :type polling_interval: int
        :param data_path_parameter_name: The name of the data path pipeline parameter to set
                                         with the changed blob path.
        :type data_path_parameter_name: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the submitted PipelineRun
                                         if a step fails. If provided, this will override the continue_on_step_failure
                                         setting for the Pipeline.
        :type continue_on_step_failure: bool
        :param path_on_datastore: Optional. The path on the datastore to monitor for modified/added blobs. Note: the
                                  path_on_datastore will be under the container for the datastore, so the actual path
                                  the schedule will monitor will be container/path_on_datastore. If none, the
                                  datastore container is monitored. Additions/modifications made in a subfolder of the
                                  path_on_datastore are not monitored. Only supported for DataStore schedules.
        :type path_on_datastore: str
        """
        if recurrence is not None:
            if self._schedule_type is not 'Recurrence':
                raise ValueError('Can not specify a recurrence for a Datastore schedule.')
            recurrence.validate()
        datastore_name = None
        if datastore is not None:
            if self._schedule_type is not 'DataStore':
                raise ValueError('Can not specify a Datastore for a Recurrence schedule.')
            if datastore.datastore_type != 'AzureBlob':
                raise ValueError('Datastore must be of type AzureBlobDatastore')
            datastore_name = datastore.name
            if polling_interval is not None and polling_interval < 0:
                raise ValueError('The polling interval must be greater')

        if status is not None and status not in ['Active', 'Disabled']:
            raise ValueError('Status must be either Active or Disabled')

        new_schedule = self._schedule_provider.update_schedule(self.id, name=name, description=description,
                                                               status=status, recurrence=recurrence,
                                                               datastore_name=datastore_name,
                                                               data_path_parameter_name=data_path_parameter_name,
                                                               polling_interval=polling_interval,
                                                               pipeline_parameters=pipeline_parameters,
                                                               continue_on_step_failure=continue_on_step_failure,
                                                               path_on_datastore=path_on_datastore)

        self._description = new_schedule.description
        self._name = new_schedule.name
        self._status = new_schedule.status
        self._recurrence = new_schedule.recurrence
        self._datastore_name = new_schedule.datastore_name
        self._polling_interval = new_schedule.polling_interval
        self._data_path_parameter_name = new_schedule.data_path_parameter_name
        self._continue_on_step_failure = new_schedule.continue_on_step_failure
        self._path_on_datastore = new_schedule.path_on_datastore

        if wait_for_provisioning:
            self._wait_for_provisioning(timeout_seconds=wait_timeout)

    def enable(self, wait_for_provisioning=False, wait_timeout=3600):
        """
        Set the schedule to be 'Active' and available to run.

        :param wait_for_provisioning: Whether to wait for provisioning of the schedule to complete.
        :type wait_for_provisioning: bool
        :param wait_timeout: Number of seconds to wait before timing out.
        :type wait_timeout: int
        """
        self._set_status('Active', wait_for_provisioning=wait_for_provisioning, wait_timeout=wait_timeout)

    def disable(self, wait_for_provisioning=False, wait_timeout=3600):
        """
        Set the schedule to be 'Disabled' and unavailable to run.

        :param wait_for_provisioning: Whether to wait for provisioning of the schedule to complete.
        :type wait_for_provisioning: bool
        :param wait_timeout: Number of seconds to wait before timing out.
        :type wait_timeout: int
        """
        self._set_status('Disabled', wait_for_provisioning=wait_for_provisioning, wait_timeout=wait_timeout)

    def _wait_for_provisioning(self, timeout_seconds):
        """
        Wait for the completion of provisioning for this schedule.

        Returns the status after the wait.

        :param timeout_seconds: Number of seconds to wait before timing out.
        :type timeout_seconds: int

        :return: The final status.
        :rtype: str
        """
        status = self._schedule_provider.get_schedule_provisioning_status(self.id)
        time_run = 0
        sleep_period = 5
        while status == 'Provisioning':
            if time_run + sleep_period > timeout_seconds:
                print('Timed out of waiting, status:%s.' % status, flush=True)
                break
            time_run += sleep_period
            time.sleep(sleep_period)
            status = self._schedule_provider.get_schedule_provisioning_status(self.id)
            print('Provisioning status:', status)
        if status == "Failed":
            print('Provisioning failed, please try again or contact support.')
        return status

    def _set_status(self, new_status, wait_for_provisioning, wait_timeout):
        """
        Set the schedule status.

        :param new_status: The new schedule status ('Active' or 'Disabled').
        :type new_status: str
        """
        self._schedule_provider.set_status(self._id, new_status)
        if wait_for_provisioning:
            self._wait_for_provisioning(timeout_seconds=wait_timeout)
        self._status = new_status

    def get_pipeline_runs(self):
        """
        Fetch the pipeline runs that were generated from the schedule.

        :return: a list of :class:`azureml.pipeline.core.run.PipelineRun`
        :rtype: :class:`list`
        """
        run_tuples = self._schedule_provider.get_pipeline_runs_for_schedule(self._id)
        pipeline_runs = []
        for (run_id, experiment_name) in run_tuples:
            experiment = Experiment(self._workspace, experiment_name)
            pipeline_run = PipelineRun(experiment=experiment, run_id=run_id,
                                       _service_endpoint=self._schedule_provider._service_caller._service_endpoint)
            pipeline_runs.append(pipeline_run)

        return pipeline_runs

    def get_last_pipeline_run(self):
        """
        Fetch the last pipeline run submitted by the schedule. Returns None if no runs have been submitted.

        :return: The last pipeline run
        :rtype: azureml.pipeline.core.run.PipelineRun
        """
        run_id, experiment_name = self._schedule_provider.get_last_pipeline_run_for_schedule(self._id)
        if run_id is None:
            return None
        experiment = Experiment(self._workspace, experiment_name)
        return PipelineRun(experiment=experiment, run_id=run_id,
                           _service_endpoint=self._schedule_provider._service_caller._service_endpoint)

    @staticmethod
    def get(workspace, id, _workflow_provider=None, _service_endpoint=None):
        """
        Get the schedule with the given id.

        :param workspace: The workspace the schedule was created on.
        :type workspace: azureml.core.Workspace
        :param id: Id of the schedule.
        :type id: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: Schedule object
        :rtype: azureml.pipeline.core.Schedule
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        return graph_context.workflow_provider.schedule_provider.get_schedule(schedule_id=id)

    @staticmethod
    def get_all(workspace, active_only=True, pipeline_id=None, _workflow_provider=None, _service_endpoint=None):
        """
        Get all schedules in the current workspace.

        NOTE: This method is being deprecated in favor of Schedule.list()

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return schedules which are currently active. Only applies if no pipeline id
                            is provided.
        :type active_only: Bool
        :param pipeline_id: If provided, only return schedules for the pipeline with the given id.
        :type pipeline_id: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.Schedule`
        :rtype: :class:`list`
        """
        logging.warning("Schedule.get_all(workspace) is being deprecated. "
                        "Use Schedule.list(workspace) instead.")
        return Schedule.list(workspace=workspace, active_only=active_only, pipeline_id=pipeline_id,
                             _workflow_provider=_workflow_provider, _service_endpoint=_service_endpoint)

    @staticmethod
    def list(workspace, active_only=True, pipeline_id=None, _workflow_provider=None, _service_endpoint=None):
        """
        Get all schedules in the current workspace.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return schedules which are currently active. Only applies if no pipeline id
                            is provided.
        :type active_only: Bool
        :param pipeline_id: If provided, only return schedules for the pipeline with the given id.
        :type pipeline_id: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.Schedule`
        :rtype: :class:`list`
        """
        if pipeline_id is not None:
            return Schedule.get_schedules_for_pipeline_id(workspace, pipeline_id,
                                                          _workflow_provider=_workflow_provider,
                                                          _service_endpoint=_service_endpoint)
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        return graph_context.workflow_provider.schedule_provider.get_all_schedules(active_only=active_only)

    @staticmethod
    def get_schedules_for_pipeline_id(workspace, pipeline_id, _workflow_provider=None, _service_endpoint=None):
        """
        Get all schedules for the given pipeline id.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param pipeline_id: The pipeline id.
        :type pipeline_id: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.Schedule`
        :rtype: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        return graph_context.workflow_provider.schedule_provider.get_schedules_by_pipeline_id(pipeline_id=pipeline_id)

    def _repr_html_(self):
        info = self._get_base_info_dict(show_link=True)
        return to_html(info)

    def _get_base_info_dict(self, show_link):
        pipeline_id = self.pipeline_id
        if show_link:
            pipeline = PublishedPipeline.get(self._workspace, self.pipeline_id)
            pipeline_id = make_link(pipeline.get_portal_url(), self.pipeline_id)
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Status', self.status),
            ('Pipeline Id', pipeline_id)
        ])

        if self._schedule_type == 'Recurrence':
            recurrence_description = "Runs"

            if self.recurrence.hours is not None or self.recurrence.minutes is not None:
                list_of_times = self._get_list_of_times(self.recurrence.hours, self.recurrence.minutes)
                recurrence_description += " at " + ', '.join(map(str, list_of_times))

            if self.recurrence.week_days is not None and self.recurrence.week_days != []:
                recurrence_description += " on " + ', '.join(map(str, self.recurrence.week_days))

            if self.recurrence.interval == 1:
                recurrence_description += " every " + str(self.recurrence.frequency)
            else:
                recurrence_description += " every " + str(self.recurrence.interval) + " " \
                                          + str(self.recurrence.frequency) + "s"

            info.update([('Recurrence Details', recurrence_description)])
        else:
            info.update([('Datastore', self.datastore_name)])
            if self.path_on_datastore is not None:
                info.update([('Path on Datastore', self.path_on_datastore)])

        return info

    @staticmethod
    def _get_list_of_times(hours, minutes):
        if not hours:
            hours = ["00"]
        if not minutes:
            minutes = ["00"]
        list_of_times = []
        for hour in hours:
            for minute in minutes:
                minute_str = str(minute)
                if minute_str == "0":
                    minute_str = "00"
                list_of_times.append(str(hour) + ":" + minute_str)
        return list_of_times

    def __str__(self):
        """Return the string representation of the Schedule."""
        info = self._get_base_info_dict(show_link=False)
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Pipeline({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the Schedule."""
        return self.__str__()


class ScheduleRecurrence(object):
    """
    A ScheduleRecurrence defines the frequency, interval and start time of a schedule.

    It also allows to specify the time zone and the hours or minutes or week days for the recurrence.

    .. remarks::

        A ScheduleRecurrence is used when creating a Schedule for a Pipeline as follows:

        .. code-block:: python

            from azureml.pipeline.core import Schedule, ScheduleRecurrence

            recurrence = ScheduleRecurrence(frequency="Hour", interval=12)
            schedule = Schedule.create(workspace, name="TestSchedule", pipeline_id=pipeline.id,
                                       experiment_name="experiment_name", recurrence=recurrence)

        The following are some examples of valid ScheduleRecurrences:

        .. code-block:: python

            from azureml.pipeline.core import ScheduleRecurrence

            # Submit the Pipeline every 15 minutes
            recurrence = ScheduleRecurrence(frequency="Minute", interval=15)
            # Submit the Pipeline every 2 weeks on Monday and Wednesday at 6:30pm UTC
            recurrence = ScheduleRecurrence(frequency="Week", interval=2, week_days=["Monday", "Wednesday"],
                                            time_of_day="18:30")

    :param frequency: The unit of time that describes how often the schedule fires.
                      Can be "Minute", "Hour", "Day", "Week", or  "Month".
    :type frequency: str
    :param interval: A value that specifies how often the schedule fires based on the frequency, which is the
                     number of time units to wait until the schedule fires again.
    :type interval: int
    :param start_time: A datetime object which describes the start date and time. The tzinfo of the datetime object
                       should be none, use time_zone property to specify a time zone if needed. Can also be a
                       string in this format: YYYY-MM-DDThh:mm:ss. If None is provided the first workload is run
                       instantly and the future workloads are run based on the schedule. If the start time is
                       in the past, the first workload is run at the next calculated run time.
    :type start_time: datetime.datetime or str
    :param time_zone: Specify the time zone of the start_time. If None is provided UTC is used.
    :type time_zone: azureml.pipeline.core.schedule.TimeZone
    :param hours: If you specify "Day" or "Week" for frequency, you can specify one or more integers from 0 to 23,
                  separated by commas, as the hours of the day when you want to run the workflow.
                  For example, if you specify "10", "12" and "14", you get 10 AM, 12 PM,
                  and 2 PM as the hour marks. Note: only time_of_day or hours and minutes can be used.
    :type hours: list of int
    :param minutes: If you specify "Day" or "Week" for frequency, you can specify one or more
                    integers from 0 to 59, separated by commas, as the minutes of the hour when you want to run
                    the workflow. For example, you can specify "30" as the minute mark and using the previous
                    example for hours of the day, you get 10:30 AM, 12:30 PM, and 2:30 PM. Note: only time_of_day
                    or hours and minutes can be used.
    :type minutes: list of int
    :param time_of_day: If you specify "Day" or "Week" for frequency, you can specify a time of day for the
                        schedule to run as a string in the form hh:mm. For example, if you specify "15:30" then
                        the schedule will run at 3:30pm. Note: only time_of_day or hours and minutes can be used.
    :type time_of_day: str
    :param week_days: If you specify "Week" for frequency, you can specify one or more days, separated by commas,
                      when you want to run the workflow: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                      "Saturday", and "Sunday"
    :type week_days: list of str
    """

    def __init__(self, frequency, interval, start_time=None, time_zone=None, hours=None, minutes=None,
                 week_days=None, time_of_day=None):
        """
        Initialize a schedule recurrence.

        It also allows to specify the time zone and the hours or minutes or week days for the recurrence.

        :param frequency: The unit of time that describes how often the schedule fires.
                          Can be "Minute", "Hour", "Day", "Week", or  "Month".
        :type frequency: str
        :param interval: A value that specifies how often the schedule fires based on the frequency, which is the
                         number of time units to wait until the schedule fires again.
        :type interval: int
        :param start_time: A datetime object which describes the start date and time. The tzinfo of the datetime
                           object should be none, use time_zone property to specify a time zone if needed. Can also
                           be a string in this format: YYYY-MM-DDThh:mm:ss. If None is provided the first workload
                           is run instantly and the future workloads are run based on the schedule. If the
                           start time is in the past, the first workload is run at the next calculated
                           run time.
        :type start_time: datetime.datetime or str
        :param time_zone: Specify the time zone of the start_time. If None is provided UTC is used.
        :type time_zone: azureml.pipeline.core.schedule.TimeZone
        :param hours: If you specify "Day" or "Week" for frequency, you can specify one or more integers from 0 to 23,
                      separated by commas, as the hours of the day when you want to run the workflow.
                      For example, if you specify "10", "12" and "14", you get 10 AM, 12 PM,
                      and 2 PM as the hour marks. Note: only time_of_day or hours and minutes can be used.
        :type hours: list of int
        :param minutes: If you specify "Day" or "Week" for frequency, you can specify one or more
                        integers from 0 to 59, separated by commas, as the minutes of the hour when you want to run
                        the workflow. For example, you can specify "30" as the minute mark and using the previous
                        example for hours of the day, you get 10:30 AM, 12:30 PM, and 2:30 PM. Note: only
                        time_of_day or hours and minutes can be used.
        :type minutes: list of int
        :param time_of_day: If you specify "Day" or "Week" for frequency, you can specify a time of day for the
                            schedule to run as a string in the form hh:mm. For example, if you specify "15:30" then
                            the schedule will run at 3:30pm. Note: only time_of_day or hours and minutes can be used.
        :type time_of_day: str
        :param week_days: If you specify "Week" for frequency, you can specify one or more days, separated by commas,
                          when you want to run the workflow: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                          "Saturday", and "Sunday"
        :type week_days: list of str
        """
        self.frequency = frequency
        self.interval = interval
        self.start_time = None
        if start_time is not None:
            if isinstance(start_time, datetime):
                if start_time.tzinfo is not None:
                    raise ValueError('Can not specify tzinfo for start_time, use time_zone instead.')
                self.start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                self.start_time = start_time
        self.time_zone = time_zone
        if self.start_time is not None and self.time_zone is None:
            self.time_zone = TimeZone.GMTStandardTime

        self.hours = hours
        self.minutes = minutes

        if time_of_day is not None and (hours is not None or minutes is not None):
            raise ValueError('Can not specify time_of_day and hours or minutes.')

        if time_of_day is not None:
            r = re.compile('[0-9]{1,2}:[0-9]{2}$')
            if r.match(time_of_day) is None:
                raise ValueError('time_of_day should be in the format hh:mm.')
            hour, minute = time_of_day.split(':')
            if int(hour) < 0 or int(hour) > 23:
                raise ValueError("Time of day hour value must be between 0 and 23.")
            if int(minute) < 0 or int(minute) > 59:
                raise ValueError("Time of day minute value must be between 0 and 59.")
            hour = [int(hour)]
            minute = [int(minute)]
            self.hours = hour
            self.minutes = minute
        self.week_days = week_days

    def validate(self):
        """Validate the schedule recurrence."""
        if self.frequency not in ["Minute", "Hour", "Day", "Week", "Month"]:
            raise ValueError("Invalid value for frequency, only one of Minute, Hour, Day, "
                             "Week, or Month accepted")
        if self.interval < 1:
            raise ValueError("Interval must be an integer greater than 0.")
        if self.frequency not in ["Day", "Week"] and self.hours is not None:
            raise ValueError("Can only specify hours if frequency is Week or Day.")
        if self.frequency not in ["Day", "Week"] and self.minutes is not None:
            raise ValueError("Can only specify minutes if frequency is Week or Day.")
        if self.frequency != "Week" and self.week_days is not None:
            raise ValueError("Can only specify week days if frequency is Week.")
        if self.hours is not None:
            for hour in self.hours:
                if hour < 0 or hour > 23:
                    raise ValueError("Hours must be between 0 and 23.")
        if self.minutes is not None:
            for minute in self.minutes:
                if minute < 0 or minute > 59:
                    raise ValueError("Minutes must be between 0 and 59.")
        if self.week_days is not None:
            for week_day in self.week_days:
                if week_day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                    raise ValueError("Week days must be a list of str, accepted values: Monday, Tuesday, Wednesday, "
                                     "Thursday, Friday, Saturday, Sunday.")
        if self.time_zone is not None and not isinstance(self.time_zone, TimeZone):
            raise ValueError("Time zone is not a valid TimeZone enum.")
        if self.start_time is not None and self.time_zone is None:
            raise ValueError('Must specify time_zone if start_time is provided.')


class TimeZone(Enum):
    """
    Enumerates the valid time zones for a recurrence :class:`azureml.pipeline.core.Schedule`.

    .. remarks::
        TimeZone can be used when creating a :class:`azureml.pipeline.core.ScheduleRecurrence` to specify the
        time zone of the recurrence start time. If None is provided UTC is used.

        Use a TimeZone when creating a Schedule as follows:

        .. code-block:: python

            from azureml.pipeline.core import Schedule, ScheduleRecurrence, TimeZone
            import datetime

            start_time = datetime.datetime(year=2019, month=5, day=20, hour=16)

            recurrence = ScheduleRecurrence(frequency="Minute",
                                            interval=30,
                                            start_time=start_time,
                                            time_zone=TimeZone.PacificStandardTime)

            schedule = Schedule.create(workspace, name="TestSchedule", pipeline_id=pipeline.id,
                                       experiment_name="experiment_name", recurrence=recurrence)

        This will create a Schedule which will trigger a Pipeline submission every 30 minutes starting May 20th, 2019
        at 4:00pm Pacific Standard Time.

        See the following link for more details on Schedules: `https://aka.ms/pl-schedule`
    """

    DatelineStandardTime = "Dateline Standard Time"
    UTC11 = "UTC-11"
    AleutianStandardTime = "Aleutian Standard Time"
    HawaiianStandardTime = "Hawaiian Standard Time"
    MarquesasStandardTime = "Marquesas Standard Time"
    AlaskanStandardTime = "Alaskan Standard Time"
    UTC09 = "UTC-09"
    PacificStandardTimeMexico = "Pacific Standard Time (Mexico)"
    UTC08 = "UTC-08"
    PacificStandardTime = "Pacific Standard Time"
    USMountainStandardTime = "US Mountain Standard Time"
    MountainStandardTimeMexico = "Mountain Standard Time (Mexico)"
    MountainStandardTime = "Mountain Standard Time"
    CentralAmericaStandardTime = "Central America Standard Time"
    CentralStandardTime = "Central Standard Time"
    EasterIslandStandardTime = "Easter Island Standard Time"
    CentralStandardTimeMexico = "Central Standard Time (Mexico)"
    CanadaCentralStandardTime = "Canada Central Standard Time"
    SAPacificStandardTime = "SA Pacific Standard Time"
    EasternStandardTimeMexico = "Eastern Standard Time (Mexico)"
    EasternStandardTime = "Eastern Standard Time"
    HaitiStandardTime = "Haiti Standard Time"
    CubaStandardTime = "Cuba Standard Time"
    USEasternStandardTime = "US Eastern Standard Time"
    ParaguayStandardTime = "Paraguay Standard Time"
    AtlanticStandardTime = "Atlantic Standard Time"
    VenezuelaStandardTime = "Venezuela Standard Time"
    CentralBrazilianStandardTime = "Central Brazilian Standard Time"
    SAWesternStandardTime = "SA Western Standard Time"
    PacificSAStandardTime = "Pacific SA Standard Time"
    TurksAndCaicosStandardTime = "Turks And Caicos Standard Time"
    NewfoundlandStandardTime = "Newfoundland Standard Time"
    TocantinsStandardTime = "Tocantins Standard Time"
    ESouthAmericaStandardTime = "E. South America Standard Time"
    SAEasternStandardTime = "SA Eastern Standard Time"
    ArgentinaStandardTime = "Argentina Standard Time"
    GreenlandStandardTime = "Greenland Standard Time"
    MontevideoStandardTime = "Montevideo Standard Time"
    SaintPierreStandardTime = "Saint Pierre Standard Time"
    BahiaStandardTime = "Bahia Standard Time"
    UTC02 = "UTC-02"
    MidAtlanticStandardTime = "Mid-Atlantic Standard Time"
    AzoresStandardTime = "Azores Standard Time"
    CapeVerdeStandardTime = "Cape Verde Standard Time"
    UTC = "UTC"
    MoroccoStandardTime = "Morocco Standard Time"
    GMTStandardTime = "GMT Standard Time"
    GreenwichStandardTime = "Greenwich Standard Time"
    WEuropeStandardTime = "W. Europe Standard Time"
    CentralEuropeStandardTime = "Central Europe Standard Time"
    RomanceStandardTime = "Romance Standard Time"
    CentralEuropeanStandardTime = "Central European Standard Time"
    WCentralAfricaStandardTime = "W. Central Africa Standard Time"
    NamibiaStandardTime = "Namibia Standard Time"
    JordanStandardTime = "Jordan Standard Time"
    GTBStandardTime = "GTB Standard Time"
    MiddleEastStandardTime = "Middle East Standard Time"
    EgyptStandardTime = "Egypt Standard Time"
    EEuropeStandardTime = "E. Europe Standard Time"
    SyriaStandardTime = "Syria Standard Time"
    WestBankStandardTime = "West Bank Standard Time"
    SouthAfricaStandardTime = "South Africa Standard Time"
    FLEStandardTime = "FLE Standard Time"
    TurkeyStandardTime = "Turkey Standard Time"
    IsraelStandardTime = "Israel Standard Time"
    KaliningradStandardTime = "Kaliningrad Standard Time"
    LibyaStandardTime = "Libya Standard Time"
    ArabicStandardTime = "Arabic Standard Time"
    ArabStandardTime = "Arab Standard Time"
    BelarusStandardTime = "Belarus Standard Time"
    RussianStandardTime = "Russian Standard Time"
    EAfricaStandardTime = "E. Africa Standard Time"
    IranStandardTime = "Iran Standard Time"
    ArabianStandardTime = "Arabian Standard Time"
    AstrakhanStandardTime = "Astrakhan Standard Time"
    AzerbaijanStandardTime = "Azerbaijan Standard Time"
    RussiaTimeZone3 = "Russia Time Zone 3"
    MauritiusStandardTime = "Mauritius Standard Time"
    GeorgianStandardTime = "Georgian Standard Time"
    CaucasusStandardTime = "Caucasus Standard Time"
    AfghanistanStandardTime = "Afghanistan Standard Time"
    WestAsiaStandardTime = "West Asia Standard Time"
    EkaterinburgStandardTime = "Ekaterinburg Standard Time"
    PakistanStandardTime = "Pakistan Standard Time"
    IndiaStandardTime = "India Standard Time"
    SriLankaStandardTime = "Sri Lanka Standard Time"
    NepalStandardTime = "Nepal Standard Time"
    CentralAsiaStandardTime = "Central Asia Standard Time"
    BangladeshStandardTime = "Bangladesh Standard Time"
    NCentralAsiaStandardTime = "N. Central Asia Standard Time"
    MyanmarStandardTime = "Myanmar Standard Time"
    SEAsiaStandardTime = "SE Asia Standard Time"
    AltaiStandardTime = "Altai Standard Time"
    WMongoliaStandardTime = "W. Mongolia Standard Time"
    NorthAsiaStandardTime = "North Asia Standard Time"
    TomskStandardTime = "Tomsk Standard Time"
    ChinaStandardTime = "China Standard Time"
    NorthAsiaEastStandardTime = "North Asia East Standard Time"
    SingaporeStandardTime = "Singapore Standard Time"
    WAustraliaStandardTime = "W. Australia Standard Time"
    TaipeiStandardTime = "Taipei Standard Time"
    UlaanbaatarStandardTime = "Ulaanbaatar Standard Time"
    NorthKoreaStandardTime = "North Korea Standard Time"
    AusCentralWStandardTime = "Aus Central W. Standard Time"
    TransbaikalStandardTime = "Transbaikal Standard Time"
    TokyoStandardTime = "Tokyo Standard Time"
    KoreaStandardTime = "Korea Standard Time"
    YakutskStandardTime = "Yakutsk Standard Time"
    CenAustraliaStandardTime = "Cen. Australia Standard Time"
    AUSCentralStandardTime = "AUS Central Standard Time"
    EAustraliaStandardTime = "E. Australia Standard Time"
    AUSEasternStandardTime = "AUS Eastern Standard Time"
    WestPacificStandardTime = "West Pacific Standard Time"
    TasmaniaStandardTime = "Tasmania Standard Time"
    VladivostokStandardTime = "Vladivostok Standard Time"
    LordHoweStandardTime = "Lord Howe Standard Time"
    BougainvilleStandardTime = "Bougainville Standard Time"
    RussiaTimeZone10 = "Russia Time Zone 10"
    MagadanStandardTime = "Magadan Standard Time"
    NorfolkStandardTime = "Norfolk Standard Time"
    SakhalinStandardTime = "Sakhalin Standard Time"
    CentralPacificStandardTime = "Central Pacific Standard Time"
    RussiaTimeZone11 = "Russia Time Zone 11"
    NewZealandStandardTime = "New Zealand Standard Time"
    UTC12 = "UTC+12"
    FijiStandardTime = "Fiji Standard Time"
    KamchatkaStandardTime = "Kamchatka Standard Time"
    ChathamIslandsStandardTime = "Chatham Islands Standard Time"
    TongaStandardTime = "Tonga Standard Time"
    SamoaStandardTime = "Samoa Standard Time"
    LineIslandsStandardTime = "Line Islands Standard Time"
