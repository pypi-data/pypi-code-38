# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class for handling notebook run configuration."""
import shutil
import os
from azureml.core.script_run_config import ScriptRunConfig
from azureml.contrib.notebook._azureml_handler import AzureMLNotebookHandler
from azureml.core.conda_dependencies import CondaDependencies


def _copy_handler(handler, destination):
    handler_filename = os.path.basename(handler)
    destination_path = os.path.join(destination, handler_filename)

    if os.path.normpath(handler) == os.path.normpath(destination_path):
        return

    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copyfile(handler, destination_path)


class NotebookRunConfig(ScriptRunConfig):
    """A class for setting up configurations for notebooks runs.

    .. remarks::

         .. code-block:: python

             # Import dependencies
             from azureml.core import Workspace, Experiment, RunConfiguration
             from azureml.contrib.notebook import NotebookRunConfig

             # Create new experiment
             workspace = Workspace.from_config()
             exp = Experiment(workspace, "simple_notebook_experiment")

             # Customize run configuration to execute in user managed environment
             run_config_user_managed = RunConfiguration()
             run_config_user_managed.environment.python.user_managed_dependencies = True

             # Create notebook run configuration and set parameters values
             cfg = NotebookRunConfig(source_directory="./notebooks",
                                     notebook="notebook-sample.ipynb",
                                     parameters={"arg1": "Machine Learning"},
                                     run_config=run_config_user_managed)

             # Submit experiment and wait for completion
             run = exp.submit(cfg)
             run.wait_for_completion(show_output=True)

    :param source_directory: Source directory
    :type source_directory: str
    :param notebook: Notebook file name
    :type notebook: str
    :param output_notebook: Output notebook file name
    :type output_notebook: str
    :param parameters: Dictionary of notebook parameters
    :type parameters: dict
    :param handler: Instance of the NotebookExecutionHandler
    :type handler: NotebookExecutionHandler
    :param run_config:
    :type run_config: azureml.core.runconfig.RunConfiguration
    :param _telemetry_values:
    :type _telemetry_values: dict
    """

    def __init__(self,
                 source_directory,
                 notebook,
                 output_notebook=None,
                 parameters=None,
                 handler=None,
                 run_config=None,
                 _telemetry_values=None):
        """Class NotebookRunConfig constructor.

        :param source_directory: Source directory
        :type source_directory: str
        :param notebook: Notebook file name
        :type notebook: str
        :param output_notebook: Output notebook file name
        :type output_notebook: str
        :param parameters: Dictionary of notebook parameters
        :type parameters: dict
        :param handler: Instance of the NotebookExecutionHandler
        :type handler: NotebookExecutionHandler
        :param run_config:
        :type run_config: azureml.core.runconfig.RunConfiguration
        :param _telemetry_values:
        :type _telemetry_values: dict
        """
        super().__init__(source_directory, run_config=run_config, _telemetry_values=_telemetry_values)

        if handler is None:
            handler = AzureMLNotebookHandler()

        _copy_handler(handler._script_source, source_directory)

        self.arguments = handler._argument_handling_contract(notebook, output_notebook, parameters)

        self.script = handler.script

        runcfg_packages = [CondaDependencies._get_package_name(pkg)
                           for pkg in list(self.run_config.environment.python.conda_dependencies.pip_packages)]

        for dep in handler.dependencies:
            # Do not overwrite run config dependencies
            if CondaDependencies._get_package_name(dep) not in runcfg_packages:
                self.run_config.environment.python.conda_dependencies.add_pip_package(dep)
