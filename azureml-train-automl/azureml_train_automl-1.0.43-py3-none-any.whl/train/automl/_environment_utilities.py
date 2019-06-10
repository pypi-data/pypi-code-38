# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SDK utilities dealing with the runtime environment."""
from typing import Optional
import json
import logging
import re

from automl.client.core.common import utilities as common_utilities
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.core import RunConfiguration


def modify_run_configuration(settings: AutoMLBaseSettings,
                             run_config: RunConfiguration,
                             logger: logging.Logger) -> RunConfiguration:
    """Modify the run configuration with the correct version of AutoML and pip feed."""
    import azureml.core
    from azureml.core.conda_dependencies import CondaDependencies, DEFAULT_SDK_ORIGIN
    try:
        core_version = azureml.core.VERSION     # type: ignore
        automl_version = azureml.train.automl.VERSION   # type: ignore

        # ignore version if it is a dev package and warn user
        warn_cannot_run_local_pkg = False
        if core_version and ("dev" in core_version or core_version == "0.1.0.0"):
            core_version = None
            warn_cannot_run_local_pkg = True
        if automl_version and ("dev" in automl_version or automl_version == "0.1.0.0"):
            automl_version = None
            warn_cannot_run_local_pkg = True

        if warn_cannot_run_local_pkg:
            logger.warning("You are running a developer or editable installation of required packages. Your "
                           "changes will not be run on your remote compute. Latest versions of "
                           "azureml-core and azureml-train-automl will be used unless you have "
                           "specified an alternative index or version to use.")
    except Exception:
        logger.warning("Could not find the version info for azureml-core or azureml-train-automl")
        core_version = None
        automl_version = None

    sdk_origin_url = CondaDependencies.sdk_origin_url()

    dependencies = run_config.environment.python.conda_dependencies
    # if debug flag sets an sdk_url use it
    if settings.sdk_url is not None:
        dependencies.set_pip_option("--extra-index-url " + settings.sdk_url)

    # if debug_flag sets packages, use those in remote run
    if settings.sdk_packages is not None:
        for package in settings.sdk_packages:
            dependencies.add_pip_package(package)

    automl_regex = r"azureml\S*automl\S*"
    numpy_regex = r"numpy([\=\<\>\~0-9\.\s]+|\Z)"

    # ensure numpy is included
    if not re.findall(numpy_regex, " ".join(dependencies.conda_packages)):
        dependencies.add_conda_package("numpy")

    # if automl package not present add it and pin the version
    if not re.findall(automl_regex, " ".join(dependencies.pip_packages)):
        azureml_pkg = "azureml-defaults"
        automl_pkg = "azureml-train-automl"
        if core_version:
            azureml_pkg = azureml_pkg + "==" + core_version
            # only add core if version should be pinned
            dependencies.add_pip_package(azureml_pkg)
        if automl_version:
            automl_pkg = automl_pkg + "==" + automl_version

        # if we pin the version we should make sure the origin index is added
        if (automl_version or core_version) and sdk_origin_url != DEFAULT_SDK_ORIGIN:
            dependencies.set_pip_option("--extra-index-url " + sdk_origin_url)

        dependencies.add_pip_package(automl_pkg)
        dependencies.add_pip_package("azureml-explain-model")

    run_config.environment.python.conda_dependencies = dependencies
    return run_config


def log_user_sdk_dependencies(run, logger):
    """
    Log the AzureML packages currently installed on the local machine to the given run.

    :param run: The run to log user depenencies.
    :param logger: The logger to write user dependencies.
    :return:
    :type: None
    """
    dependencies = {'dependencies_versions': json.dumps(common_utilities.get_sdk_dependencies())}
    logger.info("[RunId:{}]SDK dependencies versions:{}."
                .format(run.id, dependencies['dependencies_versions']))
    run.add_properties(dependencies)
