# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod, ABCMeta


class _ModuleProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_module(self, module_def, content_path=None, fingerprint=None):
        pass

    @abstractmethod
    def download(self, module_id):
        pass

    @abstractmethod
    def find_module_by_fingerprint(self, fingerprint):
        pass


class _DataSourceProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def upload(self, datasource_def, fingerprint=None):
        pass

    @abstractmethod
    def download(self, datasource_id):
        pass

    @abstractmethod
    def find_datasource_by_fingerprint(self, fingerprint):
        pass


class _GraphProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def submit(self, graph, pipeline_parameters, continue_on_step_failure, experiment_name, parent_run_id=None):
        pass

    @abstractmethod
    def create_pipeline_run(self, graph, pipeline_parameters, continue_on_step_failure, experiment_name):
        pass

    @abstractmethod
    def create_graph_from_run(self, context, pipeline_run_id):
        pass


class _PipelineRunProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_status(self, pipeline_run_id):
        pass

    @abstractmethod
    def cancel(self, pipeline_run_id):
        pass

    @abstractmethod
    def get_node_statuses(self, pipeline_run_id):
        pass

    @abstractmethod
    def get_pipeline_experiment_name(self, pipeline_run_id):
        pass

    @abstractmethod
    def get_runs_by_pipeline_id(self, pipeline_id):
        pass


class _StepRunProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_status(self, pipeline_run_id, node_id):
        pass

    @abstractmethod
    def get_run_id(self, pipeline_run_id, node_id):
        pass

    @abstractmethod
    def get_job_log(self, pipeline_run_id, node_id):
        pass

    @abstractmethod
    def get_stdout_log(self, pipeline_run_id, node_id):
        pass

    @abstractmethod
    def get_stderr_log(self, pipeline_run_id, node_id):
        pass

    @abstractmethod
    def get_outputs(self, node_run, context, pipeline_run, node_id):
        pass

    @abstractmethod
    def get_output(self, node_run, context, pipeline_run, node_id, name):
        pass


class _PortDataReferenceProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_port_data_reference(self, output_run):
        pass

    @abstractmethod
    def download(self, datastore_name, path_on_datastore, local_path, overwrite, show_progress):
        pass


class _PublishedPipelineProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def submit(self, published_pipeline_id, experiment_name, parameter_assignment=None):
        pass

    @abstractmethod
    def get_published_pipeline(self, published_pipeline_id):
        pass

    @abstractmethod
    def create_from_pipeline_run(self, name, description, version, pipeline_run_id):
        pass

    @abstractmethod
    def create_from_graph(self, name, description, version, graph):
        pass

    @abstractmethod
    def get_all(self, active_only=True):
        pass

    @abstractmethod
    def set_status(self, pipeline_id, new_status):
        pass


class _DataTypeProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all_datatypes(self):
        pass

    @abstractmethod
    def create_datatype(self, id, name, description, is_directory=False, parent_datatype_ids=[]):
        pass

    @abstractmethod
    def ensure_default_datatypes(self):
        pass

    @abstractmethod
    def update_datatype(self, id, new_description=None, new_parent_datatype_ids=None):
        pass


class _ScheduleProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_schedule(self, name, published_pipeline_id, experiment_name, recurrence, description=None,
                        pipeline_parameters=None):
        pass

    @abstractmethod
    def get_schedule(self, schedule_id):
        pass

    @abstractmethod
    def get_schedules_by_pipeline_id(self, pipeline_id):
        pass

    @abstractmethod
    def update_schedule(self, schedule_id, name=None, description=None, recurrence=None, pipeline_parameters=None,
                        status=None):
        pass

    @abstractmethod
    def get_all_schedules(self, active_only=True):
        pass

    @abstractmethod
    def set_status(self, schedule_id, new_status):
        pass

    @abstractmethod
    def get_pipeline_runs_for_schedule(self, schedule_id):
        pass

    @abstractmethod
    def get_last_pipeline_run_for_schedule(self, schedule_id):
        pass

    @abstractmethod
    def get_schedule_provisioning_status(self, schedule_id):
        pass

    @abstractmethod
    def get_all_pipeline_endpoints(self, active_only=True):
        pass


class _PipelineEndpointProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_pipeline_endpoint(self, name, description, published_pipeline_id):
        pass

    @abstractmethod
    def get_pipeline_endpoint(self, endpoint_id=None, name=None):
        pass

    @abstractmethod
    def update_pipeline_endpoint(self, endpoint_id, version=None, name=None, pipeline_id=None, description=None,
                                 add_default=False):
        pass

    @abstractmethod
    def get_all_pipeline_endpoints(self, active_only=True):
        pass

    @abstractmethod
    def submit_pipeline_run_from_pipeline_endpoint(self, endpoint_id, pipeline_submission_info, parent_run_id=None):
        pass


class _AzureMLModuleProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_module(self, name, description):
        pass

    @abstractmethod
    def get_module(self, module_id=None, name=None):
        pass

    @abstractmethod
    def update_module(self, module_id, name=None, description=None,
                      status=None, default_version=None, versions=None):
        pass


class _AzureMLModuleVersionProvider(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_module_version(self, workspace, aml_module_id, version_num, module_def, content_path=None,
                              fingerprint=None):
        pass

    @abstractmethod
    def get_module_version(self, workspace, module_version_id):
        pass

    @abstractmethod
    def update_module_version(self, module_version_id, version, status=None, description=None):
        pass
