# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import traceback


class AzureMLException(Exception):
    """
    Base class for all azureml exceptions.
    Extends Exception, if trying to catch only azureml exceptions
    then catch this class.
    """

    def __init__(self, exception_message, inner_exception=None, **kwargs):
        Exception.__init__(self, exception_message, **kwargs)
        self._exception_message = exception_message
        self._inner_exception = inner_exception
        self._exc_info = sys.exc_info()

    @property
    def message(self):

        return self._exception_message

    @property
    def inner_exception(self):

        return self._inner_exception

    def print_stacktrace(self):
        traceback.print_exception(*self._exc_info)


class TrainingException(AzureMLException):
    """An exception related to failures in configuring, running, or
    updating a training run. Validation of the run configuration covers most of
    the uses of the exception. Other possible sources can be incorrect
    metric names in a training script, which can cause downstream errors during
    hyper parameter tuning.
    """

    def __init__(self, exception_message, **kwargs):
        super(TrainingException, self).__init__(exception_message, **kwargs)


class ExperimentExecutionException(AzureMLException):
    """
    An exception related to failures in configuring, running, or
    updating a submitted run. Validation of the run configuration covers most of
    the uses of the exception. Other possible sources can be failures when
    submitting the experiment run.
    """

    def __init__(self, exception_message, **kwargs):
        super(ExperimentExecutionException, self).__init__(exception_message, **kwargs)


class ProjectSystemException(AzureMLException):
    """
    An exception related to failures while downloading snapshotted project
    files, reading from or setting up the source directory. Common uses of
    this exception include invalid or missing scope information for the
    experiment and workspace.
    """

    def __init__(self, exception_message, **kwargs):
        super(ProjectSystemException, self).__init__(exception_message, **kwargs)


class SnapshotException(AzureMLException):
    """
    An exception related to failures while snapshotting a project. Common
    sources for errors: taking a snapshot after the run already has one,
    directory size limits, and file count limits.
    """

    def __init__(self, exception_message, **kwargs):
        super(SnapshotException, self).__init__(exception_message, **kwargs)


class RunEnvironmentException(AzureMLException):
    """
    An exception related to missing or invalid information related to loading a
    Run from the current environment. Common sources for errors: attempting to
    load a run outside of an execution context.
    """

    def __init__(self, **kwargs):
        super(RunEnvironmentException, self).__init__(
            ("Could not load a submitted run, if outside "
             "of an execution context, use experiment.start_logging to "
             "initialize an azureml.core.Run."), **kwargs)


class WorkspaceException(AzureMLException):
    """
    An exception related to failures while creating or getting a workspace.
    Common sources for the exception are related to permissions and resourcing.
    Ensure that the resource group exists if specified, and that the
    authenticated user has access to the subscription.

    Workspace names are unique within a resource group.
    """

    def __init__(self, exception_message, found_multiple=False, **kwargs):
        super(WorkspaceException, self).__init__(exception_message, **kwargs)
        self.found_multiple = found_multiple


class ComputeTargetException(AzureMLException):
    """
    An exception related to failures when creating, interacting with, or
    configuring a compute target. Common sources for the exception are:
    failures while attaching a compute, missing headers, and unsupported
    configuration values.
    """

    def __init__(self, exception_message, **kwargs):
        super(ComputeTargetException, self).__init__(exception_message, **kwargs)


class AuthenticationException(AzureMLException):
    """
    An exception related to failures in authenticating. The general solution to
    most instances of this exception is to try 'az login' to authenticate
    through the browser. Other sources for the exception include invalid or
    unspecified subscription information trying 'az account set -s {subscription_id}'
    to specify the subscription usually resolves missing or ambiguous
    subscription errors.
    """

    def __init__(self, exception_message, **kwargs):
        super(AuthenticationException, self).__init__(exception_message, **kwargs)


class UserErrorException(AzureMLException):
    """
    An exception related to invalid or unsupported inputs. Common sources for
    this exception include: missing parameters, trying to access an entity that
    does not exist, or invalid value types when configuring a run.
    """

    def __init__(self, exception_message, **kwargs):
        super(UserErrorException, self).__init__(exception_message, **kwargs)


class RunConfigurationException(AzureMLException):
    """
    An exception related to failures in locating or serializing a run
    configuration. Common source for this exception include passing unsupported
    values to the run configuration. Failures in deserialization can be exposed
    after the fact while trying to submit even though the problem was
    introduced earlier.
    """

    def __init__(self, exception_message, **kwargs):
        super(RunConfigurationException, self).__init__(exception_message, **kwargs)


class WebserviceException(AzureMLException):
    """
    An exception related to failures while interacting with model management
    service. Common sources for this exception include failed rest requests to
    model management service.
    """

    def __init__(self, exception_message, status_code=None, logger=None, **kwargs):
        super(WebserviceException, self).__init__(exception_message, **kwargs)
        self.status_code = status_code

        if logger:
            try:
                logger.error(exception_message + '\n')
            except:
                pass


class ModelNotFoundException(AzureMLException):
    """
    An exception related to missing model when attempting to download a
    previously registered model. Common sources for this exception include
    trying to download a model from a different workspace, with the wrong name,
    or an invalid version.
    """

    def __init__(self, exception_message, logger=None, **kwargs):
        super(ModelNotFoundException, self).__init__(exception_message, **kwargs)

        if logger:
            try:
                logger.error(exception_message + '\n')
            except:
                pass


class ModelPathNotFoundException(AzureMLException):
    """
    An exception related to missing model files when registering a model.
    Common sources for this exception is not uploading the model files before
    trying to register the model. Calling Run.upload_file before attempting to
    register the model usually resolves the error.
    """

    def __init__(self, exception_message, logger=None, **kwargs):
        super(ModelPathNotFoundException, self).__init__(exception_message, **kwargs)

        if logger:
            try:
                logger.error(exception_message)
            except:
                pass


class DiscoveryUrlNotFoundException(AzureMLException):
    """
    An exception related to not successfully loading the location from the
    environment. If the environment variable is not found, the SDK makes a
    request to ARM to retrieve the url.
    """

    def __init__(self, discovery_key, **kwargs):
        super(DiscoveryUrlNotFoundException, self).__init__(
            "Could not load discovery key {}, from environment variables.".format(discovery_key), **kwargs)


class ActivityFailedException(AzureMLException):
    """
    An exception related to failures in an activity. Common sources for this
    exception include: failures during submitted experiment runs. The failure
    is generally seen from the control pane specifically during a
    wait_for_completion call on an activity however the source for the failure
    is usually within the activity's logic.
    """

    def __init__(self, error_details, **kwargs):
        super(ActivityFailedException, self).__init__("Activity Failed:\n{}".format(error_details), **kwargs)


class ActivityCanceledException(AzureMLException):
    """
    An exception capturing a run that was canceled. The exception
    is generally seen from the control pane specifically during a
    wait_for_completion call on an activity.
    """

    def __init__(self, cancellation_source=None, **kwargs):
        super(ActivityCanceledException, self).__init__("Activity Canceled", **kwargs)
