# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the data drift logic between two datasets, relies on the DataSets API."""

import glob
import os
import shutil
import tempfile
import warnings
from datetime import timezone, datetime
from collections import OrderedDict

import jsonpickle
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from azureml.contrib.datadrift import alert_configuration
from azureml.contrib.datadrift._logging._telemetry_logger import \
    _TelemetryLogger
from azureml.contrib.datadrift._logging._telemetry_logger_context_adapter import \
    _TelemetryLoggerContextAdapter
from azureml.contrib.datadrift._schedule_state import ScheduleState
from azureml.contrib.datadrift._restclient import DataDriftClient
from azureml.contrib.datadrift._restclient.api_versions import PUBLICPREVIEW
from azureml.contrib.datadrift._restclient.models import (AlertConfiguration,
                                                          DataDriftDto,
                                                          DataDriftRunDto)
from azureml.contrib.datadrift._utils.constants import (
    COLUMN_NAME, COMPUTE_TARGET_TYPE_AML, DATETIME, DEBUG_DATASHIFT_MCC_ALL,
    DEBUG_DATASHIFT_MCC_TEST, DEBUG_DATASHIFT_MCC_TRAIN, DRIFT_THRESHOLD,
    FIGURE_FEATURE_IMPORTANCE_TITLE, FIGURE_FEATURE_IMPORTANCE_Y_LABEL,
    HAS_DRIFT, METRIC_COLUMN_METRICS, METRIC_DATASET_METRICS,
    METRIC_DATASHIFT_FEATURE_IMPORTANCE, METRIC_DATASHIFT_MCC_ALL,
    METRIC_DATASHIFT_MCC_TEST, METRIC_DATASHIFT_MCC_TRAIN,
    METRIC_SCHEMA_VERSION_DFT, METRIC_SCHEMA_VERSION_KEY,
    METRIC_STATISTICAL_DISTANCE_ENERGY,
    METRIC_STATISTICAL_DISTANCE_WASSERSTEIN, METRIC_TYPE, METRIC_TYPE_COLUMN,
    METRIC_TYPE_DATASET, MODEL_NAME, MODEL_VERSION,
    OUTPUT_METRIC_DRIFT_COEFFICIENT, OUTPUT_METRIC_DRIFT_CONTRIBUTION,
    PIPELINE_START_TIME, RUN_ID, RUN_TYPE_ADHOC, SCORING_DATE, SERVICE,
    SERVICE_NAME)
from azureml.core import Datastore
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.workspace import Workspace
from azureml.exceptions import ComputeTargetException
from msrest.exceptions import HttpOperationError

from ._utils.parameter_validator import ParameterValidator

module_logger = _TelemetryLogger.get_telemetry_logger(__name__)

DEFAULT_COMPUTE_TARGET_NAME = "datadrift-server"
DEFAULT_VM_SIZE = "STANDARD_D2_V2"
DEFAULT_VM_MAX_NODES = 4
DEFAULT_DRIFT_THRESHOLD = 0.2


class DataDriftDetector:
    """Class for AzureML DataDriftDetector.

    DataDriftDetector class provides set of convenient APIs to identify any drifting between given training
    and/or scoring datasets for a model. A DataDriftDetector object is created with a workspace, a model name
    and a version, list of services, and optional tuning parameters. A DataDriftDetector task can be scheduled
    using enable_schedule() API and/or a one time task can be submitted using run(target_date) API.
    """

    def __init__(self, workspace, model_name, model_version):
        """Datadriftdetector constructor.

        The DataDriftDetector constructor is used to retrieve a cloud representation of a DatadriftDetector object
        associated with the provided workspace. Must provide model_name and model_version.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :return: A DataDriftDetector object
        :rtype: DataDriftDetector
        """
        if workspace is ... or model_name is ... or model_version is ...:
            # Instantiate an empty DataDriftDetector object. Will be initialized by DataDriftDetector.get()
            return

        log_context = {'workspace_name': workspace.name, 'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        self._logger = _TelemetryLoggerContextAdapter(module_logger, log_context)

        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)

        with _TelemetryLogger.log_activity(self._logger, activity_name="constructor") as logger:

            try:
                dd_list = DataDriftDetector._get_datadrift_list(workspace, model_name, model_version, logger=logger)
                if len(dd_list) > 1:
                    error_msg = "Multiple DataDriftDetector objects for: {} {} {}".format(workspace, model_name,
                                                                                          model_version)
                    logger.error(error_msg)
                    raise LookupError(error_msg)
                elif len(dd_list) == 1:
                    dto = dd_list[0]
                    self._initialize(workspace, dto.model_name, dto.model_version, dto.services,
                                     compute_target_name=dto.compute_target_name, frequency=dto.frequency,
                                     interval=dto.interval, feature_list=dto.features,
                                     drift_threshold=dto.drift_threshold, alert_config=dto.alert_configuration,
                                     schedule_start=dto.schedule_start_time if dto.schedule_start_time else None,
                                     state=dto.state, schedule_id=dto.schedule_id, dd_id=dto.id)
                else:
                    error_msg = "Could not find DataDriftDetector object for: {} {} {}".format(workspace, model_name,
                                                                                               model_version)
                    logger.error(error_msg)
                    raise KeyError(error_msg)
            except HttpOperationError or KeyError:
                # DataDriftDetector object doesn't exist for model_name and model_version, create one instead
                logger.error("DataDriftDetector object for model_name: {}, model_version: {} doesn't exist. "
                             "Create with DatadriftDetector.create()".format(model_name, model_version))
                raise

    def _initialize(self, workspace, model_name, model_version, services, compute_target_name=None, frequency=None,
                    interval=None, feature_list=None, schedule_start=None, alert_config=None, schedule_id=None,
                    state=ScheduleState.Disabled.name, dd_id=None, drift_threshold=None):
        r"""Class DataDriftDetector Constructor helper.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :param services: Optional, list of webservices to test for data drifting
        :type services: :class:list(str)
        :param compute_target_name: Optional, AzureML ComputeTarget name, may create one if needed and required
        :type compute_target_name: str
        :param frequency: Optional, how often the pipeline is run. i.e. "Day", "Week", "Month", default is "Day"
        :type frequency: str
        :param interval: Optional, how often the pipeline runs based on frequency. i.e. If frequency = "Day" and \
                         interval = 2, the pipeline will run every other day
        :type interval: int
        :param feature_list: Optional, whitelisted features to run the datadrift detection on
        :type feature_list: :class:list(str)
        :param schedule_start: Optional, start time of data drift schedule in UTC
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, alert configuration parameters
        :type alert_config: azureml.contrib.datadrift._restclient.models.AlertConfiguration
        :param schedule_id: Optional, pipeline schedule ID
        :type schedule_id: int
        :param state: Optional, denotes the state of the schedule: 'Disabled', 'Enabled', 'Disabling', 'Enabling'
        :type state: str
        :param dd_id: Optional, internal ID, only retrieved from service
        :type dd_id: int
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: A DataDriftDetector object
        :rtype: DataDriftDetector
        """
        self._workspace = workspace
        self._model_name = model_name
        self._model_version = model_version
        self._services = services
        self._compute_target_name = compute_target_name
        self._frequency = frequency
        self._interval = interval
        self._feature_list = feature_list
        # TODO: Below values are defaulted in private preview. Enable for public preview.
        self._drift_threshold = drift_threshold
        self._baseline_dataset = None
        self._baseline_dataset_start_time = None
        self._baseline_dataset_end_time = None

        self._schedule_start = schedule_start
        self._schedule_id = schedule_id
        self._state = state
        self._id = dd_id

        # Set alert configuration
        self._alert_config = alert_configuration.AlertConfiguration(
            alert_config.email_addresses) if alert_config else None

        # Instantiate service client
        self._client = DataDriftClient(self.workspace.service_context)

        if not hasattr(self, '_logger'):
            log_context = {'workspace_name': workspace.name, 'model_name': model_name, 'model_version': model_version,
                           'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

            self._logger = _TelemetryLoggerContextAdapter(module_logger, log_context)

    def __repr__(self):
        """Return the string representation of a DataDriftDetector object.

        :return: DataDriftDetector object string
        :rtype: str
        """
        return str(self.__dict__)

    @property
    def workspace(self):
        """Get the workspace of the DataDriftDetector object.

        :return: Workspace object
        :rtype: azureml.core.workspace.Workspace
        """
        return self._workspace

    @property
    def model_name(self):
        """Get the model name associated with the DataDriftDetector object.

        :return: Model name
        :rtype: str
        """
        return self._model_name

    @property
    def model_version(self):
        """Get the model version associated with the DataDriftDetector object.

        :return: Model version
        :rtype: int
        """
        return self._model_version

    @property
    def services(self):
        """Get the list of services attached to the DataDriftDetector object.

        :return: List of service names
        :rtype: :class:list(str)
        """
        return self._services

    @property
    def compute_target_name(self):
        """Get the Compute Target name attached to the DataDriftDetector object.

        :return: Compute Target name
        :rtype: str
        """
        return self._compute_target_name

    @property
    def frequency(self):
        """Get the frequency of the DataDriftDetector schedule.

        :return: String of either "Day", "Week" or "Month"
        :rtype: str
        """
        return self._frequency

    @property
    def interval(self):
        """Get the interval of the DataDriftDetector schedule.

        :return: Integer value of time unit
        :rtype: int
        """
        return self._interval

    @property
    def feature_list(self):
        """Get the list of whitelisted features for the DataDriftDetector object.

        :return: List of feature names
        :rtype: :class:list(str)
        """
        return self._feature_list

    @property
    def drift_threshold(self):
        """Get the drift threshold for the DataDriftDetector object.

        :return: Drift threshold
        :rtype: float
        """
        return self._drift_threshold

    @property
    def baseline_dataset(self):
        """Get the baseline dataset.

        :return: Dataset type of the baseline dataset
        :rtype: azureml.core.dataset.Dataset
        """
        return self._baseline_dataset

    @property
    def baseline_dataset_start_time(self):
        """Get the start time of the baseline dataset.

        :return: start_time of baseline dataset
        :rtype: datetime.datetime
        """
        return self._baseline_dataset_start_time

    @property
    def baseline_dataset_end_time(self):
        """Get the end time of the baseline dataset.

        :return: Tuple of datetime objects (start_time, end_time)
        :rtype: datetime.datetime
        """
        return self._baseline_dataset_end_time

    @property
    def schedule_start(self):
        """Get the start time of the schedule.

        :return: Datetime object of schedule start time in UTC
        :rtype: datetime.datetime
        """
        return self._schedule_start

    @property
    def alert_config(self):
        """Get the alert configuration for the DataDriftDetector object.

        :return: AlertConfiguration object.
        :rtype: azureml.contrib.datadrift.AlertConfiguration
        """
        return self._alert_config

    @property
    def state(self):
        """Denotes the state of the DataDrift schedule.

        :return: One of 'Disabled', 'Enabled', 'Disabling', 'Enabling'
        :rtype: str
        """
        return self._state

    @property
    def enabled(self):
        """Get the boolean value for whether the DataDriftDetector is enabled or not.

        :return: Boolean value; true for enabled
        :rtype: bool
        """
        return self._state == ScheduleState.Enabled.name

    @staticmethod
    def create(workspace, model_name, model_version, services, compute_target_name=None,
               frequency=None, interval=None, feature_list=None, schedule_start=None, alert_config=None,
               drift_threshold=None):
        r"""Create a new DataDriftDetector object in the Azure Machine Learning Workspace.

        Throws an exception if a DataDriftDetector for the same model_name and model_version already exists in the
        workspace.

        :param workspace: Object that points to workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :param services: Optional, list of webservices to test for data drifting
        :type services: :class:list(str)
        :param compute_target_name: Optional, AzureML ComputeTarget name
        :type compute_target_name: str
        :param frequency: Optional, how often the pipeline is run. i.e. "Day", "Week", "Month", default is "Day"
        :type frequency: str
        :param interval: Optional, how often the pipeline runs based on frequency. i.e. If frequency = "Day" and \
                         interval = 2, the pipeline will run every other day
        :type interval: int
        :param feature_list: Optional, whitelisted features to run the datadrift detection on
        :type feature_list: :class:list(str)
        :param schedule_start: Optional, start time of data drift schedule in UTC
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.contrib.datadrift.AlertConfiguration
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: A DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)
        services = ParameterValidator.validate_services(services)
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, workspace)
        frequency = ParameterValidator.validate_frequency(frequency)
        interval = ParameterValidator.validate_interval(interval)
        feature_list = ParameterValidator.validate_features(feature_list)
        schedule_start = ParameterValidator.validate_datetime(schedule_start)
        alert_config = ParameterValidator.validate_alert_configuration(alert_config)
        drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.create')
        log_context = {'workspace_name': workspace.name, 'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}

        logger = _TelemetryLoggerContextAdapter(logger, log_context)
        with _TelemetryLogger.log_activity(logger, activity_name="datadriftdetector.create") as logger:

            dd_client = DataDriftClient(workspace.service_context)

            try:
                if list(dd_client.list(model_name, model_version, logger=logger)):
                    error_msg = "DataDriftDetector already exists for model_name: {}, model_version: {}. Please use " \
                                "DataDriftDetector.get() to retrieve the object".format(model_name, model_version)
                    logger.error(error_msg)
                    raise KeyError(error_msg)
            except HttpOperationError:
                # DataDriftDetector object doesn't exist for model_name and model_version, create one instead
                logger.info("Error checking DataDriftDetector object for model_name: {}, model_version: {}"
                            .format(model_name, model_version))
                raise

            if not compute_target_name:
                # Set to default workspace compute if it exists
                compute_target_name = DataDriftDetector._get_default_compute_target(workspace)

            if not drift_threshold:
                drift_threshold = DEFAULT_DRIFT_THRESHOLD

            # Write object to service
            dto = DataDriftDto(frequency=frequency,
                               schedule_start_time=schedule_start.replace(tzinfo=timezone.utc).isoformat()
                               if schedule_start else None,
                               schedule_id=None,
                               interval=interval,
                               alert_configuration=AlertConfiguration(alert_config.email_addresses)
                               if alert_config else None,
                               id=None,
                               model_name=model_name,
                               model_version=model_version,
                               services=services,
                               compute_target_name=compute_target_name,
                               drift_threshold=drift_threshold,
                               base_line_dataset=None,
                               base_line_dataset_start_time=None,
                               base_line_dataset_end_time=None,
                               features=feature_list,
                               state=ScheduleState.Disabled.name,
                               enabled=False)
            client_dto = dd_client.create(dto, logger)
            DataDriftDetector._validate_client_dto(client_dto, logger)

            dd = DataDriftDetector(..., ..., ...)
            dd._initialize(workspace, client_dto.model_name, client_dto.model_version, client_dto.services,
                           compute_target_name=compute_target_name, frequency=client_dto.frequency,
                           interval=client_dto.interval, feature_list=client_dto.features,
                           schedule_start=client_dto.schedule_start_time if client_dto.schedule_start_time else None,
                           alert_config=client_dto.alert_configuration, schedule_id=client_dto.schedule_id,
                           state=client_dto.state, dd_id=client_dto.id,
                           drift_threshold=client_dto.drift_threshold)
            return dd

    @staticmethod
    def get(workspace, model_name, model_version):
        """Retrieve a unique DataDriftDetector object for a given workspace, model_name, model_version and list of services.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Version of model
        :type model_version: int
        :return: DataDriftDetector object
        :rtype: azureml.datadrift.DataDriftDetector
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        model_name = ParameterValidator.validate_model_name(model_name)
        model_version = ParameterValidator.validate_model_version(model_version)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.get')
        log_context = {'workspace_name': workspace.name, 'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}
        logger = _TelemetryLoggerContextAdapter(logger, log_context)

        with _TelemetryLogger.log_activity(logger, activity_name="get") as logger:
            logger.info("Getting DataDriftDetector object for: {} {} {}".format(workspace, model_name, model_version))
            return DataDriftDetector(workspace, model_name, model_version)

    @staticmethod
    def list(workspace, model_name=None, model_version=None, services=None):
        """Get a list of DataDriftDetector objects given a workspace. Model and services are optional input parameters.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Optional, name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Optional, version of model
        :type model_version: int
        :param services: Optional, names of webservices
        :type services: :class:list(str)
        :return: List of DataDriftDetector objects
        :rtype: :class:list(azureml.datadrift.DataDriftDetector)
        """
        workspace = ParameterValidator.validate_workspace(workspace)
        if model_name is not None:
            model_name = ParameterValidator.validate_model_name(model_name)
        if model_version is not None:
            model_version = ParameterValidator.validate_model_version(model_version)
        if services is not None:
            services = ParameterValidator.validate_services(services)

        logger = _TelemetryLogger.get_telemetry_logger('datadriftdetector.list')
        log_context = {'workspace_name': workspace.name, 'model_name': model_name, 'model_version': model_version,
                       'subscription_id': workspace.subscription_id, 'workspace_location': workspace.location}
        logger = _TelemetryLoggerContextAdapter(logger, log_context)

        with _TelemetryLogger.log_activity(logger, activity_name="list") as logger:
            dto_list = DataDriftDetector._get_datadrift_list(workspace, model_name, model_version, services, logger)
            dd_list = []
            for dto in dto_list:
                dd = DataDriftDetector(..., ..., ...)
                dd._initialize(workspace, dto.model_name, dto.model_version, dto.services,
                               compute_target_name=dto.compute_target_name, frequency=dto.frequency,
                               interval=dto.interval,
                               feature_list=dto.features, drift_threshold=dto.drift_threshold,
                               alert_config=dto.alert_configuration,
                               schedule_start=dto.schedule_start_time if dto.schedule_start_time else None,
                               state=dto.state, schedule_id=dto.schedule_id, dd_id=dto.id)
                # TODO: Add baseline and drift threshold info after private preview
                dd_list.append(dd)
            return dd_list

    @staticmethod
    def _get_default_compute_target(workspace):
        """If the Workspace default compute target exists retrieve its name, or return the default compute target name.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :return: Compute target name
        :rtype: str
        """
        return workspace.get_default_compute_target('CPU').name \
            if workspace.get_default_compute_target('CPU') \
            else DEFAULT_COMPUTE_TARGET_NAME

    @staticmethod
    def _get_datadrift_list(workspace, model_name, model_version, services=None, logger=None, client=None):
        """Get list of DataDriftDetector objects from service.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param model_name: Optional, name of model to run DataDriftDetector on
        :type model_name: str
        :param model_version: Optional, version of model
        :type model_version: int
        :param services: Optional, names of webservices
        :type services: :class:list(str)
        :param logger: Activity logger for service call
        :type logger: datetime.datetime
        :param client: DataDriftDetector service client
        :type client: azureml.contrib.datadrift._restclient.DataDriftClient
        :return: List of DataDriftDetector objects
        :rtype: list(azureml.contrib.datadrift._restclient.models.DataDriftDto)
        """
        dd_client = client if client else DataDriftClient(workspace.service_context)

        return list(dd_client.list(model_name=model_name, model_version=model_version, services=services,
                                   logger=logger))

    @staticmethod
    def _create_aml_compute(workspace, name):
        """Create an aml compute using name.

        Create a new one.

        :param workspace: Object that points to the workspace
        :type workspace: azureml.core.workspace.Workspace
        :param name: the name of aml compute target
        :type name: str
        :return: Azure ML Compute target
        :rtype: azureml.core.compute.compute.AmlCompute
        """
        log_context = {'workspace_name': workspace.name, 'subscription_id': workspace.subscription_id,
                       'workspace_location': workspace.location}
        # TODO: De-provision compute if it's not run
        module_logger.info("creating new compute target: {}".format(name), extra={'properties': log_context})

        if name == Workspace.DEFAULT_CPU_CLUSTER_NAME:
            # Use AzureML default aml compute config
            aml_compute = AmlCompute.create(workspace,
                                            Workspace.DEFAULT_CPU_CLUSTER_NAME,
                                            Workspace.DEFAULT_CPU_CLUSTER_CONFIGURATION)
        else:
            provisioning_config = AmlCompute.provisioning_configuration(
                vm_size=DEFAULT_VM_SIZE,
                max_nodes=DEFAULT_VM_MAX_NODES
            )
            aml_compute = AmlCompute.create(workspace, name, provisioning_config)

        aml_compute.wait_for_completion(show_output=True)
        return aml_compute

    def run(self, target_date, services, compute_target_name=None, create_compute_target=False,
            feature_list=None, drift_threshold=None):
        """Run an ad-hoc data drift detection run on a model for a specified time window.

        :param services: List of webservices to run DataDrift job on
        :type services: :class:list(str)
        :param target_date:  Target date of scoring data in UTC
        :type target_date: datetime.datetime
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param create_compute_target: Optional, whether the DataDriftDetector API should automatically create an AML
                                      compute target
        :type create_compute_target: bool
        :param feature_list: Optional, whitelisted features to run the datadrift detection on
        :type feature_list: :class:list(str)
        :param drift_threshold: Optional, threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: DataDriftDetector experiment run ID
        :rtype: str
        """
        target_date = ParameterValidator.validate_datetime(target_date)
        services = ParameterValidator.validate_services(services)
        compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name, self.workspace,
                                                                              not_exist_ok=create_compute_target)
        feature_list = ParameterValidator.validate_features(feature_list)
        drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)

        with _TelemetryLogger.log_activity(self._logger, activity_name="run") as logger:
            if not compute_target_name:
                # Fallback to object's compute target
                compute_target_name = self.compute_target_name

            if drift_threshold is None:
                # Fallback to object's drift threshold
                drift_threshold = self.drift_threshold

            self._get_compute_target(compute_target_name=compute_target_name,
                                     create_compute_target=create_compute_target, logger=logger)

            dto = DataDriftRunDto(model_name=self.model_name,
                                  model_version=self.model_version,
                                  services=services,
                                  compute_target_name=compute_target_name,
                                  start_time=target_date.replace(tzinfo=timezone.utc).isoformat(),
                                  features=feature_list,
                                  drift_threshold=drift_threshold,
                                  run_type=RUN_TYPE_ADHOC)
            run_dto = self._client.run(self._id, dto, logger, api_version=PUBLICPREVIEW)
            return run_dto.execution_run_id

    def enable_schedule(self, create_compute_target=False):
        """Create a schedule to run  a datadrift job for a specified model and webservice."""
        with _TelemetryLogger.log_activity(self._logger, activity_name="enable_schedule") as logger:
            # TODO: Add check for baseline dataset property being set
            compute_target = self._get_compute_target(self.compute_target_name, create_compute_target, logger)
            compute_target_type = compute_target.type
            if compute_target_type != COMPUTE_TARGET_TYPE_AML:
                raise AttributeError(
                    "Compute target {} must be of type {} while it is {}".format(
                        self.compute_target_name,
                        COMPUTE_TARGET_TYPE_AML,
                        compute_target_type))

            try:
                self._state = ScheduleState.Enabled.name
                dto = self._update_remote(logger)
                self._schedule_id = dto.schedule_id
                self._schedule_start = dto.schedule_start_time if dto.schedule_start_time else None
                self._state = dto.state
            except HttpOperationError or SystemError:
                logger.exception("Unable to enable the schedule in workspace: {}".format(self.workspace))
                raise

    def disable_schedule(self):
        """Disable a schedule for a specified model and web service."""
        with _TelemetryLogger.log_activity(self._logger, activity_name="disable_schedule") as logger:
            try:
                self._state = ScheduleState.Disabled.name
                self._update_remote(logger)
            except HttpOperationError or SystemError:
                logger.exception(
                    "Unable to disable the schedule with ID: {} in workspace: {}".format(
                        self._schedule_id,
                        self.workspace))
                raise

    def get_output(self, start_time, end_time, run_id=None, daily_latest_only=True):
        """Get a tuple of the drift results and metrics for a specific DataDriftDetector object over a given time window.

        :param start_time: Start time of results window in UTC
        :type start_time: datetime.datetime
        :param end_time: End time of results window in UTC
        :type end_time: datetime.datetime
        :param run_id: Optional, adhoc run id
        :type run_id: int
        :param daily_latest_only: Optional, flag of whether return only each day's latest output.
        :type run_id: bool
        :return: Tuple of a list of drift results, and a list of individual dataset and columnar metrics
        :rtype: tuple(:class:list(), :class:list())
        """
        # example of outputs:
        # results : [{'service_name': 'service1', 'result':
        #                                         [{'has_drift': True, 'datetime': '2019-04-03', 'model_name':
        #                                           'modelName', 'model_version': 2, 'drift_threshold': 0.3}]}]
        #
        # metrics : [{'service_name': 'service1',
        #             'metrics': [{'datetime': '2019-04-03',
        #                          'model_name': 'modelName',
        #                          'model_version': 2,
        #                          'schema_version': '0.1'
        #                          'dataset_metrics': [{'name': 'datadrift_coefficient', 'value': 0.345345345345559}],
        #                          'column_metrics': [{'feature1': [{'name': 'datadrift_contribution',
        #                                                            'value': 288.0},
        #                                                           {'name': 'wasserstein_distance',
        #                                                            'value': 4.858040000000001},
        #                                                           {'name': 'energy_distance',
        #                                                           'value': 2.7204799576545313}]}]}]}]
        #

        start_time = ParameterValidator.validate_datetime(start_time)
        end_time = ParameterValidator.validate_datetime(end_time)
        if run_id is not None:
            run_id = ParameterValidator.validate_run_id(run_id)

        results = []
        metrics = []

        get_metrics = self._get_metrics(daily_latest_only)

        # Check if metrics exist
        if not get_metrics or len(get_metrics) == 0:
            error_msg = "Metrics do not exist for model: {} with version: {}".format(self.model_name,
                                                                                     self.model_version)
            self._logger.error(error_msg)
            raise NameError(error_msg)

        # Filter based on input params
        if run_id:
            get_metrics = [m for m in get_metrics if m.get_extended_properties()[RUN_ID] == run_id]
        get_metrics = [m for m in get_metrics if
                       start_time <= m.get_extended_properties()[SCORING_DATE] <= end_time]

        for metric in get_metrics:
            ep = metric.get_extended_properties()
            if metric.name == OUTPUT_METRIC_DRIFT_COEFFICIENT:
                # Overall drift coefficient; add to results return object
                service_exists = False
                for r in results:
                    if r[SERVICE_NAME] == ep['service']:
                        # Service already in dict; add metric to result list
                        service_exists = True
                        res = r['result']
                        res.append({HAS_DRIFT: metric.value > ep[DRIFT_THRESHOLD],
                                    DATETIME: ep[SCORING_DATE],
                                    MODEL_NAME: ep[MODEL_NAME],
                                    MODEL_VERSION: ep[MODEL_VERSION],
                                    DRIFT_THRESHOLD: ep[DRIFT_THRESHOLD]})
                if not service_exists:
                    # Add new service to results list
                    result = [{
                        HAS_DRIFT: metric.value > ep[DRIFT_THRESHOLD],
                        DATETIME: ep[SCORING_DATE],
                        MODEL_NAME: ep[MODEL_NAME],
                        MODEL_VERSION: ep[MODEL_VERSION],
                        DRIFT_THRESHOLD: ep[DRIFT_THRESHOLD]
                    }]
                    res = {SERVICE_NAME: ep['service'], "result": result}
                    results.append(res)
            # Add to metrics return object
            metric_service_exists = False
            for m in metrics:
                if m[SERVICE_NAME] == ep['service']:
                    metric_service_exists = True
                    met_metric_exists = False
                    for met in m['metrics']:
                        datetime_check = met[DATETIME] == ep[SCORING_DATE]
                        model_name_check = met[MODEL_NAME] == ep[MODEL_NAME]
                        model_version_check = met[MODEL_VERSION] == ep[MODEL_VERSION]
                        if datetime_check and model_name_check and model_version_check:
                            _metric = {'name': metric.name, 'value': metric.value}
                            met_metric_exists = True
                            # Add to already existing metric dictionary
                            if ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
                                if METRIC_DATASET_METRICS not in met:
                                    met[METRIC_DATASET_METRICS] = []
                                met[METRIC_DATASET_METRICS].append(_metric)

                            elif ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
                                column_in_metrics = False
                                if METRIC_COLUMN_METRICS not in met:
                                    met[METRIC_COLUMN_METRICS] = []
                                for c_metric in met[METRIC_COLUMN_METRICS]:
                                    if ep['column_name'] in c_metric:
                                        column_in_metrics = True
                                        column = c_metric[ep['column_name']]
                                        column.append(_metric)
                                if not column_in_metrics:
                                    # Create column dict in column_metrics
                                    column_dict = {ep['column_name']: [_metric]}
                                    met[METRIC_COLUMN_METRICS].append(column_dict)
                    if not met_metric_exists:
                        # Add new metric in metrics list
                        metric_dict = DataDriftDetector._create_metric_dict(metric)
                        m['metrics'].append(metric_dict)

            if not metric_service_exists:
                # Add metrics service dict
                metrics_list = []
                metric_dict = DataDriftDetector._create_metric_dict(metric)
                metrics_list.append(metric_dict)
                service_metric = {SERVICE_NAME: ep['service'], 'metrics': metrics_list}
                metrics.append(service_metric)

        return results, metrics

    @staticmethod
    def _create_metric_dict(metric):
        """Create metrics dictionary.

        :param metric: Metric object
        :type metric: azureml.contrib.datadrift._datadiff.Metric
        :return: Dictionary of metrics delineated by service
        :rtype: dict()
        """
        ep = metric.get_extended_properties()
        _metric = {'name': metric.name, 'value': metric.value}
        metric_dict = {DATETIME: ep[SCORING_DATE],
                       MODEL_NAME: ep[MODEL_NAME],
                       MODEL_VERSION: ep[MODEL_VERSION],
                       METRIC_SCHEMA_VERSION_KEY: metric.schema_version}

        # Use user friendly key without postfix such as "(Test)"
        if metric.name == METRIC_DATASHIFT_MCC_TEST:
            _metric['name'] = OUTPUT_METRIC_DRIFT_COEFFICIENT

        if ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
            if METRIC_DATASET_METRICS not in metric_dict:
                metric_dict[METRIC_DATASET_METRICS] = []
            metric_dict[METRIC_DATASET_METRICS].append(_metric)

        elif ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
            column_dict = {ep['column_name']: [_metric]}
            metric_dict[METRIC_COLUMN_METRICS].append(column_dict)

        return metric_dict

    def update(self, services=..., compute_target_name=..., frequency=..., interval=..., feature_list=...,
               schedule_start=..., alert_config=..., create_compute_target=False, drift_threshold=...):
        r"""Update the schedule associated with the DataDriftDetector object.

        :param services: Optional, list of services to update
        :type services: :class:list(str)
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param frequency: How often the pipeline is run. i.e. "Day", "Week", "Month", default is "Day"
        :type frequency: str
        :param interval: Optional, how often the pipeline runs based on frequency. i.e. If frequency = "Day" and \
                         interval = 2, the pipeline will run every other day
        :type interval: int
        :param feature_list: Whitelisted features to run the datadrift detection on
        :type feature_list: :class:list(str)
        :param schedule_start: Start time of data drift schedule in UTC
        :type schedule_start: datetime.datetime
        :param alert_config: Optional, configuration object for DataDriftDetector alerts
        :type alert_config: azureml.contrib.datadrift.AlertConfiguration
        :param create_compute_target: Whether the DataDriftDetector API should automatically create an AML compute
                                      target. Will be ignored if the schedule is disabled.
        :type create_compute_target: bool
        :param drift_threshold: Threshold to enable DataDriftDetector alerts on
        :type drift_threshold: float
        :return: self
        :rtype: azureml.contrib.datadrift.DataDriftDetector
        """
        with _TelemetryLogger.log_activity(self._logger, activity_name="update") as logger:
            if services is not ...:
                services = ParameterValidator.validate_services(services)
                self._services = services
            if compute_target_name is not ...:
                self._compute_target_name = ParameterValidator.validate_compute_target_name(compute_target_name,
                                                                                            self.workspace)
                if not self._compute_target_name:
                    self._compute_target_name = self._get_default_compute_target(self.workspace)
            if frequency is not ...:
                self._frequency = ParameterValidator.validate_frequency(frequency, instance_logger=self._logger)
            if interval is not ...:
                self._interval = ParameterValidator.validate_interval(interval, instance_logger=self._logger)
            if feature_list is not ...:
                self._feature_list = ParameterValidator.validate_features(feature_list)
            if schedule_start is not ...:
                self._schedule_start = ParameterValidator.validate_datetime(schedule_start)
            if alert_config is not ...:
                self._alert_config = ParameterValidator.validate_alert_configuration(alert_config)
            if drift_threshold is not ...:
                self._drift_threshold = ParameterValidator.validate_drift_threshold(drift_threshold)
                if not self._drift_threshold:
                    self._drift_threshold = DEFAULT_DRIFT_THRESHOLD
            # TODO: Re-enable below values after private preview
            # if baseline_dataset is not ...:
            #     self._baseline_dataset = baseline_dataset
            # if baseline_dataset_start_time is not ...:
            #     self._baseline_dataset_start_time = baseline_dataset_start_time
            # if baseline_dataset_end_time is not ...:
            #     self._baseline_dataset_end_time = baseline_dataset_end_time

            self._update_remote(logger)
            return self

    def _update_remote(self, logger):
        """Update the DataDriftDetector entry in the service database.

        :param logger: Activity logger for service call
        :type logger: datetime.datetime
        :return: DataDriftDetector data transfer object
        :rtype: logging.Logger
        """
        dto = DataDriftDto(frequency=self._frequency,
                           schedule_start_time=self._schedule_start.replace(tzinfo=timezone.utc).isoformat()
                           if self._schedule_start else None,
                           schedule_id=self._schedule_id,
                           interval=self._interval,
                           alert_configuration=AlertConfiguration(self.alert_config.email_addresses)
                           if self.alert_config else None,
                           id=self._id,
                           model_name=self._model_name,
                           model_version=self._model_version,
                           services=self._services,
                           compute_target_name=self._compute_target_name,
                           base_line_dataset=self._baseline_dataset,
                           base_line_dataset_start_time=self._baseline_dataset_start_time,
                           base_line_dataset_end_time=self._baseline_dataset_end_time,
                           features=self._feature_list,
                           state=self._state,
                           drift_threshold=self._drift_threshold)
        client_dto = self._client.update(self._id, dto, logger, api_version=PUBLICPREVIEW)
        DataDriftDetector._validate_client_dto(client_dto, logger)
        return client_dto

    def _get_compute_target(self, compute_target_name=None, create_compute_target=False, logger=None):
        """Get compute target.

        :type compute_target_name: str
        :param create_compute_target: if or not or create a aml compute target if not existing
        :type create_compute_target: boolean
        :param compute_target_name: Optional, AzureML ComputeTarget name, creates one if none is specified
        :type compute_target_name: str
        :param logger: Optional, Datadrift logger
        :type logger: logging.LoggerAdapter
        :return: ComputeTarget
        :rtype: azureml.core.compute.ComputeTarget
        """
        # If any of the params below are None, this is a schedule run so default to the DataDriftDetector object's args
        if compute_target_name is None:
            compute_target_name = self.compute_target_name
        if logger is None:
            logger = self._logger

        try:
            compute_target = ComputeTarget(self.workspace, compute_target_name)
            return compute_target

        except ComputeTargetException as e:
            # get the aml compute target or create if it is not available and create_compute_target is True
            if create_compute_target:
                return self._create_aml_compute(self.workspace, compute_target_name)
            else:
                error_message = "compute target {} is not available." \
                                "Use create_compute_target=True to allow creation of a new compute target." \
                    .format(self.compute_target_name)
                logger.error(error_message)
                raise ComputeTargetException(error_message) from e

    @staticmethod
    def _get_metrics_path(model_name, model_version, service, target_date=None):
        """Get the metric path for a given model version, instance target date and frequency of diff.

        :param model_name: Model name
        :type model_name: str
        :param model_version: Model version
        :type model_version: int
        :param service: Service name
        :type service: str
        :param target_date: Diff instance start time. If none datetime portion is ommitted.
        :type target_date: datetime.datetime
        :return: Relative path to metric on datastore
        :rtype: str
        """
        metrics_output_path = "DataDrift/Metrics/{}/{}/{}/".format(
            model_name, model_version, service)

        if target_date is not None:
            metrics_output_path += "{}/".format(target_date.strftime('%Y/%m/%d'))

        return metrics_output_path

    def _get_metrics(self, daily_latest_only=True):
        """Get all metrics for current DataDriftDetector instance."""
        ds = Datastore(self.workspace, "workspaceblobstore")
        local_temp_root = os.path.join(tempfile.gettempdir(), self.workspace.get_details()["workspaceid"])
        os.makedirs(local_temp_root, exist_ok=True)

        metrics = []

        for s in self.services:
            metrics_rel_path = DataDriftDetector._get_metrics_path(self.model_name, self.model_version, s)

            ds.download(target_path=local_temp_root, prefix=metrics_rel_path, show_progress=False)

            metrics_list = glob.glob(os.path.join(
                local_temp_root, *"{}/**/*.json".format(metrics_rel_path).split("/")), recursive=True)

            for f in metrics_list:
                with open(f, 'r') as metrics_json:
                    data = metrics_json.read()
                    metrics = metrics + jsonpickle.decode(data)

        # Refine metrics and be compatible for old data:
        #   1. Assign default schema version (0.1) if unavailable in old data
        #   2. Refresh data drift coefficient key if unavailable and put mcc pairs in extended property
        mcc_train_value = 0.0
        mcc_all_value = 0.0
        for m in metrics:
            if m.name == METRIC_DATASHIFT_MCC_TRAIN:
                mcc_train_value = m.value
                metrics.remove(m)
            if m.name == METRIC_DATASHIFT_MCC_ALL:
                mcc_all_value = m.value
                metrics.remove(m)

        for m in metrics:
            if hasattr(m, METRIC_SCHEMA_VERSION_KEY) is False:
                m.schema_version = METRIC_SCHEMA_VERSION_DFT
                if m.name == METRIC_DATASHIFT_MCC_TEST:
                    ep = m.get_extended_properties()
                    m.name = OUTPUT_METRIC_DRIFT_COEFFICIENT
                    ep[DEBUG_DATASHIFT_MCC_TEST] = m.value
                    ep[DEBUG_DATASHIFT_MCC_TRAIN] = mcc_train_value
                    ep[DEBUG_DATASHIFT_MCC_ALL] = mcc_all_value
                if m.name == METRIC_DATASHIFT_FEATURE_IMPORTANCE:
                    m.name = OUTPUT_METRIC_DRIFT_CONTRIBUTION

        # dedup data based on pipeline start time.
        # NOTICE:
        #  The dedup won't include multiple scoring dates, even if those records have same pipeline start date.
        #  (It's possible that outputs in different scoring date attached same date's pipeline start time.)
        #
        #  Therefore the dedup key is made by combination of scoring date and pipeline start date.
        #  (Here assuming the all metrics retrieved are with the same service name and model name/version
        #   since this method is an instance method.)
        if daily_latest_only is True:
            skipping = False
            dedupped_pipeline_start_times = {}
            for m in metrics:
                # Skip dedupping if pipeline start time or scoring date is unavailable.
                if SCORING_DATE not in m.extended_properties or PIPELINE_START_TIME not in m.extended_properties:
                    skipping = True
                    break
                if skipping is False and m.name == OUTPUT_METRIC_DRIFT_COEFFICIENT:
                    # Check scoring date & pipeline start time for dedupping if available
                    ep = m.get_extended_properties()
                    _scoring_date = ep[SCORING_DATE]
                    pipeline_time = ep[PIPELINE_START_TIME]
                    pipeline_date = pipeline_time.date()

                    dedup_key = "SD-{}-PD-{}".format(_scoring_date, pipeline_date)

                    if dedup_key not in dedupped_pipeline_start_times:
                        dedupped_pipeline_start_times[dedup_key] = pipeline_time
                    else:
                        dedupped_pipeline_start_times[dedup_key] = pipeline_time \
                            if pipeline_time > dedupped_pipeline_start_times[dedup_key] \
                            else dedupped_pipeline_start_times[dedup_key]
            # dedupping
            if skipping is False:
                metrics = [x for x in metrics
                           if x.get_extended_properties()[PIPELINE_START_TIME]
                           in dedupped_pipeline_start_times.values()]

        # tempfile.gettempdir() always points to same folder with same guid
        # thus empty temp folder to ensure new contents will be downloaded in each running.
        shutil.rmtree(local_temp_root, ignore_errors=True)

        return metrics

    @staticmethod
    def _generate_plot_figure(environment, ordered_content, with_details):
        """Show trends for a metrics.

        :param environment: information of workspace, model, model version and service
        :type ordered_content: str
        :param ordered_content: all contents to present presorted by date
        :type ordered_content: nested dict
        :param with_details: flag of show all or not
        :type with_details: bool
        :return: matplotlib.figure.Figure
        """
        dates = list(ordered_content.keys())
        drifts_train = []
        drift_contribution = {}
        distance_energy = {}
        distnace_wasserstein = {}
        columns = []
        summary_contribute = {}
        bottoms_contribute = []
        columns_distance_e = []
        columns_distance_w = []

        for d in dates:
            drifts_train.append(ordered_content[d][OUTPUT_METRIC_DRIFT_COEFFICIENT])
            summary_contribute[d] = 0
            bottoms_contribute.append(0)
            for c in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION].keys():
                if c not in columns:
                    columns.append(c)

        for d in dates:
            if with_details is True:
                for c in columns:
                    if OUTPUT_METRIC_DRIFT_CONTRIBUTION in ordered_content[d]:
                        if c not in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION]:
                            warnings.warn("Drift Contribution of column {} is unavailable.".format(c))
                        if c not in drift_contribution:
                            drift_contribution[c] = {}
                        if c in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION]:
                            drift_contribution[c][d] = ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION][c]
                            summary_contribute[d] += ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION][c]
                        else:
                            # if drift coefficient is missing on that day, set its ratio to 0.
                            drift_contribution[c][d] = 0

                    # add distance for all columns, will eliminate columns without distance later.
                    if c not in distance_energy:
                        distance_energy[c] = {}
                    # default value is null
                    distance_energy[c][d] = np.nan
                    # update value if distance output is available
                    if METRIC_STATISTICAL_DISTANCE_ENERGY in ordered_content[d]:
                        if c in ordered_content[d][METRIC_STATISTICAL_DISTANCE_ENERGY]:
                            distance_energy[c][d] = ordered_content[d][METRIC_STATISTICAL_DISTANCE_ENERGY][c]
                            if c not in columns_distance_e:
                                columns_distance_e.append(c)

                    # add distance for all columns, will eliminate columns without distance later.
                    if c not in distnace_wasserstein:
                        distnace_wasserstein[c] = {}
                    # default value is null
                    distnace_wasserstein[c][d] = np.nan
                    # update value if distance output is available
                    if METRIC_STATISTICAL_DISTANCE_WASSERSTEIN in ordered_content[d]:
                        if c in ordered_content[d][METRIC_STATISTICAL_DISTANCE_WASSERSTEIN]:
                            distnace_wasserstein[c][d] = ordered_content[d][METRIC_STATISTICAL_DISTANCE_WASSERSTEIN][c]
                            if c not in columns_distance_w:
                                columns_distance_w.append(c)

        # sum up daily coefficient
        daily_summary_contribution = list(summary_contribute.values())
        columns_contribution = list(drift_contribution.keys())

        # remove columns if distance is unavailable for all days.
        distance_energy = {k: v for k, v in distance_energy.items() if k in columns_distance_e}
        distnace_wasserstein = {k: v for k, v in distnace_wasserstein.items() if k in columns_distance_w}

        # show data drift
        width = 10
        height = 8
        ratio = 2 if with_details is True else 1
        myFmt = mdates.DateFormatter('%Y-%m-%d')
        xrange = pd.date_range(dates[0], dates[-1], freq='D')

        # when time range is wide and dates are actually uncontinuous, just show dates with drifts.
        xrange = [x for x in xrange if x.date() in [y.date() for y in dates]]

        figure = plt.figure(figsize=(width * ratio, height * ratio))
        plt.suptitle(environment, fontsize=14)
        plt.subplots_adjust(bottom=0.1, top=0.85 if with_details is True else 0.75, hspace=0.5)
        plt.tight_layout()
        ax1 = plt.subplot(ratio, ratio, 1)

        ax1.xaxis.set_major_formatter(myFmt)
        plt.sca(ax1)
        plt.plot_date(dates, drifts_train, '-g', marker='.', linewidth=0.5, markersize=5)
        plt.xlabel("Date", fontsize=16)
        plt.ylabel("Drift", fontsize=16)
        plt.xticks(xrange, rotation=15)
        plt.title("Drift Coefficient\n", fontsize=20)

        if with_details is True:
            ax2 = plt.subplot(ratio, ratio, 2)
            ax3 = plt.subplot(ratio, ratio, 3)
            ax4 = plt.subplot(ratio, ratio, 4)
            colors = plt.cm.get_cmap('gist_rainbow')

            plt.sca(ax2)
            yvals = ax2.get_yticks()
            ax2.set_yticklabels(['{:,.2%}'.format(v) for v in yvals])
            ax2.xaxis.set_major_formatter(myFmt)
            for c in columns_contribution:
                # draw bar graph
                contribution = list(drift_contribution[c].values())
                bar_ratio = [x / y for x, y in zip(contribution, daily_summary_contribution)]
                ax2.bar(dates, height=bar_ratio, bottom=bottoms_contribute)
                bottoms_contribute = [x + y for x, y in zip(bottoms_contribute, bar_ratio)]

            plt.xlabel("Date", fontsize=16)
            plt.ylabel(FIGURE_FEATURE_IMPORTANCE_Y_LABEL, fontsize=16)
            plt.xticks(xrange, rotation=15)
            plt.title(FIGURE_FEATURE_IMPORTANCE_TITLE, fontsize=20)
            plt.legend(columns_contribution)

            plt.sca(ax3)
            plt.yscale('log')
            # to present value 0 under logscale
            ax3.set_xscale('symlog')
            ax3.set_yscale('symlog')
            ax3.xaxis.set_major_formatter(myFmt)
            for c in columns_distance_e:
                plt.plot_date(dates, distance_energy[c].values(),
                              c=colors(1. * columns.index(c) / len(columns)),
                              linestyle='dashed', marker='.', linewidth=0.5, markersize=5)
            plt.xlabel("Date", fontsize=16)
            plt.ylabel("Distance", fontsize=16)
            plt.xticks(xrange, rotation=15)
            plt.title("Energy Distance\n", fontsize=20)
            plt.legend(columns_distance_e)

            plt.sca(ax4)
            plt.yscale('log')
            # to present value 0 under logscale
            ax4.set_xscale('symlog')
            ax4.set_yscale('symlog')
            ax4.xaxis.set_major_formatter(myFmt)
            for c in columns_distance_w:
                plt.plot_date(dates, distnace_wasserstein[c].values(),
                              c=colors(1. * columns.index(c) / len(columns)),
                              linestyle='dashed', marker='.', linewidth=0.5, markersize=5)
            plt.xlabel("Date", fontsize=16)
            plt.ylabel("Distance", fontsize=16)
            plt.xticks(xrange, rotation=15)
            plt.title("Wasserstein Distance\n", fontsize=20)
            plt.legend(columns_distance_w)

        return figure

    def show(self, start_time=datetime.min, end_time=datetime.max, with_details=False):
        """Show data drift trend in given time range for a given model, version and service.

        :param start_time:  Optional, start of presenting data time window in UTC, default is 0001-01-01 00:00:00
        :type start_time: datetime.datetime
        :param end_time: Optional, end of presenting data time window in UTC, default is 9999-12-31 23:59:59.999999
        :type end_time: datetime.datetime
        :param with_details: Show additional graphs of feature contribution and energy/wasserstein distance if True
        :type with_details: bool
        :return: diction of all figures. Key is service_name
        :rtype: dict()
        """
        start_time_valid = ParameterValidator.validate_datetime(start_time)
        end_time_valid = ParameterValidator.validate_datetime(end_time)

        metrics = self._get_metrics(daily_latest_only=True)

        if len(metrics) == 0:
            raise FileNotFoundError("DataDriftDetector results are unavailable.")

        metrics_dates = set()
        metrics_services = set()
        for m in metrics:
            metrics_dates.add(m.get_extended_properties()[SCORING_DATE])
            metrics_services.add(m.get_extended_properties()["service"])

        # build metrics for graph showing of each service in valid date range
        # the graph is per service; In side each graph, there might be sub plots for different measurements.
        # considering the order in dict is not guaranteed, organize all contents with date key and sort by date
        # general data drift will be stored per day
        # detailed measurement will be sorted per measurement per column per day
        contents = {}
        found_nothing = True
        for s in metrics_services:
            if s not in contents:
                contents[s] = {}
            for m in metrics:
                metric_ep = m.get_extended_properties()
                date = metric_ep[SCORING_DATE]
                if start_time_valid <= date <= end_time_valid:
                    found_nothing = False
                    if date not in contents[s]:
                        contents[s][date] = {}
                    if metric_ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
                        contents[s][date][m.name] = m.value
                        contents[s][date][SERVICE] = metric_ep[SERVICE]
                    if with_details is True and metric_ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
                        if m.name not in contents[s][date]:
                            contents[s][date][m.name] = {}
                        contents[s][date][m.name][metric_ep[COLUMN_NAME]] = m.value

        if found_nothing is True:
            self._logger.error("No available drift outputs found (from {} to {}).".format(start_time, end_time))
            raise ValueError("No available drift outputs from {} to {}".format(start_time, end_time))

        # produce figures
        figures = {}
        for c in contents:
            # sort by date to ensure correct order in graph
            ordered_content = OrderedDict(sorted(contents[c].items(), key=lambda t: t[0]))

            # environment information (alignment refined with extra spaces
            environment = "Workspace Name : {}           \n" \
                          "Model Name : {}\n" \
                          "Model Version : {}                            \n" \
                          "Service Name : {}  ". \
                format(self.workspace.name, self.model_name, self.model_version, c)

            figure = DataDriftDetector._generate_plot_figure(environment, ordered_content, with_details)

            figures[c] = figure

        return figures

    @staticmethod
    def _validate_client_dto(datadriftdto, logger):
        if datadriftdto is not None and datadriftdto.alert_configuration is not None and \
           datadriftdto.alert_configuration.email_addresses is not None \
           and len(datadriftdto.alert_configuration.email_addresses) > 0:
            # this means alert config is supposed to be set.
            if datadriftdto.alert_id is None:
                warnings.warn("Alert has not been setup for data-drift with model {} and version {}.\n".
                              format(datadriftdto.model_name, datadriftdto.model_version))
                if logger is not None:
                    logger.info("Alert has not been setup for data-drift with model {} and version {}.\n".
                                format(datadriftdto.model_name, datadriftdto.model_version))
