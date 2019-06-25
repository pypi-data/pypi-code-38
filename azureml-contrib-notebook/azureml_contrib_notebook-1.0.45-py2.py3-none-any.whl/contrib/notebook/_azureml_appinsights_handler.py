# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
from azureml.contrib.notebook._notebook_handler import NotebookExecutionHandler, _insert_suffix


class AzureMLApplicationInsightsNotebookHandler(NotebookExecutionHandler):
    """Papermill-based notebook execution handler.

    .. remarks::

         .. code-block:: python

             # Import dependencies
             from azureml.core import Workspace, Experiment, RunConfiguration
             from azureml.contrib.notebook import NotebookRunConfig, AzureMLApplicationInsightsNotebookHandler

             # Create new experiment
             workspace = Workspace.from_config()
             experiment_name = "azureml_notebook_experiment"
             exp = Experiment(workspace, experiment_name)

             # Customize run configuration to execute in user managed environment
             run_config_user_managed = RunConfiguration()
             run_config_user_managed.environment.python.user_managed_dependencies = True

             # Instante AzureML Application Insights notebook handler
             handler = AzureMLApplicationInsightsNotebookHandler(appinsights_key=_appinsights_key,
                                                                 tag="notebook-test",
                                                                 payload={"experiment_name": experiment_name},
                                                                 timeout=600)

             # Create notebook run configuration
             cfg = NotebookRunConfig(source_directory="./notebooks",
                                     notebook="notebook-sample.ipynb",
                                     handler=handler,
                                     parameters={"arg2": "Universe"},
                                     run_config=run_config_user_managed)

             # Submit experiment and wait for completion
             run = exp.submit(cfg)
             run.wait_for_completion(show_output=True)

        Handler logs notebook execution status as an event named as `tag` to ApplicationInsights.
        CustomDimensions payload contains

            - notebook metadata from papermill execution
            - user specified payload
            - status - one of failed, completed or timeout

        In a case of a failure CustomDimensions extended with the following properties

            - cell_index - execution count of a failed cell
            - source - source code of the cell
            - error_type - exception type
            - error_message - exception message
            - traceback - stack trace

    :param appinsights_key: ApplicationInsights key
    :type appinsights_key: str
    :param tag: Event name
    :type tag: str
    :param payload: Event payload
    :type payload: dict
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

    def __init__(self, appinsights_key, tag, payload=None, history=True, timeout=None, **kwargs):
        """Construct PapermillExecutionHandler object."""
        super().__init__(os.path.join(os.path.dirname(__file__),
                                      "_handlers",
                                      "papermill_notebook_run_handler.py"))

        for key, val in kwargs.items():
            if key not in self.supported_options:
                raise Exception("Unsupported option: {}".format(key))

        kwargs["engine_name"] = "azureml_appinsights_engine"

        if not appinsights_key or not tag:
            raise Exception('appinsights_key and tag parameters are required but at least one of them is not set')

        self.papermill_args = kwargs
        self.execution_args = {
            "history": history,
            "timeout": timeout,
            "appinsights_key": appinsights_key,
            "tag": tag,
            "payload": payload}
        self.dependencies.append("azureml-contrib-notebook[full]")
        self.dependencies.append("applicationinsights")

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
