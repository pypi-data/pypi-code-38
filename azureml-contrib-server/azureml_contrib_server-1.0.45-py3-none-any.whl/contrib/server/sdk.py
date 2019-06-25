# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# TODO
# - need error for invalid/expired tokens
"""Utility methods that glues together the AML SDK and the REST API."""

import functools
import io
import logging
import os
import shlex
import sys
import time
import threading

from azureml.core import Workspace, RunConfiguration, Experiment, ScriptRun, ScriptRunConfig
from azureml.core.authentication import ArmTokenAuthentication
from azureml.core._serialization_utils import _serialize_to_dict
from azureml.core.model import Model
from azureml.core.image import Image
from azureml.core.image.container import ContainerImageConfig
from azureml.core.webservice import Webservice, AciWebservice, AksWebservice
from azureml.exceptions import AzureMLException, AuthenticationException
from azureml.core.compute import ComputeTarget

logger = logging.getLogger(__name__)


def dump_args(function):
    """Print the arguments passed to a function before calling it."""
    argnames = function.__code__.co_varnames[:function.__code__.co_argcount]
    fname = function.__name__

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if logger.isEnabledFor(logging.DEBUG):
            entries = list(zip(argnames, args[:len(argnames)])) \
                + [('args', list(args[len(argnames):]))] \
                + [('kwargs', kwargs)]
            message = ''.join([fname, ' (', ', '.join(('%s=%r' % entry for entry in entries)), ')'])
            logger.debug(message)
        return function(*args, **kwargs)
    return wrapper


def time_method(function):
    """Print the duration of calls to the decorated function."""
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        logger.debug('Function time(ms): {}'.format((end - start) * 1000.0))
        return result
    return wrapper


# Workspaces

@dump_args
@time_method
def create_workspace(token, subscription_id, resource_group, name, location):
    """Create a workspace and return it."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    ws = Workspace.create(
        name=name,
        auth=auth,
        subscription_id=subscription_id,
        resource_group=resource_group,
        location=location
    )
    return ws._get_create_status_dict()


@dump_args
@time_method
def delete_workspace(token, subscription_id, resource_group, name):
    """Delete the specified workspace."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    ws = Workspace(
        auth=auth,
        subscription_id=subscription_id,
        resource_group=resource_group,
        workspace_name=name
    )
    return ws.delete()


@dump_args
@time_method
def list_workspaces(token, subscription_id, resource_group=None):
    """Return a list the workspaces under the given subscription."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    workspaces_dict = Workspace.list(
        subscription_id=subscription_id,
        auth=auth,
        resource_group=resource_group
    )
    result = dict()
    for name in workspaces_dict:
        result[name] = list(ws._to_dict() for ws in workspaces_dict[name])
    return result


@dump_args
@time_method
def get_workspace_by_name(token, subscription_id, resource_group, name):
    """Return the workspace with the given name."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    workspace = Workspace.get(
        auth=auth,
        subscription_id=subscription_id,
        resource_group=resource_group,
        name=name
    )
    return workspace.get_details()


# Projects

@dump_args
@time_method
def get_experiment_info(token, project_path):
    """Return info of the project located at the given path."""
    info = None
    auth = ArmTokenAuthentication(arm_access_token=token)
    try:
        experiment = Experiment.from_directory(path=project_path, auth=auth)
    except AuthenticationException as e:
        raise e
    except Exception:
        info = None
    else:
        info = {
            "name": experiment.name,
            "path": project_path
        }
    return info


@dump_args
@time_method
def attach_project(token, subscription_id, resource_group, workspace_name, project_path, experiment_name):
    """Attach a local folder to a history and return the project details."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    workspace = Workspace.get(
        auth=auth,
        subscription_id=subscription_id,
        resource_group=resource_group,
        name=workspace_name
    )
    workspace._initialize_folder(
        experiment_name=experiment_name,
        directory=project_path
    )


@dump_args
@time_method
def detach_project(token, project_path):
    """Detach the project located at the given path from its history."""
    # not reimplemented in the SDK
    pass


# Run Configurations


@dump_args
@time_method
def get_run_configuration(token, project_path, run_configuration_name):
    """Return the run configuration in the given project with the given name."""
    conf = RunConfiguration.load(path=project_path, name=run_configuration_name)
    return _serialize_to_dict(conf)


@dump_args
@time_method
def create_run_configuration(token, project_path, run_configuration_name, target, prepare):
    """Create a run configuration and return it."""
    conf = RunConfiguration()
    conf.target = target
    conf.auto_prepare_environment = prepare
    conf.save(path=project_path, name=run_configuration_name)
    return _serialize_to_dict(conf)


@dump_args
@time_method
def delete_run_configuration(token, project_path, run_configuration_name):
    """Delete the specified run configuration from a project."""
    RunConfiguration.delete(path=project_path, name=run_configuration_name)


# Runs

@dump_args
@time_method
def submit_run(token, project_path, run_config, script=None, arguments=None, python_path=None, target=None):
    """Submit an experiment run and return its run ID."""
    config = RunConfiguration.load(path=project_path, name=run_config)
    if isinstance(arguments, str):
        arguments = shlex.split(arguments, posix='win' not in sys.platform)
    if not config:
        raise AzureMLException('Run configuration not found: {}'.format(run_config))
    if python_path:
        config.environment.python.interpreter_path = python_path
    if target:
        config.target = target
    script_run_config = ScriptRunConfig(source_directory=project_path,
                                        script=script,
                                        run_config=config,
                                        arguments=arguments)
    auth = ArmTokenAuthentication(arm_access_token=token)
    experiment = Experiment.from_directory(path=project_path, auth=auth)
    run = experiment.submit(script_run_config)
    return {"runId": run.id}


@dump_args
@time_method
def stream_run_output(token, project_path, run_config, run_id):
    """Return a stream of the run's output."""
    auth = ArmTokenAuthentication(arm_access_token=token)
    experiment = Experiment.from_directory(path=project_path, auth=auth)
    run = ScriptRun(experiment=experiment, run_id=run_id)
    sio = io.StringIO()

    def read_logs():
        try:
            run._stream_run_output(file_handle=sio)
        finally:
            sio.flush()

    fetch_logs_thread = threading.Thread(target=read_logs, daemon=True)
    fetch_logs_thread.start()

    def generator():
        n_read = 0
        while True:
            eof = not fetch_logs_thread.is_alive()
            text = sio.getvalue()
            text_len = len(text)
            if text_len > n_read:
                delta = text[n_read:text_len]
                n_read = text_len
                yield delta
            if eof:
                break
            time.sleep(0.250)
        sio.close()

    return generator()


# Models

@dump_args
@time_method
def register_model(token, subscription_id, resource_group, workspace_name, model_path, model_name,
                   tags=None, description=None):
    """Register a model to a workspace from a model file and return the model object."""
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    model = Model.register(workspace=ws, model_path=model_path, model_name=model_name,
                           tags=tags, description=description)
    return model.serialize()


@dump_args
@time_method
def download_model(token, subscription_id, resource_group, workspace_name, model_id, target_dir):
    """Download a registered model in a workspace."""
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    model = Model(workspace=ws, id=model_id)
    model.download(target_dir=target_dir)


# Images

@dump_args
@time_method
def create_image(token, subscription_id, resource_group, workspace_name, name, runtime, directory, execution_script,
                 models=None, docker_file=None, conda_file=None, dependencies=None, schema_file=None,
                 enable_gpu=False, tags=None, description=None, is_async=False, cuda_version=None):
    """Register models from files, create an image from the models, and return the image."""
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    models = models or []
    with cd(directory):
        image_config = ContainerImageConfig(
            execution_script=execution_script,
            runtime=runtime,
            conda_file=conda_file,
            docker_file=docker_file,
            schema_file=schema_file,
            dependencies=dependencies,
            enable_gpu=enable_gpu,
            cuda_version=cuda_version,
            tags=tags,
            description=description
        )
        image = Image.create(workspace=ws, name=name, models=models, image_config=image_config)
        if not is_async:
            image.wait_for_creation(True)
        result = image.serialize()
        result.update({'operationLocation': image._operation_endpoint})
        return result


# Web Services

@dump_args
@time_method
def create_service_from_image(token, subscription_id, resource_group, workspace_name, name, image_id,
                              deployment_config_params=None, deployment_target_name=None, deployment_type=None,
                              is_async=False):
    """Register models, creates an image from them, and deploys the image."""
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    deployment_config, deployment_target = _get_deployment_config_and_target(
        ws, deployment_config_params, deployment_target_name, deployment_type
    )
    image = next((i for i in Image.list(ws) if i.id == image_id), None)
    if not image:
        raise AzureMLException("Image not found: {}".format(image_id))
    webservice = Webservice.deploy_from_image(
        workspace=ws, name=name, image=image, deployment_config=deployment_config,
        deployment_target=deployment_target
    )
    if not is_async:
        webservice.wait_for_deployment()
    result = webservice.serialize()
    result.update({'operationLocation': webservice._operation_endpoint})
    return result


@dump_args
@time_method
def create_service_from_registered_models(token, subscription_id, resource_group, workspace_name, name,
                                          image_config_params, model_ids=None, deployment_config_params=None,
                                          deployment_target_name=None, deployment_type=None, is_async=False):
    """Register models, creates an image from them, and deploys the image."""
    # TODO: maybe optionally include models by name or tags as well?
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    model_ids = model_ids or []
    models = list(m for m in Model.list(ws) if m.id in model_ids)
    deployment_config, deployment_target = _get_deployment_config_and_target(
        ws, deployment_config_params, deployment_target_name, deployment_type
    )
    with cd(image_config_params['directory']):
        image_config = _get_image_config(image_config_params)
        webservice = Webservice.deploy_from_model(
            workspace=ws,
            name=name,
            models=models,
            image_config=image_config,
            deployment_config=deployment_config,
            deployment_target=deployment_target
        )
        if not is_async:
            webservice.wait_for_deployment()
        result = webservice.serialize()
        result.update({'operationLocation': webservice._operation_endpoint})
        return result


@dump_args
@time_method
def create_service_from_models(
        token, subscription_id, resource_group, workspace_name, name, image_config_params,
        model_paths=None, deployment_config_params=None, deployment_target_name=None, deployment_type=None,
        is_async=False
):
    """Register models, creates an image from them, and deploys the image."""
    ws = _get_workspace(token, subscription_id, resource_group, workspace_name)
    model_paths = model_paths or []

    deployment_config, deployment_target = _get_deployment_config_and_target(
        ws, deployment_config_params, deployment_target_name, deployment_type
    )
    with cd(image_config_params['directory']):
        image_config = _get_image_config(image_config_params)
        webservice = Webservice.deploy(
            workspace=ws, name=name, model_paths=model_paths, image_config=image_config,
            deployment_config=deployment_config, deployment_target=deployment_target
        )
        if not is_async:
            webservice.wait_for_deployment()
        result = webservice.serialize()
        result.update({'operationLocation': webservice._operation_endpoint})
        return result


def _get_workspace(token, subscription_id, resource_group, workspace_name):
    auth = ArmTokenAuthentication(arm_access_token=token)
    ws = Workspace(subscription_id=subscription_id, resource_group=resource_group,
                   workspace_name=workspace_name, auth=auth)
    return ws


def _get_image_config(image_config_params):
    """All files in the config should be in the current working directory."""
    image_config = ContainerImageConfig(
        execution_script=image_config_params['executionScript'],
        runtime=image_config_params['runtime'],
        conda_file=image_config_params.get('condaFile'),
        docker_file=image_config_params.get('dockerFile'),
        schema_file=image_config_params.get('schemaFile'),
        dependencies=image_config_params.get('dependencies'),
        enable_gpu=image_config_params.get('enableGpu'),
        cuda_version=image_config_params.get('cudaVersion'),
        tags=image_config_params.get('tags'),
        description=image_config_params.get('description')
    )
    return image_config


def _get_deployment_config_and_target(workspace, deployment_config_params=None, deployment_target_name=None,
                                      deployment_type=None):
    deployment_config = None
    if deployment_config_params:
        if deployment_type == 'ACI':
            deployment_config = AciWebservice.deploy_configuration(
                cpu_cores=deployment_config_params.get('cpu_cores'),
                memory_gb=deployment_config_params.get('memory_gb'),
                tags=deployment_config_params.get('tags'),
                properties=deployment_config_params.get('properties'),
                description=deployment_config_params.get('description'),
                location=deployment_config_params.get('location'),
                auth_enabled=deployment_config_params.get('auth_enabled')
            )
        elif deployment_type == 'AKS':
            deployment_config = AksWebservice.deploy_configuration(
                autoscale_enabled=deployment_config_params.get('autoscale_enabled'),
                autoscale_min_replicas=deployment_config_params.get('autoscale_min_replicas'),
                autoscale_max_replicas=deployment_config_params.get('autoscale_max_replicas'),
                autoscale_refresh_seconds=deployment_config_params.get('autoscale_refresh_seconds'),
                autoscale_target_utilization=deployment_config_params.get('autoscale_target_utilization'),
                collect_model_data=deployment_config_params.get('collect_model_data'),
                auth_enabled=deployment_config_params.get('auth_enabled'),
                cpu_cores=deployment_config_params.get('cpu_cores'),
                memory_gb=deployment_config_params.get('memory_gb'),
                enable_app_insights=deployment_config_params.get('enable_app_insights'),
                scoring_timeout_ms=deployment_config_params.get('scoring_timeout_ms'),
                replica_max_concurrent_requests=deployment_config_params.get('replica_max_concurrent_requests'),
                num_replicas=deployment_config_params.get('num_replicas'),
                primary_key=deployment_config_params.get('primary_key'),
                secondary_key=deployment_config_params.get('secondary_key'),
                tags=deployment_config_params.get('tags'),
                properties=deployment_config_params.get('properties'),
                description=deployment_config_params.get('description')
            )
    # lookup target by name
    deployment_target = None
    if deployment_target_name:
        deployment_target = next(
            (target for target in ComputeTarget.list(workspace) if target.name == deployment_target_name),
            None
        )

    return deployment_config, deployment_target


class cd:
    """Context manager that changes the current working directory and restores it on exit."""

    def __init__(self, new_cwd):
        """Constructor.

        :param new_cwd: Path of directory to change into.
        :type new_cwd: str
        """
        self.new_cwd = os.path.expanduser(new_cwd)

    def __enter__(self):
        """Save current working directory and changes to `new_cwd`."""
        self.saved_cwd = os.getcwd()
        os.chdir(self.new_cwd)

    def __exit__(self, exc_type, exc_value, traceback):
        """Restore original current working directory."""
        os.chdir(self.saved_cwd)
