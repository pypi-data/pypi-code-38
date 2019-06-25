# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import path
import logging
import copy

from azureml.core.workspace import WORKSPACE_DEFAULT_BLOB_STORE_NAME
from azureml.core.runconfig import DEFAULT_GPU_IMAGE, DEFAULT_CPU_IMAGE, MpiConfiguration, RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute_target import _BatchAITarget
from azureml.core.compute import AmlCompute, HDInsightCompute
from azureml.exceptions import ComputeTargetException, UserErrorException, TrainingException
from azureml._base_sdk_common.utils import convert_dict_to_list, merge_list, \
    list_remove_empty_items
from azureml.data.data_reference import DataReference
from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore


module_logger = logging.getLogger(__name__)
OPENMPI_CPU_IMAGE = "mcr.microsoft.com/azureml/base:openmpi3.1.2-ubuntu16.04"
OPENMPI_GPU_IMAGE = "mcr.microsoft.com/azureml/base-gpu:openmpi3.1.2-cuda9.0-cudnn7-ubuntu16.04"


def _estimator_submit_method(estimator, workspace, experiment_name, **kwargs):
    """
    Submit an experiment using a generic estimator.

    :param estimator: The estimator object.
    :type estimator: azureml.train.estimator.Estimator
    :param workspace: The workspace object.
    :type workspace: azureml.core.workspace.Workspace
    :param experiment_name: The name of the experiment.
    :type experiment_name: str
    :param kwargs: Additional parameters used to override estimator properties.
    :return: A ScriptRun object which can be queried for status, output path, model path, etc.
    :rtype: azureml.core.script_run.ScriptRun
    """
    override_params = False
    if kwargs:
        unexpected_params = set(kwargs.keys()) - set(["script_params", "inputs", "source_directory_data_store"])
        if unexpected_params:
            raise TrainingException("{} parameters cannot be overridden. Allowed paramemters are: script_params, "
                                    "inputs and source_directory_data_store.".format(list(unexpected_params)))
        override_params = True

    script_params = kwargs.get("script_params", None)
    inputs = kwargs.get("inputs", None)
    source_directory_data_store = kwargs.get("source_directory_data_store", None)
    if source_directory_data_store is None \
            and estimator._estimator_config.source_directory_data_store is None \
            and estimator._estimator_config.node_count > 1:
        # Try to use the workspace blob store as source directory store if we're multinode
        source_directory_data_store = workspace.datastores.get(WORKSPACE_DEFAULT_BLOB_STORE_NAME, None)
        if source_directory_data_store:
            override_params = True

    # TODO: Throw error if unexpected param?

    if override_params:
        estimator._original_config = copy.deepcopy(estimator._estimator_config)
        estimator._override_params(
            script_params=script_params,
            inputs=inputs,
            source_directory_data_store=source_directory_data_store)

    experiment_run = estimator._fit(workspace, experiment_name)

    if override_params:
        estimator._estimator_config = estimator._original_config

    return experiment_run


def _init_run_config(estimator, source_directory, compute_target, vm_size=None, vm_priority=None, entry_script=None,
                     script_params=None, node_count=1, process_count_per_node=1, distributed_backend=None,
                     distributed_training=None, use_gpu=None, use_docker=None, custom_docker_image=None,
                     image_registry_details=None, user_managed=False, conda_packages=None, pip_packages=None,
                     conda_dependencies_file_path=None, pip_requirements_file_path=None,
                     environment_variables=None, environment_definition=None, inputs=None,
                     source_directory_data_store=None, shm_size=None, max_run_duration_seconds=None):

    _validate_run_config_parameters(estimator, compute_target, vm_size, node_count, process_count_per_node,
                                    distributed_backend, distributed_training, use_gpu, use_docker,
                                    custom_docker_image, image_registry_details, user_managed, conda_packages,
                                    pip_packages, conda_dependencies_file_path, pip_requirements_file_path,
                                    environment_variables, environment_definition, source_directory_data_store,
                                    shm_size)

    if not source_directory:
        source_directory = "."

    arguments = _get_arguments(script_params)
    estimator_config = RunConfiguration(script=entry_script, arguments=arguments)

    # 1) data references...
    data_inputs = _get_data_inputs(script_params)
    data_references = _get_data_references(inputs, data_inputs, source_directory_data_store)
    estimator_config.data_references = data_references

    # 2) distributed training...
    estimator_config.node_count = node_count
    estimator_config.framework = "Python"

    if distributed_backend and distributed_backend.lower() == "mpi":
        estimator_config.communicator = "IntelMpi"
        estimator_config.mpi.process_count_per_node = process_count_per_node

    if distributed_training and isinstance(distributed_training, MpiConfiguration):
        estimator_config.communicator = "IntelMpi"
        estimator_config.mpi = distributed_training

    # 3) compute target...
    estimator_config.amlcompute.vm_size = vm_size
    estimator_config.amlcompute.vm_priority = vm_priority
    # For a single run, aml compute will have the same node count as batchai.
    estimator_config.amlcompute._cluster_max_node_count = node_count
    estimator_config.target = compute_target if compute_target else "amlcompute"

    # 4) environment...
    if environment_definition:
        estimator_config.environment = environment_definition
    else:
        conda_dependencies = _create_conda_dependencies(pip_packages, conda_packages, pip_requirements_file_path,
                                                        conda_dependencies_file_path, source_directory)
        _update_environment(environment=estimator_config.environment,
                            use_gpu=use_gpu,
                            use_docker=use_docker,
                            custom_docker_image=custom_docker_image,
                            image_registry_details=image_registry_details,
                            user_managed=user_managed,
                            conda_dependencies=conda_dependencies,
                            environment_variables=environment_variables,
                            shm_size=shm_size)

    # flip the docker automatically in case of AmlCompute
    if estimator_config.environment.docker.enabled is False and \
            compute_target and (isinstance(compute_target, _BatchAITarget) or isinstance(compute_target, AmlCompute)):
        module_logger.warning("This compute target type doesn't support non-Docker runs; "
                              "overriding run configuration enable Docker.")
        estimator_config.environment.docker.enabled = True

    # 5) others...
    estimator_config.max_run_duration_seconds = max_run_duration_seconds

    # Super constructor overrides source_directory_data_store to None, so overriding it back here.
    # Now that we've added the datastore to the reference list, we only want the name
    estimator_config.source_directory_data_store = source_directory_data_store.name \
        if source_directory_data_store else None

    return estimator_config


def _validate_run_config_parameters(estimator, compute_target, vm_size, node_count, process_count_per_node,
                                    distributed_backend, distributed_training, use_gpu, use_docker,
                                    custom_docker_image, image_registry_details, user_managed, conda_packages,
                                    pip_packages, conda_dependencies_file_path, pip_requirements_file_path,
                                    environment_variables, environment_definition, source_directory_data_store,
                                    shm_size):

    if process_count_per_node != 1:
        logging.warning("'process_count_per_node' parameter will be deprecated. Please use it as part of "
                        "'distributed_training' parameter.")
    if use_docker is False:
        logging.warning("'use_docker' parameter will be deprecated. Please use 'environment_definition' instead.")
        if custom_docker_image:
            raise TrainingException('If use_docker parameter is set to false, custom_docker_image '
                                    'parameter is not allowed')
    if environment_definition and (pip_packages or pip_requirements_file_path or conda_packages or
                                   conda_dependencies_file_path or custom_docker_image or
                                   image_registry_details or use_gpu or user_managed or shm_size or
                                   environment_variables):
        raise TrainingException('If environment_definition parameter is specified, the following parameters cannot '
                                'be specified: pip_packages, pip_requirements_file_path, conda_packages, '
                                'conda_dependencies_file_path, custom_docker_image, image_registry_details, '
                                'use_gpu, user_managed, shm_size, environment_variables')

    if conda_dependencies_file_path and (pip_packages or pip_requirements_file_path or conda_packages):
        raise TrainingException('If conda_dependencies_file_path parameter is specified, the following parameters '
                                'cannot be specified: pip_packages, pip_requirements_file_path, conda_packages')

    if source_directory_data_store:
        logging.warning("'source_directory_data_store' parameter will be deprecated. Please use 'inputs' "
                        "parameter to use Data references.")

    if node_count < 1:
        raise TrainingException("Node count should be at least 1.")
    if process_count_per_node < 1:
        raise TrainingException("Process count per node should be at least 1.")
    if distributed_backend:
        logging.warning("'distributed_backend' parameter will be deprecated. Please use "
                        "'distributed_training' instead.")
        if estimator is not None:
            supported_backends = estimator._get_supported_backends()
            if distributed_backend.lower() not in supported_backends:
                raise TrainingException("Unsupported distributed backend value: "
                                        "{}. Supported backend(s): {}.".format(distributed_backend,
                                                                               supported_backends))
            if all([supported_backends == ["mpi"], distributed_training, not isinstance(distributed_training,
                                                                                        MpiConfiguration)]):
                raise TrainingException("Unsupported distributed backend value: "
                                        "{}. Supported backend: mpi.".format(distributed_backend))

    if user_managed and (conda_packages or pip_packages or conda_dependencies_file_path or
                         pip_requirements_file_path):
        raise UserErrorException("If user_managed is True, then conda_packages, conda_dependencies_file_path, "
                                 "pip_packages or pip_requirements_file_path cannot be specified.")

    if not distributed_backend and not distributed_training and (node_count > 1 or process_count_per_node > 1):
        raise TrainingException("'distributed_backend' or 'distributed_training' must be specified when "
                                "node_count > 1 or process_count_per_node > 1.")

    if compute_target and isinstance(compute_target, HDInsightCompute):
        raise ComputeTargetException("Unsupported compute target type. Type={}".format(type(compute_target)))

    if vm_size is None and compute_target is None:
        raise TrainingException("Either compute target or VM size should be specified.")

    if node_count > 1 and compute_target and \
            not (isinstance(compute_target, _BatchAITarget) or
                 isinstance(compute_target, AmlCompute)):
        raise TrainingException("Compute target should be Batch AI for distributed training (node_count > 1).")


def _update_config_for_notebook_run(run_config, use_gpu, custom_docker_image):
    run_config.environment.environment_variables['NCCL_SOCKET_IFNAME'] = 'eth0'
    run_config.environment.environment_variables['NCCL_IB_DISABLE'] = '1'
    # If no custom image was specified and not user managed use openmpi images for notebook run
    if not _is_user_managed_environment(run_config.environment) and custom_docker_image is None:
        if use_gpu:
            run_config.environment.docker.base_image = OPENMPI_GPU_IMAGE
        else:
            run_config.environment.docker.base_image = OPENMPI_CPU_IMAGE


def _update_environment(environment, use_gpu, use_docker, custom_docker_image,
                        image_registry_details, user_managed, conda_dependencies,
                        environment_variables, shm_size):
    # dependencies...
    environment.python.user_managed_dependencies = user_managed
    environment.python.conda_dependencies = conda_dependencies
    environment.spark.precache_packages = False

    # docker...
    environment.docker.enabled = use_docker
    environment.docker.gpu_support = use_gpu

    if custom_docker_image:
        environment.docker.base_image = custom_docker_image
    else:
        environment.docker.base_image = DEFAULT_GPU_IMAGE if use_gpu else DEFAULT_CPU_IMAGE

    if image_registry_details:
        environment.docker.base_image_registry = image_registry_details

    # others...
    if shm_size:
        environment.docker.shm_size = shm_size
    if environment_variables:
        environment.environment_variables = environment_variables


def _create_conda_dependencies(pip_packages, conda_packages, pip_requirements_file_path, conda_dependencies_file_path,
                               source_directory):
    if pip_requirements_file_path:
        full_pip_requirements_path = path.normpath(
            path.join(source_directory, pip_requirements_file_path))

        if not path.isfile(full_pip_requirements_path):
            raise UserErrorException("{} path doesn't exist. "
                                     "The pip requirements file should be inside the project "
                                     "folder".format(full_pip_requirements_path))

        pip_packages = _merge_pip_packages_and_requirements(full_pip_requirements_path,
                                                            pip_packages)

    # No package merge should happen if conda_dependencies_file_path is provided
    conda_dependencies = CondaDependencies()
    if conda_dependencies_file_path:
        full_conda_dependencies_path = path.normpath(
            path.join(source_directory, conda_dependencies_file_path))

        if not path.isfile(full_conda_dependencies_path):
            raise UserErrorException("{} path doesn't exist. "
                                     "The conda dependencies file should be inside the project "
                                     "folder".format(full_conda_dependencies_path))

        conda_dependencies = CondaDependencies(full_conda_dependencies_path)
    else:
        if pip_packages:
            for pip_package in pip_packages:
                conda_dependencies.add_pip_package(pip_package)

        if conda_packages:
            for conda_dependency in conda_packages:
                conda_dependencies.add_conda_package(conda_dependency)

    return conda_dependencies


def _merge_pip_packages_and_requirements(pip_requirements_file_path=None, pip_packages=None):
    if not pip_requirements_file_path:
        return pip_packages

    requirements_list = []
    with open(pip_requirements_file_path) as in_file:
        requirements_list = in_file.read().splitlines()

    return CondaDependencies.merge_requirements(merge_list(requirements_list, pip_packages, True))


def _is_user_managed_environment(environment_definition):
    if environment_definition and environment_definition.python is not None:
        return environment_definition.python.user_managed_dependencies

    return False


def _is_notebook_run(entry_script):
    return entry_script and entry_script.lower().endswith(".ipynb")


def _get_data_references(inputs, data_inputs, source_directory_data_store):
    merged_inputs = merge_list(inputs, data_inputs, True)
    if source_directory_data_store:
        merged_inputs.append(source_directory_data_store)
    data_references = {}
    for item in merged_inputs:
        if isinstance(item, AbstractAzureStorageDatastore):
            item_ref = item._get_data_reference()
            data_references[item_ref.data_reference_name] = item_ref.to_config()
        elif isinstance(item, DataReference):
            data_references[item.data_reference_name] = item.to_config()
        else:
            raise UserErrorException("Type {0} is not supported for inputs.".format(type(item)))
    return data_references


def _get_data_inputs(script_params):
    from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
    data_inputs = []
    if script_params:
        for key in script_params:
            if isinstance(script_params[key], DataReference) \
                    or isinstance(script_params[key], AbstractAzureStorageDatastore):
                data_inputs.append(script_params[key])
    return data_inputs


def _get_arguments(script_params):
    from azureml.data.azure_storage_datastore import AbstractAzureStorageDatastore
    script_params_copy = copy.deepcopy(script_params)
    if script_params_copy:
        for key in script_params_copy:
            if isinstance(script_params_copy[key], DataReference):
                script_params_copy[key] = str(script_params_copy[key])
            elif isinstance(script_params_copy[key], AbstractAzureStorageDatastore):
                script_params_copy[key] = str(script_params_copy[key]._get_data_reference())
    return list_remove_empty_items(convert_dict_to_list(script_params_copy))
