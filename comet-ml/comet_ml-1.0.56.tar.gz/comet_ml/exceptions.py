# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

"""
Author: Boris Feld

This module contains comet generated Exceptions

"""

from ._logging import INVALID_API_KEY, INVALID_PROJECT_NAME, INVALID_WORKSPACE_NAME


class CometException(Exception):
    """ Base-class for all comet specific exceptions
    """


class OptimizationMultipleParams(CometException):
    def __str__(self):
        return "You cannot call multiple time set_params or set_params file"


class NotParametrizedException(CometException):
    def __str__(self):
        return "Please call set_params or set_params_file before calling get_suggestion"


class ValidationError(CometException):
    pass


class AuthenticationError(CometException):
    pass


class NoMoreSuggestionsAvailable(CometException):
    def __str__(self):
        return "No more suggestions available!"


class PCSParsingError(CometException):
    """ Exception raised when parsing a PCS file
    """

    def __init__(self, faulty_line):
        self.faulty_line = faulty_line

    def __str__(self):
        # Needed for Python 2, Python 3 correctly displays the faulty line
        return self.faulty_line


class PCSCastingError(CometException):
    def __init__(self, value, pcs_type):
        self.value = value
        self.pcs_type = pcs_type


class OptimizationMissingExperiment(CometException):
    def __str__(self):
        return "You must create an experiment instance to perform optimization"


class InvalidAPIKey(CometException):

    log_message = INVALID_API_KEY

    def __init__(self, api_key):
        super(CometException, self).__init__()
        self.api_key = api_key
        self.args = (self.api_key,)


class InvalidWorkspace(CometException):

    log_message = INVALID_WORKSPACE_NAME

    def __init__(self, workspace):
        super(CometException, self).__init__()
        self.workspace = workspace
        self.args = (self.workspace,)


class ProjectNameEmpty(CometException):

    log_message = INVALID_PROJECT_NAME

    def __init__(self):
        super(CometException, self).__init__()
        self.args = tuple()


class InvalidOfflineDirectory(CometException):
    def __init__(self, directory, reason):
        self.directory = directory
        self.reason = reason

    def __str__(self):
        msg = "Invalid offline directory: %s\nReason:%s"
        return msg % (self.directory, self.reason)


class InterruptedExperiment(KeyboardInterrupt):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        msg = "The experiment has been stopped by user %s from the Comet project page"
        return msg % self.username


class RPCFunctionAlreadyRegistered(CometException):
    def __init__(self, function_name):
        self.function_name = function_name

    def __str__(self):
        msg = "The callback name %r is already taken"
        return msg % self.function_name


class LambdaUnsupported(CometException):
    def __init__(self):
        pass

    def __str__(self):
        return "Lambda are not supported as remote actions"


class BadCallbackArguments(CometException):

    msg = "Remote action %r should accepts at least one argument named `experiment`"

    def __init__(self, callback):
        self.callback = callback

    def __str__(self):
        return self.msg % self.callback


class ExperimentAlreadyUploaded(CometException):
    msg = "Experiment with id %r was already uploaded"

    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def __str__(self):
        return self.msg % self.experiment_id


class FileIsTooBig(CometException):
    msg = "File %r size %d is greater than the upload limit %d"

    def __init__(self, file_path, file_size, max_size):
        self.file_path = file_path
        self.file_size = file_size
        self.max_size = max_size

    def __str__(self):
        return self.msg % (self.file_path, self.file_size, self.max_size)
