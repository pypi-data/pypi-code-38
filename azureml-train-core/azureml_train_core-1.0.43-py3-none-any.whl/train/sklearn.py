# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The Scikit-learn estimator class."""

import logging

from azureml.core._experiment_method import experiment_method

from .estimator import _FrameworkBaseEstimator, _estimator_submit_method


class SKLearn(_FrameworkBaseEstimator):
    """An SKLearn Estimator is used to train a Scikit-learn specific experiment.

    This estimator only supports single-node CPU training.

    Supported versions: 0.20.3

    .. remarks::

            While submitting a training job, Azure ML runs your script in a conda environment within
            a Docker container. The SKLearn containers have the following dependencies installed.

            | Dependencies | Scikit-learn 0.20.3 |
            | ---------------------- | ----------------- |
            | Python                 | 3.6.2             |
            | azureml-defaults       | Latest            |
            | IntelMpi               | 2018.3.222        |
            | scikit-learn           | 0.20.3            |
            | numpy                  | 1.16.2            |
            | miniconda              | 4.5.11            |
            | scipy                  | 1.2.1             |


            The Docker images extend Ubuntu 16.04.

            If you need to install additional dependencies, you can either use pip_packages/conda_packages
            parameters or provide your pip requirements.txt/conda environment.yml file. Alternatively,
            you can build your own image, and pass the custom_docker_image parameter to the estimator
            constructor.

    :param source_directory: A local directory containing experiment configuration files.
    :type source_directory: str
    :param compute_target: The ComputeTarget where training will happen. This can either be an object or the
        string "local".
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
    :param vm_size: The VM size of the compute target that will be created for the training.

        Supported values: Any Azure VM size.

        The list of available VM sizes are listed here:
        https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
    :type vm_size: str
    :param vm_priority: The VM priority of the compute target that will be created for the training. If not
        specified, it will be defaulted to 'dedicated'.

        Supported values: 'dedicated' and 'lowpriority'.

        This takes effect only when the vm_size param is specified in the input.
    :type vm_priority: str
    :param entry_script: A string representing the relative path to the file used to start training.
    :type entry_script: str
    :param script_params: A dict containing parameters to the entry_script.
    :type script_params: dict
    :param custom_docker_image: The name of the docker image from which the image to use for training
        will be built. If not set, a default CPU based image will be used as the base image.
    :type custom_docker_image: str
    :param image_registry_details: The details of the docker image registry.
    :type image_registry_details: azureml.core.container_registry.ContainerRegistry
    :param user_managed: True means that AzureML reuses an existing python environment, False means
        that AzureML will create a python environment based on the Conda dependencies specification.
    :type user_managed: bool
    :param conda_packages: List of strings representing conda packages to be added to the Python environment
        for the experiment.
    :type conda_packages: list
    :param pip_packages: List of strings representing pip packages to be added to the Python environment
        for the experiment.
    :type pip_packages: list
    :param conda_dependencies_file_path: A string representing the relative path to the conda dependencies yaml file.
        This can be provided in combination with the conda_packages parameter.
    :type conda_dependencies_file_path: str
    :param pip_requirements_file_path: A string representing the relative path to the pip requirements file.
        This can be provided in combination with the pip_packages parameter.
    :type pip_requirements_file_path: str
    :param environment_variables: A dictionary of environment variables names and values.
        These environment variables are set on the process where user script is being executed.
    :type environment_variables: dict
    :param environment_definition: The EnvironmentDefinition for the experiment. It includes
        PythonSection and DockerSection and environment variables. Any environment option not directly
        exposed through other parameters to the Estimator construction can be set using environment_definition
        parameter. If this parameter is specified, it will take precedence over other environment related
        parameters like use_gpu, custom_docker_image, conda_packages or pip_packages and errors will be
        reported on these invalid combinations.
    :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
    :param inputs: Data references as input.
    :type inputs: list
    :param shm_size: The size of the Docker container's shared memory block. Please refer to
        https://docs.docker.com/engine/reference/run/ for more information. If not set, default is 1G.
    :type shm_size: str
    :param max_run_duration_seconds: Maximum allowed time for the run. The system will attempt to automatically
        cancel the run, if it took longer than this value.
    :type max_run_duration_seconds: int
    :param framework_version: Scikit-learn version to be used for executing training code.
        SKLearn.get_supported_versions() returns a list of the versions supported by the current SDK.
    :type framework_version: str
    """

    FRAMEWORK_NAME = "SKLearn"
    DEFAULT_VERSION = '0.20.3'

    @experiment_method(submit_function=_estimator_submit_method)
    def __init__(self,
                 source_directory,
                 *,
                 compute_target=None,
                 vm_size=None,
                 vm_priority=None,
                 entry_script=None,
                 script_params=None,
                 use_docker=True,
                 custom_docker_image=None,
                 image_registry_details=None,
                 user_managed=False,
                 conda_packages=None,
                 pip_packages=None,
                 conda_dependencies_file_path=None,
                 pip_requirements_file_path=None,
                 environment_variables=None,
                 environment_definition=None,
                 inputs=None,
                 shm_size=None,
                 max_run_duration_seconds=None,
                 framework_version=None,
                 _enable_optimized_mode=False):
        """Initialize a Scikit-learn estimator.

        :param source_directory: A local directory containing experiment configuration files.
        :type source_directory: str
        :param compute_target: The ComputeTarget where training will happen. This can either be an object or the
            string "local".
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget or str
        :param vm_size: The VM size of the compute target that will be created for the training.

            Supported values: Any Azure VM size.

            The list of available VM sizes are listed here:
            https://docs.microsoft.com/en-us/azure/cloud-services/cloud-services-sizes-specs
        :type vm_size: str
        :param vm_priority: The VM priority of the compute target that will be created for the training. If not
            specified, it will be defaulted to 'dedicated'.

            Supported values: 'dedicated' and 'lowpriority'.

            This takes effect only when the vm_size param is specified in the input.
        :type vm_priority: str
        :param entry_script: A string representing the relative path to the file used to start training.
        :type entry_script: str
        :param script_params: A dict containing parameters to the entry_script.
        :type script_params: dict
        :param use_docker: A bool value indicating if the environment to run the experiment should be docker-based.
        :type use_docker: bool
        :param custom_docker_image: The name of the docker image from which the image to use for training
            will be built. If not set, a default CPU based image will be used as the base image.
        :type custom_docker_image: str
        :param image_registry_details: The details of the docker image registry.
        :type image_registry_details: azureml.core.container_registry.ContainerRegistry
        :param user_managed: True means that AzureML reuses an existing python environment, False means
            that AzureML will create a python environment based on the Conda dependencies specification.
        :type user_managed: bool
        :param conda_packages: List of strings representing conda packages to be added to the Python environment
            for the experiment.
        :type conda_packages: list
        :param pip_packages: List of strings representing pip packages to be added to the Python environment
            for the experiment.
        :type pip_packages: list
        :param conda_dependencies_file_path: A string representing the relative path to the conda dependencies
            yaml file.
            This can be provided in combination with the conda_packages parameter.
        :type conda_dependencies_file_path: str
        :param pip_requirements_file_path: A string representing the relative path to the pip requirements file.
            This can be provided in combination with the pip_packages parameter.
        :type pip_requirements_file_path: str
        :param environment_variables: A dictionary of environment variables names and values.
            These environment variables are set on the process where user script is being executed.
        :type environment_variables: dict
        :param environment_definition: The EnvironmentDefinition for the experiment. It includes
            PythonSection and DockerSection and environment variables. Any environment option not directly
            exposed through other parameters to the Estimator construction can be set using environment_definition
            parameter. If this parameter is specified, it will take precedence over other environment related
            parameters like use_gpu, custom_docker_image, conda_packages or pip_packages and errors will be
            reported on these invalid combinations.
        :type environment_definition: azureml.core.runconfig.EnvironmentDefinition
        :param inputs: Data references as input.
        :type inputs: list
        :param shm_size: The size of the Docker container's shared memory block. Please refer to
            https://docs.docker.com/engine/reference/run/ for more information. If not set, default is 1G.
        :type shm_size: str
        :param max_run_duration_seconds: Maximum allowed time for the run. The system will attempt to automatically
            cancel the run, if it took longer than this value.
        :type max_run_duration_seconds: int
        :param framework_version: Scikit-learn version to be used for executing training code.
            SKLearn.get_supported_versions() returns a list of the versions supported by the current SDK.
        :type framework_version: str
        :type framework_version: str
        :param _enable_optimized_mode: Enable incremental environment build with pre-built framework images for faster
            environment preparation. A pre-built framework image is built on top of Azure ML default CPU/GPU base
            images with framework dependencies pre-installed.
        :type _enable_optimized_mode: bool
        """
        if environment_definition is not None and environment_definition.docker.gpu_support:
            logging.warning("The SKLearn estimator does not have GPU support. The experiment will be run on "
                            "a CPU instead.")
            environment_definition.docker.gpu_support = False

        super().__init__(source_directory, compute_target=compute_target, vm_size=vm_size,
                         vm_priority=vm_priority, entry_script=entry_script,
                         script_params=script_params, node_count=1,
                         process_count_per_node=1,
                         distributed_backend=None, distributed_training=None,
                         use_gpu=False, use_docker=use_docker, custom_docker_image=custom_docker_image,
                         image_registry_details=image_registry_details,
                         user_managed=user_managed, conda_packages=conda_packages,
                         pip_packages=pip_packages,
                         conda_dependencies_file_path=conda_dependencies_file_path,
                         pip_requirements_file_path=pip_requirements_file_path,
                         environment_variables=environment_variables,
                         environment_definition=environment_definition, inputs=inputs,
                         source_directory_data_store=None,
                         shm_size=shm_size, max_run_duration_seconds=max_run_duration_seconds,
                         framework_name=self.FRAMEWORK_NAME,
                         framework_version=framework_version,
                         _enable_optimized_mode=_enable_optimized_mode)
