# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Include notebook extension to capture notebooks on runs."""
from azureml.contrib.notebook.extension import Extension, load_ipython_extension
from azureml.contrib.notebook._notebook_handler import NotebookExecutionHandler
from azureml.contrib.notebook._notebook_run_config import NotebookRunConfig
from azureml.contrib.notebook._papermill_deprecated_handler import PapermillExecutionHandler
from azureml.contrib.notebook._azureml_handler import AzureMLNotebookHandler
from azureml.contrib.notebook._azureml_appinsights_handler import AzureMLApplicationInsightsNotebookHandler

__all__ = [
    "Extension",
    "load_ipython_extension",
    "NotebookExecutionHandler",
    "NotebookRunConfig",
    "PapermillExecutionHandler",
    "AzureMLNotebookHandler",
    "AzureMLApplicationInsightsNotebookHandler"
]


def _jupyter_server_extension_paths():
    return [{
        "module": "notebook"
    }]


# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="_scripts",
        dest="azureml",
        require="azureml/kernel")]
