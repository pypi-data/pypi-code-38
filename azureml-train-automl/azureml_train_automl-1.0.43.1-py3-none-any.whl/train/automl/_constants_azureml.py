# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used throughout AutoML that will not be migrating packages."""
from automl.client.core.common.exceptions import ErrorTypes
MODEL_PATH = "outputs/model.pkl"


class Properties:
    """Problem Info constants."""

    PROBLEM_INFO = 'ProblemInfoJsonString'
    AML_SETTINGS = 'AMLSettingsJsonString'


class RunState:
    """Names for the states a run can be in."""

    START_RUN = 'running'
    FAIL_RUN = 'failed'
    CANCEL_RUN = 'canceled'
    COMPLETE_RUN = 'completed'


class API:
    """Names for the AzureML API operations that can be performed."""

    CreateExperiment = 'Create Experiment'
    CreateParentRun = 'Create Parent Run'
    GetNextPipeline = 'Get Pipeline'
    SetParentRunStatus = 'Set Parent Run Status'
    StartRemoteRun = 'Start Remote Run'
    StartRemoteSnapshotRun = 'Start Remote Snapshot Run'
    CancelChildRun = 'Cancel Child Run'
    StartChildRun = 'Start Child Run'
    SetRunProperties = 'Set Run Properties'
    LogMetrics = 'Log Metrics'
    InstantiateRun = 'Get Run'


HTTP_ERROR_MAP = {
    'default':
        {
            'Name': 'Unknown',
            'default': 'An unknown error has occurred.',
            'type': ErrorTypes.Unclassified
        },
    400:
        {
            'Name': 'Bad Request',
            'default': '',
            'type': ErrorTypes.User
        },
    401:
        {
            'Name': 'Unauthorized',
            'default': 'Authentication failed. Please ensure you have access and run az login.',
            API.CreateParentRun: 'Unauthorized to create runs in this workspace or project.',
            API.SetParentRunStatus: 'Unauthorized to modify this parent run.',
            API.StartRemoteRun: 'Unauthorized to start a remote run.',
            API.CancelChildRun: 'Unauthorized to cancel this run.',
            'type': ErrorTypes.User
        },
    403:
        {
            'Name': 'Forbidden',
            'default': 'Forbidden from accessing resources for this workspace or project. Contact the owner to gain'
                       'access and refresh your credentials by running az login.',
            'type': ErrorTypes.User
        },
    404:
        {
            'Name': 'Not Found',
            'default': 'Server not found for this operation. Verify that this data center is supported for AutoML.',
            API.StartRemoteRun: 'Could not find all resources for remote execution. Verify that the compute'
                                'target has been attached to the project and that you are passing the correct'
                                'credentials.',
            API.CancelChildRun: 'Could not find the child run to cancel. You may only cancel in progress run. '
                                'This run may have already completed or has yet to be started.',
            API.SetParentRunStatus: 'Update status failed since parent run could not be found.',
            API.CreateExperiment: 'Could not find all resources for creating an AutoML experiment. Verify that your'
                                  'Azure resource group, workspace, and project all exist.',
            API.GetNextPipeline: 'Could not retrieve all previous scores to predict new pipeline.',
            API.InstantiateRun: 'Could not find this run in this project\'s history. Please verify that this run '
                                'was under the same workspace and resource group.',
            'type': ErrorTypes.User
        },
    408:
        {
            'Name': 'Timeout',
            'default': 'Server operation timed out. Please try again.',
            'type': ErrorTypes.Service
        },
    413:
        {
            'Name': 'Payload too large',
            'default': '',
            API.StartRemoteRun: 'Project folder too large. There is a 2MB limit on the size of the project.',
            'type': ErrorTypes.User
        },
    429:
        {
            'Name': 'Too many requests.',
            'default': 'The server has received too many requests. Please wait and try again later.',
            'type': ErrorTypes.Service
        },
    500:
        {
            'Name': 'Internal Error',
            'default': 'Server ran into an internal error. Please try again.',
            'type': ErrorTypes.Service
        },
    501:
        {
            'Name': 'Not Implemented',
            'default': 'This API has not been implemented. In the case of a new feature, this may not have rolled out'
                       'to your data center.',
            'type': ErrorTypes.User
        },
    503:
        {
            'Name': 'Service Unavailable',
            'default': 'The remote service is down at this time. Please try again.',
            'type': ErrorTypes.Service
        },

    504:
        {
            'Name': 'Gateway Timeout',
            'default': 'Server operation timed out. Please try again.',
            'type': ErrorTypes.Service
        },

}
