# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Package containing AzureML Training SDK Widgets.

Training SDK widgets can show status of your runs with corresponding properties, logs and metrics.

The following platforms are supported:
- Jupyter notebooks (both local and cloud): Full support with interactivity, async auto-updates and non-blocking cell
execution.
- Jupyter Lab: Everything supported as Jupyter notebooks except child-run pop-up support.
- Databricks (Experimental):  Synchronous Auto-updates but non-interactive currently.

There are four types of widgets currently supported:
- Single Run: Shows run properties, output logs, metrics.
- HyperDrive Run: Shows parent run properties, logs, child runs, primary metric chart and parallel coordinate chart
of hyperparameters.
- AutoML Run: Shows child runs, primary metric chart with option to select individual metrics.
- Pipeline Run: Shows running/non-running nodes of a pipeline along with graphical representation of nodes and edges.

Selected widget type is inferred implicitly from the run type. You do not need to set it explicitly.
"""

from .run_details import RunDetails

__all__ = ["RunDetails"]


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'azureml_widgets',
        'require': 'azureml_widgets/extension'
    }]
