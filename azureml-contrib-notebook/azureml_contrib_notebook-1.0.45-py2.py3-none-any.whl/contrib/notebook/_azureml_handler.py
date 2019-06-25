# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
from azureml.contrib.notebook._notebook_handler import NotebookExecutionHandler, _insert_suffix


class AzureMLNotebookHandler(NotebookExecutionHandler):
    """Papermill-based notebook execution handler.

    .. remarks::

         .. code-block:: python

             # Import dependencies
             from azureml.core import Workspace, Experiment, RunConfiguration
             from azureml.contrib.notebook import NotebookRunConfig, AzureMLNotebookHandler

             # Create new experiment
             workspace = Workspace.from_config()
             exp = Experiment(workspace, "azureml_notebook_experiment")

             # Customize run configuration to execute in user managed environment
             run_config_user_managed = RunConfiguration()
             run_config_user_managed.environment.python.user_managed_dependencies = True

             # Instante AzureML notebook handler with cell execution timeout
             handler = AzureMLNotebookHandler(timeout=600, progress_bar=False)

             # Create notebook run configuration
             cfg = NotebookRunConfig(source_directory="./notebooks",
                                     notebook="notebook-sample.ipynb",
                                     handler=handler,
                                     run_config=run_config_user_managed)

             # Submit experiment and wait for completion
             run = exp.submit(cfg)
             run.wait_for_completion(show_output=True)

    :param history: Enable metrics logs to run history. Enabled by default
    :type history: bool
    :param timeout: Cell execution timeout in seconds
    :type history: int
    :param kwargs: Dictionary of optional parameters. See `:attr:supported_options`
    :type path: dict
    """

    supported_options = ["progress_bar",
                         "log_output",
                         "kernel_name",
                         "cwd"]

    def __init__(self, history=True, timeout=None, **kwargs):
        """Construct PapermillExecutionHandler object."""
        super().__init__(os.path.join(os.path.dirname(__file__),
                                      "_handlers",
                                      "papermill_notebook_run_handler.py"))

        for key, val in kwargs.items():
            if key not in self.supported_options:
                raise Exception("Unsupported option: {}".format(key))

        kwargs["engine_name"] = "azureml_engine"

        self.papermill_args = kwargs
        self.execution_args = {"history": history, "timeout": timeout}
        self.dependencies.append("azureml-contrib-notebook[full]")

    def _argument_handling_contract(self, notebook, output_notebook, parameters=None):
        """Return list of arguments in handler accepted format.

        :param notebook: Input notebook
        :type path: str
        :param output_notebook: Output notebook
        :type path: str
        :param parameters: Dictionary of parameters
        :type path: dict

        :return: List of parameters.
        :rtype: list
        """
        if not output_notebook:
            output_notebook = _insert_suffix(notebook)

        return ["-i", notebook,
                "-o", output_notebook,
                "-e", json.dumps(self.execution_args),
                "-p", json.dumps(self.papermill_args),
                "-n", json.dumps(parameters)]
