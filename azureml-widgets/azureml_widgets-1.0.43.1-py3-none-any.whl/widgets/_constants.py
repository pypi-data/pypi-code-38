# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants used in the widgets."""

WIDGET_MODULE_NAME = "azureml_widgets"

# Sleep time (in seconds) between widget refresh
WIDGET_REFRESH_SLEEP_TIME = 5
MULTIRUN_WIDGET_REFRESH_SLEEP_TIME = 15
AUTOML_WIDGET_REFRESH_SLEEP_TIME = 30
WIDGET_REFRESH_SLEEP_TIME_DATABRICKS = 120

WEB_WORKBENCH_PARENT_RUN_ENDPOINT = ("https://mlworkspace.azure.ai/portal/subscriptions/{}/resource"
                                     "Groups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}"
                                     "/experiment/{}/run/{}")
